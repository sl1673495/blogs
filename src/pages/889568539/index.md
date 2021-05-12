---
title: '[RFC] 关于 Vue 3 的 IE11 支持'
date: '2021-05-12'
spoiler: ''
---

## 知乎官宣

凌晨时分，尤雨溪突然在知乎上发布了一个消息，宣布 Vue3 将不再支持 IE11，来通过详细的 RFC 了解一下为什么 Vue 团队做出这个决策。


## 原因

从 Vue 3 开发开始，一直到 2018 年底，我们就一直被问及 IE11 支持的问题。

很多用户都问过，Vue 3 是否会支持 IE11，我们最初的计划是先发布 Vue 3，让它稳定下来，然后再增加对 IE11 的支持。

在漫长的开发过程中，我们也对 IE11 的兼容性进行了**研究和实验**，但**较高的复杂度**以及手上**繁多的工作**，让我们不得不**推迟它的优先级**。

当时间来到 2021 年，我们重新审视这个问题时，浏览器和 JavaScript 已经发生了很大的变化。

越来越多的开发人员开始使用更现代的语言特性，更重要的是，[微软自己也开始通过对 Edge 的投资，积极推动用户远离 IE](https://techcommunity.microsoft.com/t5/windows-it-pro-blog/the-perils-of-using-internet-explorer-as-your-default-browser/ba-p/331732)。

[它还在自己的主要项目(如微软 365)中放弃了对 IE11 的支持](https://techcommunity.microsoft.com/t5/microsoft-365-blog/microsoft-365-apps-say-farewell-to-internet-explorer-11-and/ba-p/1591666)。

就在几天前，[WordPress 也决定放弃对 IE11 的支持](https://make.wordpress.org/core/2021/03/25/discussion-summary-dropping-support-for-ie11/)。

IE11 的全球使用率已经[降至 1%以下](https://caniuse.com/usage-table)。

当我们谈论面向公众的网站和应用程序时，IE11 正在明显快速下滑。

已经到了重新考虑 Vue3 对 IE11 支持的时机了。

## 在 Vue3 中支持 IE11，代价如何？

### 行为不一致

Vue 2 的响应式系统是基于 ES5 getter/setters 的。

Vue 3 利用 ES2015 Proxy 提供了一个性能更好、更加完善的响应式系统，而 IE11 无法 polyfill 这些特性。

这是主要的障碍，因为这意味着 Vue 3 要支持 IE11，它本质上需要发布**两个具有不同行为的版本**：一个使用基于 Proxy 的响应式系统，另一个使用类似于 Vue 2 的基于 ES5 getter/setters 的版本。

Vue 3 基于 Proxy 的响应式系统提供了**近乎完整**的语言特性覆盖。

它能够检测到许多在 ES5 中不敢想象的操作，例如属性的添加/删除、数组索引和长度突变，以及 `in` 操作符的拦截。

为 Vue 3 的 Proxy 版本编写的应用**肯定不能在 IE11 版本中工作**。这不仅给我们带来了技术上的复杂性，也给开发人员带来了持续的精神负担。

我们最初的计划是在 IE11 版本的开发构建中**同时发布 Proxy 和 ES5 的两种响应性版本**。

当它在支持 Proxy 的开发环境中运行时，会**检测并警告**不兼容 ie11 的一些用法。理论上可行，但是复杂度巨大，因为它需要将两种实现混合在一起，并且有可能导致**开发和生产之间的行为差异**。

### 长期维护的负担

支持 IE11 也意味着我们必须考虑在整个代码库中使用的语言特性，并为我们的发布版本找到合适的 poliyfill / 编译策略。

每一个不能在 IE11 中被 polyfill 的新特性都会带来新的行为警告。一旦 Vue 3 承诺支持 IE11，就永远没办法摆脱了，直到下一个大版本。

### 给库作者带来的复杂度

如果 Vue 本身可以完全覆盖掉这些复杂度，那么一定程度上我们还是可以接受的。然而，在与社区成员讨论后，我们意识到共存的两个响应性实现也不可避免地**影响库作者的开发**。

通过在 Vue 3 中支持 IE11，库作者本质上也需要同样做一些决定。库作者不得不考虑他们的库**使用的是哪种 Vue 3 版本**(可能还支持 Vue 2)。如果他们决定支持 IE11，他们在编写库时，脑子里也必须**时刻考虑 ES5 响应式系统的一些缺陷**。

### 为 IE11 持续存在做贡献

**没有人想支持 IE11**。它是一个**死气沉沉的浏览器**，停留在过去。Web 生态系统向前发展得越远，我们在尝试支持它时，需要填补的缺口就越大。讽刺的是，通过在 Vue 3 中支持 IE11，我们给了它**更多的生命力**。考虑到我们的用户基础，放弃对 IE11 的支持可能会让它**更快地被淘汰**。

## 对于那些实在需要 IE11 支持的人

我们很清楚，对 IE11 的真正需求来自那些没办法做升级的人：金融机构、教育部门和那些依赖 IE11 作为屏幕阅读器的人。如果你正在构建一个针对这些领域的应用，你可能没有选择。

如果您需要 IE11 支持，我们的建议是使用 Vue 2。与其为 Vue3 和未来的版本承担巨大的技术债，我们相信，把工作重心放在让 Vue2 **拥有更多 Vue3 类似的特性**更有意义，让两个版本之间的开发体验更相似。

一些我们考虑带给 Vue 2.7 的功能：

- 把 [@vue/composition-api plugin](https://github.com/vuejs/composition-api)合并进 Vue2。这会让使用 Composition API 开发的库同时支持 Vue2 和 Vue3。
- 单文件组件（SFC）中的[script setup](https://github.com/vuejs/rfcs/pull/227)语法。
- `emits` 选项。
- 提升 TypeScript 类型支持。
- 在 Vite 中正式支持 Vue 2(目前通过[非官方插件](https://github.com/underfin/vite-plugin-vue2))

注：以上列表是**暂时的/不详尽**的，我们最后会在单独的 RFC 中讨论/最终确定。


## 引用

- [RFC 原文地址](https://github.com/vuejs/rfcs/blob/ie11/active-rfcs/0000-vue3-ie11-support.md#for-those-who-absolutely-need-ie11-support "RFC 原文地址")
- [社区讨论](https://github.com/vuejs/rfcs/discussions/296 "社区讨论")
- [知乎中文发布](https://zhuanlan.zhihu.com/p/362000763 "知乎中文发布")
