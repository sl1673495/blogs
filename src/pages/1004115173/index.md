---
title: '应用性能前端监控，字节跳动这些年经验都在这了'
date: '2021-09-22'
spoiler: ''
---

## 背景

字节跳动发展至今，线上已经有数量级庞大的 Web 项目，服务着数以亿计的用户。

随着用户数量的不断增长，对于**站点体验衡量**的的需求也日益紧迫，用户会将产品和他们每天使用的体验最好的 Web 站点进行比较。想着手优化，则必须先有相关的监控数据，才能对症下药。

**性能是留住用户的关键。** 大量的研究报告已经表明了性能和商业成绩的关系，糟糕的性能会让您的站点损失用户数、转化率和口碑。**错误监控则能够让开发者第一时间发现并修复问题**，单靠用户遇到问题并反馈是不现实的，当用户遇到白屏或者接口错误时，更多的人可能会重试几次、失去耐心然后直接关掉您的网站。

字节跳动开发团队根据内部数十款产品的体验监控需求，逐渐打磨出了一版性能监控平台。经过不断的锤炼和沉淀，正式在火山引擎上对外发布**应用性能监控** **全链路版**。本文将会重点介绍它到底是一个怎样的监控平台，以及可以帮助企业解决哪些痛点。

## 产品简述

应用性能监控全链路版是字节跳动旗下的企业级技术服务平台，为企业提供针对应用服务的品质、性能以及自定义埋点的 APM 服务。

基于海量数据的聚合分析，平台可帮助客户发现多类异常问题，并及时报警，做分配处理，同时平台提供了丰富的归因能力，包括且不限于异常分析、多维分析、自定义上报、单点日志查询等，结合灵活的报表能力可了解各类指标的趋势变化。更多功能介绍，详见各子监控服务的功能模块说明。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/124823f534d94a7e9f82805b13b50caf~tplv-k3u1fbpfcp-zoom-1.image)

## 产品亮点

该部分仅以整个产品的视角说明了应用性能监控全链路版的亮点，更多技术亮点与优势，我们会在各功能模块中为您详细说明。

**更低的接入成本：** **非侵入式** **SDK**

在接入 SDK 时，只需要初始化几行代码即可接入成功。

```js
npm install @apm-insight-web/rangers-site-sdk
```

```js
// 在项目最开始的地方引入下面的代码

import vemars from '@apm-insight-web/rangers-site-sdk/private'



vemars('config', {

  app_id: {{你的appid}},

  serverDomain: {{私有化部署服务器地址}},

})
```

或者通过一段 JavaScript 脚本，直接通过 CDN 接入：

```js
<!-- 脚本 -->

<!-- 页面 <head> 标签顶部添加以下代码 -->

<script>

(function(i,s,o,g,r,a,m){i["RangerSiteSDKObject"]=r;(i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)}),(i[r].l=1*new Date());(a=s.createElement(o)),(m=s.getElementsByTagName(o)[0]);a.async=1;a.src=g;a.crossOrigin="anonymous";m.parentNode.insertBefore(a,m);i[r].globalPreCollectError=function(){i[r]("precollect","error",arguments)};if(typeof i.addEventListener==="function"){i.addEventListener("error",i[r].globalPreCollectError,true);i.addEventListener('unhandledrejection', i[r].globalPreCollectError)}if('PerformanceLongTaskTiming'in i){var g=i[r].lt={e:[]};g.o=new PerformanceObserver(function(l){g.e=g.e.concat(l.getEntries())});g.o.observe({entryTypes:['longtask']})}})(window,document,"script","{{你的CDN地址}}","RangersSiteSDK");

</script>

<script>

window.RangersSiteSDK("config",{

    app_id: {{你的app_id}},

    serverDomain: {{私有化部署服务器地址}},

});

</script>
```

**更丰富的异常现场还原能力**

应用性能监控全链路版不仅帮助您无死角地发现各类异常问题，还提供了丰富的现场还原能力，包括且不限于堆栈回溯、用户交互还原等。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8c4dfb55fb264bad95627cd500d8e809~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/be5e039265c84ea8b03c67836ad06e3d~tplv-k3u1fbpfcp-zoom-1.image)

**更灵活的采样方式，以节省开支**

应用性能监控全链路版为您提供了采样配置，支持按功能模块设置采样、按用户设置采样，以帮助您节省事件量。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/fc9566a7faa149108d1992eacef1edbd~tplv-k3u1fbpfcp-zoom-1.image)

如此完善的性能监控平台，背后一定有一套成熟的方法论。从平台设计之初，我们就做好了详细的技术方案设计和衡量标准设计，接下来我会从更细节的角度来介绍这些设计，以及背后详细的原理。

## 怎样衡量 Web 体验

### **站点体验**

