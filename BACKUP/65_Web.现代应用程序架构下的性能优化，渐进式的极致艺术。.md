# [Web 现代应用程序架构下的性能优化，渐进式的极致艺术。](https://github.com/sl1673495/blogs/issues/65)

## 前言

本文是 [Rendering on the Web: Performance Implications of Application Architecture (Google I/O ’19)](https://www.youtube.com/watch?v=k-A2VfuUROg&feature=youtu.be&t=1036) 这篇谷歌工程师带来的现代应用架构体系下的优化相关演讲的总结，演讲介绍了以下优化手段：

- 预渲染
- 同构渲染
- 流式渲染
- **渐进式注水**（非常精彩）

## 应用架构体系

当我们讨论「应用架构」的时候，可以理解为通过以下几个部分组合来构建网站。

1. `Component model` 组件模型。
2. `Rendering and loading` 渲染和加载。
3. `Routing and transitions` 路由和过渡。
4. `Data/state management` 数据、状态的管理。

![image](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6fd50dc605224818b1f936e6261279ca~tplv-k3u1fbpfcp-zoom-1.image)

## 性能指标

在分析页面渲染性能之前，先了解一下几个比较重要的指标，方便下文理解：

1. `FP`: First Paint，是 Paint Timing API 的一部分，是页面导航与浏览器将该网页的第一个像素渲染到屏幕上所用的中间时，渲染是任何与输入网页导航前的屏幕上的内容不同的内容。

2. `FCP`: First Contentful Paint，首次有内容的渲染是当浏览器渲染 DOM 第一块内容，第一次回馈用户页面正在载入。

3. `TTI`: Time to interactive 第一次可交互时间，此时用户可以真正的触发 DOM 元素的事件，和页面进行交互。

4. `FID`: First Input Delay 第一输入延迟测量用户首次与您的站点交互时的时间（即，当他们单击链接，点击按钮或使用自定义的 JavaScript 驱动控件时）到浏览器实际能够的时间回应这种互动。

5. `TTFB`: Time to First Byte 首字节时间，顾名思义，是指从客户端开始和服务端交互到服务端开始向客户端浏览器传输数据的时间（包括 DNS、socket 连接和请求响应时间），是能够反映服务端响应速度的重要指标。

如果你还不太熟悉这些指标也没关系，接下来的内容中，会结合实际用例分析这些指标。

## 渲染开销 The cost of rendering

### 客户端渲染 Client-side rendering

从服务端获取 HTML、CSS、JavaScript 都是需要成本的，以一个 CSR（客户端渲染）的网站为例，客户端渲染的网站依赖框架库(bundle)、应用程序（app)来进行初始化渲染，假设它有 1MB 的 JavaScript Bundle 代码，那么只有当这一大段的代码加载并执行完成以后，用户才能看到页面。

它的结构一般如下：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8bd1b0712c454e97b6eb2ba3c5f2b658~tplv-k3u1fbpfcp-watermark.image)

分析一下它的流程：

1. 用户输入网址进入网站，拉取 HTML 资源。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1c90c0d570364c91a0fe99aded1c4370~tplv-k3u1fbpfcp-watermark.image)

2. HTML 资源中发现 script 标签加载的 bundle 再一次发起请求拉取 bundle。此时也是性能统计指标中的 `FP` 完成。

在这个阶段，页面基本上是没什么意义的，当然你也可以放置一些静态的骨架屏或者加载提示，来友好的提示用户。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/464e3f1d4ba9468eb78953039c9fe640~tplv-k3u1fbpfcp-watermark.image)

3. JavaScript bundle 下载并执行完毕，此时页面才真正渲染出有意义的内容。对应 `FCP` 完成。

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/fec883ea600a4f7a9469a974f48a0ef6~tplv-k3u1fbpfcp-watermark.image)

当框架对 DOM 节点添加各类事件绑定后，用户才真正可以和页面交互，此时也对应 `TTI` 完成。

它的**缺点**在于，直到整个 JavaScript 依赖执行完成之前，用户都看不到什么有意义的内容。

### 服务端同构渲染 SSR with Hydration

基于以上客户端渲染的缺点以及用户对于 CSR 应用交互更加丰富的需求，于是诞生了集 SSR 和 CSR 的**性能、SEO、数据获取**的优点与一身的「**同构渲染**」，简单点说，就是：

