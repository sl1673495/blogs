---
title: '前端高级进阶指南'
date: '2020-03-26'
spoiler: ''
---

## 前言

我曾经一度很迷茫，在学了 Vue、React 的实战开发和应用以后，好像遇到了一些瓶颈，不知道该怎样继续深入下去。相信这也是很多一两年经验的前端工程师所遇到共同问题，这篇文章，笔者想结合自己的一些成长经历整理出一些路线，帮助各位初中级前端工程师少走一些弯路。

这篇文章会提到非常非常多的学习路线和链接，如果你还在初中级的阶段，不必太焦虑，可以把这篇文章作为一个进阶的`路线图`，在未来的时日里朝着这个方向努力就好。  
我也并不是说这篇文章是进阶高级工程师的唯一一条路线，如果你在业务上做的精进，亦或是能在沟通上八面玲珑，配合各方面力量把项目做的漂漂亮亮，那你也一样可以拥有这个头衔。本文只是我自己的一个成长路线总结。

本篇文章面对的人群是开发经验`1到3年的初中级前端工程师`，希望能和你们交个心。

已经晋升高级前端的同学，欢迎你在评论区留下你的心得，补充我的一些缺失和不足。

笔者本人 17 年毕业于一所普通的本科学校，20 年 6 月在三年经验的时候顺利通过面试进入大厂，职级是高级前端开发。