首先，从**站点体验**方面来讲，[Web Vitals](https://web.dev/vitals/) 定义了 LCP、FID、CLS 指标，成为了业界主流的标准。

基于长期以来的体验指标优化积累，最新的核心体验指标主要专注于**加载、交互、视觉稳定**，**加载的速度**决定用户是否可以尽早访问到视觉上的图像，**可交互的速度**则决定用户心理上是否可以尽快感觉页面上的元素可以操作，而**视觉稳定性**则负责衡量页面的视觉抖动对用户造成的负面影响。

综合下来就是下面的 3 个指标：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4c95ceacae0a4354ad86aa20f3a58589~tplv-k3u1fbpfcp-zoom-1.image)

**[Largest Contentful Paint (LCP)](https://web.dev/lcp/)**

最大内容绘制，是用来测量**加载**的性能。这个指标上报视口中可见的最大图像或文本块的渲染的时间点，为了提供良好的用户体验，LCP 分数最好保证在 **2.5 秒**以内。

**[First Input Delay (FID)](https://web.dev/fid/)**

第一次输入延迟，用于测量**可交互性**。FID 衡量的是从用户第一次与页面交互（例如，当他们点击链接，点击按钮，或使用自定义的 JavaScript 驱动的控件）到浏览器实际能够开始响应该交互的时间，为了提供良好的用户体验，站点应该努力使 FID 保持在 **100 毫秒**以内。

**[Cumulative Layout Shift (CLS)](https://web.dev/cls/)**

累计布局位移，用于测量**视觉稳定性**。CLS 是衡量页面的整个生命周期中，发生的每次布局变化中的最大幅度的布局变化得分的指标。为了提供良好的用户体验，站点应该努力使 CLS 分数达到 **0.1** 或更低。

### **错误监控**

再从**错误监控**来讲，当页面达到数以亿计的访问量时，无论发布前单元测试、集成测试以及人工测试过了再多轮，都难以避免的会漏掉某些边缘操作路径的测试，甚至偶尔会出现难以复现的玄学故障。哪怕这些错误只有 0.1% 的出现率，在亿级访问量的站点也会导致用户遭遇百万次故障。

这时候，完善的错误监控体系就派上很大的用场。

我们对 **JavaScript 错误、静态资源错误以及请求错误**都提供了宏观的**错误数、错误率、影响用户数、影响用户比例**等指标，一目了然的关注到当前还存留的错误以及对用户的影响，以协助开发人员尽快修复问题。

同时对于请求的监控，为了进一步保证用户在获取数据上的体验，我们还进一步的细化到了**请求的成功率、慢查询相关**的指标。

## SDK 采集

有了这些衡量标准，我们来具体看看 SDK 是怎样具体落地这些标准的。

### 需要采集什么指标？

- **RUM** **(Real User Monitoring) 指标**，包括 FP, TTI, FCP, FMP, FID, MPFID。
- **Navigation Timing**，各阶段指标，包括 DNS, TCP, DOM 解析等阶段的指标。
- **JS Error**，解析后可以细分为运行时异常、以及静态资源异常。
- **请求状态码**，采集上报后，可以分析请求异常等信息。

### 如何采集这些指标？

**RUM 指标的采集**，主要依赖于 [Event Timing API](https://wicg.github.io/event-timing) 进行测量。

以 FID 指标为例，先创建 [PerformanceObserver](https://developer.mozilla.org/zh-CN/docs/Web/API/PerformanceObserver/PerformanceObserver) 对象，监听 `first-input` 事件，监听到 `first-input` 事件后，利用 Event Timing API，通过事件的开始处理时间，减去事件的发生时间，即为 FID。

```js
// Create the Performance Observer instance.

const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    const FID = entry.processingStart - entry.startTime;

    console.log("FID:", FID);
  }
});

// Start observing first-input entries.

observer.observe({
  type: "first-input",

  buffered: true,
});
```

**Navigation Timing** 指标，可以通过 `PerformanceTiming` 接口得到它们，以加载时间的计算为例：

```js
function onLoad() {
  var now = new Date().getTime();

  var page_load_time = now - performance.timing.navigationStart;

  console.log("User-perceived page loading time: " + page_load_time);
}
```

**JS Error** 指标，通过 `window.onerror` **回调函数即可监听**JavaScript 运行时错误\*\*：

```js
window.onerror = function (message, source, lineno, colno, error) {
  // 构造异常数据格式并上报
};
```

通过 `unhandledrejection` 事件监听 **Promise rejections 异步错误**：

```js
window.addEventListener("unhandledrejection", (event) => {
  // 构造异常数据格式并上报
});
```

**请求状态码**，则可以通过覆写 `window.fetch` 和 `XMLHttpRequest` 对象来实现监听，以覆写 `fetch` 为例，以下是简化后的代码：

```js
const _fetch = window.fetch;

window.fetch = (req: RequestInfo, options: RequestInit = {}) => {
  // 省略一些逻辑……

  return _fetch(req, options).then(
    // 成功

    (res) => {
      // 上报成功请求信息

      return res;
    },

    // 失败

    (res) => {
      // 上报失败请求信息

      return Promise.reject(res);
    }
  );
};
```

## 服务端处理

SDK 数据采集完毕后，会交由服务端端进行**收集、清洗以及存储**等处理。

服务端接收数据后，对数据进行实时纬度解析补充，堆栈反解析等清洗任务。 根据不同平台产品功能，分门别类落地在不同类型的存储中：

无法复制加载中的内容

- 数据收集层： 数据收集层是无状态的 API 服务，逻辑较轻。只提供针对 SDK 上报数据的鉴权校验， 拆包等工作， 然后写入消息队列 Kafka 供数据清洗层消费

- 数据清洗层：数据清洗层是数据处理的逻辑中心。 提供堆栈格式化，堆栈还原（SourceMap 解析）， 纬度补充（IP -> 地理位置， User-Agent -> 设备信息）等处理工作。 为平台的多维分析统计，数据下钻等提供数据支撑。

- 存储层：平台根据不同的功能需求， 选择不同类型的存储方案， 实现实时秒级响应的平台查询。

  - OLAP: 我们选择 Clickhouse 作为我们数据分析的存储方案。 Clickhouse 强大的性能和字节内部针对性的优化， 可以帮助我们实现每日千亿级别数据， 秒级查询的效果。
  - KV：字节内部自研高性能 KV 存储数据索引信息， 结合 HDFS 存储详情。实现平台单点查询等详情追查功能。
  - ES：对于一些自定义日志分析搜索场景，我们使用 Elastic Search 作为存储，实现比较灵活的日志搜索分析功能。

在报警功能上，我们通过实现抽象的报警查询引擎（底层可适配不同数据源），对数据实时进行报警分析。我们支持灵活的报警规则配置，并接入各类第三方通知平台作为消息通知的媒介。

在 SDK 的配置层面，我们通过 SDK Setting 服务，实现平台化的采样率配置功能，实时管理控制上报数据。

## 可视化平台展示

经过了上文所述的采集上报 —— 存储清洗 —— 统计分析等工作后，接下来就需要把这些数据交由用户来消费，**可视化平台**的功能也是至关重要的，接下来我将为您详细介绍平台中的各个功能。

### 性能分析

性能分析模块，分为页面加载和静态资源性能两个子模块。

**页面加载**监控是对用户会话过程中前端页面的性能监控。其中可查看的指标分类包括：真实用户性能指标和页面技术性能指标。通过页面加载监控，您可以对用户可感知到的耗时、页面性能有全面的了解。

**真实用户性能指标**也就是上文有所提及的 RUM 以及平台自己扩展的一些额外的指标，包括以下指标：

- **首次绘制时间（** **FP** **）** ：即 First Paint，为首次渲染的时间点。

<!---->

- **首次内容绘制时间（** **FCP** **）** ：即 First Contentful Paint，为首次有内容渲染的时间点。

<!---->

- **首次有效绘制时间（** **FMP** **）** ：用户启动页面加载与页面呈现首屏之间的时间。

<!---->

- **首次交互时间（** **FID** **）** ：即 First Input Delay，记录页面加载阶段，用户首次交互操作的延时时间。FID 指标影响用户对页面交互性和响应性的第一印象。

<!---->

- **交互中最大延时（** **MPFID** **）** ：页面加载阶段，用户交互操作可能遇到的最大延时时间。

<!---->

- **完全可交互时间（TTI**）：即 Time to interactive，记录从页面加载开始，到页面处于完全可交互状态所花费的时间。

<!---->

- **首次加载** **跳出率**：第一个页面完全加载前用户跳出率。

<!---->

- **慢开比**：完全加载耗时超过 5s 的 PV 占比。

在页面中，您可以完整清晰的查看这些指标的状况：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bf2cc1d103d248a8ad146b873b1a2399~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/79f95919653047009f76f99acca91153~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e798f0c5886a4ddb8fbc2fef633cbb2f~tplv-k3u1fbpfcp-zoom-1.image)

**页面技术性能指标**

页面技术性能指标中提供的指标定义来自：[Navigation Timing](https://www.w3.org/TR/navigation-timing-2/) 的说明。

无法复制加载中的内容

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8825232d86fc404b85634b7a40303720~tplv-k3u1fbpfcp-zoom-1.image)

**慢加载列表**列出了加载比较缓慢的页面，方便您进行针对性优化：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5a722004fc5b45c8ae6e37c48a753741~tplv-k3u1fbpfcp-zoom-1.image)

在慢加载列表中，给出了具体的 URL 列表。点击 URL，可进入**详情页**具体分析该 URL 的耗时。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f6ee16219f8a48a59e12fb805f849795~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/55aa7f1e421947a088d28ea4078576df~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c3a4b03655804c34a904c34033a31514~tplv-k3u1fbpfcp-zoom-1.image)

在**多维分析**功能中，您可以对会话性能所有的指标查询维度分布和占比情况。通过维度分析，可以发现和定位某项异常。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/14fa1d7e99c84563a31ed069ee0eb3b9~tplv-k3u1fbpfcp-zoom-1.image)

**静态资源性能**的监控，也提供了类似于上述图表的功能，且支持通过**瀑布图和耗时分布图**来进行其他视角的浏览。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5833f0697d0f4979a5569e1afbb1c79c~tplv-k3u1fbpfcp-zoom-1.image)

