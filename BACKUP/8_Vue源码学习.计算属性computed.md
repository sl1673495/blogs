# [Vue源码学习 计算属性computed](https://github.com/sl1673495/blogs/issues/8)

上一篇讲解（摘抄）了Vue响应式实现的原理，良好的设计为很多看似复杂的功能奠定了基础，使得这些功能的实际实现变得很简单。

**我们先得出个结论，Watcher这个类即可以用做渲染函数的watcher， 也可以用作计算属性的Watcher，这两者在初始化和部分函数的分支都是不同的， watcher的更新核心方法是update，可以说计算属性的update是为了驱动渲染watcher的update，而渲染watcher的update是为了重新调用vm._update(vm._render())方法去更新真正的页面。**

首先来看初始化函数的简化版本

### initComputed
```js
function initComputed (vm: Component, computed: Object) {
  const watchers = vm._computedWatchers = Object.create(null)

  for (const key in computed) {
    const userDef = computed[key]
    const getter = typeof userDef === 'function' ? userDef : userDef.get

   watchers[key] = new Watcher(
        vm,
        getter || noop,
        noop,
        computedWatcherOptions
    )

    if (!(key in vm)) {
      defineComputed(vm, key, userDef)
    }
  }
}
```
vm就是vue实例，computed就是用户定义的computed对象。

首先定义了watchers数组和vm.__computedWatchers为一个空对象
```js
  const watchers = vm._computedWatchers = Object.create(null)
```
接下来遍历用户传入的computed对象，computed里面可以是
```js
key: {
  get: ...,
  set: ...
}
```
的形式，也可以是
```js
key: function() {}
```
的形式， 所以先取到这个getter函数，
```js
const userDef = computed[key]
const getter = typeof userDef === 'function' ? userDef : userDef.get
```

然后为每个computed的key生成一个watcher观察者， getter就是用户传入的计算函数
```js
watchers[key] = new Watcher(
        vm,
        getter || noop,
        noop,
        computedWatcherOptions
 )
```
computedWatcherOptions其实就是{ computed: true }这个对象，这会使得watcher被初始化为计算属性的watcher（下文简称计算watcher）,

在watcher构造函数里有这么一段，
可以看到计算watcher的value被初始化为undefined，这说明了计算属性是惰性求值，并且计算watcher的实例下定义了this.dep = new Dep()。
```js
if (this.computed) {
      this.value = undefined
      this.dep = new Dep()
    } else {
      this.value = this.get()
    }
```


```js
defineComputed(vm, key, userDef)
```

在这之后调用了defineComputed把计算属性的key代理到了this下面，getter就定义为createComputedGetter(key),先看看createComputedGetter做了什么。
```js
function createComputedGetter (key) {
  return function computedGetter () {
    const watcher = this._computedWatchers && this._computedWatchers[key]
    if (watcher) {
      watcher.depend()
      return watcher.evaluate()
    }
  }
}
```
条件判断语句中有两句关键的代码，我们分开来看
```js
 watcher.depend()
 return watcher.evaluate()
```

### watcher.depend()

这个getter函数会在渲染模板遇到{{ computedValue }}这样的值的时候触发。
这时会先取到key对应的计算watcher， 并且调用watcher的depend()方法收集依赖。
```js
  /**
   * Depend on this watcher. Only for computed property watchers.
   */
  depend () {
    if (this.dep && Dep.target) {
      this.dep.depend()
    }
  }
```
this.dep就是在初始化时为watcher生成的，可以思考一下在这个时候调用dep的depend会收集到什么，我们来看看dep的depend
```js
 depend () {
    if (Dep.target) {
      Dep.target.addDep(this)
    }
  }

```
因为正在根据template生成对应的真实dom，所以这个时候的Dep.target一定是当前组件的**渲染watcher**，那么其实这个dep收集到的就是渲染watcher。

到这个时候，依赖收集完成了。 那我们接下来看
### return watcher.evaluate()
```js
  evaluate () {
    if (this.dirty) {
      this.value = this.get()
      this.dirty = false
    }
    return this.value
  }

```
这个其实是专为计算watcher设计的求值函数，this.dirty一定是在计算watcher的情况下才为true，
这时候会把this.value调用this.get()去求值，我们来看看this.get做了什么。

```js
  get () {
    pushTarget(this)
    let value
    const vm = this.vm
    try {
      value = this.getter.call(vm, vm)
    } catch (e) {
      if (this.user) {
        handleError(e, vm, `getter for watcher "${this.expression}"`)
      } else {
        throw e
      }
    } finally {
      // "touch" every property so they are all tracked as
      // dependencies for deep watching
      if (this.deep) {
        traverse(value)
      }
      popTarget()
      this.cleanupDeps()
    }
    return value
  }
```
首先调用pushTarget(this)， 把计算watcher设置为现在的全局Dep.target，这样其他的dep收集依赖就会收集到计算watcher了， 然后
```js
 value = this.getter.call(vm, vm)
```
这个时候的getter就会调用用户自定义的计算函数 比如
```js
computed: {
  sum() {
     return this.a + this. b
  }
}
```
那么此时的getter会去调用return this.a + this. b,
而在求这个值的过程中， 又会触发a和b的dep的depend， 这个时候a和b都会收集到这个计算watcher作为依赖

那么我们之后再一些methods里写this.a = 2 这样去改变a的值， 会触发a的dep去通知计算watcher去做update， 计算watcher的update方法又会去
```js
this.dep.notify()
```
触发watcher的dep的notify， 这个dep收集了渲染watcher， 这样会驱动渲染watcher去执行update()就会去重新渲染页面， 这样就达成了修改a属性去触发依赖a的视图和依赖sum的视图重新进行渲染。
```js
 update () {
    queueWatcher(this)
  }
```
queueWatcher会在nextTick执行watcher.run()
```js
run () {
    if (this.active) {
      this.getAndInvoke(this.cb)
    }
  }
```
此时的this.cb 是渲染watcher的cb 也就是vm._update(vm._render())
这样页面就会重新渲染，更新视图

---

关于计算属性的缓存，在网上看过挺多篇文章并没有讲的很清楚，今天我们从源码来分析一下它这个缓存到底是怎么做的。

首先我们知道 当依赖值a改变的时候 a会触发dep.notify 这个dep里收集了计算属性sum的watcher 会触发这个watcher的update， 我们来看update里关键的节选
```js
update () {
    if (this.computed) {
      ....
        this.getAndInvoke(() => {
          this.dep.notify()
        })
    }
  }
```
我们会把触发渲染watcher更新的this.dep.notify包裹在 this.getAndInvoke内部，那我们来看看那 this.getAndInvoke做了什么

```js
getAndInvoke (cb: Function) {
    const value = this.get()
    if (
      value !== this.value ||
      isObject(value) ||
      this.deep
    ) {
      const oldValue = this.value
      this.value = value
      this.dirty = false
      if (this.user) {
        try {
          cb.call(this.vm, value, oldValue)
        } catch (e) {
          handleError(e, this.vm, `callback for watcher "${this.expression}"`)
        }
      } else {
        cb.call(this.vm, value, oldValue)
      }
    }
  }
```
首先会调用this.get() ，获取到当前计算属性最新的值，然后去和上次计算属性的值进行比较，只有在值发生变化以后才回去执行接下来的回调， 才会去触发视图的重新渲染，这也就是为什么说新版的计算属性是更多计算，更少的更新。