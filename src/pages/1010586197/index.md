---
title: 'Nuxt 3 来了！'
date: '2021-09-29'
spoiler: ''
---

先放个彩蛋，Nuxt3 官网有趣的小交互：
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f4897ee8cc924b5dab4488fc2987edf4~tplv-k3u1fbpfcp-zoom-1.image "GIF 2021-9-21 2-35-02.gif")

NuxtJS 让你构建你的下一个 Vue.js 应用程序变得更有信心。这是一个开源的框架，让 Web 开发变得简单而强大。Nuxt 3.0 来了，让我们一起来看看它有哪些让人激动的新特性！

## 新特性！

Nuxt 3 的重构精简了内核，并且让速度更快，开发体验更好。

### 更轻量

以现代浏览器为目标的情况下，服务器部署和客户端产物最多可达 **75** 倍的减小。

### 更快

用动态服务端代码分割来优化冷启动，由 nitro 提供能力。

### Hybrid

增量静态生成和其他高级模式现在都成为可能。

### Suspense

导航前后皆任何组件中获取数据。

### Composition API

使用 Composition API 和 Nuxt 3 的 composables 实现真正的可复用性。

### Nuxt CLI

全新的零依赖体验，助您轻松搭建项目和集成模块。

### Nuxt Devtools

更多的信息和快速修复，在浏览器中高效工作。

### Nuxt Kit

全新的基于 TypeScript 和跨版本兼容的模块开发。

### Webpack 5

更快的构建速度和更小的构建产物，并且零配置。

### Vite

用 Vite 作为你的打包器，体验轻量级的快速 HMR。

### Vue3

Vue3 会成为您下一个应用的坚实基础。

### TypeScript

由原生 TypeScript 和 ESM 构成 —— 没有额外的步骤。

## Nitro 引擎

我们在 Nuxt 的新服务端引擎 **Nitro** 上工作了整整 9 个月。它解锁了 Nuxt 服务端等方面新的**全栈能力** 。

在开发中，它使用 rollup 和 Node.js workers 来为服务端代码和上下文隔离服务。并且通过读取 `server/api/` 目录下的文件和 `server/functions` 目录下的服务端函数来**生成你的服务端 API**。

在生产中，它将您的 app 和服务端代码构建到独立的 `.output` 目录中。**这份输出是很轻量的**： 代码是压缩的，并且移除了所有 Node.js 模块。你可以在任何支持 JavaScript 的系统下部署这份产物，Node.js、Severless、Workers、边缘渲染（Edge Side Rendering）或纯静态部署。

这份产物包含了运行时代码，来支持在任意环境下运行 Nuxt 服务端（包括实验性的浏览器 Service Workers！）的，并且启动静态文件服务，这使得它成为了一个符合 JAMStack 架构的**真正的 hybrid 框架**。另外还实现了一个原生存储层，支持多个源、驱动和本地资源。

Nitro 的基础是 rollup 和 h3：一个为高性能和可移植性而生的最小 http 框架。

## Nuxt 桥梁

经过四年的开发，我们迁移到 Vue3，重写了 Nuxt，使它有了更坚实的基础，为未来的更多新特性做好准备。

### 流畅的升级到 Nuxt3

我们致力于在让用户更加轻松的从 Nuxt2 升级到 Nuxt3。

- 遗留的插件和模块将保持工作
- Nuxt2 配置是兼容的
- 部分 pages options API 可用

### 将 Nuxt 3 的体验带到现有的 Nuxt2 项目中

当我们在开发 Nuxt 3 的新特性的同时，也将其中的一些特性移植到了 Nuxt 2 中。

- 在 Nuxt2 中启用 Nitro
- 在 Nuxt2 中使用 Composition API（和 Nuxt3 一样）
- 在 Nuxt2 中使用新的 CLI 和 Devtools
- 渐进式升级到 Nuxt3
- 兼容 Nuxt2 的模块生态系统
- 一片片的升级（Nitro、Composition API、Nuxt Kit）

感谢您的耐心，我们已经迫不及待的发布它，并且得到您的反馈 —— **Nuxt 团队**。

## 演讲
Vue 北京的活动来跟大家见面啦～ 这次我们邀请了 Nuxtlab 的创始人之一 Sebastien Chopin 来分享 Nuxt3 之旅。对 Nuxt3 期待已久的同学一定要来听哟。 9月26号本周日下午4点50，我们不见不散！

📅 时间: 9月26日下午这周日 16:50 ~ 18:30

🏠地点：B站直播间：http://live.bilibili.com/22948040

视频号：VueBeijing


💵 票价：0元：任何人都可以免费参加
    10元：如果您认为我们的活动是有意义的，可以赞助我们10元，用于以后举办更多优质的技术分享活动。

📖 语言: 英语带AI识别中文字幕

🤝 媒体伙伴： ⚡️ 掘金

👇 立即报名 
http://hdxu.cn/D9oun


![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/47dcf4aef2df4d7ca71800d89ab3c222~tplv-k3u1fbpfcp-watermark.image?)


## 官网原文地址

https://nuxtjs.org/v3
