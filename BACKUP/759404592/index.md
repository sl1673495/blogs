---
title: 'Vue Router 4.0 正式发布！焕然一新。'
date: '2020-12-08'
spoiler: ''
---

> [原文发布地址](https://github.com/vuejs/vue-router-next/releases/tag/v4.0.0)

今天，Vue Router 4 正式发布稳定版本。

在经历了 14 个 Alpha，13 个 Beta 和 6 个 RC 版本之后，Vue Router v4 闪亮登场，为你带来了 TypeScript 集成、新功能以及对现代应用程序的一致性改进，已经准备好成为 Vue3 新应用的最佳伴侣。

将近 2 年的时间，大约 1500 次提交，15 个[RFC](https://github.com/vuejs/rfcs/pulls?q=is%3Apr+sort%3Aupdated-desc+label%3Arouter+is%3Aclosed)，无数的心血……以及许多用户的帮助以及他们的错误报告和功能请求。 谢谢大家的帮助！

## 项目结构优化

Vue Router 现在分为三个模块：

- **History 实现**： 处理地址栏，并且特定于 Vue Router 运行的环境（节点，浏览器，移动设备等）
- **Router 匹配器**：处理类似 `/users/:id` 的路由解析和**优先级处理**。
- **Router**: 将一切连接在一起，并处理路由特定功能，例如导航守卫。

## 动态路由

[动态路由](https://next.router.vuejs.org/guide/advanced/dynamic-routing.html)是 Vue Router 最受欢迎的功能之一。 它让路由变得更灵活，更强大，让曾经不可能的功能成为了现实！ Vue Router4 新增了有**自动优先级排名**的高级路径解析功能，用户新现在可以以随意的顺序定义路由，因为 Router 会根据 URL 字符串表示来**猜测**应该匹配的路由。

优先级排名，其实就是根据你路径书写的规则计算出一个得分，根据得分来优先选用最有可能的那一项。

举个例子来说，你同时写了 `/users` 和 `/:w+` 这两个路由：

```js
const routes = [
  {
    path: '/users',
    Component: Users
  },
  {
    path: '/:w+',
    Component: NotFound
  }
]
```

那么你当然希望在输入 `/users` 这个更精确的路径的时候，走上面的规则，而下面则作为兜底规则。在旧版的 Vue Router 中需要通过路由声明的顺序来保证这个行为，而新版则无论你怎样放置，都会按照得分系统来计算该匹配哪个路由。

甚至专门有 [Path Ranker](https://paths.esm.dev/?p=AAMeJVyBwRkJTALagIAOuGrgACU.#) 这个网页来帮助你计算路由的优先级得分。

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e9a489d6c63e4232882d5ce773b3ea24~tplv-k3u1fbpfcp-watermark.image)

在测试用例中，ssh 找到了一个更具体的**优先级得分**排名，可以先感受一下：

```js
it('works', () => {
  checkPathOrder([
    '/a/b/c',
    '/a/b',
    '/a/:b/c',
    '/a/:b',
    '/a',
    '/a-:b-:c',
    '/a-:b',
    '/a-:w(.*)',
    '/:a-:b-:c',
    '/:a-:b',
    '/:a-:b(.*)',
    '/:a/-:b',
    '/:a/:b',
    '/:w',
    '/:w+'
  ])
})
```

简单来说，越明确的路由排名越高，越模糊则反之，无关顺序，非常有意思。

## 改进后的导航系统

新的导航系统更加具有一致性，它改善了滚动行为的体验，使其更加接近原生浏览器的行为。 它还为用户提供了有关导航状态的几乎更多信息，用户可以用这些信息，通过 `ProgressBar`和 `Modal`之类的全局 UI 元素让用户的体验变得更好。

## 更强大的 Devtools

多亏了新的[Vue Devtools](https://chrome.google.com/webstore/detail/vuejs-devtools/ljjemllljcmogpfapbkkighbhhppjdbg)，Vue Router 能够和浏览器进行以下更高级的整合。

1. **时间轴**记录路由变化：

![时间轴记录下你的路由变化](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d58556ac84354cc9a36e5b6a0358be5f~tplv-k3u1fbpfcp-watermark.image)

2. **完整 route 目录**，能够帮助你轻松进行调试：
   ![清晰的路由目录](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9f62dd5303844fdf986d3917f5e3a894~tplv-k3u1fbpfcp-watermark.image)

## 更好的路由守卫

和 `next` 说拜拜，现在确认跳转不需要再手动执行这个函数了，而是根据你的返回值来决定行为。同样支持异步返回 Promise。

现在的路由守卫 API 更加友好且合理了，可以完美利用 `async await` 做异步处理，比如这样：

```js
router.beforeEach(async (to, from) => {
  // canUserAccess() returns `true` or `false`
  return await canUserAccess(to)
})
```

## 一致的编码

编码方式（Encoding）做了统一的适配，现在将在不同的浏览器和路由位置属性（`params`, `query` 和 `hash`）中保持一致。 作为参数传递给 `router.push()` 时，不需要做任何编码，在你使用 `$route` 或 `useRoute()`去拿到参数的时候永远是解码（Decoded）的状态。

## 迁移成本低

Vue Router 4 主要致力于于在改善现有 Router 的同时保持非常相似的 API，如果你已经很上手旧版的 Vue Router 了，那你的迁移会做的很顺利，可以查看文档中的[完整迁移指南](https://next.router.vuejs.org/guide/migration/index.html)。

## 展望未来

在过去的几个月中，Vue Router 一直稳定而且好用，现在它可以做些更好玩的事儿了：

- 使用现有工具（Vetur，Vite，Devtools 等）得到更好的开发体验。
- 与 Suspense 等现代功能更好地集成。
- RFCs 和社区共同探讨出更好用的 API。
- 开发更轻型的版本。

## 试试看

等不及想试试 Vue Router 4 了？这里有[CodeSandbox](https://codesandbox.io/s/vue-router-4-reproduction-hb9lh)，还有[集成好 Tailwind CSS 的 Vite 模板](https://vite-tailwind.esm.dev/about)，或使用[CLI](https://cli.vuejs.org/)来开始你的游玩。

想学习 Vue Router 4 的更多先进理念了？请立刻查看我们的[新文档](https://next.router.vuejs.org/)。 如果您是现有的 Vue 2.x 用户，请直接转到[迁移指南](https://next.router.vuejs.org/guide/migration/index.html#breaking-changes)。


## 相关阅读

[深入揭秘前端路由本质，手写 mini-router](https://mp.weixin.qq.com/s?__biz=MzI3NTM5NDgzOA==&mid=2247485173&idx=1&sn=0eb7739aaf8e456d1b7a58dd353107ef&chksm=eb043e8cdc73b79a16f3982662041aed684b63198d772d3b6a47b5a89816e524e09dd8d92781&token=1581050816&lang=zh_CN&scene=21#wechat_redirect)

## 感谢关注

> 本文首发于公众号「**[前端从进阶到入院](https://ssh-1300257814.cos.ap-shanghai.myqcloud.com/public_qrcode)**」，点击关注领取**万字高级前端进阶路线，前端算法零基础精选题解**。也可以找我**内推字节跳动**，大量 HC！