### 异常监控

异常监控主要分为 JS 错误监控、请求错误监控以及静态资源错误监控，这些错误监控模块的宏观消费维度都以**错误数、错误率、影响用户数、影响用户比例**为主。

在 **JS 错误监控**中，我们提供了 JavaScript 错误监控与分析能力，同时支持上报自定义错误。整体上分为大盘指标概览以及 issue 详情分析。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a6fd92560b3344f2af068042a751495d~tplv-k3u1fbpfcp-zoom-1.image)

对 issue 进行状态的管理和处理人分配：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/746f3cbaaef84752994c0ec7d4e9171b~tplv-k3u1fbpfcp-zoom-1.image)

您还可以查询该条 issue 中每一条错误事件中，用户的设备信息、版本信息等。点击 UUID/会话 ID，可跳转至单点追查，查询该用户或单次 session 的详细日志。同时还有：

- 错误堆栈：发生错误的混淆堆栈，如果上传了 SourceMap，则可以查看原始堆栈。

<!---->

- 面包屑：用户在发生该错误前后的操作行为记录，除了系统自动收集的请求类型，还支持自定义埋点的交互事件类型。

<!---->

- 自定义维度：除了系统自动采集的维度外，支持上报自定义维度。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f1c12337e3c84f29a2809c06ee6d3d42~tplv-k3u1fbpfcp-zoom-1.image)

**静态资源错误**和**请求错误**的模块都和 JS 错误模块类似，提供概览、Issue 管理以及详情分析等功能。

### 单点追查

单点追查的作用是可以针对特定的用户去查询在使用产品过程中的问题。目前支持了查询单个用户的日志，即**日志查询**。

通过输入 UUID（即用户 ID）或 Session_ID（即会话 ID）可查询单个用户一段时间内的前端日志，通过还原用户的操作路径，更好的定位事件发生的根因。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/47c021f23e6c455e99dc648fd59fac48~tplv-k3u1fbpfcp-zoom-1.image)

### 报警

对于监控平台来说，完善的报警系统也是必不可缺的。针对各类数据、异常创建业务相关的报警机制，有助于尽早的发现和解决问题。

**报警任务**中，支持创建报警策略以及对已创建好的策略进行管理。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a6bb97d2f6054e769944a75667aff417~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3b6a063b27bb4c11aa91427293e84a88~tplv-k3u1fbpfcp-zoom-1.image)

可以很方便的对接飞书中的报警通知机器人，在接收到报警之后第一时间反馈到飞书群里：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e2bfb6f49ebf48f9bfb876cf7e8d806b~tplv-k3u1fbpfcp-zoom-1.image)

当然，在平台中您也可以查看报警的概况、历史列表。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/80c4a8bc4aa04330903f9510aa1aff64~tplv-k3u1fbpfcp-zoom-1.image)

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a763a811c6a64ed1a09980762c00a591~tplv-k3u1fbpfcp-zoom-1.image)

# 总结

**应用性能监控全链路版**，是终端技术团队基于字节跳动内部抖音、今日头条、Tik Tok、飞书等多个超大规模用户量级移动 App 的多年沉淀和积累后的完全自研的应用性能监控产品。并拥有多个外部客户的实践，如：虎扑、作业帮、甄云科技等，为企业和开发者提供**一站式APM**服务。

目前**应用性能监控全链路版**面向新用户提供**试用30天**的限时免费服务。其中包含 App 监控、Web 监控、Server 监控、小程序监控，App 监控和 Web 监控**各 500万条事件量**，Server 与小程序监控**限时不限量**。

**更多产品信息，欢迎点击[这里](https://github.com/sl1673495/bytedance-apm-group/blob/main/APM.md)联系我进群交流**

产品体验地址：https://www.volcengine.com/products/apmplus

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![](https://oscimg.oschina.net/oscnet/up-fa75de6c6ac2dbce9cb2e85b58753d4568b.png)

