---
title: 'Vue3中不止composition-api，其他的提案(RFC)也很精彩。'
date: '2020-01-06'
spoiler: ''
---

最近一段时间，Vue3带来的新能力composition-api带来了比较大的轰动，虽然是灵感是源React Hook，但是在很多方面却超越了它。但是除了composition-api，其他的改动却比较少有人讨论，本篇文章就由[vuejs/rfcs](https://github.com/vuejs/rfcs) 这个仓库来看看其他比较让人振奋的RFC。

RFC其实就是（Request For Comments）征求修正意见书，它不代表这个api一定会正式通过，但是却可以让社区知道vuejs团队正在进行的一些工作，和一些新想法。

Vue的RFC分为四个阶段：

1. Pending：当RFC作为PR提交时。

2. Active：当RFC PR正在合并时。

3. Landed：当RFC提出的更改在实际发行版中发布时。

4. Rejected：关闭RFC PR而不合并时。  



本篇讨论的RFC都在[Active](https://github.com/vuejs/rfcs/tree/master/active-rfcs)阶段

## 删除filters的支持

```html
<!-- before -->
{{ msg | format }}

<!-- after -->
{{ format(msg) }}
```

动机：
1. 过滤器的功能可以轻松地通过方法调用或计算的属性来复制，因此它主要提供语法而不是实用的价值。

2. 过滤器需要一种自定义的微语法，该语法打破了表达式只是“ JavaScript”的假设-这增加了学习和实现成本。 实际上，它与JavaScript自己的按位或运算符（|）冲突，并使表达式解析更加复杂。

3. 过滤器还会在模板IDE支持中增加额外的复杂性（由于它们不是真正的JavaScript）。

替代：
1. 可以简单的利用method替换filter的能力，统一语法，Vue.filter全局注册的能力也可以用Vue.prototype全局挂载方法来实现。

2. 目前有一个stage-1的提案[pipeline-operator](https://github.com/tc39/proposal-pipeline-operator) 可以优雅的实现方法组合。
```js
let transformedMsg = msg |> uppercase |> reverse |> pluralize
```

## render函数的改变

原文：  
https://github.com/vuejs/rfcs/blob/master/active-rfcs/0008-render-function-api-change.md  

概览：
1. h现在已全局导入，而不是传递给渲染函数作为参数

2. 渲染函数参数已更改，并使stateful组件和functional组件之间保持一致

3. VNode现在具有拉平的props结构

基本示例：
```js
// globally imported `h`
import { h } from 'vue'

export default {
  render() {
    return h(
      'div',
      // flat data structure
      {
        id: 'app',
        onClick() {
          console.log('hello')
        }
      },
      [
        h('span', 'child')
      ]
    )
  }
}
```

动机：
在2.x中，VNode是特定于上下文的-这意味着创建的每个VNode都绑定到创建它的组件实例（“上下文”），

在2.x中，这样的一段代码：
```js
{
    render(h) {
        return h('div')
    }
}
```

h其实是通过render中的形参传入的，这是因为它需要关心是哪个组件实例在调用它，在3.x中，文章中介绍说vnode将会成为`context free`的，这意味着更加灵活的组件声明位置（不止在.vue文件中，不需要到处传递h参数）。  

并且如果`context free`真的实现，那么在2.x中Vue高阶组件的一些诟病也可以一同解决掉了，如果对context带来的高阶组件的bug感兴趣的话，可以查看HcySunYang大大的这篇文章：  
https://segmentfault.com/p/1210000012743259/read  


另外本篇中还提到了一个vnode的属性拉平，
```js
// before
{
  class: ['foo', 'bar'],
  style: { color: 'red' },
  attrs: { id: 'foo' },
  domProps: { innerHTML: '' },
  on: { click: foo },
  key: 'foo'
}

// after
{
  class: ['foo', 'bar'],
  style: { color: 'red' },
  id: 'foo',
  innerHTML: '',
  onClick: foo,
  key: 'foo'
}
```  

目前看来，由于jsx最终会被编译成生成vnode的方法，这个改动可能会让vue中书写jsx变得更加容易，现在的一些写法可以看我写的这篇文章：  
[手把手教你用jsx封装Vue中的复杂组件（网易云音乐实战项目需求）](https://juejin.im/post/5d40fa605188255d2e32c929)  

在这篇文章中可以看出，目前嵌套的vnode结构会让jsx的书写也变得很困难。  

由于render函数的一些另外的细微变动，Vue3中理想的functional component的书写方式是这样的：

```js
import { inject } from 'vue'
import { themeSymbol } from './ThemeProvider'

const FunctionalComp = props => {
  const theme = inject(themeSymbol)
  return h('div', `Using theme ${theme}`)
}
```
是不是很像React，哈哈。  

## 全局方法的导入方式  

为了更好的支持`tree-shaking`，Vue3把2.x中统一导出Vue的方式更改为分散导出，这样只有项目中用到的方法会被打包进bundle中，有效的减少了包的大小。

```js
import { nextTick, observable } from 'vue'

nextTick(() => {})

const obj = observable({})
```
简单的来说，如果你项目中只用到了`observable`和`nextTick`，那么例如`use`，`reactive`等这些另外的api就不会被打包进你的项目中。  

关于`tree-shaking`，我特别喜欢的作者[相学长](https://juejin.im/user/58f876dc5c497d0058e38ae1)有一篇文章可以看一下：  

[https://zhuanlan.zhihu.com/p/32831172](https://zhuanlan.zhihu.com/p/32831172)  

## 总结
在这个仓库中，还有一些提案大家也可以自行去看一下，剩下的都是一些细节的优化，这些优化或多或少的会让Vue3更好用一些，非常期待Vue3的到来。  

另外由于plugin的存在，我已经在2.x中用Vue3的composition-api做了一些尝鲜，不得不说**真香**！

[Vue3 Composition-Api + TypeScript + 新型状态管理模式探索](https://juejin.im/post/5e0da5606fb9a048483ecf64)