---
title: 'Vue 的生命周期之间到底做了什么事清？（源码详解）'
date: '2020-04-04'
spoiler: ''
---

## 前言
相信大家对 Vue 有哪些生命周期早就已经烂熟于心，但是对于这些生命周期的前后分别做了哪些事情，可能还有些不熟悉。

本篇文章就从一个完整的流程开始，详细讲解各个生命周期之间发生了什么事情。

注意本文不涉及 `keep-alive` 的场景和错误处理的场景。

## 初始化流程
### new Vue
从 `new Vue(options)` 开始作为入口，`Vue` 只是一个简单的构造函数，内部是这样的：
```js
function Vue (options) {
  this._init(options)
}
```

进入了 `_init` 函数之后，先初始化了一些属性，然后开始第一个生命周期：
```js
callHook(vm, 'beforeCreate')
```

### beforeCreate被调用完成
`beforeCreate` 之后
1. 初始化 `inject`
2. 初始化 `state`
   - 初始化 `props`
   - 初始化 `methods`
   - 初始化 `data`
   - 初始化 `computed`
   - 初始化 `watch`
3. 初始化 `provide`

所以在 `data` 中可以使用 `props` 上的值，反过来则不行。

然后进入 `created` 阶段：

```js
callHook(vm, 'created')
```

### created被调用完成
调用 `$mount` 方法，开始挂载组件到 `dom` 上。

如果使用了 `runtime-with-compile` 版本，则会把你传入的 `template` 选项，或者 `html` 文本，通过一系列的编译生成 `render` 函数。
 - 编译这个 `template`，生成 `ast` 抽象语法树。
 - 优化这个 `ast`，标记静态节点。（渲染过程中不会变的那些节点，优化性能）。
 - 根据 `ast`，生成 `render` 函数。

对应具体的代码就是：
```js
const ast = parse(template.trim(), options)
if (options.optimize !== false) {
  optimize(ast, options)
}
const code = generate(ast, options)
```

如果是脚手架搭建的项目的话，这一步 `vue-cli` 已经帮你做好了，所以就直接进入 `mountComponent` 函数。

那么，确保有了 `render` 函数后，我们就可以往`渲染`的步骤继续进行了

### beforeMount被调用完成
把 `渲染组件的函数` 定义好，具体代码是：
```js
updateComponent = () => {
  vm._update(vm._render(), hydrating)
}
```

拆解来看，`vm._render` 其实就是调用我们上一步拿到的 `render` 函数生成一个 `vnode`，而 `vm._update` 方法则会对这个 `vnode` 进行 `patch` 操作，帮我们把 `vnode` 通过 `createElm`函数创建新节点并且渲染到 `dom节点` 中。

接下来就是执行这段代码了，是由 `响应式原理` 的一个核心类 `Watcher` 负责执行这个函数，为什么要它来代理执行呢？因为我们需要在这段过程中去 `观察` 这个函数读取了哪些响应式数据，将来这些响应式数据更新的时候，我们需要重新执行 `updateComponent` 函数。

如果是更新后调用 `updateComponent` 函数的话，`updateComponent` 内部的 `patch` 就不再是初始化时候的创建节点，而是对新旧 `vnode` 进行 `diff`，最小化的更新到 `dom节点` 上去。具体过程可以看我的上一篇文章：

