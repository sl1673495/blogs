---
title: '关于如何触发浏览器重绘的一些尝试。'
date: '2018-11-23'
spoiler: ''
---

我们动态的往body节点上挂一个小球 并且更改它的top值 让它触发动画
（以下代码均在chrome控制台执行）
```js
var div = document.createElement('div')
div.style.cssText = 'position: fixed;width: 30px; height: 30px; left: 0; top: 0; background: red;transition: all 1s'
document.body.appendChild(div)
div.style.top = '500px'
```

这样写是没用的，因为浏览器很聪明，它会把你在一次task中的样式更改收集起来，再执行渲染的时候再把它一次性改变，但是网上很多人说getComputedStyle这个api可以直接触发重绘，那么我们来试试

```js
var div = document.createElement('div')
div.style.cssText = 'position: fixed;width: 30px; height: 30px; left: 0; top: 0; background: red;transition: all 1s'
document.body.appendChild(div)

// 想触发重绘
getComputedStyle(div)
div.style.top = '500px'
```

按理说应该会执行动画吧， 可是并没有，这很让人疑惑，我们再这样试试

```js
var div = document.createElement('div')
div.style.cssText = 'position: fixed;width: 30px; height: 30px; left: 0; top: 0; background: red;transition: all 1s'
document.body.appendChild(div)

// 想触发重绘
getComputedStyle(div).top
div.style.top = '500px'
```

咦，这次终于执行动画了，看来浏览器优化程度到了这一步，就算你去getComputedStyle 它也会惰性的给你返回一个对象， 等到你真正的去读取里面的样式值，才会触发重绘。




再来一个小实验，我们想要让浏览器闪烁两个颜色
```js
document.body.style.background = 'blue'
document.body.style.background = 'red'
```
显而易见这样是没用的， 那么我们用setTimeout去让中间经历一次浏览器渲染
```js
document.body.style.background = 'blue'
setTimeout(() => { document.body.style.background = 'red' })
```
这次好像可以了 把这段代码在浏览器里执行多次， 会发现有时候还是会直接变成红色背景，这是为什么呢？ 我们继续做个试验

```js
document.body.style.background = 'blue'
setTimeout(() => { document.body.style.background = 'red' }, 16.7)
```
这段代码再执行n次， 这下每次都会闪烁两种颜色了， 16.7是个什么数字呢，我们一般电脑的屏幕刷新率是60hz，也就是每秒更新60次视图，1000ms / 60 ≈ 16.7 浏览器会根据你的屏幕刷新率去约束渲染线程的执行，去除掉多余无效的渲染。

那牵扯到硬件，假如我们的刷新率只有30hz呢， 或者更多，更少呢？
这也就是为什么浏览器给我们提供了一个api叫requestAnimationFrame，不懂的朋友们可以去查阅一下这个api的用法。
真正保证屏幕一定会闪烁两次的做法
```js
requestAnimationFrame(() => {
  document.body.style.background = 'red' 
  requestAnimationFrame(() => {
    document.body.style.background = 'blue'
  })
})
```