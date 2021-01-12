---
title: 'Atomic CSS-in-JS'
date: '2021-01-04'
spoiler: ''
---

> 原文地址：https://sebastienlorber.com/atomic-css-in-js
>
> 翻译 / 润色：ssh

随着 Facebook 和 Twitter 最近的产品部署，我认为一个新的趋势正在缓慢增长:**Atomic CSS-in-JS**。

在这篇文章中，我们将看到什么是Atomic CSS（原子 CSS），它如何与 Tailwind CSS 这种实用工具优先的样式库联系起来，目前很多大公司在 React 代码仓库中使用它们。

由于我不是这方面的专家，所以我不会去深入探讨它的利弊。我只是希望能帮助你了解它的大致内容。

先抛出一个令人开心的结论，新的 CSS 编写和构建方式让 Facebook 的主页**减少了 80% 的 CSS 体积**。

## 什么是原子 CSS？

你可能听说过各种 CSS 方法，如 BEM, OOCSS…

```html
<button class="button button--state-danger">Danger button</button>
```

现在，人们真的很喜欢 [Tailwind CSS](https://tailwindcss.com/) 和它的 [实用工具优先（utility-first）](https://tailwindcss.com/docs/utility-first) 的概念。这与 Functional CSS 和 [Tachyon](https://github.com/tachyons-css/tachyons) 这个库的理念非常接近。

```html
<button
  class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
>
  Button
</button>
```

用海量的实用工具类（utility classes）组成的样式表，让我们可以在网页里大显身手。

原子 CSS 就像是实用工具优先（utility-first）CSS 的一个极端版本: 所有 CSS 类都有一个唯一的 CSS 规则。原子 CSS 最初是由 Thierry Koblentz (Yahoo!)在 2013 年[挑战 CSS 最佳实践](https://www.smashingmagazine.com/2013/10/challenging-css-best-practices-atomic-approach/)时使用的。

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

使用实用工具/原子 CSS，我们可以把结构层和表示层结合起来:当我们需要改变按钮颜色时，我们直接修改 HTML，而不是 CSS！

这种**紧密耦合**在现代 CSS-in-JS 的 React 代码库中也得到了承认，但似乎 是 CSS 世界里最先对传统的**关注点分离**有一些异议。

CSS 权重也不是什么问题，因为我们使用的是最简单的类选择器。

我们现在通过 html 标签来添加样式，发现了一些有趣的事儿：

- 我们增加新功能的时候，样式表的增长减缓了。
- 我们可以到处移动 html 标签，并且能确保样式也同样生效。
- 我们可以删除新特性，并且确保样式也同时被删掉了。

可以肯定的缺点是，html 有点臃肿。对于服务器渲染的 web 应用程序来说可能是个缺点，但是类名中的高冗余使得 gzip 可以压缩得很好。同时它可以很好地处理之前重复的 css 规则。

一旦你的实用工具/原子 CSS 准备好了，它将不会有太大的变化或增长。可以更有效地缓存它(你可以将它附加到 vendor.css 中，重新部署的时候它也不会失效)。它还具有相当好的可移植性，可以在任意其他应用程序中使用。

## 实用工具/原子 CSS 的限制

实用工具/原子 CSS 看起来很有趣，但它们也带来了一些挑战。

人们通常手工编写实用工具/原子 CSS，精心制定命名约定。但是很难保证这个约定易于使用、保持一致性，而且不会随着时间的推移而变得臃肿。

这个 CSS 可以**团队协作开发**并保持**一致性**吗?它受[**巴士因子**](https://zh.wikipedia.org/wiki/%E5%B7%B4%E5%A3%AB%E5%9B%A0%E5%AD%90)的影响吗?

> 巴士系数是软件开发中关于软件专案成员之间讯息与能力集中、未被共享的衡量指标，也有些人称作“货车因子”、“卡车因子”（lottery factor/truck factor）。一个专案或计划至少失去若干关键成员的参与（“被巴士撞了”，指代职业和生活方式变动、婚育、意外伤亡等任意导致缺席的缘由）即导致专案陷入混乱、瘫痪而无法存续时，这些成员的数量即为巴士系数。

你还需要**预先开发好**一个不错的实用工具/原子样式表，然后才能开始开发新功能。

如果实用工具/原子 CSS 是由别人制作的，你将不得不首先学习类命名约定(即使你知道 CSS 的一切)。这种约定是**有主观性**的，很可能你不喜欢它。

有时，你需要一些**额外的 CSS**，而实用工具/原子 CSS 并不提供这些 CSS。没有约定好的方法来提供这些一次性样式。

## Tailwind 赶来支援

Tailwind 使用的方法是非常便捷的，并且解决了上述一些问题。

它通过 **Utility-First** 的理念来解决 CSS 的一些缺点，通过抽象出一组类名 -> 原子功能的集合，来避免你为每个 div 都写一个专有的 class，然后整个网站重复写很多重复的样式。

传统卡片样式写法：

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/04a75ec8a88d4586af9c59ce190a6293~tplv-k3u1fbpfcp-watermark.image)

Tailwind 卡片样式写法：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9dd33144e8d54c67b18ba15834e68ab1~tplv-k3u1fbpfcp-watermark.image)

它并不是真的为所有网站提供一些唯一的实用工具 CSS，取而代之的是，它提供了一些公用的命名约定。通过一个[配置文件](https://tailwindcss.com/docs/configuration)，你可以为你的网站生成一套**专属**的实用工具 CSS。
 
ssh 注：这里原作者没有深入介绍，为什么说是一套命名约定呢而不是生成一些定死的 CSS 呢？

举几个例子让大家感受一些，Tailwind 提供了一套强大的构建系统，比如默认情况下它提供了一些响应式的断点值：
```js
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      // => @media (min-width: 640px) { ... }

      'md': '768px',
      // => @media (min-width: 768px) { ... }

      'lg': '1024px',
      // => @media (min-width: 1024px) { ... }

      'xl': '1280px',
      // => @media (min-width: 1280px) { ... }
    }
  }
}
```

你可以随时在配置文件中更改这些断点，比如你所需要的小屏幕 `sm` 可能指的是更小的 `320px`，那么你想要在小屏幕时候采用 flex 布局，还是照常写 `sm:flex`，遵循同样的约定，只是这个 `sm` 已经被你修改成适合于项目需求的值了。

在比如说，Tailwind 里的 `spacing` 掌管了 margin、padding、width 等各个属性里的代表空间占用的值，默认是采用了 rem 单位，当你在配置里这样覆写后：

```js
// tailwind.config.js
module.exports = {
  theme: {
    spacing: {
      '1': '8px',
      '2': '12px',
      '3': '16px',
      '4': '24px',
      '5': '32px',
      '6': '48px',
    }
  }
}
```

你再去写 `h-6`（height）, `m-2`（margin）, `mb-4`（margin-bottom），后面数字的意义就被你改变了。

也许从桌面端换到移动端项目，这个 `6` 代表的含义变成了 `6rem`，但是这套约定却深深的印在你的脑海里，成为你知识的一部分了。

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

CSS-in-JS 和实用工具/原子 CSS 有密切关系。这两种方法都提倡使用**标签**进行样式化。以某种方式试图模仿**内联样式**，这让它们有了很多相似的特性(比如在移动某些功能的时候更有信心)。

[Christopher Chedeau](https://twitter.com/vjeux) 一直致力于推广 React 生态系统中 CSS-in-JS 理念。在很多次演讲中，他都解释了 CSS 的问题:

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3d923a2dd76141a78242d0308e1d117a~tplv-k3u1fbpfcp-watermark.image)

1. 全局命名空间
2. 依赖
3. 无用代码消除
4. 代码压缩
5. 共享常量
6. 非确定性（Non-Deterministic）解析
7. 隔离

实用工具/原子 CSS 也解决了其中的一些问题，但也确实没法解决所有问题（特别是样式的**非确定性解析**)。

如果它们有很多相似之处，那我们能否同时使用它们呢?

## 探索原子 CSS-in-JS

原子 CSS-in-JS 可以被视为是“自动化的原子 CSS”：

- 你不再需要创建一个 class 类名约定

- 通用样式和一次性样式的处理方式是一样的

- 能够提取页面所需要的的关键 CSS，并进行代码拆分

- 有机会修复 JS 中 CSS 规则插入顺序的问题

我想强调两个特定的解决方案，它们最近推动了两个大规模的原子 CSS-in-JS 的部署使用，来源于以下两个演讲。

- React-Native-Web at Twitter (更多细节在[Nicolas Gallagher 的演讲](https://www.youtube.com/watch?v=tFFn39lLO-U))。

- Stylex at Facebook (更多细节在[Frank Yan 的演讲](https://www.youtube.com/watch?v=9JZHodNR184))。

也可以看看这些库：

- Styletron
- Fela
- Style-Sheet
- cxs
- otion
- css-zero
- ui-box
- style9
- stitches
- catom

### React-Native-Web

React-Native-Web 是一个非常有趣的库，让浏览器也可以渲染 React-Native 原语。不过我们这里并不讨论跨平台开发（演讲里有更多细节）。

作为 web 开发人员，你只需要理解 React-Native-Web 是一个常规的 CSS-in-JS 库，它自带一些原始的 React 组件。所有你写 `View` 组件的地方，都可以用 div 替换。

React-Native-Web 的作者是 Nicolas Gallagher，他致力于开发 Twitter 移动版。他们逐渐把它部署到移动设备上，不太确定具体时间，大概在 2017/2018 年左右。

从那以后，很多公司都在用它(美国职业足球大联盟、Flipkart、Uber、纽约时报……)，但最重要的一次部署，则是由 Paul Armstrong 领导的团队在 2019 年推出的新的 Twitter 桌面应用。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9f76238711cd46f7bbc27e27cb6e65b5~tplv-k3u1fbpfcp-watermark.image)

### Stylex

Stylex 是一个新的 CSS-in-JS 库，Facebook 团队为了 2020 年的 Facebook 应用重构而开发它。未来可能会开源，有可能用另一个名字。

值得一提的是，React-Native-Web 的作者 Nicolas Gallagher 被 Facebook 招安。所以里面出现一些熟悉的概念一点也不奇怪。

我的所有信息都来自演讲 :)，还需要等待更多的细节。

## 可扩展性

不出所料，在 Atomic CSS 的加成下，Twitter 和 Facebook 的 CSS**体积都大幅减少**了，现在它的**增长遵循的是对数曲线**。不过，简单的应用则会多了一些 **初始体积**。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/35b528d6aa254a82a67b1ed7c57788ef~tplv-k3u1fbpfcp-watermark.image)

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b6ef346634f44d218c6900f99353299d~tplv-k3u1fbpfcp-watermark.image)

Facebook 分享了具体数字:

- 旧的网站**仅仅首页**就用了 `413Kb` 的 CSS
- 新的网站**整个站点**只用了 `74Kb`，包括暗黑模式

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a7681df905c74ce2a28f188f8ddb1c20~tplv-k3u1fbpfcp-watermark.image)

