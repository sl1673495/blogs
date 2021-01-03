# [Vue源码学习 观察属性watch](https://github.com/sl1673495/blogs/issues/9)

上一篇介绍computed的文章讲到了，良好的设计对于功能的实现非常有帮助，computed的核心实现原理是计算watcher，那么watch其实也是基于watcher来实现的，我们还是从initWatch初始化看起。

### initWatch
```js
function initWatch (vm, watch) {
  for (var key in watch) {
    // 遍历用户定义的watch属性 
    var handler = watch[key];
   // 如果watch是数组 就循环createWatcher
    if (Array.isArray(handler)) {
      for (var i = 0; i < handler.length; i++) {
        createWatcher(vm, key, handler[i]);
      }
    } else {
      // 否则直接createWatcher
      createWatcher(vm, key, handler);
    }
  }
}
```

我们可以看到，对于用户定义的单个watch属性，最终vue调用了createWatcher方法

### createWatcher
```js
function createWatcher (
  vm,
  expOrFn,
  handler,
  options
) {
  if (isPlainObject(handler)) {
    options = handler;
    handler = handler.handler;
  }
  if (typeof handler === 'string') {
    handler = vm[handler];
  }
  return vm.$watch(expOrFn, handler, options)
}
```

这段代码的开头对参数进行了规范化，因为watch是可以支持多种形式的。
```js
{
   key: function() {}
}
{
   key: {
      handle: function() {},
      deep: true,
  }
}
```

最终调用了$watch，第一个参数是要观测的key或者'a.b.c'这样的表达式，handler是用户定义的回调函数，options是{deep: true}这样的watch配置
```js
 vm.$watch(expOrFn, handler, options)
```

### $watch
在vue中以$开头的api一般也提供给用户在外部使用，所以我们在外部也可以通过函数的方式去调用$watch, 比如
```js
this.$watch(
  'a', 
  function() {}, 
  { deep: true }
)
```

接下来我们来看看$watch的实现
```js
Vue.prototype.$watch = function (
    expOrFn,
    cb,
    options
  ) {
    var vm = this;
    if (isPlainObject(cb)) {
      return createWatcher(vm, expOrFn, cb, options)
    }
    // 把options的user属性设为true，让watcher内部使用
    options = options || {};
    options.user = true;
    // 调用Watcher
    var watcher = new Watcher(vm, expOrFn, cb, options);
    if (options.immediate) {
      cb.call(vm, watcher.value);
    }
    return function unwatchFn () {
      watcher.teardown();
    }
  };
```
可以看到， 在把options的user设为true以后，
调用了
```js
var watcher = new Watcher(vm, expOrFn, cb, options);
```
我们看看这段函数进入Watcher以后会做什么

### Watcher
进入了watcher的构造函数以后
```js
 if (options) {
    this.deep = !!options.deep;
    this.user = !!options.user;
    this.computed = !!options.computed;
    this.sync = !!options.sync;
    this.before = options.before;
  }
this.cb = cb;
```
这个watcher示例的user属性会被设置为true，
sync属性也会被设置为用户定义的sync 表示这个watcher的update函数会同步执行。

```js
if (typeof expOrFn === 'function') {
    this.getter = expOrFn;
  } else {
    this.getter = parsePath(expOrFn);
    if (!this.getter) {
      this.getter = function () {};
      process.env.NODE_ENV !== 'production' && warn(
        "Failed watching path: \"" + expOrFn + "\" " +
        'Watcher only accepts simple dot-delimited paths. ' +
        'For full control, use a function instead.',
        vm
      );
    }
  }
```
这时候我们的expOrFn应该是个key 或者 'a.b.c'这样的访问路径，所以会进入else逻辑。
首先看
```js
this.getter = parsePath(expOrFn);
```

### parsePath
```js
var bailRE = /[^\w.$]/;
function parsePath (path) {
  if (bailRE.test(path)) {
    return
  }
  var segments = path.split('.');
  return function (obj) {
    for (var i = 0; i < segments.length; i++) {
      if (!obj) { return }
      obj = obj[segments[i]];
    }
    return obj
  }
}
```
我们还是以a.b.c这个路径为例，
segments被以.号分隔成['a','b','c']这样的数组，
然后返回一个函数
```js
function (obj) {
    for (var i = 0; i < segments.length; i++) {
      if (!obj) { return }
      obj = obj[segments[i]];
    }
    return obj
}
```
这个函数接受一个对象 然后会依次去访问对象的.a 再去访问.a.b 再去访问.a.b.c，
其实这个的目的就是在访问的过程中为这些属性下挂载的dep去收集依赖。

回到我们的watcher的初始化，接下来执行的是
```js
if (this.computed) {
    this.value = undefined;
    this.dep = new Dep();
  } else {
    this.value = this.get();
  }
```
显然我们会走else逻辑，我们继续看this.get()
### Watcher.prototype.get
```js
Watcher.prototype.get = function get () {
  // 将全局的Dep.target设置成这个watch属性的watcher
  pushTarget(this);
  var value;
  var vm = this.vm;
  try {
    // 调用刚刚生成的getter函数，就是parsePath返回的那个函数
    // 这里把vm作为obj传入，所以会依次去读取vm.a vm.a.b vm.a.b.c 并且为这几个元素都收集了依赖。
    value = this.getter.call(vm, vm);
  } catch (e) {
    if (this.user) {
      handleError(e, vm, ("getter for watcher \"" + (this.expression) + "\""));
    } else {
      throw e
    }
  } finally {
    // "touch" every property so they are all tracked as
    // dependencies for deep watching
    if (this.deep) {
      // 如果watch的options里设置了deep，就递归的去收集依赖。
      traverse(value);
    }
    // 收集完毕，将Dep.target弹出栈
    popTarget();
    this.cleanupDeps();
  }
  return value
};
```

至此为止，我们vm下的a a下的b b下的c都收集了这个watcher作为依赖，
那么当这些值中的任意值进行改变， 会触发他们内部dep.notify()

### dep.notify
```js
Dep.prototype.notify = function notify () {
  // stabilize the subscriber list first
  var subs = this.subs.slice();
  for (var i = 0, l = subs.length; i < l; i++) {
    subs[i].update();
  }
};
```
subs[i].update()其实就是调用了watcher的update方法，再回到watcher

### watcher.update()
```js
Watcher.prototype.update = function update () {
   // 省略多余逻辑
   if (this.sync) {
    this.run();
   } else {
    queueWatcher(this);
  }
};
```
这个update是省略掉其他逻辑的，我们之前说过 如果watch的sync设置为true，
那么就会直接执行 this.run();

### watcher.run
```js
Watcher.prototype.run = function run () {
  if (this.active) {
    this.getAndInvoke(this.cb);
  }
};
```
这里调用了getAndInvoke(this.cb)，将我们定义的watch回调函数传入
### watcher.getAndInvoke
```js
Watcher.prototype.getAndInvoke = function getAndInvoke (cb) {
  var value = this.get();
  if (
    value !== this.value ||
    isObject(value) ||
    this.deep
  ) {
    if (this.user) {
      try {
        cb.call(this.vm, value, oldValue);
      } catch (e) {
        handleError(e, this.vm, ("callback for watcher \"" + (this.expression) + "\""));
      }
    }
  }
};
```
其实就是做了个判断，如果上一次的值和这次的值不相等，或者deep为true，都会直接出发cb.call(this.vm)，并且将新值和旧值传入，这就是我们可以在watch的回调函数里获取新值和旧值的来源。

至此watch函数的实现就分析完毕了，再次感叹一下，良好的设计是成功的开端啊！