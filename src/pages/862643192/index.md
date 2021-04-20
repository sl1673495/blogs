---
title: 'VueConf 2021 抢先看，Evan You 和你聊聊 Vue 的未来'
date: '2021-04-20'
spoiler: ''
---

> 本文首发公众号「[前端从进阶到入院](https://oscimg.oschina.net/oscnet/up-fa75de6c6ac2dbce9cb2e85b58753d4568b.png)」，欢迎关注！

![](https://images.gitee.com/uploads/images/2021/0415/012015_630e101a_1087321.png)

## 近况

![](https://images.gitee.com/uploads/images/2021/0415/012030_b8ea9e2f_1087321.png)

**158 万**周活跃用户（通过 devtools 插件来统计），**940 万**的月下载量。

## 对比去年

![](https://images.gitee.com/uploads/images/2021/0415/012151_cbf950ef_1087321.png)

Devtools：110 万 -> 158 万（+43.6%） NPM：620 万 -> 940 万（+51.6%）

## Vue 3.0 One Piece

![](https://images.gitee.com/uploads/images/2021/0415/012242_a695cd67_1087321.png)

![](https://images.gitee.com/uploads/images/2021/0415/012303_70986902_1087321.png)

自那之后，Vue3 逐渐趋于稳定，继续探索用户体验。

## Vue Router 4.0

![](https://images.gitee.com/uploads/images/2021/0415/012410_c150f18a_1087321.png)

已经稳定。

## Vuex 4.0

![](https://images.gitee.com/uploads/images/2021/0415/012436_975c87ba_1087321.png)

已经稳定。

## 生态

![](https://images.gitee.com/uploads/images/2021/0415/012507_3a502d58_1087321.png)

慢慢赶上了！

-   Nuxt 3
-   Vuetify
-   Quasar
-   Element Plus
-   Ant Design Vue

## 用户体验

![](https://images.gitee.com/uploads/images/2021/0415/012602_8eece2b0_1087321.png)

持续探索中：

-   新的构建工具
-   更棒的语法
-   IDE/TS 支持

## 构建工具

![](https://images.gitee.com/uploads/images/2021/0415/012817_2b34b042_1087321.png)

Vite，不用说了，今年的明星项目。

-   和 Vue-CLI 更加相似的体验
-   基于 ESM 的 HMR 热更新
-   ESBuild 提供依赖预构建
-   Rollup 兼容的插件接口
-   内置 SSR 支持
-   更多更多……

可以扩展阅读笔者之前写的[浅谈 Vite 2.0 原理，依赖预编译，插件机制是如何兼容 Rollup 的？](https://juejin.cn/post/6932367804108800007)

![](https://images.gitee.com/uploads/images/2021/0415/013328_a14d8061_1087321.png)

Vite 还是 Vue-CLI？

-   短期内会共存
-   长期会融合：Vite 的速度 + Vue-CLI 的全面度支持

## 测试

![](https://images.gitee.com/uploads/images/2021/0415/013456_ee8f5725_1087321.png)

-   Cypress 新版组件测试
-   @web/test-runner
-   Jest 集成进行中

看了下 `@web/test-runner` 的简介，非常全面的测试解决方案：

![](https://images.gitee.com/uploads/images/2021/0415/013730_8ab1be13_1087321.png)

## VitePress

![](https://images.gitee.com/uploads/images/2021/0415/014112_43c3431a_1087321.png)

基于 Vue3 + Vite 的静态站点生成器。

![](https://images.gitee.com/uploads/images/2021/0415/014145_35ec8a41_1087321.png)

它的独特之处在于：

-   利用 SPA 的开发体验来定制用户主题
-   在 Markdown 里自由加入动态组件
-   自动消除静态内容的“双重负载”

![](https://images.gitee.com/uploads/images/2021/0415/015752_04714064_1087321.png)

利用 VitePress 这个平台，探索未来 SSR/SSG 优化（Eat Your Own Dog Food）

-   更积极的消除静态内容（甚至是主题组件）
-   更高效的构建
-   按需构建 \+ 边缘缓存

## 新的开发体验

![](https://images.gitee.com/uploads/images/2021/0415/020121_3075f295_1087321.png)

利用编译器做更多事情：

-   `script setup`
-   `style` CSS 变量注入

### script setup

![](https://images.gitee.com/uploads/images/2021/0415/020154_4a152c1e_1087321.png)

![](https://images.gitee.com/uploads/images/2021/0415/020209_8a1f98d5_1087321.png)

-   [RFC 地址](https://github.com/vuejs/rfcs/blob/script-setup-2/active-rfcs/0000-script-setup.md)
-   在单文件组件中提供更符合用户体验的 Composition API
-   提高运行时性能

### style 变量注入

![](https://images.gitee.com/uploads/images/2021/0415/020339_ec39cc14_1087321.png)

-   [RFC 地址](https://github.com/vuejs/rfcs/blob/style-vars-2/active-rfcs/0000-sfc-style-variables.md)
-   利用 `v-bind()` 在单文件组件的 `style` 中注入 JS 状态驱动的 CSS 变量
-   CSS-in-JS 的好处尽享，但避免了它的心智负担。

## 更好的 IDE/TS 支持

![](https://images.gitee.com/uploads/images/2021/0415/020519_813698a3_1087321.png)

多个探索中的项目

-   Vetur
-   VueDX
-   Volar

获得了：

-   类型检查，语法提示和 SFC templates 的自动重构

接下来：

-   **把这些努力整合成更推荐的链路**
-   提供 CLI 工具来利用 TS 校验 SFC

![](https://images.gitee.com/uploads/images/2021/0415/020759_6a709583_1087321.png)

计划：

-   基于 Volar 的**新的官方 VSCode 插件**，从 Vetur 和 VueDX 上汲取很多灵感。
-   通过内部设计来支持其他编辑器，通过 LSP（Language Service Protocol）

## 未来

![](https://images.gitee.com/uploads/images/2021/0415/020936_e3b1730e_1087321.png)

我们在 Vue3 中放弃了 IE11。

-   [RFC](https://github.com/vuejs/rfcs/blob/ie11/active-rfcs/0000-vue3-ie11-support.md)
-   [讨论](https://github.com/vuejs/rfcs/discussions/296)

笔者对这个 RFC 也进行了翻译：

[Vue3 考虑彻底放弃 IE 浏览器](https://mp.weixin.qq.com/s?__biz=MzI3NTM5NDgzOA==&mid=2247495151&idx=1&sn=981920c2345fb3a70097b2a8dfa5ba66&chksm=eb07d596dc705c80b9db1bf62b0cc614b4f4012087e994ad178d5d91cfc3b9ad16f5c5ae72f0&token=1932513687&lang=zh_CN#rd)

![](https://images.gitee.com/uploads/images/2021/0415/021110_2343bc4d_1087321.png)

Vue 2.7 会成为坚持留守 IE11 人群的选择，它会提供更多的 Vue3 特性和 TS 支持。（估计在 2021 第三季度）

![](https://images.gitee.com/uploads/images/2021/0415/021245_168586dc_1087321.png)

Vue3 的集成构建也要来了！

-   估计在**四月末**
-   可单独配置来兼容 v2

![](https://images.gitee.com/uploads/images/2021/0415/021338_7e3fe333_1087321.png)

![](https://images.gitee.com/uploads/images/2021/0415/021353_dddaff8e_1087321.png)

Vue3 会在 2021 二季度末尾，变成新的默认版本！

-   npm 的 lastest tag 会默认安装 Vue3
-   [vuejs.org](http://vuejs.org) 官网会指向 Vue3 的文档

![](https://images.gitee.com/uploads/images/2021/0415/021440_19fa2876_1087321.png)

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![](https://oscimg.oschina.net/oscnet/up-fa75de6c6ac2dbce9cb2e85b58753d4568b.png)