## 源码和输出

这两个库的 API 看起来很相似，但也很难说，因为我们对 Stylex 了解不多。

值得强调的是，React-Native-Web 会扩展 CSS 语法糖，比如 `margin: 0`，会被输出为 4 个方向的 margin 原子规则。

以一个组件为例，来看看旧版传统 CSS 和新版原子 CSS 输出的区别。

```html
<Component1 classNames="class1" /> <Component2 classNames="class2" />
```

```css
.class1 {
  background-color: mediumseagreen;
  cursor: default;
  margin-left: 0px;
}
.class2 {
  background-color: thistle;
  cursor: default;
  jusify-content: flex-start;
  margin-left: 0px;
}
```

可以看出这两个样式中 `cursor` 和 `margin-left` 是一模一样的，但它在输出中都会占体积。

再来看看原子 CSS 的输出：

```html
<Component1 classNames="classA classC classD" />
<Component2 classNames="classA classB classD classE" />
```

```css
class a {
  cursor: default;
}
class b {
  background-color: mediumseagreen;
}
class C {
  background-color: thistle;
}
class D {
  margin-left: 0px;
}
class E {
  jusify-content: flex-start;
}
```

可以看出，虽然标签上的**类名变多**了，但是 CSS 的输出体积会**随着功能的增多而减缓增长**，因为出现过一次的 CSS Rule 就不会再重复出现了。

