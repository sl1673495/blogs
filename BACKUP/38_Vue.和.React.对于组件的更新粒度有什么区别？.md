# [Vue 和 React 对于组件的更新粒度有什么区别？](https://github.com/sl1673495/blogs/issues/38)

## 前言
我们都知道 Vue 对于响应式属性的更新，只会精确更新依赖收集的`当前组件`，而不会递归的去更新子组件，这也是它性能强大的原因之一。

## 例子
举例来说 这样的一个组件：
```xml
<template>
   <div>
      {{ msg }}
      <ChildComponent />
   </div>
</template>
```
我们在触发 `this.msg = 'Hello, Changed~'`的时候，会触发组件的更新，视图的重新渲染。

但是 `<ChildComponent  />` 这个组件其实是不会重新渲染的，这是 Vue 刻意而为之的。

在以前的一段时间里，我曾经认为因为组件是一棵树，所以它的更新就是理所当然的深度遍历这棵树，进行递归更新。本篇就从源码的角度带你一起分析，Vue 是怎么做到`精确更新`的。

## React的更新粒度
而 React 在类似的场景下是`自顶向下的进行递归更新的`，也就是说，React 中假如 `ChildComponent` 里还有十层嵌套子元素，那么所有层次都会递归的重新render（在不进行手动优化的情况下），这是性能上的灾难。（因此，React 创造了`Fiber`，创造了`异步渲染`，其实本质上是弥补被自己搞砸了的性能）。

他们能用收集依赖的这套体系吗？不能，因为他们遵从`Immutable`的设计思想，永远不在原对象上修改属性，那么基于 `Object.defineProperty` 或 `Proxy` 的响应式依赖收集机制就无从下手了（你永远返回一个新的对象，我哪知道你修改了旧对象的哪部分？）

同时，由于没有响应式的收集依赖，React 只能递归的把所有子组件都重新 `render`一遍，然后再通过 `diff算法` 决定要更新哪部分的视图，这个递归的过程叫做 `reconciler`，听起来很酷，但是性能很灾难。

## Vue的更新粒度
那么，Vue 这种精确的更新是怎么做的呢？其实每个组件都有自己的`渲染 watcher`，它掌管了当前组件的视图更新，但是并不会掌管 `ChildComponent` 的更新。

具体到源码中，是怎么样实现的呢？

在 `patch`  的过程中，当组件更新到`ChildComponent`的时候，会走到
`patchVnode`，那么这个方法大致做了哪些事情呢？

### patchVnode
#### 执行 `vnode` 的 `prepatch` 钩子。

注意，只有 `组件vnode` 才会有 `prepatch` 这个生命周期，

这里会走到`updateChildComponent`方法，这个 `child` 具体指什么呢？
```js
  prepatch (oldVnode: MountedComponentVNode, vnode: MountedComponentVNode) {
    const options = vnode.componentOptions
    // 注意 这个child就是ChildComponent组件的 vm 实例，也就是咱们平常用的 this
    const child = vnode.componentInstance = oldVnode.componentInstance
    updateChildComponent(
      child,
      options.propsData, // updated props
      options.listeners, // updated listeners
      vnode, // new parent vnode
      options.children // new children
    )
  },
```

其实看传入的参数也能猜到大概了，就是做了：
1. 更新props（后续详细讲）
2. 更新绑定事件
3. 对于slot做一些更新（后续详细讲）

#### 如果有子节点的话，对子节点进行 diff。

比如这样的场景：
```xml
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
<ul>
```
要对于 `ul` 中的三个 `li` 子节点 `vnode` 利用 `diff` 算法来更新，本篇略过。

然后到此为止，`patchVnode` 就结束了，并没有像常规思维中的那样去递归的更新子组件树。

这也就说明了，**Vue 的组件更新确实是精确到组件本身的**。

### props的更新如何触发重渲染？

那么有同学可能要问了，如果我们把 `msg` 这个响应式元素通过props传给 `ChildComponent`，此时它怎么更新呢？

其实，`msg` 在传给子组件的时候，会被保存在子组件实例的 `_props` 上，并且被定义成了`响应式属性`，而子组件的模板中对于 `msg` 的访问其实是被代理到 `_props.msg` 上去的，所以自然也能精确的收集到依赖，只要 `ChildComponent` 在模板里也读取了这个属性。

这里要注意一个细节，其实父组件发生重渲染的时候，是会重新计算子组件的 `props` 的，具体是在 `updateChildComponent` 中的：
```js
  // update props
  if (propsData && vm.$options.props) {
    toggleObserving(false)
    // 注意props被指向了 _props
    const props = vm._props
    const propKeys = vm.$options._propKeys || []
    for (let i = 0; i < propKeys.length; i++) {
      const key = propKeys[i]
      const propOptions: any = vm.$options.props // wtf flow?
      // 就是这句话，触发了对于 _props.msg 的依赖更新。
      props[key] = validateProp(key, propOptions, propsData, vm)
    }
    toggleObserving(true)
    // keep a copy of raw propsData
    vm.$options.propsData = propsData
  }
```
那么，由于上面注释标明的那段代码，`msg` 的变化通过 `_props` 的响应式能力，也让子组件重新渲染了，到目前为止，都只有真的用到了 `msg` 的组件被重新渲染了。