[我的 github 地址](https://github.com/sl1673495)，欢迎 follow，我会持续更新一些值得你关注的项目。

[我的 blog 地址](https://github.com/sl1673495/blogs)，这里会持续更新，点个 star 不失联！✨

## 基础能力

我整理了一篇中级前端的必备技术栈能力，[写给女朋友的中级前端面试秘籍](https://juejin.im/post/5e7af0685188255dcf4a497e) 。这篇文章里的技术栈当然都是需要扎实掌握的，（其实我自己也有一些漏缺，偷偷补一下）。

当然了，上进心十足的你不会一直满足于做中级前端，我们要继续向上，升职加薪，迎娶白富美！

## JavaScript

#### 原生 js 系列

冴羽大佬的这篇博客里，除了 undescore 的部分，你需要全部都能掌握。并且灵活的运用到开发中去。  
[JavaScript 深入系列、JavaScript 专题系列、ES6 系列](https://github.com/mqyqingfeng/Blog)

#### 完全熟练掌握 eventLoop。

[tasks-microtasks-queues-and-schedules](https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules)

#### Promise

1. 你需要阅读 Promise A+规范，注意其中的细节，并且灵活的运用到开发当中去。  
   [Promise A+ 英文文档](http://promisesaplus.com)

2. 你需要跟着精品教程手写一遍 Promise，对里面的细节深入思考，并且把其中异步等待、错误处理等等细节融会贯通到你的开发思想里去。  
   [剖析 Promise 内部结构，一步一步实现一个完整的、能通过所有 Test case 的 Promise 类](https://github.com/xieranmaya/blog/issues/3)

3. 最后，对于 promise 的核心，异步的链式调用，你必须能写出来简化版的代码。  
   [最简实现 Promise，支持异步链式调用（20 行）](https://juejin.im/post/5e6f4579f265da576429a907)

题外话，当时精炼这 20 行真的绕了我好久 😂，但是搞明白了会有种恍然大悟的感觉。这种异步队列的技巧要融会贯通。

#### async await

对于 Promise 我们非常熟悉了，进一步延伸到 async await，这是目前开发中非常非常常用的异步处理方式，我们最好是熟悉它的 babel 编译后的源码。

[手写 async await 的最简实现（20 行搞定）](https://juejin.im/post/5e79e841f265da5726612b6e)  
babel 对于 async await 配合 generator 函数，做的非常巧妙，这里面的思想我们也要去学习，如何递归的处理一个串行的 promise 链？

这个技巧在[axios 的源码](https://github.com/axios/axios/blob/e50a08b2c392c6ce3b5a9dc85ebc860d50414529/lib/core/Axios.js#L49-L62)里也有应用。平常经常用的拦截器，本质上就是一串 promise 的串行执行。

当然，如果你还有余力的话，也可以继续深入的去看 generator 函数的 babel 编译源码。不强制要求，毕竟 generator 函数在开发中已经用的非常少了。  
[ES6 系列之 Babel 将 Generator 编译成了什么样子](https://github.com/mqyqingfeng/Blog/issues/102)

#### 异常处理

你必须精通异步场景下的错误处理，这是高级工程师必备的技能，如果开发中的异常被你写的库给吞掉了，那岂不是可笑。  
[Callback Promise Generator Async-Await 和异常处理的演进](https://juejin.im/post/589036f8570c3500621a3be2)

#### 插件机制

你需要大概理解前端各个库中的`插件`机制是如何实现的，在你自己开发一些库的时候也能融入自己适合的插件机制。  
[Koa 的洋葱中间件，Redux 的中间件，Axios 的拦截器让你迷惑吗？实现一个精简版的就彻底搞懂了。](https://juejin.im/post/5e13ea6a6fb9a0482b297e8e)

#### 设计模式

对于一些复杂场景，你的开发不能再是`if else`嵌套一把梭了，你需要把设计模式好好看一遍，在合适的场景下选择合适的设计模式。这里就推荐掘金小册吧，相信这篇小册会让你的`工程能力`得到质的飞跃，举例来说，在 Vue 的源码中就用到了`观察者模式`、`发布订阅模式`、`策略模式`、`适配器模式`、`发布订阅模式`、`工厂模式`、`组合模式`、`代理模式`、`门面模式`等等。

而这些设计模式如果你没学习过可能很难想到如何应用在工程之中，但是如果你学习过，它就变成了你内在的`工程能力`，往大了说，也可以是`架构能力`的一部分。

> 在《设计模式》这本小册中我们提到过，即使是在瞬息万变的前端领域，也存在一些具备“一次学习，终生受用”特性的知识。从工程的角度看，我推荐大家着重学习的是设计模式。 -修言

这里推荐掘金修言的[设计模式小册](https://user-gold-cdn.xitu.io/2020/5/6/171e6247f6ea460a?w=750&h=1334&f=png&s=679081)。

#### 开发思想

有时候组合是优于继承的，不光是面向对象编程可以实现复用，在某些场景下，组合的思想可能会更加简洁优雅。

https://medium.com/javascript-scene/master-the-javascript-interview-what-s-the-difference-between-class-prototypal-inheritance-e4cd0a7562e9

> “…the problem with object-oriented languages is they’ve got all this implicit environment that they carry around with them. You wanted a banana but what you got was a gorilla holding the banana and the entire jungle.” ~ Joe Armstrong — “Coders at Work”

> 面向对象语言的问题在于它们带来了所有这些隐含的环境。
> 你想要一个香蕉，但你得到的是拿着香蕉和整个丛林的大猩猩。

#### 代码规范

你需要熟读 clean-code-javascript，并且深入结合到日常开发中，结合你们小组的场景制定自己的规范。  
[clean-code-javascript](https://github.com/beginor/clean-code-javascript)

## 算法

算法这里我就不推荐各种小册，笔记，博文了。因为从我自己学习算法的经验来看，在没有太多的算法基础的情况下，文章基本上是很难真正的看进去并理解的，这里只推荐慕课网 bobo 老师的 [LeetCode 真题课程](https://coding.imooc.com/class/82.html)，在这个课程里算法大牛 bobo 老师会非常细心的把各个算法做成动图，由浅入深给你讲解各种分类的 LeetCode 真题。这是我最近学到的最有收获的一门课程了。

由于这门课程是 C++ 为主要语言的（不影响理解课程），我也针对此课程维护了一个对应的 [JavaScript 版题解仓库](https://github.com/sl1673495/leetcode-javascript/issues)，在 Issue 里也根据标签分类整理了各个题型的讲解，欢迎 Star ✨。

算法对于前端来说重要吗？也许你觉得做题没用，但是我个人在做题后并且分门别类的整理好各个题型的思路和解法后，是能真切的感觉到自己的代码能力在飞速提高的。

对于很多觉得自己不够聪明，不敢去学习算法的同学来说，推荐 bobo 老师的这篇[《天生不聪明》](https://mp.weixin.qq.com/s/QvXIDpyrpiOmvEhcOUUmxQ)，也正是这篇文章激励我开始了算法学习的旅程。

在这里列一下前端需要掌握的基础算法知识，希望能给你一个路线：
1. 算法的复杂度分析。
2. 排序算法，以及他们的区别和优化。
3. 数组中的双指针、滑动窗口思想。
4. 利用 Map 和 Set 处理查找表问题。
5. 链表的各种问题。
6. 利用递归和迭代法解决二叉树问题。
7. 栈、队列、DFS、BFS。
8. 回溯法、贪心算法、动态规划。

算法是底层的基础，把地基打扎实后，会让你在后续的职业生涯中大受裨益的。

这里也推荐我的整合文章 [前端算法进阶指南](https://github.com/sl1673495/blogs/issues/53)。

## 框架篇

对于高级工程师来说，你必须要有一个你趁手的框架，它就像你手中的一把利剑，能够让你披荆斩棘，斩杀各种项目于马下。

下面我会分为`Vue`和`React`两个方面深入去讲。

### Vue

Vue 方面的话，我主要是师从黄轶老师，跟着他认真走，基本上在 Vue 这方面你可以做到基本无敌。

#### 熟练运用

1. 对于 Vue 你必须非常熟练的运用，官网的 api 你基本上要全部过一遍。并且你要利用一些高级的 api 去实现巧妙的封装。举几个简单的例子。

2. 你要知道怎么用`slot-scope`去做一些数据和 ui 分离的封装。
   以[vue-promised](https://github.com/posva/vue-promised)这个库为例。
   Promised 组件并不关注你的视图展示成什么样，它只是帮你管理异步流程，并且通过你传入的`slot-scope`，在合适的时机把数据回抛给你，并且帮你去展示你传入的视图。

```xml
<template>
  <Promised :promise="usersPromise">
    <!-- Use the "pending" slot to display a loading message -->
    <template v-slot:pending>
      <p>Loading...</p>
    </template>
    <!-- The default scoped slot will be used as the result -->
    <template v-slot="data">
      <ul>
        <li v-for="user in data">{{ user.name }}</li>
      </ul>
    </template>
    <!-- The "rejected" scoped slot will be used if there is an error -->
    <template v-slot:rejected="error">
      <p>Error: {{ error.message }}</p>
    </template>
  </Promised>
</template>
```

3. 你需要熟练的使用`Vue.extends`，配合项目做一些`命令式api`的封装。并且知道它为什么可以这样用。（需要具备源码知识）
   [confirm 组件](https://github.com/sl1673495/vue-netease-music/blob/master/src/base/confirm.vue)

```js
export const confirm = function (text, title, onConfirm = () => {}) {
  if (typeof title === "function") {
    onConfirm = title;
    title = undefined;
  }
  const ConfirmCtor = Vue.extend(Confirm);
  const getInstance = () => {
    if (!instanceCache) {
      instanceCache = new ConfirmCtor({
        propsData: {
          text,
          title,
          onConfirm,
        },
      });
      // 生成dom
      instanceCache.$mount();
      document.body.appendChild(instanceCache.$el);
    } else {
      // 更新属性
      instanceCache.text = text;
      instanceCache.title = title;
      instanceCache.onConfirm = onConfirm;
    }
    return instanceCache;
  };
  const instance = getInstance();
  // 确保更新的prop渲染到dom
  // 确保动画效果
  Vue.nextTick(() => {
    instance.visible = true;
  });
};
```

4. 你要开始使用`JSX`来编写你项目中的复杂组件了，比如在我的网易云音乐项目中，我遇到了一个[复杂的音乐表格需求](https://juejin.im/post/5d40fa605188255d2e32c929)，支持搜索文字高亮、动态隐藏列等等。  
   当然对于现在版本的 Vue，JSX 还是不太好用，有很多属性需要写嵌套对象，这会造成很多不必要的麻烦，比如没办法像 React 一样直接把外层组件传入的 props 透传下去，Vue3 的 rfc 中提到会把 vnode 节点的属性进一步扁平化，我们期待得到接近于 React 的完美 JSX 开发体验吧。

5. 你要深入了解 Vue 中 nextTick 的原理，并且知道为什么要用微任务队列优于宏任务队列，结合你的 eventloop 知识深度思考。最后融入到你的`异步合并优化`的知识体系中去。  
   [Vue 源码详解之 nextTick：MutationObserver 只是浮云，microtask 才是核心！](https://segmentfault.com/a/1190000008589736)

6. 你要能理解 Vue 中的高阶组件。关于这篇文章中为什么 slot-scope 不生效的问题，你不能看他的文章讲解都一头雾水。（需要你具备源码知识）  
   [探索 Vue 高阶组件 | HcySunYang](https://segmentfault.com/p/1210000012743259/read)

7. 推荐一下我自己总结的 Vue 高阶组件文章，里面涉及到了一些进阶的用法。  
   [Vue 进阶必学之高阶组件 HOC](https://juejin.im/post/5e8b5fa6f265da47ff7cc139)

8. 对于 Vuex 的使用必须非常熟练，知道什么时候该用 Vuex，知道怎么根据需求去编写 Vuex 的 plugin，合理的去使用 Vuex 的 subscribe 功能完成一些全局维度的封装，比如我对于 Vuex 中 action 的错误处理懒得一个个去`try catch`，就封装了一个[vuex-error-plugin](https://github.com/sl1673495/vuex-error-plugin/blob/master/plugin.js)。代码很简单，重要的是去理解为什么能这样做。这里用了 `monkey patch` 的做法，并不是很好的实践，仅以此作为引子。
9. 对于 vue-router 的使用必须非常熟练，知道什么需求需要利用什么样的 router 钩子，这样才能 hold 住一个大型的项目，这个我觉得官方仓库里的进阶中文文档其实很好，不知道为什么好像没放在官网。  
   [vue-router-advanced](https://github.com/vuejs/vue-router/tree/dev/docs/zh/guide/advanced)

10. 理解虚拟 DOM 的本质，虚拟 DOM 一定比真实 DOM 更快吗？这篇是尤雨溪的回答，看完这个答案，相信你会对虚拟 DOM 有更进一步的认识和理解。  
    [网上都说操作真实 DOM 慢，但测试结果却比 React 更快，为什么？](https://www.zhihu.com/question/31809713/answer/53544875)

#### 源码深入

1. 你不光要熟练运用 Vue，由于 Vue 的源码写的非常精美，而且阅读难度不是非常大，很多人也选择去阅读 Vue 的源码。视频课这里推荐黄轶老师的 Vue 源码课程。这里也包括了 Vuex 和 vue-router 的源码。  
   [Vue.js 源码全方位深入解析 （含 Vue3.0 源码分析）](https://coding.imooc.com/class/228.html)

3. 推荐 HcySunYang 大佬的 Vue 逐行分析，需要下载 git 仓库，切到 elegant 分支自己本地启动。  
   [Vue 逐行级别的源码分析](https://github.com/HcySunYang/vue-design)

4. 当然，这个仓库的 master 分支也是宝藏，是这个作者的渲染器系列文章，脱离框架讲解了 vnode 和 diff 算法的本质  
   [组件的本质](http://hcysun.me/vue-design/zh/essence-of-comp.html#%E7%BB%84%E4%BB%B6%E7%9A%84%E4%BA%A7%E5%87%BA%E6%98%AF%E4%BB%80%E4%B9%88)

#### Vue3 展望

1. Vue3 已经发布了 Beta 版本，你可以提前学习`Hook`相关的开发模式了。这里推荐一下我写的这篇 Vue3 相关介绍：  
  [Vue3 究竟好在哪里？（和 React Hook 的详细对比）](https://juejin.im/post/5e9ce011f265da47b8450c11)

#### Vue3 源码

对于响应式部分，如果你已经非常熟悉 Vue2 的响应式原理了，那么 Vue3 的响应式原理对你来说应该没有太大的难度。甚至在学习之中你会相互比较，知道 Vue3 为什么这样做更好，Vue2 还有哪部分需要改进等等。

Vue3 其实就是把实现换成了更加强大的 Proxy，并且把响应式部分做的更加的抽象，甚至可以，不得不说，Vue3 的响应式模型更加接近`响应式类库`的核心了，甚至`react-easy-state`等 React 的响应式状态管理库，也是用这套类似的核心做出来的。

再次强调，非常非常推荐学习 Vue3 的`@vue/reactivity`这个分包。

推一波自己的文章吧，细致了讲解了 Vue3 响应式的核心流程。

1. [带你彻底搞懂 Vue3 的 Proxy 响应式原理！TypeScript 从零实现基于 Proxy 的响应式库。](https://juejin.im/post/5e21196fe51d454d523be084)

2. [带你彻底搞懂 Vue3 的 Proxy 响应式原理！基于函数劫持实现 Map 和 Set 的响应式](https://juejin.im/post/5e23b20f51882510073eb571)

3. [深度解析：Vue3 如何巧妙的实现强大的 computed](https://juejin.im/post/5e2fdf29e51d45026866107d)

在学习之后，我把`@vue/reactivity`包轻松的集成到了 React 中，做了一个状态管理的库，这也另一方面佐证了这个包的抽象程度：  
[40 行代码把 Vue3 的响应式集成进 React 做状态管理](https://juejin.im/post/5e70970af265da576429aada)

### React

React 已经进入了 Hook 为主的阶段，社区的各个库也都在积极拥抱 Hook，虽然它还有很多陷阱和不足，但是这基本上是未来的方向没跑了。这篇文章里我会减少 class 组件的开发技巧的提及，毕竟好多不错的公司也已经全面拥抱 Hook 了。

#### 熟练应用

1. 你必须掌握官网中提到的所有技巧，就算没有使用过，你也要大概知道该在什么场景使用。

2. 推荐 React 小书，虽然书中的很多 api 已经更新了，但是核心的设计思想还是没有变  
   [React.js 小书](http://huziketang.mangojuice.top/books/react)

3. 关于熟练应用，其实掘金的小册里有几个宝藏

   1. 诚身大佬（悄悄告诉你，他的职级非常高）的企业级管理系统小册，这个项目里的代码非常深入，而且在抽象和优化方面也做的无可挑剔，自己抽象了`acl`权限管理系统和`router`路由管理，并且引入了`reselect`做性能优化，一年前我初次读的时候，很多地方懵懵懂懂，这一年下来我也从无到有经手了一套带`acl`和`权限路由`的管理系统后，才知道他的抽象能力有多强。真的是

      > 初闻不知曲中意，再闻已是曲中人。

      [React 组合式开发实践：打造企业管理系统五大核心模块](https://juejin.im/book/5b1e15f76fb9a01e516d14a0)

   2. 三元大佬的 React Hooks 与 Immutable 数据流实战，深入浅出的带你实现一个音乐播放器。三元大家都认识吧？那是神，神带你们写应用项目，不学能说得过去吗？
      [React Hooks 与 Immutable 数据流实战](https://juejin.im/book/5da96626e51d4524ba0fd237)

4. 深入理解 React 中的`key`  
   [understanding-reacts-key-prop](https://kentcdodds.com/blog/understanding-reacts-key-prop)

   [react 中为何推荐设置 key](https://zhuanlan.zhihu.com/p/112917118)

5. React 官方团队成员对于`派生状态`的思考：  
   [you-probably-dont-need-derived-state](https://zh-hans.reactjs.org/blog/2018/06/07/you-probably-dont-need-derived-state.html)

#### React Hook

你必须熟练掌握 Hook 的技巧，除了官网文档熟读以外：

1. 推荐 Dan 的博客，他就是 Hook 的代码实际编写者之一，看他怎么说够权威了吧？这里贴心的送上汉化版。  
   [useEffect 完整指南](https://overreacted.io/zh-hans/a-complete-guide-to-useeffect/)  
   看完这篇以后，进入[dan 的博客主页](https://overreacted.io/zh-hans)，找出所有和 Hook 有关的，全部精读！

2. 推荐黄子毅大佬的精读周刊系列  
   [096.精读《useEffect 完全指南》.md](https://github.com/dt-fe/weekly/blob/v2/096.%E7%B2%BE%E8%AF%BB%E3%80%8AuseEffect%20%E5%AE%8C%E5%85%A8%E6%8C%87%E5%8D%97%E3%80%8B.md)  
   注意！不是只看这一篇，而是这个仓库里所有有关于 React Hook 的文章都去看一遍，结合自己的思想分析。

3. Hook 陷阱系列
   还是 Dan 老哥的文章，详细的讲清楚了所谓`闭包陷阱`产生的原因和设计中的权衡。  
   [函数式组件与类组件有何不同？](https://overreacted.io/zh-hans/how-are-function-components-different-from-classes/)

4. 去找一些社区的精品自定义 hook，看看他们的开发和设计思路，有没有能融入自己的日常开发中去的。  
   [精读《Hooks 取数 - swr 源码》](https://segmentfault.com/a/1190000020964640)  
   [Umi Hooks - 助力拥抱 React Hooks](https://zhuanlan.zhihu.com/p/103150605?utm_source=wechat_session)  
   [React Hooks 的体系设计之一 - 分层](https://zhuanlan.zhihu.com/p/106665408)

#### React 性能优化

React 中优化组件重渲染，这里有几个隐含的知识点。  
[optimize-react-re-renders](https://kentcdodds.com/blog/optimize-react-re-renders)

如何对 React 函数式组件进行性能优化？这篇文章讲的很详细，值得仔细阅读一遍。
[如何对 React 函数式组件进行优化](https://juejin.im/post/5dd337985188252a1873730f)

#### React 单元测试

1. 使用`@testing-library/react`测试组件，这个库相比起 enzyme 更好的原因在于，它更注重于**站在用户的角度**去测试一个组件，而不是测试这个组件的**实现细节**。  
   [Introducing The React Testing Library](https://kentcdodds.com/blog/introducing-the-react-testing-library)  
   [Testing Implementation Details](https://kentcdodds.com/blog/testing-implementation-details)

2. 使用`@testing-library/react-hooks`测试自定义 Hook  
   [how-to-test-custom-react-hooks](https://kentcdodds.com/blog/how-to-test-custom-react-hooks)

#### React 和 TypeScript 结合使用

1. 这个仓库非常详细的介绍了如何把 React 和 TypeScript 结合，并且给出了一些进阶用法的示例，非常值得过一遍！  
   [react-typescript-cheatsheet](https://github.com/typescript-cheatsheets/react-typescript-cheatsheet)

2. 这篇文章是蚂蚁金服数据体验技术部的同学带来的，其实除了这里面的技术文章以外，蚂蚁金服的同学也由非常生动给我们讲解了一个高级前端同学是如何去社区寻找方案，如何思考和落地到项目中的，由衷的佩服。  
   [React + Typescript 工程化治理实践](https://juejin.im/post/5dccc9b8e51d4510840165e2)

3. 微软的大佬带你写一个类型安全的组件，非常深入，非常过瘾...  
   [Writing Type-Safe Polymorphic React Components (Without Crashing TypeScript)](https://blog.andrewbran.ch/polymorphic-react-components/)

4. React + TypeScript 10 个需要避免的错误模式。  
   [10-typescript-pro-tips-patterns-with-or-without-react](https://medium.com/@martin_hotell/10-typescript-pro-tips-patterns-with-or-without-react-5799488d6680)

#### React 代码抽象思考

1. 何时应该把代码拆分为组件？  
   [when-to-break-up-a-component-into-multiple-components](https://kentcdodds.com/blog/when-to-break-up-a-component-into-multiple-components)

2. 仔细思考你的 React 应用中，状态应该放在什么位置，是组件自身，提升到父组件，亦或是局部 context 和 redux，这会有益于提升应用的性能和可维护性。  
   [state-colocation-will-make-your-react-app-faster](https://kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster/)

3. 仔细思考 React 组件中的状态应该如何管理，优先使用派生状态，并且在适当的时候利用 useMemo、reselect 等库去优化他们。  
   [dont-sync-state-derive-it](https://kentcdodds.com/blog/dont-sync-state-derive-it)

4. React Hooks 的自定义 hook 中，如何利用 reducer 的模式提供更加灵活的数据管理，让用户拥有数据的控制权。  
   [the-state-reducer-pattern-with-react-hooks](https://kentcdodds.com/blog/the-state-reducer-pattern-with-react-hooks)

## TypeScript

自从 Vue3 横空出世以来，TypeScript 好像突然就火了。这是一件好事，推动前端去学习强类型语言，开发更加严谨。并且第三方包的 ts 类型支持的加入，让我们甚至很多时候都不再需要打开文档对着 api 撸了。

关于 TypeScript 学习，其实几个月前我还对于这门 JavaScript 的超集一窍不通，经过两三个月的静心学习，我能够去理解一些相对复杂的类型了，

可以说 TypeScript 的学习和学一个库或者学一个框架是完全不同的，

#### 入门

1. 除了官方文档以外，还有一些比较好的中文入门教程。  
   [TypeScript Handbook 入门教程 ](https://zhongsp.gitbooks.io/typescript-handbook/content/)

2. TypeScript Deep Dive 非常高质量的英文入门教学。  
   [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/type-system)

3. 工具泛型在日常开发中都非常的常用，必须熟练掌握。  
   [TS 一些工具泛型的使用及其实现](https://zhuanlan.zhihu.com/p/40311981)

4. 视频课程，还是黄轶大佬的，并且这个课程对于单元测试、前端手写框架、以及网络请求原理都非常有帮助。  
   [基于 TypeScript 从零重构 axios](https://coding.imooc.com/class/330.html)

#### 进阶

1. 这五篇文章里借助非常多的案例，为我们讲解了 ts 的一些高级用法，请务必反复在 ide 里尝试，理解，不懂的概念及时回到文档中补习。  
   [巧用 TypeScript 系列 一共五篇](https://juejin.im/post/5c8a518ee51d455e4d719e2e)

2. TS 进阶非常重要的一点，条件类型，很多泛型推导都需要借助它的力量。  
   [conditional-types-in-typescript](https://mariusschulz.com/blog/conditional-types-in-typescript)

3. 以及上面那个大佬博客中的所有 TS 文章。  
   https://mariusschulz.com

#### 实战

1. 一个参数简化的实战，涉及到的高级知识点非常多。

   1. 🎉TypeScript 的高级类型（Advanced Type）
   2. 🎉Conditional Types (条件类型)
   3. 🎉Distributive conditional types (分布条件类型)
   4. 🎉Mapped types（映射类型）
   5. 🎉 函数重载  
      [TypeScript 参数简化实战](https://juejin.im/post/5e38dd65518825492b509dd6)

2. 实现一个简化版的 Vuex，同样知识点结合满满。
   1. 🎉TypeScript 的高级类型（[Advanced Type](https://www.typescriptlang.org/docs/handbook/advanced-types.html)）
   2. 🎉TypeScript 中利用泛型进行反向类型推导。([Generics](https://www.typescriptlang.org/docs/handbook/generics.html))
   3. 🎉Mapped types（映射类型）
   4. 🎉Distributive Conditional Types（条件类型分配）
   5. 🎉TypeScript 中 Infer 的实战应用（[Vue3 源码里 infer 的一个很重要的使用](https://github.com/vuejs/vue-next/blob/985f4c91d9d3f47e1314d230c249b3faf79c6b90/packages/reactivity/src/ref.ts#L89)）  
      [TS 实现智能类型推导的简化版 Vuex](https://juejin.im/post/5e38dd65518825492b509dd6)

#### 刻意训练

它几乎是一门新的语言（在类型世界里来说），需要你花费很大的精力去学好它。

我对于 TypeScript 的学习建议其实就是一个关键词：`刻意训练`，在过基础概念的时候，不厌其烦的在`vscode`中敲击，理解，思考。在基础概念过完以后去寻找实践文章，比如我上面`进阶`和`实战`部分推荐的几篇，继续`刻意训练`，一定要堆积代码量，学习一门新的语言是不可能靠看文档获得成功的。

我会建立一个仓库，专门记录我遇到的[TypeScript 的有趣代码](https://github.com/sl1673495/typescript-codes)，自己动手敲一遍，并且深入理解。

#### 能力分级

其实 TypeScript 的能力也是两级分化的，日常写业务来说，你定义一些 interface，配合 React.FC 这种官方内置的类型也就跑通了，没什么特别难的点。

但是如果是造轮子呢？如果你自己写了一个工具库，并且类型比较复杂，你能保证推导出来吗？亦或者就拿 Vue3 来说，ref 是一个很复杂的嵌套类型，

假如我们这样定义一个值`const value = ref(ref(2))`，对于嵌套的 ref，Vue3 会做一层`拆包`，也就是说其实`ref.value`会是 2，

那么它是如何让 ts 提示出 value 的类型是 number 的呢？

如果你看到源码里的这段代码，你只有基础的话，保证懵逼。  
[Vue3 跟着尤雨溪学 TypeScript 之 Ref 类型从零实现](https://juejin.im/post/5e94595c6fb9a03c341daa75)

```js
// Recursively unwraps nested value bindings.
export type UnwrapRef<T> = {
  cRef: T extends ComputedRef<infer V> ? UnwrapRef<V> : T
  ref: T extends Ref<infer V> ? UnwrapRef<V> : T
  array: T
  object: { [K in keyof T]: UnwrapRef<T[K]> }
}[T extends ComputedRef<any>
  ? 'cRef'
  : T extends Array<any>
    ? 'array'
    : T extends Ref | Function | CollectionTypes | BaseTypes
      ? 'ref' // bail out on types that shouldn't be unwrapped
      : T extends object ? 'object' : 'ref']
```

##### 业务开发人员

如果短期内你对自己的要求是能上手业务，那么你理解 TypeScript 基础的`interface`和`type`编写和泛型的普通使用（可以理解为类型系统里的函数传参）也已经足够。

##### 框架开发人员

但是长期来看，如果你的目的是能够自己编写一些类型完善的库或框架，或者说你在公司扮演`前端架构师`、`轮子专家`等等角色，经常需要写一些偏底层的库给你的小伙伴们使用，那么你必须深入学习，这样才能做到给你的框架使用用户完美的类型体验。

#### 面试题

TypeScript 相关的面试题我见得不多，不过`力扣中国`的面试题算是难度偏高的，其中有一道 TS 的面试题，可以说是实用性和难度都有所兼顾，简单来说就是解包。

```ts
// 解开参数和返回值中的Promise
asyncMethod<T, U>(input: Promise<T>): Promise<Action<U>>
 ↓
asyncMethod<T, U>(input: T): Action<U>

// 解开参数中的Action
syncMethod<T, U>(action: Action<T>): Action<U>
 ↓
syncMethod<T, U>(action: T): Action<U>
```

我在高强度学习了两三个月 TS 的情况下，已经能把这道题目相对轻松的解出来，相信这也是说明我的学习路线没有走偏（题解就不放了，尊重面试题，其实就是考察了`映射类型`和`infer`的使用）。  
[力扣面试题](https://github.com/LeetCode-OpenSource/hire/blob/master/typescript_zh.md)

## 代码质量

#### 代码风格

1. 在项目中集成 Prettier + ESLint + Airbnb Style Guide
   [integrating-prettier-eslint-airbnb-style-guide-in-vscode](https://blog.echobind.com/integrating-prettier-eslint-airbnb-style-guide-in-vscode-47f07b5d7d6a)

2. [在项目中集成 ESLint with Prettier, TypeScript](https://levelup.gitconnected.com/setting-up-eslint-with-prettier-typescript-and-visual-studio-code-d113bbec9857)

#### 高质量架构

1. 如何重构一个过万 Star 开源项—BetterScroll，是由滴滴的大佬[嵇智](https://github.com/theniceangel)所带来的，无独有偶的是，这篇文章除了详细的介绍一个合格的开源项目应该做到的代码质量保证，测试流程，持续集成流程以外，也体现了他的一些思考深度，非常值得学习。  
   [如何重构一个过万 Star 开源项目—BetterScroll](https://juejin.im/post/5e40f72df265da5732551bdf)

#### Git 提交信息

1. 很多新手在提交 Git 信息的时候会写的很随意，比如`fix`、`test`、`修复`，这么糊弄的话是会被 leader 揍的！

   [[译]如何撰写 Git 提交信息](https://jiongks.name/blog/git-commit)

   [Git-Commit-Log 规范（Angular 规范）](https://www.jianshu.com/p/c7e40dab5b05)

   [commitizen](https://www.npmjs.com/package/commitizen)规范流程的 commit 工具，规范的 commit 格式也会让工具帮你生成友好的`changelog`

## 构建工具

1. webpack 基础和优化  
   [深入浅出 webpack](http://www.xbhub.com/wiki/webpack/)
2. 滴滴前端工程师的 webpack 深入源码分析系列，非常的优秀。  
   [webpack 系列之一总览](https://github.com/DDFE/DDFE-blog/issues/36)

## 性能优化

1. 推荐修言大佬的[性能优化小册](https://user-gold-cdn.xitu.io/2020/5/6/171e625d5fe327af?w=750&h=1334&f=png&s=807503)，这个真的是讲的深入浅出，从`webpack`到`网络`到`dom操作`，全方位的带你做一些性能优化实战。这本小册我当时看的时候真的是完全停不下来，修言大佬的风格既轻松又幽默。但是讲解的东西却能让你受益匪浅。

2. 谷歌开发者性能优化章节，不用多说了吧？很权威了。左侧菜单栏里还有更多相关内容，可以按需选择学习。  
   [user-centric-performance-metrics](https://developers.google.com/web/fundamentals/performance/user-centric-performance-metrics)

3. 详谈合成层，合成层这个东西离我们忽远忽近，可能你的一个不小心的操作就造成`层爆炸`，当然需要仔细关注啦。起码，在性能遇到瓶颈的时候，你可以打开 chrome 的`layer`面板，看看你的页面到底是怎么样的一个层分布。  
   [详谈层合成（composite）](https://juejin.im/entry/59dc9aedf265da43200232f9)

4. 刘博文大佬的性能优化指南，非常清晰的讲解了网页优化的几个重要的注意点。  
   [让你的网页更丝滑](https://zhuanlan.zhihu.com/p/66398148)

## 社区讨论

作为一个合格的前端工程师，一定要积极的深入社区去了解最新的动向，比如在`twitter`上关注你喜欢的技术开发人员，如 Dan、尤雨溪。

另外 Github 上的很多 issue 也是宝藏讨论，我就以最近我对于 Vue3 的学习简单的举几个例子。

#### 为什么 Vue3 不需要时间切片？

尤雨溪解释关于为什么在 Vue3 中不加入 React 时间切片功能？并且详细的分析了 React 和 Vue3 之间的一些细节差别，狠狠的吹了一波 Vue3（爱了爱了）。  
[Why remove time slicing from vue3?](https://github.com/vuejs/rfcs/issues/89)

#### Vue3 的`composition-api`到底好在哪？

Vue3 的 functional-api 相关的 rfc，尤大舌战群儒，深入浅出的为大家讲解了 Vue3 的设计思路等等。  
[Amendment proposal to Function-based Component API](https://github.com/vuejs/rfcs/issues/63)

#### Vue3`composition-api`的第一手文档

vue-composition-api 的 rfc 文档，在国内资料还不齐全的情况下，我去阅读了  
[vue-composition-api-rfc](https://vue-composition-api-rfc.netlify.com/#summary) 英文版文档，对于里面的设计思路叹为观止，学到了非常非常多尤大的思想。

总之，对于你喜欢的仓库，都可以去看看它的 issue 有没有看起来感兴趣的讨论，你也会学到非常多的东西。并且你可以和作者保持思路上的同步，这是非常难得的一件事情。

#### 关于 Hook 的一些收获

我在狠狠的吸收了一波尤大对于 Vue3 `composition-api`的设计思路的讲解，新旧模式的对比以后，这篇文章就是我对 Vue3 新模式的一些见解。  
[Vue3 Composition-Api + TypeScript + 新型状态管理模式探索。](https://juejin.im/post/5e0da5606fb9a048483ecf64)

在 Vue2 里，可以通过`plugin`先体验`composition-api`，截取这篇文章对应的实战项目中的一小部分代码吧：

```xml
<template>
  <Books :books="booksAvaluable" :loading="loading" />
</template>

<script lang="ts">
import { createComponent } from '@vue/composition-api';
import Books from '@/components/Books.vue';
import { useAsync } from '@/hooks';
import { getBooks } from '@/hacks/fetch';
import { useBookListInject } from '@/context';
export default createComponent({
  name: 'books',
  setup() {
    const { books, setBooks, booksAvaluable } = useBookListInject();
    const loading = useAsync(async () => {
      const requestBooks = await getBooks();
      setBooks(requestBooks);
    });
    return { booksAvaluable, loading };
  },
  components: {
    Books,
  },
});
</script>

<style>
.content {
  max-width: 700px;
  margin: auto;
}
</style>
```

本实战对应仓库：

[vue-bookshelf](https://github.com/sl1673495/vue-bookshelf)

并且由于它和`React Hook`在很多方面的思想也非常相近，这甚至对于我在`React Hook`上的使用也大有裨益，比如代码组织的思路上，

在第一次使用`Hook`开发的时候，大部分人可能还是会保留着以前的思想，把`state`集中起来定义在代码的前一大段，把`computed`集中定义在第二段，把`mutation`定义在第三段，如果不看尤大对于设计思想的讲解，我也一直是在这样做。

但是为什么 Logical Concerns 优于 Vue2 和 React Class Component 的 Option Types？看完[detailed-design](https://vue-composition-api-rfc.netlify.com/#detailed-design)这个章节你就全部明白了，并且这会融入到你日常开发中去。

总之，看完这篇以后，我果断的把公司里的首屏组件的一坨代码直接抽成了 n 个自定义 hook，维护效率提升简直像是坐火箭。

当然，社区里的宝藏 issue 肯定不止这些，我只是简单的列出了几个，但就是这几个都让我的技术视野开阔了很多，并且是真正的融入到公司的业务实战中去，是`具有业务价值`的。希望你养成看 issue，紧跟英文社区的习惯，Github issue 里单纯的技术探讨氛围，真的是国内很少有社区可以媲美的。

```js
function AppInner({ children }) {
  const [menus, setMenus] = useState({});

  // 用户信息
  const user = useUser();

  // 主题能力
  useTheme();

  // 权限获取
  useAuth({
    setMenus,
  });

  // 动态菜单也需要用到菜单的能力
  useDynamicMenus({
    menus,
    setMenus,
  });

  return (
    <Context.Provider value={user}>
      <Layout routers={backgrounds}>{children}</Layout>
    </Context.Provider>
  );
}
```

可以看到，`Hook`在代码组织的方面有着得天独厚的优势，甚至各个`模块`之间值的传递都是那么的自然，仅仅是函数传参而已。  
总之，社区推出一些新的东西，它总归是解决了之前的一些痛点。我们跟着大佬的思路走，一定有肉吃。

#### Tree Shaking 的 Issue

相学长的文章[你的 Tree-Shaking 并没什么卵用](https://zhuanlan.zhihu.com/p/32831172)中，也详细的描述了他对于`副作用`的一些探寻过程，在[UglifyJS 的 Issue](https://github.com/mishoo/UglifyJS2/issues/1261)中找到了最终的答案，然后贡献给中文社区，这些内容最开始不会在任何中文社区里出现，只有靠你去探寻和发现。

## 学习方法的转变

从初中级前端开始往高级前端进阶，有一个很重要的点，就是很多情况下国内社区能找到的资料已经不够用了，而且有很多优质资料也是从国外社区二手、三手翻译过来的，翻译质量也不能保证。

这就引申出我们进阶的第一个点，**开始接受英文资料**。

这里很多同学说，我的英文能力不行啊，看不懂。其实我想说，笔者的英语能力也很一般，从去年开始我立了个目标，就是带着划词翻译插件也要开始艰难的看英文文章和资料，遇到不懂的单词就划出来看两眼（没有刻意去背），第五六次遇见这个单词的时候，就差不多记得它是什么意思了。

半年左右的时间下来，（大概保持每周 3 篇以上的阅读量）能肉眼可见的感觉自己的英语能力在进步，很多时候不用划词翻译插件，也可以完整的阅读下来一段文章。

这里是我当时阅读英文优质文章的一些记录，

[英文技术文章阅读](https://github.com/sl1673495/blogs/issues/15)

后面英文阅读慢慢成了一件比较自然的事情，也就没有再刻意去记录，前期可以用这种方式激励自己。

推荐两个英文站点吧，有很多高质量的前端文章。

[dev.to](https://dev.to/t/javascript)  
[medium](https://medium.com)

medium 可能需要借助一些科学工具才能查看，但是里面的会员付费以及作者激励机制使得文章非常的优质。登录自己的谷歌账号即可成为会员，前期可能首页不会推荐一些前端相关的文章，你可以自己去搜索关键字如`Vue`、`React`、`Webpack`，任何你兴趣的前端技术栈，不需要过多久你的首页就会出现前端的推荐内容。好好享受这个高质量的英文社区吧。

## 关于实践

社区有很多大佬实力很强，但是对新手写的代码嗤之以鼻，认为有 `any` 的就不叫 `TypeScript`、认为没有`单元测试`就没资格丢到 Github 上去。这种言论其实也不怪他们，他们也只是对开源软件的要求高到偏执而已。但是对于新手学习来说，这种言论很容易对大家造成打击，导致不敢写 ts，写的东西不敢放出来。其实大可不必，`工业聚` 对于这些观点就发表了一篇很好的看法，让我觉得深受打动，也就是这篇文章开始，我慢慢的把旧项目用 ts 改造起来，慢慢的进步。

[Vue 3.0 公开代码之后……](https://mp.weixin.qq.com/s?__biz=MzA4Njc2MTE3Ng==&mid=2456151423&idx=1&sn=2fec2ff0606b865abaaaaea48ddfd167&chksm=88528ec8bf2507de91cec62b4bad281fb8bf6d16c8a1ea04ea3fedb871099dfb7fda42082fff&mpshare=1&scene=1&srcid=&sharer_sharetime=1585884823115&sharer_shareid=82384198865aad802052fa45394cd852#rd)

## 总结

本篇文章是我在这一年多的学习经历抽象中总结出来，还有很多东西我会陆续加入到这篇文章中去。

希望作为初中级前端工程师的你，能够有所收获。如果能够帮助到你就是我最大的满足。

未完待续... 持续更新中。

## ❤️ 感谢大家

1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149ccf687b7699?w=910&h=436&f=jpeg&s=78195)