## 生产环境验证

我们看看 Twitter 上的标签是什么样子的:

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1ad731068ec64116b879df2fce8696f8~tplv-k3u1fbpfcp-watermark.image)

现在，让我们来看看新 Facebook:

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0ea33216ade1445ba7d075910333b4b0~tplv-k3u1fbpfcp-watermark.image)

很多人可能会被吓到，但是其实它很好用，而且保持了 [可访问性](https://github.com/necolas/react-native-web/blob/master/packages/docs/src/guides/accessibility.stories.mdx)。

在 Chrome 里检查样式可能有点难，但 devtools 里就看得很清楚了:

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9bfd4e96a8f546909d45b0322c690434~tplv-k3u1fbpfcp-watermark.image)

## CSS 规则顺序

与手写的工具/原子 CSS 不同，JS 库能让样式不依赖于 CSS 规则的插入顺序。

在规则冲突的情况下，生效的不是标签上 class attribute 中的最后一个类，而是样式表中**最后插入**的规则。

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/05aadd15366a4658b166c8e5dca7f57a~tplv-k3u1fbpfcp-watermark.image)

以这张图为例，我们期望的是**书写在后**的 `blue` 类覆盖前面的类，但实际上 CSS 会以**样式表中的顺序**来决定优先级，最后我们看到的是红色的文字。