正如官网 api 文档中所说：
> `vm.$forceUpdate`：迫使 Vue 实例重新渲染。注意它仅仅影响实例本身和插入插槽内容的子组件，而不是所有子组件。
—— [vm-forceUpdate文档](https://cn.vuejs.org/v2/api/#vm-forceUpdate)

我们需要知道一个小知识点，`vm.$forceUpdate` 本质上就是触发了`渲染watcher`的重新执行，和你去修改一个响应式的属性触发更新的原理是一模一样的，它只是帮你调用了 `vm._watcher.update()`（只是提供给你了一个便捷的api，在设计模式中叫做`门面模式`）

### slot是怎么更新的？
注意这里也提到了一个细节，也就是 `插入插槽内容的子组件`：

举例来说

假设我们有父组件`parent-comp`：
```xml
<div>
  <slot-comp>
     <span>{{ msg }}</span>
  </slot-comp>
</div>
```

子组件 `slot-comp`：
```xml
<div>
   <slot></slot>
</div>
```
组件中含有 `slot`的更新 ，是属于比较特殊的场景。

这里的 `msg` 属性在进行依赖收集的时候，收集到的是 `parent-comp` 的`渲染watcher。（至于为什么，你看一下它所在的渲染上下文就懂了。）

那么我们想象 `msg` 此时更新了，

```xml
<div>
  <slot-comp>
     <span>{{ msg }}</span>
  </slot-comp>
</div>
```

这个组件在更新的时候，遇到了一个子组件 `slot-comp`，按照 Vue 的精确更新策略来说，子组件是不会重新渲染的。

但是在源码内部，它做了一个判断，在执行 `slot-comp` 的 `prepatch` 这个hook的时候，会执行 `updateChildComponent` 逻辑，在这个函数内部会发现它有 `slot` 元素。
```js
  prepatch (oldVnode: MountedComponentVNode, vnode: MountedComponentVNode) {
    const options = vnode.componentOptions
    // 注意 这个child就是 slot-comp 组件的 vm 实例，也就是咱们平常用的 this
    const child = vnode.componentInstance = oldVnode.componentInstance
    updateChildComponent(
      child,
      options.propsData, // updated props
      options.listeners, // updated listeners
      vnode, // new parent vnode
      options.children // new children
    )
  },
```

在 `updateChildComponent` 内部
```js
  const hasChildren = !!(
    // 这玩意就是 slot 元素
    renderChildren ||               // has new static slots
    vm.$options._renderChildren ||  // has old static slots
    parentVnode.data.scopedSlots || // has new scoped slots
    vm.$scopedSlots !== emptyObject // has old scoped slots
  )
```

然后下面走一个判断
```js
  if (hasChildren) {
    vm.$slots = resolveSlots(renderChildren, parentVnode.context)
    vm.$forceUpdate()
  }
```
这里调用了 `slot-comp` 组件vm实例上的 `$forceUpdate`，那么它所触发的`渲染watcher`就是属于`slot-comp`的`渲染watcher`了。  

总结来说，这次 `msg` 的更新不光触发了 `parent-comp` 的重渲染，也进一步的触发了拥有slot的子组件 `slot-comp` 的重渲染。  

它也只是触发了两层渲染，如果 `slot-comp` 内部又渲染了其他组件 `slot-child`，那么此时它是不会进行递归更新的。（只要 `slot-child` 组件不要再有 slot 了）。

比起 React 的递归更新，是不是还是好上很多呢？

## 赠礼 一个小issue
有人给 Vue 2.4.2 版本提了一个[issue](https://github.com/vuejs/vue/issues/7573)，在下面的场景下会出现 bug。

```js
let Child = {
  name: "child",
  template:
    '<div><span>{{ localMsg }}</span><button @click="change">click</button></div>',
  data: function() {
    return {
      localMsg: this.msg
    };
  },
  props: {
    msg: String
  },
  methods: {
    change() {
      this.$emit("update:msg", "world");
    }
  }
};

new Vue({
  el: "#app",
  template: '<child :msg.sync="msg"><child>',
  beforeUpdate() {
    alert("update twice");
  },
  data() {
    return {
      msg: "hello"
    };
  },
  components: {
    Child
  }
});

```

具体的表现是点击 `click按钮`，会 alert 出两次 `update twice`。 这是由于子组件在执行 `data` 这个函数初始化组件的数据时，会错误的再收集一遍 `Dep.target` （也就是`渲染watcher`）。

由于数据初始化的时机是 `beforeCreated` -> `created` 之间，此时由于还没有进入子组件的渲染阶段， `Dep.target` 还是父组件的`渲染watcher`。

这就导致重复收集依赖，重复触发同样的更新，具体表现可以看这里：https://jsfiddle.net/sbmLobvr/9 。

怎么解决的呢？很简单，在执行 `data` 函数的前后，把 `Dep.target` 先设置为 null 即可，在 `finally` 中再恢复，这样响应式数据就没办法收集到依赖了。
 
```diff
export function getData (data: Function, vm: Component): any {
  const prevTarget = Dep.target
+ Dep.target = null
  try {
    return data.call(vm, vm)
  } catch (e) {
    handleError(e, vm, `data()`)
    return {}
+ } finally {
+   Dep.target = prevTarget
  }
}
```

## 后记
如果你对于 `Dep.target`、 `渲染watcher`等概念还不太理解，可以看我写的一篇最简实现 Vue 响应式的文章，欢迎阅读：

[手把手带你实现一个最精简的响应式系统来学习Vue的data、computed、watch源码](https://juejin.im/post/5db6433b51882564912fc30f)

本文也存放在[我的Github博客仓库](https://github.com/sl1673495/blogs)中，欢迎订阅和star。

## 鸣谢
感谢 [嵇智](https://github.com/theniceangel) 大佬对于本文一些细节的纠正。