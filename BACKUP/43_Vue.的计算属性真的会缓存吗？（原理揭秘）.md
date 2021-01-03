# [Vue 的计算属性真的会缓存吗？（原理揭秘）](https://github.com/sl1673495/blogs/issues/43)

## 前言
很多人提起 Vue 中的 computed，第一反应就是计算属性会缓存，那么它到底是怎么缓存的呢？缓存的到底是什么，什么时候缓存会失效，相信还是有很多人对此很模糊。

本文以 Vue 2.6.11 版本为基础，就深入原理，带你来看看所谓的缓存到底是什么样的。

## 注意
本文假定你对 Vue 响应式原理已经有了基础的了解，如果对于 `Watcher`、`Dep`和什么是 `渲染watcher` 等概念还不是很熟悉的话，可以先找一些基础的响应式原理的文章或者教程看一下。视频教程的话推荐黄轶老师的，如果想要看简化实现，也可以先看我写的文章：

[手把手带你实现一个最精简的响应式系统来学习Vue的data、computed、watch源码](https://juejin.im/post/5db6433b51882564912fc30f)

注意，这篇文章里我也写了 computed 的原理，但是这篇文章里的 computed 是基于 Vue 2.5 版本的，和当前 2.6 版本的变化还是非常大的，可以仅做参考。

## 示例
按照我的文章惯例，还是以一个最简的示例来演示。
```xml
<div id="app">
  <span @click="change">{{sum}}</span>
</div>
<script src="./vue2.6.js"></script>
<script>
  new Vue({
    el: "#app",
    data() {
      return {
        count: 1,
      }
    },
    methods: {
      change() {
        this.count = 2
      },
    },
    computed: {
      sum() {
        return this.count + 1
      },
    },
  })
</script>
```

这个例子很简单，刚开始页面上显示数字 `2`，点击数字后变成 `3`。

## 解析

### 回顾 watcher 的流程
进入正题，Vue 初次运行时会对 computed 属性做一些初始化处理，首先我们回顾一下 watcher 的概念，它的核心概念是 `get` 求值，和 `update` 更新。

1. 在求值的时候，它会先把**自身**也就是 watcher 本身赋值给 `Dep.target` 这个全局变量。

2. 然后求值的过程中，会读取到响应式属性，那么响应式属性的 dep 就会收集到这个 watcher 作为依赖。

3. 下次响应式属性更新了，就会从 dep 中找出它收集到的 watcher，触发 `watcher.update()` 去更新。

所以最关键的就在于，这个 `get` 到底用来做什么，这个 `update` 会触发什么样的更新。

在基本的响应式更新视图的流程中，以上概念的 `get` 求值就是指 Vue 的组件重新渲染的函数，而 `update` 的时候，其实就是重新调用组件的渲染函数去更新视图。

而 Vue 中很巧妙的一点，就是这套流程也同样适用于 computed 的更新。

### 初始化 computed
这里先提前剧透一下，Vue 会对 options 中的每个 computed 属性也用 watcher 去包装起来，它的 `get` 函数显然就是要执行用户定义的求值函数，而 `update` 则是一个比较复杂的流程，接下来我会详细讲解。

首先在组件初始化的时候，会进入到初始化 computed 的函数
```js
if (opts.computed) { initComputed(vm, opts.computed); }
```

进入 `initComputed` 看看
```js
var watchers = vm._computedWatchers = Object.create(null);

// 依次为每个 computed 属性定义
for (const key in computed) {
  const userDef = computed[key]
  watchers[key] = new Watcher(
      vm, // 实例
      getter, // 用户传入的求值函数 sum
      noop, // 回调函数 可以先忽视
      { lazy: true } // 声明 lazy 属性 标记 computed watcher
  )

  // 用户在调用 this.sum 的时候，会发生的事情
  defineComputed(vm, key, userDef)
}
```

首先定义了一个空的对象，用来存放所有计算属性相关的 watcher，后文我们会把它叫做 `计算watcher`。

然后循环为每个 computed 属性生成了一个 `计算watcher`。

它的形态保留关键属性简化后是这样的：
```js
{
    deps: [],
    dirty: true,
    getter: ƒ sum(),
    lazy: true,
    value: undefined
}
```

可以看到它的 `value` 刚开始是 undefined，`lazy` 是 true，说明它的值是惰性计算的，只有到真正在模板里去读取它的值后才会计算。

这个 `dirty` 属性其实是缓存的关键，先记住它。

接下来看看比较关键的 `defineComputed`，它决定了用户在读取 `this.sum` 这个计算属性的值后会发生什么，继续简化，排除掉一些不影响流程的逻辑。

```js
Object.defineProperty(target, key, { 
    get() {
        // 从刚刚说过的组件实例上拿到 computed watcher
        const watcher = this._computedWatchers && this._computedWatchers[key]
        if (watcher) {
          // ✨ 注意！这里只有dirty了才会重新求值
          if (watcher.dirty) {
            // 这里会求值 调用 get
            watcher.evaluate()
          }
          // ✨ 这里也是个关键 等会细讲
          if (Dep.target) {
            watcher.depend()
          }
          // 最后返回计算出来的值
          return watcher.value
        }
    }
})
```

这个函数需要仔细看看，它做了好几件事，我们以初始化的流程来讲解它：

首先 `dirty` 这个概念代表脏数据，说明这个数据需要重新调用用户传入的 `sum` 函数来求值了。我们暂且不管更新时候的逻辑，第一次在模板中读取到  `{{sum}}` 的时候它一定是 true，所以初始化就会经历一次求值。

```js
evaluate () {
  // 调用 get 函数求值
  this.value = this.get()
  // 把 dirty 标记为 false
  this.dirty = false
}
```

这个函数其实很清晰，它先求值，然后把 `dirty` 置为 false。

再回头看看我们刚刚那段 `Object.defineProperty` 的逻辑，

下次没有特殊情况再读取到 `sum` 的时候，发现 `dirty`是false了，是不是直接就返回 `watcher.value` 这个值就可以了，这其实就是**计算属性缓存**的概念。

### 更新
初始化的流程讲完了，相信大家也对 `dirty` 和 `缓存` 有了个大概的概念（如果没有，再仔细回头看一看）。

接下来就讲更新的流程，细化到本文的例子中，也就是 `count` 的更新到底是怎么触发 `sum` 在页面上的变更。

首先回到刚刚提到的 `evalute` 函数里，也就是读取 `sum` 时发现是脏数据的时候做的求值操作。

```js
evaluate () {
  // 调用 get 函数求值
  this.value = this.get()
  // 把 dirty 标记为 false
  this.dirty = false
}
```

####  Dep.target 变更为 渲染watcher
这里进入 `this.get()`，首先要明确一点，在模板中读取 `{{ sum }}` 变量的时候，全局的 `Dep.target` 应该是 `渲染watcher`，这里不理解的话可以到我最开始提到的文章里去理解下。

全局的 `Dep.target` 状态是用一个栈 `targetStack` 来保存，便于前进和回退 `Dep.target`，至于什么时候会回退，接下来的函数里就可以看到。

```!
此时的 Dep.target 是 渲染watcher，targetStack 是 [ 渲染watcher ] 。
```

```js
get () {
  pushTarget(this)
  let value
  const vm = this.vm
  try {
    value = this.getter.call(vm, vm)
  } finally {
    popTarget()
  }
  return value
}
```

首先刚进去就 `pushTarget`，也就是把 `计算watcher` 自身置为 `Dep.target`，等待收集依赖。


执行完 `pushTarget(this)` 后，

####  Dep.target 变更为 计算watcher

```!
此时的 Dep.target 是 计算watcher，targetStack 是 [ 渲染watcher，计算watcher ] 。
```

`getter` 函数，上一章的 watcher 形态里已经说明了，其实就是用户传入的 `sum` 函数。

```js
sum() {
    return this.count + 1
}
```

这里在执行的时候，读取到了 `this.count`，注意它是一个响应式的属性，所以冥冥之中它们开始建立了千丝万缕的联系……

这里会触发 `count` 的 `get` 劫持，简化一下

```js
// 在闭包中，会保留对于 count 这个 key 所定义的 dep
const dep = new Dep()

// 闭包中也会保留上一次 set 函数所设置的 val
let val

Object.defineProperty(obj, key, {
  get: function reactiveGetter () {
    const value = val
    // Dep.target 此时就是计算watcher
    if (Dep.target) {
      // 收集依赖
      dep.depend()
    }
    return value
  },
})
```

那么可以看出，`count` 会收集 `计算watcher` 作为依赖，具体怎么收集呢

```js
// dep.depend()
depend () {
  if (Dep.target) {
    Dep.target.addDep(this)
  }
}
```

其实这里是调用 `Dep.target.addDep(this)` 去收集，又绕回到 `计算watcher` 的 `addDep` 函数上去了，这其实主要是 Vue 内部做了一些去重的优化。

```js
// watcher 的 addDep函数
addDep (dep: Dep) {
  // 这里做了一系列的去重操作 简化掉 
  
  // 这里会把 count 的 dep 也存在自身的 deps 上
  this.deps.push(dep)
  // 又带着 watcher 自身作为参数
  // 回到 dep 的 addSub 函数了
  dep.addSub(this)
}
```

又回到 `dep` 上去了。

```js
class Dep {
  subs = []

  addSub (sub: Watcher) {
    this.subs.push(sub)
  }
}
```

这样就保存了 `计算watcher` 作为 `count` 的 dep 里的依赖了。

经历了这样的一个收集的流程后，此时的一些状态：

`sum 的计算watcher`：

```js
{
    deps: [ count的dep ],
    dirty: false, // 求值完了 所以是false
    value: 2, // 1 + 1 = 2
    getter: ƒ sum(),
    lazy: true
}
```

`count的dep`: 
```js
{
    subs: [ sum的计算watcher ]
}
```

可以看出，计算属性的 watcher 和它所依赖的响应式值的 dep，它们之间互相保留了彼此，相依为命。

此时求值结束，回到 `计算watcher` 的 `getter` 函数：

```js
get () {
  pushTarget(this)
  let value
  const vm = this.vm
  try {
    value = this.getter.call(vm, vm)
  } finally {
    // 此时执行到这里了
    popTarget()
  }
  return value
}
```

执行到了 `popTarget`，`计算watcher` 出栈。

####  Dep.target 变更为 渲染watcher
```!
此时的 Dep.target 是 渲染watcher，targetStack 是 [ 渲染watcher ] 。
```

然后函数执行完毕，返回了 `2` 这个 value，此时对于 `sum` 属性的 `get` 访问还没结束。

```js
Object.defineProperty(vm, 'sum', { 
    get() {
          // 此时函数执行到了这里
          if (Dep.target) {
            watcher.depend()
          }
          return watcher.value
        }
    }
})
```

此时的 `Dep.target` 当然是有值的，就是 `渲染watcher`，所以进入了 `watcher.depend()` 的逻辑，这一步**相当关键**。

```js
// watcher.depend
depend () {
  let i = this.deps.length
  while (i--) {
    this.deps[i].depend()
  }
}
```

还记得刚刚的 `计算watcher` 的形态吗？它的 `deps` 里保存了 `count` 的 dep。

也就是说，又会调用 `count` 上的 `dep.depend()`

```js
class Dep {
  subs = []
  
  depend () {
    if (Dep.target) {
      Dep.target.addDep(this)
    }
  }
}
```

这次的 `Dep.target` 已经是 `渲染watcher` 了，所以这个 `count` 的 dep 又会把 `渲染watcher` 存放进自身的 `subs` 中。

`count的dep`: 
```js
{
    subs: [ sum的计算watcher，渲染watcher ]
}
```

那么来到了此题的重点，这时候 `count` 更新了，是如何去触发视图更新的呢？

再回到 `count` 的响应式劫持逻辑里去：

```js
// 在闭包中，会保留对于 count 这个 key 所定义的 dep
const dep = new Dep()

// 闭包中也会保留上一次 set 函数所设置的 val
let val

Object.defineProperty(obj, key, {
  set: function reactiveSetter (newVal) {
      val = newVal
      // 触发 count 的 dep 的 notify
      dep.notify()
    }
  })
})
```

好，这里触发了我们刚刚精心准备的 `count` 的 dep 的 `notify` 函数，感觉离成功越来越近了。

```js
class Dep {
  subs = []
  
  notify () {
    for (let i = 0, l = subs.length; i < l; i++) {
      subs[i].update()
    }
  }
}

```

这里的逻辑就很简单了，把 `subs` 里保存的 watcher 依次去调用它们的 `update` 方法，也就是

1. 调用 `计算watcher` 的 update
2. 调用 `渲染watcher` 的 update

拆解来看。

#### 计算watcher 的 update

```js
update () {
  if (this.lazy) {
    this.dirty = true
  }
}
```

wtf，就这么一句话…… 没错，就仅仅是把 `计算watcher` 的 `dirty` 属性置为 true，静静的等待下次读取即可。

#### 渲染watcher 的 update

这里其实就是调用 `vm._update(vm._render())` 这个函数，重新根据 `render` 函数生成的 `vnode` 去渲染视图了。

而在 `render` 的过程中，一定会访问到 `sum` 这个值，那么又回回到 `sum` 定义的 `get` 上：

```js
Object.defineProperty(target, key, { 
    get() {
        const watcher = this._computedWatchers && this._computedWatchers[key]
        if (watcher) {
          // ✨上一步中 dirty 已经置为 true, 所以会重新求值
          if (watcher.dirty) {
            watcher.evaluate()
          }
          if (Dep.target) {
            watcher.depend()
          }
          // 最后返回计算出来的值
          return watcher.value
        }
    }
})
```

由于上一步中的响应式属性更新，触发了 `计算 watcher` 的 `dirty` 更新为 true。 所以又会重新调用用户传入的 `sum` 函数计算出最新的值，页面上自然也就显示出了最新的值。

至此为止，整个计算属性更新的流程就结束了。


## 缓存生效的情况
根据上面的总结，只有计算属性依赖的响应式值发生更新的时候，才会把 `dirty` 重置为 true，这样下次读取的时候才会发生真正的计算。

这样的话，假设 `sum` 函数是一个用户定义的一个比较耗费时间的操作，优化就比较明显了。

```xml
<div id="app">
  <span @click="change">{{sum}}</span>
  <span @click="changeOther">{{other}}</span>
</div>
<script src="./vue2.6.js"></script>
<script>
  new Vue({
    el: "#app",
    data() {
      return {
        count: 1,
        other: 'Hello'
      }
    },
    methods: {
      change() {
        this.count = 2
      },
      changeOther() {
        this.other = 'ssh'
      }
    },
    computed: {
      // 非常耗时的计算属性
      sum() {
        let i = 100000
        while(i > 0) {
            i--
        }
        return this.count + 1
      },
    },
  })
</script>
```

在这个例子中，`other` 的值和计算属性没有任何关系，如果 `other` 的值触发更新的话，就会重新渲染视图，那么会读取到 `sum`，如果计算属性不做缓存的话，每次都要发生一次很耗费性能的没有必要的计算。

所以，只有在 `count` 发生变化的时候，`sum` 才会重新计算，这是一个很巧妙的优化。

## 总结
2.6 版本计算属性更新的路径是这样的：

1. 响应式的值 `count` 更新
2. 同时通知 `computed watcher` 和 `渲染 watcher` 更新 
3. `omputed watcher` 把 dirty 设置为 true 
4. 视图渲染读取到 computed 的值，由于 dirty 所以 `computed watcher` 重新求值。

通过本篇文章，相信你可以完全理解计算属性的缓存到底是什么概念，在什么样的情况下才会生效了吧？

对于缓存和不缓存的情况，分别是这样的流程：

### 不缓存：

1. `count` 改变，先通知到 `计算watcher` 更新，设置 `dirty = true` 
2. 再通知到 `渲染watcher` 更新，视图重新渲染的时候去 `计算watcher` 中读取值，发现 `dirty` 是 true，重新执行用户传入的函数求值。

### 缓存：
1. `other` 改变，直接通知 `渲染watcher` 更新。
2. 视图重新渲染的时候去 `计算watcher` 中读取值，发现 `dirty` 为 false，直接用缓存值 `watcher.value`，不执行用户传入的函数求值。

## 展望
事实上这种通过 `dirty` 标志位来实现计算属性缓存的方式，和 Vue3 中的实现原理是一致的。这可能也说明在各种需求和社区反馈的千锤百炼下，尤大目前认为这种方式是实现 computed 缓存的相对最优解了。

如果对 Vue3 的 computed 实现感兴趣的同学，还可以看我的这篇文章，原理大同小异。只是收集的方式稍有变化。

[深度解析：Vue3如何巧妙的实现强大的computed](https://juejin.im/post/5e2fdf29e51d45026866107d)

## ❤️感谢大家
1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)