1. 第一次请求，在服务端就利用框架提供的服务端渲染能力，直接原地请求数据，生成包含完整内容的 html 页面，用户不需要等待框架的 js 加载就可以看到内容。

2. 等到页面渲染后，再利用框架提供的 Hydration（注水）能力，让服务端返回的“干瘪”的 HTML 注册事件等等，变的丰富起来，拥有了各种事件后，就和传统 CSR 一样拥有了丰富多彩的客户端交互。

在同构应用中，只要 HTML 页面返回，用户就可以看到丰富多彩的页面：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/25347cfa3f164b928d4e4524adb26658~tplv-k3u1fbpfcp-watermark.image)

而 JavaScript 加载完毕后，用户就可以和这些内容进行交互（比如点击放大、跳转页面等等……）

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8699cbf1c2e94a53ae676b0df7988676~tplv-k3u1fbpfcp-watermark.image)

### 代码对比

典型的 CSR React 应用的代码是这样的：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0714c447f4844eb580ba28db8f4b2ed0~tplv-k3u1fbpfcp-watermark.image)

而 SSR 的代码则需要服务端的配合，

先由服务端通过 `ReactDOMServer.renderToString` 在服务端把组件给序列化成 html 字符串，返回给前端：
![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2f2fe7ed202c4539905258f9c0774e3b~tplv-k3u1fbpfcp-watermark.image)

前端通过 `hydrate` 注水，使得功能交互变的完整：
![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2c9eb5a496b1460ea5aa6d915b85146e~tplv-k3u1fbpfcp-watermark.image)

Vue 的 SSR 也是同理：

### 同构的缺陷

至此看来，难道同构应用就是完美的吗？当然不是，其实普通的同构应用只是提升了 FCP 也就是用户看到内容的速度，但是却还是要等到框架代码下载完成，`hydrate` 注水完毕等一系列过程执行完毕以后才能真正的**可交互**。

并且对于 `FID` 也就是 First Input Delay 第一输入延迟这个指标来说，由于 SSR 快速渲染出内容，更容易让用户误以为页面已经是可交互状态，反而会使「用户第一次点击 - 浏览器响应事件」 这个时间变得更久。

因此，同构应用很可能变成一把「双刃剑」。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/abbda5930e2d4b68a815f006ce2dde5c~tplv-k3u1fbpfcp-watermark.image)

下面我们来讨论一些方案。

## Pre-rendering 预渲染。

对于不经常发生变化的内容来说，使用预渲染是一种很好的办法，它在代码构建时就通过框架能力生成好静态的 HTML 页面，而不是像同构应用那样在用户请求页面时再生成，这让它可以几乎立刻返回页面。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/07afefd7e6fd49c1a5aaa6d303a9cc4b~tplv-k3u1fbpfcp-watermark.image)

当然它也有很大的限制：

1. 只适用于静态页面。
2. 需要提前列举出需要预渲染的 URLs。

## 流式渲染 Streaming

流式渲染可以让服务端对大块的内容分片发送，使得客户端不需要完整的接收到 HTML，而是接受到第一部分时就开始渲染，这大大提升了 `TTFB` 首字节时间。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0b06fd15df3a4c1ea6522f332b4fab51~tplv-k3u1fbpfcp-watermark.image)

在 React 中，可以通过 `renderToNodeStream` 来使用流式渲染：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/401dd28293ec4cdf98eb5640dfe545e5~tplv-k3u1fbpfcp-watermark.image)

## 渐进式注水 Progressive Hydration

我们知道 `hydrate` 的过程需要遍历整颗 React 节点树来添加事件，这在页面很大的情况下耗费的时间一定是很长的，我们能否先只对关键的部分，比如视图中可见的部分，进行「注水」，让这部分先一步可以进行交互？

想象一下它的特点：

1. 组件级别的渐进式注水。
2. 服务端依旧整页渲染。
3. 页面可以根据优先级来分片“启动”组件。

通过一张动图来直观的感受一下普通注水（左）和渐进式注水（右）的区别：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/28225f2172f0411ab5974eea6c52623e~tplv-k3u1fbpfcp-watermark.image)

可以看到用户第一次可以交互的时间大大的提前了。

