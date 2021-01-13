---
title: '前端动画必知必会：React 和 Vue 都在用的 FLIP 思想实战'
date: '2020-06-03'
spoiler: ''
---

## 前言

在 Vue 的官网中的过渡动画章节中，可以看到一个很酷炫的[动画效果](https://cn.vuejs.org/v2/guide/transitions.html#%E5%88%97%E8%A1%A8%E7%9A%84%E6%8E%92%E5%BA%8F%E8%BF%87%E6%B8%A1)

![](https://user-gold-cdn.xitu.io/2020/6/3/1727890a0a2d9845?w=706&h=682&f=gif&s=1928105)

乍一看，让我们手写出这个逻辑应该是非常复杂的，先看看本文最后要实现的效果吧，和这个案例是非常类似的。

## 预览

![](https://user-gold-cdn.xitu.io/2020/6/3/17278961a474678c?w=500&h=679&f=gif&s=4061003)

也可以直接进预览网址里看：

http://sl1673495.gitee.io/flip-animation

图片素材依然引用自知乎问题[《有个漂亮女朋友是种怎样的体验？》](https://www.zhihu.com/question/28997505)，侵删。

## 分析需求

拿到了这个需求，第一直觉是怎么做？假设第一行第一个图片移动到了第二行第三列，是不是要计算出第一行的高度，再计算出第二行前两个元素的宽度，然后从初始的坐标点通过 CSS 或者一些动画 API 移动过去？这样做是可以，但是在图片不定高不定宽，并且一次要移动很多图片情况下，这个计算方法就非常复杂了。并且这种情况下，图片的坐标都需要我们手动管理，非常不利于维护和扩展。

换种思路，能不能直接很自然的把 DOM 元素通过原生 API 添加到 DOM 树中，然后让浏览器帮我们好这个终点值，最后我们再动画位移过去？

在文档里我们发现一个名词：`FLIP`，这给了我们一个线索，是不是用这个玩意就可以写出这个动画呢？

答案是肯定的，顺着这个线索找到 `Aerotwist` 社区里的一篇文章：[flip-your-animations](https://aerotwist.com/blog/flip-your-animations/)，以这篇文章为切入点，一步步来实现一个类似的效果。

## FLIP

`FLIP` 究竟是什么东西呢？先看下它的定义：

### First

即将做动画的元素的初始状态（比如位置、透明度等等）。

### Last

即将做动画的元素的最终状态。

### Invert

这一步比较关键，假设我们图片的初始位置是 `左: 0, 上：0`，元素动画后的最终位置是 `左：100, 上100`，那么很明显这个元素是向右下角运动了 `100px`。

**但是**，此时我们不按照常规思维去先计算它的最终位置，然后再命令元素从 `0, 0` 运动到 `100, 100`，而是**先让元素自己移动过去**（比如在 Vue 中用数据来驱动，在数组前面追加几个图片，之前的图片就自己移动到下面去了）。

这里有一个关键的知识点要注意了，也是我在之前的文章[《深入解析你不知道的 EventLoop 和浏览器渲染、帧动画、空闲回调》](https://juejin.im/post/5ec73026f265da76da29cb25)中提到过的：

DOM 元素属性的改变（比如 `left`、`right`、 `transform` 等等），会被集中起来延迟到浏览器的下一帧统一渲染，所以我们可以得到一个这样的中间时间点：**DOM 状态（位置信息）改变了，而浏览器还没渲染**。

有了这个前置条件，我们就可以保证先让 Vue 去操作 DOM 变更，此时浏览器还未渲染，我们已经能得到 DOM 状态变更后的位置了。

说的具体点，假设我们的图片是一行两个排列，图片数组初始化的状态是 `[img1, img2`，此时我们往数组头部追加两个元素 `[img3, img4, img1, img2]`，那么 `img1` 和 `img2` 就自然而然的被挤到下一行去了。

假设 `img1` 的初始位置是 `0, 0`，被数据驱动导致的 DOM 改变挤下去后的位置是 `100, 100`，那么此时浏览器还没有渲染，我们可以在这个时间点把 `img1.style.transform = translate(-100px, -100px)`，让它 先 **Invert** 倒置回位移前的位置。

### Play

倒置了以后，想要让它做动画就很简单了，再让它回到 `0, 0` 的位置即可，本文会采用最新的 `Web Animation API` 来实现最后的 `Play`。

[MDN 文档：Web Animation](https://developer.mozilla.org/zh-CN/docs/Web/API/Animation)

## 实现

首先图片渲染很简单，就让图片通过简单的排成 4 列即可：

```xml
.wrap {
  display: flex;
  flex-wrap: wrap;
}

.img {
  width: 25%;
}

<div v-else class="wrap">
  <div class="img-wrap" v-for="src in imgs" :key="src">
    <img ref="imgs" class="img" :src="src" />
  </div>
</div>
```

那么关键点就在于怎么往这个 `imgs` 数组里追加元素后，做一个流畅的路径动画。

我们来实现追加图片的方法 `add`：

```js
async add() {
  const newData = this.getSister()
  await preload(newData)
}
```

首先随机的取出几张图片作为待放入数组的元素，利用 `new Image` 预加载这些图片，防止渲染一堆空白图片到屏幕上。

然后定义一个计算一组 DOM 元素位置的函数 `getRects`，利用 `getBoundingClientRect` 可以获得最新的位置信息，这个方法在接下来获取图片元素旧位置和新位置时都要使用。

```js
function getRects(doms) {
  return doms.map((dom) => {
    const rect = dom.getBoundingClientRect()
    const { left, top } = rect
    return { left, top }
  })
}

// 当前已有的图片
const prevImgs = this.$refs.imgs.slice()
const prevPositions = getRects(prevImgs)
```

记录完图片的旧位置后，就可以向数组里追加新的图片了：

```js
this.imgs = newData.concat(this.imgs)
```

随后就是比较关键的点了，我们知道 Vue 是异步渲染的，也就是改变了这个 `imgs` 数组后不会立刻发生 DOM 的变动，此时我们要用到 `nextTick` 这个 API，这个 API 把你传入的回调函数放进了 `microTask` 队列，正如上文提到的事件循环的文章里所说，`microTask`队列的执行一定发生在浏览器重新渲染前。

由于先调用了 `this.imgs = newData.concat(this.imgs)` 这段代码，触发了 Vue 的响应式依赖更新，此时 Vue 内部会把本次 DOM 更新的渲染函数先放到 `microTask`队列中，此时的队列是`[changeDOM]`。

调用了 `nextTick(callback)` 后，这个`callback`函数也会被追加到队列中，此时的队列是 `[changeDOM, callback]`。

这下聪明的你肯定就明白了，为什么 `nextTick`的回调函数里一定能获取到最新的 DOM 状态。

由于我们之前保存了图片元素节点的数组 `prevImgs`，所以在 `nextTick` 里调用同样的 `getRect` 方法获取到的就是旧图片的最新位置了。

```js
async add() {
  // 最新 DOM 状态
  this.$nextTick(() => {
    // 再调用同样的方法获取最新的元素位置
    const currentPositions = getRects(prevImgs)
  })
},
```

此时我们已经拥有了 `Invert` 步骤的关键信息，新位置和旧位置，那么接下来就很简单了，把图片数组循环做一个倒置后 `Play`的动画即可。

```js
prevImgs.forEach((imgRef, imgIndex) => {
  const currentPosition = currentPositions[imgIndex]
  const prevPosition = prevPositions[imgIndex]

  // 倒置后的位置，虽然图片移动到最新位置了，但你先给我回去，等着我来让你做动画。
  const invert = {
    left: prevPosition.left - currentPosition.left,
    top: prevPosition.top - currentPosition.top,
  }

  const keyframes = [
    // 初始位置是倒置后的位置
    {
      transform: `translate(${invert.left}px, ${invert.top}px)`,
    },
    // 图片更新后本来应该在的位置
    { transform: "translate(0)" },
  ]

  const options = {
    duration: 300,
    easing: "cubic-bezier(0,0,0.32,1)",
  }

  // 开始运动！
  const animation = imgRef.animate(keyframes, options)
})
```

此时一个非常流畅的路径动画效果就完成了。

完整实现如下：

```js
async add() {
  const newData = this.getSister()
  await preload(newData)

  const prevImgs = this.$refs.imgs.slice()
  const prevPositions = getRects(prevImgs)

  this.imgs = newData.concat(this.imgs)

  this.$nextTick(() => {
    const currentPositions = getRects(prevImgs)

    prevImgs.forEach((imgRef, imgIndex) => {
      const currentPosition = currentPositions[imgIndex]
      const prevPosition = prevPositions[imgIndex]

      const invert = {
        left: prevPosition.left - currentPosition.left,
        top: prevPosition.top - currentPosition.top,
      }

      const keyframes = [
        {
          transform: `translate(${invert.left}px, ${invert.top}px)`,
        },
        { transform: "translate(0)" },
      ]

      const options = {
        duration: 300,
        easing: "cubic-bezier(0,0,0.32,1)",
      }

      const animation = imgRef.animate(keyframes, options)
    })
  })
},
```

## 乱序

现在我们想要实现官网 demo 中的 `shuffle` 效果，有了追加图片逻辑的铺垫，是不是已经觉得思路如泉涌了？没错，即使图片被打乱的再厉害，只要我们有「图片开始时的位置」和「图片结束时的位置」，那就可以轻松做到路径动画。

现在我们需要做的是把动画的逻辑抽离出来，我们分析一下整条链路：

`保存旧位置 -> 改变数据驱动视图更新 -> 获得新位置 -> 利用 FLIP 做动画`

其实外部只需要传入一个 `update` 方法告诉我们如何去更新图片数组，就可以把这个逻辑完全抽象到一个函数里去。

```js
scheduleAnimation(update) {
  // 获取旧图片的位置
  const prevImgs = this.$refs.imgs.slice()
  const prevSrcRectMap = createSrcRectMap(prevImgs)
  // 更新数据
  update()
  // DOM更新后
  this.$nextTick(() => {
    const currentSrcRectMap = createSrcRectMap(prevImgs)
    Object.keys(prevSrcRectMap).forEach((src) => {
      const currentRect = currentSrcRectMap[src]
      const prevRect = prevSrcRectMap[src]

      const invert = {
        left: prevRect.left - currentRect.left,
        top: prevRect.top - currentRect.top,
      }

      const keyframes = [
        {
          transform: `translate(${invert.left}px, ${invert.top}px)`,
        },
        { transform: "" },
      ]
      const options = {
        duration: 300,
        easing: "cubic-bezier(0,0,0.32,1)",
      }

      const animation = currentRect.img.animate(keyframes, options)
    })
  })
}
```

那么追加图片和乱序的函数就变得非常简单了：

```js
// 追加图片
async add() {
  const newData = this.getSister()
  await preload(newData)
  this.scheduleAnimation(() => {
    this.imgs = newData.concat(this.imgs)
  })
},
// 乱序图片
shuffle() {
  this.scheduleAnimation(() => {
    this.imgs = shuffle(this.imgs)
  })
}
```

## 源码地址

https://github.com/sl1673495/flip-animation

## 总结

### FLIP

FLIP 不光可以做位置变化的动画，对于透明度、宽高等等也一样可以很轻松的实现。

比如电商平台中经常会出现一个动画，点击一张商品图片后，商品从它本来的位置慢慢的放大成了一张完整的页面。

`FLIP`的思路掌握后，只要你知道元素动画前的状态和元素动画后的状态，你都可以轻松的通过「倒置状态」后，让它们做一个流畅的动画后到达目的地，并且此时的 DOM 状态是很干净的，而不是通过大量计算的方式强迫它从 `0, 0` 位移到 `100, 100`，并且让 DOM 样式上留下 `transform: translate(100px, 100px)` 类似的字样。

### Web Animation

利用 `Web Animation API` 可以让我们用 JavaScript 更加直观的描述我们需要元素去做的动画，想象一下这个需求如果用 CSS 来做，我们大概会这样去完成这个需求：

```js
const currentImgStyle = currentRect.img.style
currentImgStyle.transform = `translate(${invert.left}px, ${invert.top}px)`
currentImgStyle.transitionDuration = "0s"

this._reflow = document.body.offsetHeight

currentRect.img.classList.add("move")

currentImgStyle.transform = currentRect.img.style.transitionDuration = ""

currentRect.img.addEventListener("transitionend", () => {
  currentRect.img.classList.remove("move")
})
```

这也是 Vue 内部 `transition-group` 组件实现 `FLIP` 动画的大致思路，Vue 应该是为了兼容性和代码体积等一些方面的权衡，还是选择用比较原生的方式去实现 FLIP 动画，这段代码让我觉得不舒服的点在于：

1. 需要通过 `class` 的增加和删除来和 CSS 来进行交互，整体流程不太符合直觉。
2. 需要监听动画完成事件，并且做一些清理操作，容易遗漏。
3. 需要利用 `document.body.offsetHeight` 这样的方式触发 `强制同步布局`，比较 hack 的知识点。
4. 需要利用 `this._reflow = document.body.offsetHeight` 这样的方式向元素实例上增加一个没有意义的属性，防止被 Rollup 等打包工具 `tree-shaking` 误删。 比较 hack 的知识点 +1。

而利用 `Web Animation API` 的代码则变得非常符合直觉和易于维护：

```js
const keyframes = [
  {
    transform: `translate(${invert.left}px, ${invert.top}px)`,
  },
  { transform: "" },
]
const options = {
  duration: 300,
  easing: "cubic-bezier(0,0,0.32,1)",
}

const animation = currentRect.img.animate(keyframes, options)
```

关于兼容性问题，W3C 已经提供了 [`Web Animation API Polyfill`](https://github.com/web-animations/web-animations-js)，可以放心大胆的使用。

期待在不久的未来，我们可以抛弃旧的动画模式，迎接这种更新更好的 API。

希望这篇文章能让对动画发愁的你有一些收获，谢谢！

## ❤️ 感谢大家

1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)
