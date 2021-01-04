# [Atomic CSS-in-JS](https://github.com/sl1673495/blogs/issues/69)

原子 CSS

随着 Facebook 和 Twitter 最近的产品部署，我认为一个新的趋势正在缓慢增长:**atomic CSS-in-JS**。

在这篇文章中，我们将看到什么是原子 CSS，它如何与 **functional / utility-first CSS**(如 TailwindCSS)联系起来，目前很多大公司在 React 代码仓库中使用它们。

由于我不是这方面的专家，所以我不会去深入探讨它的利弊。我只是希望能帮助你了解它的大致内容。

注意：Atomic CSS 与 [Atomic Design](https://atomicdesign.bradfrost.com/) 并没有真正的关系。

## 什么是原子 CSS？

你可能听说过各种 CSS 方法，如 BEM, OOCSS…

```html
<button class="button button--state-danger">Danger button</button>
```

现在，人们真的很喜欢 [Tailwind CSS](https://tailwindcss.com/) 和它的 [工具优先（utility-first）](https://tailwindcss.com/docs/utility-first) 的概念。这与 Functional CSS 和 [Tachyon](https://github.com/tachyons-css/tachyons) 这个库的理念非常接近。

```html
<button
  class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
>
  Button
</button>
```

用海量的工具类（utility classes）组成的样式表，让我们可以在网页里大显身手。

原子 CSS 就像是 工具优先（utility-first）CSS 的一个极端版本: 所有 CSS 类都有一个唯一的 CSS 规则。原子 CSS 最初是由 Thierry Koblentz (Yahoo!)在 2013 年[挑战 CSS 最佳实践](https://www.smashingmagazine.com/2013/10/challenging-css-best-practices-atomic-approach/)时使用的。

```css
/* 原子 CSS */
.bw-2x {
  border-width: 2px;
}
.bss {
  border-style: solid;
}
.sans {
  font-style: sans-serif;
}
.p-1x {
  padding: 10px;
}
/* 不是原子 CSS 因为这个类包含了两个规则 */
.p-1x-sans {
  padding: 10px;
  font-style: sans-serif;
}
```

使用工具/原子 CSS，我们可以把结构层和表示层结合起来:当我们需要改变按钮颜色时，我们直接修改 HTML，而不是 CSS！

这种**紧密耦合**在现代 CSS-in-JS 的 React 代码库中也得到了承认，但似乎 是 CSS 世界里最先对传统的“关注点分离”有一些异议。

比较特殊的样式需求也不是什么问题，因为我们使用的是最简单的类选择器。

我们现在通过 html 标签来添加样式，发现了几个有趣的属性：

- 我们增加新功能的时候，样式表的增长减缓了。
- 我们可以到处移动 html 标签，并且能确保样式也同样生效。
- 我们可以删除新特性，并且确保样式也同时被删掉了。

可以肯定的缺点是，html 有点臃肿。对于服务器渲染的 web 应用程序来说可能是个缺点，但是类名中的高冗余使得 gzip 可以压缩得很好。同时它可以很好地处理之前重复的 css 规则。

一旦你的工具/原子 CSS 准备好了，它将不会有太大的变化或增长。可以更有效地缓存它(你可以将它附加到 vendor.css 中，重新部署的时候它也不会失效)。它还具有相当好的可移植性，可以在任意其他应用程序中使用。

## 工具/原子 CSS 的限制

工具/原子 CSS 看起来很有趣，但它们也带来了一些挑战。

人们通常手工编写工具/原子 CSS，精心制定命名约定。但是很难保证这个约定易于使用、保持一致性，而且不会随着时间的推移而变得臃肿。

这个 CSS 可以**团队协作开发**并保持**一致性**吗?它受[**巴士因子**](https://zh.wikipedia.org/wiki/%E5%B7%B4%E5%A3%AB%E5%9B%A0%E5%AD%90)的影响吗?

> 巴士系数是软件开发中关于软件专案成员之间讯息与能力集中、未被共享的衡量指标，也有些人称作“货车因子”、“卡车因子”（lottery factor/truck factor）。一个专案或计划至少失去若干关键成员的参与（“被巴士撞了”，指代职业和生活方式变动、婚育、意外伤亡等任意导致缺席的缘由）即导致专案陷入混乱、瘫痪而无法存续时，这些成员的数量即为巴士系数。

你还需要**预先开发好**一个不错的工具/原子样式表，然后才能开始开发新功能。

如果工具/原子 CSS 是由别人制作的，你将不得不首先学习类命名约定(即使你知道 CSS 的一切)。这种约定是**有主观性**的，很可能你不喜欢它。

有时，你需要一些**额外的 CSS**，而工具/原子 CSS 并不提供这些 CSS。没有约定好的方法来提供这些一次性样式。

## Tailwind 赶来支援

Tailwind 使用的方法是非常便捷的，并且解决了上述一些问题。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/fd402582aefa467e98daaa9e18516435~tplv-k3u1fbpfcp-watermark.image)

它并不是真的为所有网站提供一些唯一的工具 CSS，取而代之的是，它提供了一些公用的命名约定。通过一个[配置文件](https://tailwindcss.com/docs/configuration)，你可以为你的网站生成一套**专属**的工具 CSS。

Tailwind 的知识可以迁移到其他应用程序，即使它们使用的类名并不完全相同。这让我想起了 React 的「一次学习，到处编写」理念。

我看到一些用户反馈说，Tailwind 提供的类名能覆盖他们 90% - 95% 的需求。这个覆盖面似乎已经足够广了，并不需要经常写一次性的 CSS 了。

此时，你可能想知道**为什么要使用原子 CSS 而不是 Tailwind CSS**?强制执行原子 CSS 规则的**一个规则，一个类名**，有什么好处?你最终会得到更大的 html 标签和更烦人的命名约定吗?Tailwind 已经有了足够多的原子类了啊。

那么，我们是否应该放弃原子 CSS 的想法，而仅仅使用 Tailwind CSS?

Tailwind 是一个优秀的解决方案，但仍然有一些问题没有解决:

- 需要学习一套主观的命名约定

- CSS 规则插入顺序仍然很重要

- 未使用的规则可以轻松删除吗?

- 我们如何处理剩下的一次性样式?

与 Tailwind 相比，手写原子 CSS 可能**不是最方便**的。

## 和 CSS-in-JS 比较

CSS-in-JS 和工具/原子 CSS 有密切关系。这两种方法都提倡使用**标签**进行样式化。以某种方式试图模仿**内联样式**，这让它们有了很多相似的特性(比如在移动某些功能的时候更有信心)。

[Christopher Chedeau](https://twitter.com/vjeux) 一直致力于推广 React 生态系统中 CSS-in-JS 理念。在很多次演讲中，他都解释了 CSS 的问题:
