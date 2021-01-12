---
title: '深入解析你不知道的 EventLoop 和浏览器渲染、帧动画、空闲回调'
date: '2020-05-21'
spoiler: ''
---

## 前言

关于 Event Loop 的文章很多，但是有很多只是在讲「宏任务」、「微任务」，我先提出几个问题：

1. 每一轮 Event Loop 都会伴随着渲染吗？
2. `requestAnimationFrame` 在哪个阶段执行，在渲染前还是后？在 `microTask` 的前还是后？
3. `requestIdleCallback` 在哪个阶段执行？如何去执行？在渲染前还是后？在 `microTask` 的前还是后？
4. `resize`、`scroll` 这些事件是何时去派发的。

这些问题并不是刻意想刁难你，如果你不知道这些，那你可能并不能在遇到一个动画需求的时候合理的选择 `requestAnimationFrame`，你可能在做一些需求的时候想到了 `requestIdleCallback`，但是你不知道它运行的时机，只是胆战心惊的去用它，祈祷不要出线上 bug。

这也是本文想要从规范解读入手，深挖底层的动机之一。本文会酌情从规范中排除掉一些比较晦涩难懂，或者和主流程不太相关的概念。更详细的版本也可以直接去读这个规范，不过比较费时费力。

## 事件循环

我们先依据[HTML 官方规范](https://html.spec.whatwg.org/multipage/webappapis.html#task-queue)从浏览器的事件循环讲起，因为剩下的 API 都在这个循环中进行，它是浏览器调度任务的基础。

### 定义

为了协调事件，用户交互，脚本，渲染，网络任务等，浏览器必须使用本节中描述的事件循环。

### 流程

1. 从任务队列中取出一个**宏任务**并执行。

2. 检查微任务队列，执行并清空**微任务**队列，如果在微任务的执行中又加入了新的微任务，也会在这一步一起执行。

3. 进入更新渲染阶段，判断是否需要渲染，这里有一个 `rendering opportunity` 的概念，也就是说不一定每一轮 event loop 都会对应一次浏览 器渲染，要根据屏幕刷新率、页面性能、页面是否在后台运行来共同决定，通常来说这个渲染间隔是固定的。（所以多个 task 很可能在一次渲染之间执行）
   - 浏览器会尽可能的保持帧率稳定，例如页面性能无法维持 60fps（每 16.66ms 渲染一次）的话，那么浏览器就会选择 30fps 的更新速率，而不是偶尔丢帧。
   - 如果浏览器上下文不可见，那么页面会降低到 4fps 左右甚至更低。
   - 如果满足以下条件，也会跳过渲染：
     1. 浏览器判断更新渲染不会带来视觉上的改变。
     2. `map of animation frame callbacks` 为空，也就是帧动画回调为空，可以通过 `requestAnimationFrame` 来请求帧动画。
4. 如果上述的判断决定本轮**不需要渲染**，那么**下面的几步也不会继续运行**：

   > This step enables the user agent to prevent the steps below from running for other reasons, for example, to ensure certain tasks are executed immediately after each other, with only microtask checkpoints interleaved (and without, e.g., animation frame callbacks interleaved). Concretely, a user agent might wish to coalesce timer callbacks together, with no intermediate rendering updates.
   > 有时候浏览器希望两次「定时器任务」是合并的，他们之间只会穿插着 `microTask`的执行，而不会穿插屏幕渲染相关的流程（比如`requestAnimationFrame`，下面会写一个例子）。

5. 对于需要渲染的文档，如果窗口的大小发生了变化，执行监听的 `resize` 方法。
6. 对于需要渲染的文档，如果页面发生了滚动，执行 `scroll` 方法。
7. 对于需要渲染的文档，执行帧动画回调，也就是 **`requestAnimationFrame`** 的回调。（后文会详解）
8. 对于需要渲染的文档， 执行 IntersectionObserver 的回调。
9. 对于需要渲染的文档，**重新渲染**绘制用户界面。
10. 判断 `task队列`和`microTask`队列是否都为空，如果是的话，则进行 `Idle` 空闲周期的算法，判断是否要执行 **`requestIdleCallback`** 的回调函数。（后文会详解）

对于`resize` 和 `scroll`来说，并不是到了这一步才去执行滚动和缩放，那岂不是要延迟很多？浏览器当然会立刻帮你滚动视图，根据[CSSOM 规范](https://drafts.csswg.org/cssom-view/#scrolling-events)所讲，浏览器会保存一个 `pending scroll event targets`，等到事件循环中的 `scroll`这一步，去派发一个事件到对应的目标上，驱动它去执行监听的回调函数而已。`resize`也是同理。

可以在这个流程中仔细看一下「宏任务」、「微任务」、「渲染」之间的关系。

### 多任务队列

`task` 队列并不是我们想象中的那样只有一个，根据规范里的描述：

> An event loop has one or more task queues. For example, a user agent could have one task queue for mouse and key events (to which the user interaction task source is associated), and another to which all other task sources are associated. Then, using the freedom granted in the initial step of the event loop processing model, it could give keyboard and mouse events preference over other tasks three-quarters of the time, keeping the interface responsive but not starving other task queues. Note that in this setup, the processing model still enforces that the user agent would never process events from any one task source out of order.

事件循环中可能会有**一个或多个**任务队列，这些队列分别为了处理：

1. 鼠标和键盘事件
2. 其他的一些 Task

浏览器会在保持任务顺序的前提下，可能分配四分之三的优先权给鼠标和键盘事件，保证用户的输入得到最高优先级的响应，而剩下的优先级交给其他 `Task`，并且保证不会“饿死”它们。

这个规范也导致 Vue 2.0.0-rc.7 这个版本 `nextTick` 采用了从微任务 `MutationObserver` 更换成宏任务 `postMessage` 而导致了一个 [Issue](https://github.com/vuejs/vue/issues/3771#issuecomment-249692588)。

目前由于一些“未知”的原因，jsfiddle 的案例打不开了。简单描述一下就是采用了 `task` 实现的 `nextTick`，在用户持续滚动的情况下 `nextTick` 任务被延后了很久才去执行，导致动画跟不上滚动了。

迫于无奈，尤大还是改回了 `microTask` 去实现 `nextTick`，当然目前来说 `promise.then` 微任务已经比较稳定了，并且 Chrome 也已经实现了 `queueMicroTask` 这个官方 API。不久的未来，我们想要调用微任务队列的话，也可以节省掉实例化 `Promise` 在开销了。

从这个 Issue 的例子中我们可以看出，稍微去深入了解一下规范还是比较有好处的，以免在遇到这种比较复杂的 Bug 的时候一脸懵逼。

下面的章节中咱们来详细聊聊 `requestIdleCallback` 和 `requestAnimationFrame`。

## requestAnimationFrame

> 以下内容中 `requestAnimationFrame`简称为`rAF`

在解读规范的过程中，我们发现 `requestAnimationFrame` 的回调有两个特征：

1. 在重新渲染前调用。
2. 很可能在宏任务之后不调用。

我们来分析一下，为什么要在重新渲染前去调用？因为 `rAF` 是官方推荐的用来做一些流畅动画所应该使用的 API，做动画不可避免的会去更改 DOM，而如果在渲染之后再去更改 DOM，那就只能等到下一轮渲染机会的时候才能去绘制出来了，这显然是不合理的。

`rAF`在浏览器决定渲染之前给你最后一个机会去改变 DOM 属性，然后很快在接下来的绘制中帮你呈现出来，所以这是做流畅动画的不二选择。下面我用一个 `setTimeout`的例子来对比。

### 闪烁动画

假设我们现在想要快速的让屏幕上闪烁 `红`、`蓝`两种颜色，保证用户可以观察到，如果我们用 `setTimeout` 来写，并且带着我们长期的误解「宏任务之间一定会伴随着浏览器绘制」，那么你会得到一个预料之外的结果。

```js
setTimeout(() => {
  document.body.style.background = "red"
  setTimeout(() => {
    document.body.style.background = "blue"
  })
})
```

![](https://user-gold-cdn.xitu.io/2020/5/21/172368a480f5f3ef?w=1028&h=902&f=gif&s=269568)

可以看出这个结果是非常不可控的，如果这两个 `Task` 之间正好遇到了浏览器认定的渲染机会，那么它会重绘，否则就不会。由于这俩宏任务的间隔周期太短了，所以很大概率是不会的。

如果你把延时调整到 `17ms` 那么重绘的概率会大很多，毕竟这个是一般情况下 `60fps` 的一个指标。但是也会出现很多不绘制的情况，所以并不稳定。

如果你依赖这个 API 来做动画，那么就很可能会造成「掉帧」。

接下来我们换成 `rAF` 试试？我们用一个递归函数来模拟 10 次颜色变化的动画。

```js
let i = 10
let req = () => {
  i--
  requestAnimationFrame(() => {
    document.body.style.background = "red"
    requestAnimationFrame(() => {
      document.body.style.background = "blue"
      if (i > 0) {
        req()
      }
    })
  })
}

req()
```

这里由于颜色变化太快，`gif` 录制软件没办法截出这么高帧率的颜色变换，所以各位可以放到浏览器中自己执行一下试试，我这边直接抛结论，浏览器会非常规律的把这 10 组也就是 20 次颜色变化绘制出来，可以看下 performance 面板记录的表现：

![](https://user-gold-cdn.xitu.io/2020/5/21/172369395743293b?w=792&h=170&f=png&s=36999)

### 定时器合并

在第一节解读规范的时候，第 4 点中提到了，定时器宏任务可能会直接跳过渲染。

按照一些常规的理解来说，宏任务之间理应穿插渲染，而定时器任务就是一个典型的宏任务，看一下以下的代码：

```js
setTimeout(() => {
  console.log("sto")
  requestAnimationFrame(() => console.log("rAF"))
})
setTimeout(() => {
  console.log("sto")
  requestAnimationFrame(() => console.log("rAF"))
})

queueMicrotask(() => console.log("mic"))
queueMicrotask(() => console.log("mic"))
```

从直觉上来看，顺序是不是应该是：

```
mic
mic
sto
rAF
sto
rAF
```

呢？也就是每一个宏任务之后都紧跟着一次渲染。

实际上不会，浏览器会合并这两个定时器任务：

```
mic
mic
sto
sto
rAF
rAF
```

## requestIdleCallback

### 草案解读

> 以下内容中 `requestIdleCallback`简称为`rIC`。

我们都知道 `requestIdleCallback` 是浏览器提供给我们的空闲调度算法，关于它的简介可以看 [MDN 文档](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/requestIdleCallback)，意图是让我们把一些计算量较大但是又没那么紧急的任务放到空闲时间去执行。不要去影响浏览器中优先级较高的任务，比如动画绘制、用户输入等等。

React 的时间分片渲染就想要用到这个 API，不过目前浏览器支持的不给力，他们是自己去用 `postMessage` 实现了一套。

#### 渲染有序进行

首先看一张图，很精确的描述了这个 API 的意图：

![](https://user-gold-cdn.xitu.io/2020/5/21/172362067212340f?w=737&h=139&f=png&s=19313)

当然，这种有序的 `浏览器 -> 用户 -> 浏览器 -> 用户` 的调度基于一个前提，就是我们要把任务切分成比较小的片，不能说浏览器把空闲时间让给你了，你去执行一个耗时 `10s` 的任务，那肯定也会把浏览器给阻塞住的。这就要求我们去读取 `rIC` 提供给你的 `deadline` 里的时间，去动态的安排我们切分的小任务。浏览器信任了你，你也不能辜负它呀。

#### 渲染长期空闲

![](https://user-gold-cdn.xitu.io/2020/5/21/17236209c86c248f?w=670&h=173&f=png&s=19531)
还有一种情况，也有可能在几帧的时间内浏览器都是空闲的，并没有发生任何影响视图的操作，它也就不需要去绘制页面：
这种情况下为什么还是会有 `50ms` 的 `deadline` 呢？是因为浏览器为了提前应对一些可能会突发的用户交互操作，比如用户输入文字。如果给的时间太长了，你的任务把主线程卡住了，那么用户的交互就得不到回应了。50ms 可以确保用户在无感知的延迟下得到回应。

MDN 文档中的[幕后任务协作调度 API ](https://developer.mozilla.org/zh-CN/docs/Web/API/Background_Tasks_API) 介绍的比较清楚，来根据里面的概念做个小实验：

屏幕中间有个红色的方块，把 MDN 文档中[requestAnimationFrame](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/requestAnimationFrame)的范例部分的动画代码直接复制过来。

草案中还提到：

1. 当浏览器判断这个页面对用户不可见时，这个回调执行的频率可能被降低到 10 秒执行一次，甚至更低。这点在解读 EventLoop 中也有提及。

2. 如果浏览器的工作比较繁忙的时候，不能保证它会提供空闲时间去执行 `rIC` 的回调，而且可能会长期的推迟下去。所以如果你需要保证你的任务在一定时间内一定要执行掉，那么你可以给 `rIC` 传入第二个参数 `timeout`。  
   这会强制浏览器不管多忙，都在超过这个时间之后去执行 `rIC` 的回调函数。所以要谨慎使用，因为它会打断浏览器本身优先级更高的工作。

3. 最长期限为 50 毫秒，是根据研究得出的，研究表明，人们通常认为 100 毫秒内对用户输入的响应是瞬时的。 将闲置截止期限设置为 50ms 意味着即使在闲置任务开始后立即发生用户输入，浏览器仍然有剩余的 50ms 可以在其中响应用户输入而不会产生用户可察觉的滞后。

4. 每次调用 `timeRemaining()` 函数判断是否有剩余时间的时候，如果浏览器判断此时有优先级更高的任务，那么会动态的把这个值设置为 0，否则就是用预先设置好的 `deadline - now` 去计算。

5. 这个 `timeRemaining()` 的计算非常动态，会根据很多因素去决定，所以不要指望这个时间是稳定的。

### 动画例子

#### 滚动

如果我鼠标不做任何动作和交互，直接在控制台通过 `rIC` 去打印这次空闲任务的剩余时间，一般都稳定维持在 `49.xx` ms，因为此时浏览器没有什么优先级更高的任务要去处理。

![](https://user-gold-cdn.xitu.io/2020/5/21/172367edc582db9c?w=1612&h=978&f=gif&s=460995)

而如果我不停的滚动浏览器，不断的触发浏览器的重新绘制的话，这个时间就变的非常不稳定了。

![](https://user-gold-cdn.xitu.io/2020/5/21/172368088eca1422?w=1612&h=978&f=gif&s=3952633)

通过这个例子，你可以更加有体感的感受到什么样叫做「繁忙」，什么样叫做「空闲」。

#### 动画

这个动画的例子很简单，就是利用`rAF`在每帧渲染前的回调中把方块的位置向右移动 10px。

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <style>
      #SomeElementYouWantToAnimate {
        height: 200px;
        width: 200px;
        background: red;
      }
    </style>
  </head>
  <body>
    <div id="SomeElementYouWantToAnimate"></div>
    <script>
      var start = null
      var element = document.getElementById("SomeElementYouWantToAnimate")
      element.style.position = "absolute"

      function step(timestamp) {
        if (!start) start = timestamp
        var progress = timestamp - start
        element.style.left = Math.min(progress / 10, 200) + "px"
        if (progress < 2000) {
          window.requestAnimationFrame(step)
        }
      }
      // 动画
      window.requestAnimationFrame(step)

      // 空闲调度
      window.requestIdleCallback(() => {
        alert("rIC")
      })
    </script>
  </body>
</html>
```

注意在最后我加了一个 `requestIdleCallback` 的函数，回调里会 `alert('rIC')`，来看一下演示效果：

![](https://user-gold-cdn.xitu.io/2020/5/21/17235e089ed53d75?w=928&h=432&f=gif&s=51770)

`alert` 在最开始的时候就执行了，为什么会这样呢一下，想一下「空闲」的概念，我们每一帧仅仅是把 `left` 的值移动了一下，做了这一个简单的渲染，没有占满空闲时间，所以可能在最开始的时候，浏览器就找到机会去调用 `rIC` 的回调函数了。

我们简单的修改一下 `step` 函数，在里面加一个很重的任务，1000 次循环打印。

```js
function step(timestamp) {
  if (!start) start = timestamp
  var progress = timestamp - start
  element.style.left = Math.min(progress / 10, 200) + "px"
  let i = 1000
  while (i > 0) {
    console.log("i", i)
    i--
  }
  if (progress < 2000) {
    window.requestAnimationFrame(step)
  }
}
```

再来看一下它的表现：

![](https://user-gold-cdn.xitu.io/2020/5/21/17235e0b45c0bd6b?w=928&h=432&f=gif&s=124529)

其实和我们预期的一样，由于浏览器的每一帧都"太忙了",导致它真的就无视我们的 `rIC` 函数了。

如果给 `rIC` 函数加一个 `timeout` 呢：

```js
// 空闲调度
window.requestIdleCallback(
  () => {
    alert("rID")
  },
  { timeout: 500 },
)
```

![](https://user-gold-cdn.xitu.io/2020/5/21/17235e30289293f2?w=928&h=432&f=gif&s=89713)

浏览器会在大概 `500ms` 的时候，不管有多忙，都去强制执行 `rIC` 函数，这个机制可以防止我们的空闲任务被“饿死”。

## 总结

通过本文的学习过程，我自己也打破了很多对于 Event Loop 以及 rAF、rIC 函数的固有错误认知，通过本文我们可以整理出以下的几个关键点。

1. 事件循环**不一定**每轮都伴随着重渲染，但是如果有微任务，一定会伴随着**微任务执行**。
2. 决定浏览器视图是否渲染的因素很多，浏览器是非常聪明的。
3. `requestAnimationFrame`在重新渲染屏幕**之前**执行，非常适合用来做动画。
4. `requestIdleCallback`在渲染屏幕**之后**执行，并且是否有空执行要看浏览器的调度，如果你一定要它在某个时间内执行，请使用 `timeout`参数。
5. `resize`和`scroll`事件其实自带节流，它只在 Event Loop 的渲染阶段去派发事件到 `EventTarget` 上。

另外，本文也是对于规范的解读，规范里的一些术语比较晦涩难懂，所以我也结合了一些自己的理解去写这篇文章，如果有错误的地方欢迎各位小伙伴指出。

## 参考资料

[HTML 规范文档](https://html.spec.whatwg.org/multipage/webappapis.html#task-queue)

[W3C 标准](https://w3c.github.io/requestidlecallback)

[Vue 源码详解之 nextTick：MutationObserver 只是浮云，microtask 才是核心！](https://segmentfault.com/a/1190000008589736)（强烈推荐这篇文章）

## ❤️ 感谢大家

1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)