[为什么 Vue 中不要用 index 作为 key？（diff 算法详解）](https://juejin.im/post/5e8694b75188257372503722)

这一切交给 `Watcher` 完成：

```js
new Watcher(vm, updateComponent, noop, {
  before () {
    if (vm._isMounted) {
      callHook(vm, 'beforeUpdate')
    }
  }
}, true /* isRenderWatcher */)
```
注意这里在`before` 属性上定义了`beforeUpdate` 函数，也就是说在 `Watcher` 被响应式属性的更新触发之后，重新渲染新视图之前，会先调用 `beforeUpdate` 生命周期。

关于 `Watcher` 和响应式的概念，如果你还不清楚的话，可以阅读我之前的文章：

[手把手带你实现一个最精简的响应式系统来学习Vue的data、computed、watch源码](https://juejin.im/post/5db6433b51882564912fc30f)

注意，在 `render` 的过程中，如果遇到了 `子组件`，则会调用 `createComponent` 函数。

`createComponent` 函数内部，会为子组件生成一个属于自己的`构造函数`，可以理解为子组件自己的 `Vue` 函数：

```js
Ctor = baseCtor.extend(Ctor)
```

在普通的场景下，其实这就是 `Vue.extend` 生成的构造函数，它继承自 `Vue` 函数，拥有它的很多全局属性。

这里插播一个知识点，除了组件有自己的`生命周期`外，其实 `vnode` 也是有自己的 `生命周期的`，只不过我们平常开发的时候是接触不到的。

那么`子组件的 vnode` 会有自己的 `init` 周期，这个周期内部会做这样的事情：
```js
// 创建子组件
const child = createComponentInstanceForVnode(vnode)
// 挂载到 dom 上
child.$mount(vnode.elm)
```

而 `createComponentInstanceForVnode` 内部又做了什么事呢？它会去调用 `子组件` 的构造函数。

```js
new vnode.componentOptions.Ctor(options)
```

构造函数的内部是这样的：
```js
const Sub = function VueComponent (options) {
  this._init(options)
}
```

这个 `_init` 其实就是我们文章开头的那个函数，也就是说，如果遇到 `子组件`，那么就会优先开始`子组件`的构建过程，也就是说，从 `beforeCreated` 重新开始。这是一个递归的构建过程。

也就是说，如果我们有 `父 -> 子 -> 孙` 这三个组件，那么它们的初始化生命周期顺序是这样的：
```js
父 beforeCreate 
父 create 
父 beforeMount 
子 beforeCreate 
子 create 
子 beforeMount 
孙 beforeCreate 
孙 create 
孙 beforeMount 
孙 mounted 
子 mounted 
父 mounted 
```

然后，`mounted` 生命周期被触发。

### mounted被调用完成
到此为止，组件的挂载就完成了，初始化的生命周期结束。

## 更新流程
当一个响应式属性被更新后，触发了 `Watcher` 的回调函数，也就是 `vm._update(vm._render())`，在更新之前，会先调用刚才在 `before` 属性上定义的函数，也就是

```js
callHook(vm, 'beforeUpdate')
```

注意，由于 Vue 的异步更新机制，`beforeUpdate` 的调用已经是在 `nextTick` 中了。
具体代码如下：
```js
nextTick(flushSchedulerQueue)

function flushSchedulerQueue {
  for (index = 0; index < queue.length; index++) {
    watcher = queue[index]
    if (watcher.before) {
     // callHook(vm, 'beforeUpdate')
      watcher.before()
    }
 }
}
```

### beforeUpdate被调用完成

然后经历了一系列的 `patch`、`diff` 流程后，组件重新渲染完毕，调用 `updated` 钩子。

注意，这里是对 `watcher` 倒序 `updated` 调用的。

也就是说，假如同一个属性通过 `props` 分别流向 `父 -> 子 -> 孙` 这个路径，那么收集到依赖的先后也是这个顺序，但是触发 `updated` 钩子确是 `孙 -> 子 -> 父` 这个顺序去触发的。

```js
function callUpdatedHooks (queue) {
  let i = queue.length
  while (i--) {
    const watcher = queue[i]
    const vm = watcher.vm
    if (vm._watcher === watcher && vm._isMounted) {
      callHook(vm, 'updated')
    }
  }
}
```

### updated被调用完成
至此，渲染更新流程完毕。

## 销毁流程
在刚刚所说的更新后的 `patch` 过程中，如果发现有组件在下一轮渲染中消失了，比如 `v-for` 对应的数组中少了一个数据。那么就会调用 `removeVnodes` 进入组件的销毁流程。

`removeVnodes` 会调用 `vnode` 的 `destroy` 生命周期，而 `destroy` 内部则会调用我们相对比较熟悉的 `vm.$destroy()`。（keep-alive 包裹的子组件除外）

这时，就会调用 `callHook(vm, 'beforeDestroy')`

### beforeDestroy被调用完成

之后就会经历一系列的`清理`逻辑，清除父子关系、`watcher` 关闭等逻辑。但是注意，`$destroy` 并不会把组件从视图上移除，如果想要手动销毁一个组件，则需要我们自己去完成这个逻辑。

然后，调用最后的 `callHook(vm, 'destroyed')`

### destroyed被调用完成

## 总结
至此为止，Vue 的生命周期我们就完整的回顾了一遍。知道各个生命周期之间发生了什么事，可以让我们在编写 Vue 组件的过程中更加胸有成竹。

希望这篇文章对你有帮助。

## ❤️感谢大家
1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17146620730c6889?w=573&h=265&f=jpeg&s=54095)