在实际场景中，这些库避免在同一个元素上写入多个规则冲突的类。它们会确保标签上**书写在最后**的类名生效。其他的**被覆盖**的类名则被规律掉，甚至压根不会出现在 DOM 上。

```js
const styles = pseudoLib.create({
  red: {color: "red"},
  blue: {color: "blue"},
});

// 只会输出 blue 相关的 CSS
<div style={[styles.red, styles.blue]}>
  Always blue!
</div>

// 只会输出 red 相关的 CSS
<div style={[styles.blue, styles.red]}>
  Always red!
</div>
```

> 注意:只有使用最严格的原子 CSS 库才能实现这种可预测的行为。

如果一个类里有多个 CSS 规则，并且只有其中的一个 CSS 规则被覆盖，那么 CSS-in-JS 库没办法进行相关的过滤，这也是原子 CSS 的优势之一。

如果一个类只有一个简单的 CSS 规则，如 `margin: 0`，而覆盖的是 `marginTop: 10`。像 `margin: 0` 这样的简写语法被扩展为 4 个不同的原子类，这个库就能更加轻松的过滤掉不该出现在 DOM 上的类名。

## 仍然喜欢 Tailwind？

只要你熟悉所有的 Tailwind 命名约定，你就可以很高效的完成 UI 编写。一旦你熟悉了这个设定，就很难回到手写每个 CSS 规则的时代了，就像你写 CSS-in-JS 那样。

没什么能阻止你在原子 CSS-in-JS 的框架上建立你自己的抽象 CSS 规则，[Styled-system](https://styled-system.com/) 就能在 CSS-in-JS 库里完成一些类似的事情。它基于一些约定创造出一些原子规则，在 `emotion` 中使用它试试：

```js
import styled from '@emotion/styled';
import { typography, space, color } from 'styled-system';

const Box = styled('div')(typography, space, color);
```

等效于：

```js
<Box
  fontSize={4}
  fontWeight="bold"
  p={3}
  mb={[4, 5]}
  color="white"
  bg="primary"
>
  Hello
</Box>
```

甚至有可能在 JS 里复用一些 Tailwind 的命名约定，如果你喜欢的话。

先看些 Tailwind 的代码：

```html
<div className="absolute inset-0 p-4 bg-blue-500" />
```

我们在谷歌上随便找一个方案，比如我刚刚发现 [react-native-web-tailwindcss](https://www.npmjs.com/package/react-native-web-tailwindcss)：

```js
import { t } from 'react-native-tailwindcss';

<View style={[t.absolute, t.inset0, t.p4, t.bgBlue500]} />;
```

就生产力的角度而言，并没有太大的不同。甚至可以用 TS 来避免错别字。

## 结论

这就是我要说的关于原子 CSS-in-JS 所有内容。

我从来没有在任何大型生产部署中使用过原子 CSS、原子 CSS-in-JS 或 Tailwind。我可能在某些方面是错的，请随时纠正我。

我觉得在 React 生态系统中，原子 CSS-in-JS 是一个非常值得关注的趋势，我希望你能从这篇文章中学到一些有用的东西。

感谢阅读。


---

> “比较特殊的样式需求也不是什么问题，因为我们使用的是最简单的类选择器。” 这里翻译的不对，原文指的是 CSS Specificity。以及作为译文为什么没有贴原文链接？https://sebastienlorber.com/atomic-css-in-js

还未完成。。。 这里是草稿

---

> “比较特殊的样式需求也不是什么问题，因为我们使用的是最简单的类选择器。” 这里翻译的不对，原文指的是 CSS Specificity。以及作为译文为什么没有贴原文链接？https://sebastienlorber.com/atomic-css-in-js

已经把完成度高一些的版本粘贴过来了，多谢大佬的指正~ 哈哈。