光说不做假把式，我们看看用 React 完成这个功能的代码，首先我们需要准备一个组件 `Hydrator` 用来实现当某个组件**进入视图范围以后**再进行注水。

首先来看看应用的整体结构：

```jsx
let load = () => import('./stream');
let Hydrator = ClientHydrator;

if (typeof window === 'undefined') {
  Hydrator = ServerHydrator;
  load = () => require('./stream');
}

export default function App() {
  return (
    <div id="app">
      <Header />
      <Intro />
      <Hydrator load={load} />
    </div>
  );
}
```

根据客户端和服务端的环境区分使用不同的 `Hydrator`，在服务端就直接返回普通的 html 文本：

```jsx
function interopDefault(mod) {
  return (mod && mod.default) || mod;
}

export function ServerHydrator({ load, ...props }) {
  const Child = interopDefault(load());
  return (
    <section>
      <Child {...props} />
    </section>
  );
}
```

而客户端，则需要实现渐进式注水的关键部分：

```jsx
export class Hydrator extends React.Component {
  render() {
    return (
      <section
        ref={c => (this.root = c)}
        dangerouslySetInnerHTML={{ __html: '' }}
        suppressHydrationWarning
      />
    );
  }
}
```

首先 render 部分，利用 `dangerouslySetInnerHTML` 来使得这部分初始化为空的 html 文本，并且由于 server 端肯定还是和往常一样全量渲染内容，而客户端由于初始化需要先不做任何处理，会导致 React 内部对于服务端内容和客户端内容的「一致性检测」失败。

而利用 `dangerouslySetInnerHTML` 的特性，会让 React 不再进一步 `hydrate` 遍历 `children` 而是直接沿用服务端渲染返回的 HTML，保证在注水前渲染的样式也是 OK 的。

再利用 `suppressHydrationWarning` 取消 React 对于内容一致性检测失败的警告。

```jsx
export class Hydrator extends React.Component {
  componentDidMount() {
    new IntersectionObserver(async ([entry], obs) => {
      if (!entry.isIntersecting) return;
      obs.unobserve(this.root);

      const { load, ...props } = this.props;
      const Child = interopDefault(await load());
      ReactDOM.hydrate(<Child {...props} />, this.root);
    }).observe(this.root);
  }

  render() {
    return (
      <section
        ref={c => (this.root = c)}
        dangerouslySetInnerHTML={{ __html: '' }}
        suppressHydrationWarning
      />
    );
  }
}
```

接下来，组件在客户端初始化的时候，利用 `IntersectionObserver` 监控组件元素是否进入视图，一旦进入视图了，才会动态的去 `import` 组件，并且利用 `ReactDOM.hydrate` 来真正的进行注水。

此时不光注水是动态化的，包括组件代码的下载都会在组件进入视图时才发生，真正做到了「按需加载」。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7874c6f5d7284fd990ad0cd596e91a22~tplv-k3u1fbpfcp-watermark.image)

动图中紫色动画出现，就说明渐进式 `hydrate` 完成了。

对比一下全量注水和渐进式注水的性能会发现首次可交互的时间被大大提前了：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8e9a5e5a9b274d5fb4703cec07b66bac~tplv-k3u1fbpfcp-watermark.image)

当然，我们了解原理就发现，不光可以通过监听组件进入视图来 `hydrate`，甚至可以通过 `hover`、`click` 等时机来触发，根据业务需求的不同而灵活调整吧。

可以访问图片中的网址获取你喜欢的框架在这方面的相关文章：

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4f9b465601214edcb485a7d393ba572f~tplv-k3u1fbpfcp-watermark.image)

## 总结

本文通过总结了 [Rendering on the Web: Performance Implications of Application Architecture (Google I/O ’19)](https://www.youtube.com/watch?v=k-A2VfuUROg&feature=youtu.be&t=1036) 这段 Google 团队的精彩演讲，来介绍了现代应用架构体系中的优化手段，包括：

- 预渲染
- 同构渲染
- 流式渲染
- 渐进式注水

在不同的业务场景下选择对应的优化手段，是一名优秀的前端工程师必备的技能，相信看完这篇文章的你一定有所收获。

本文 demo 地址：https://github.com/GoogleChromeLabs/progressive-rendering-frameworks-samples
