# [Vue源码学习 nextTick](https://github.com/sl1673495/blogs/issues/11)

vue在视图更新的时候是异步更新，这个很多人已经知道了，这么做的好处有很多，今天我们就来看看vue是如何调度这个异步更新队列去优化性能的。

src/core/util/next-tick.js
```js
/* @flow */
/* globals MessageChannel */

import { noop } from 'shared/util'
import { handleError } from './error'
import { isIOS, isNative } from './env'

const callbacks = []
let pending = false

function flushCallbacks () {
  pending = false
  const copies = callbacks.slice(0)
  callbacks.length = 0
  for (let i = 0; i < copies.length; i++) {
    copies[i]()
  }
}

// Here we have async deferring wrappers using both microtasks and (macro) tasks.
// In < 2.4 we used microtasks everywhere, but there are some scenarios where
// microtasks have too high a priority and fire in between supposedly
// sequential events (e.g. #4521, #6690) or even between bubbling of the same
// event (#6566). However, using (macro) tasks everywhere also has subtle problems
// when state is changed right before repaint (e.g. #6813, out-in transitions).
// Here we use microtask by default, but expose a way to force (macro) task when
// needed (e.g. in event handlers attached by v-on).
let microTimerFunc
let macroTimerFunc
let useMacroTask = false

// Determine (macro) task defer implementation.
// Technically setImmediate should be the ideal choice, but it's only available
// in IE. The only polyfill that consistently queues the callback after all DOM
// events triggered in the same loop is by using MessageChannel.
/* istanbul ignore if */
if (typeof setImmediate !== 'undefined' && isNative(setImmediate)) {
  macroTimerFunc = () => {
    setImmediate(flushCallbacks)
  }
} else if (typeof MessageChannel !== 'undefined' && (
  isNative(MessageChannel) ||
  // PhantomJS
  MessageChannel.toString() === '[object MessageChannelConstructor]'
)) {
  const channel = new MessageChannel()
  const port = channel.port2
  channel.port1.onmessage = flushCallbacks
  macroTimerFunc = () => {
    port.postMessage(1)
  }
} else {
  /* istanbul ignore next */
  macroTimerFunc = () => {
    setTimeout(flushCallbacks, 0)
  }
}

// Determine microtask defer implementation.
/* istanbul ignore next, $flow-disable-line */
if (typeof Promise !== 'undefined' && isNative(Promise)) {
  const p = Promise.resolve()
  microTimerFunc = () => {
    p.then(flushCallbacks)
    // in problematic UIWebViews, Promise.then doesn't completely break, but
    // it can get stuck in a weird state where callbacks are pushed into the
    // microtask queue but the queue isn't being flushed, until the browser
    // needs to do some other work, e.g. handle a timer. Therefore we can
    // "force" the microtask queue to be flushed by adding an empty timer.
    if (isIOS) setTimeout(noop)
  }
} else {
  // fallback to macro
  microTimerFunc = macroTimerFunc
}

/**
 * Wrap a function so that if any code inside triggers state change,
 * the changes are queued using a (macro) task instead of a microtask.
 */
export function withMacroTask (fn: Function): Function {
  return fn._withTask || (fn._withTask = function () {
    useMacroTask = true
    const res = fn.apply(null, arguments)
    useMacroTask = false
    return res
  })
}

export function nextTick (cb?: Function, ctx?: Object) {
  let _resolve
  callbacks.push(() => {
    if (cb) {
      try {
        cb.call(ctx)
      } catch (e) {
        handleError(e, ctx, 'nextTick')
      }
    } else if (_resolve) {
      _resolve(ctx)
    }
  })
  if (!pending) {
    pending = true
    if (useMacroTask) {
      macroTimerFunc()
    } else {
      microTimerFunc()
    }
  }
  // $flow-disable-line
  if (!cb && typeof Promise !== 'undefined') {
    return new Promise(resolve => {
      _resolve = resolve
    })
  }
}

```

首先这个文件的开头定义了两个全局变量
```js
const callbacks = []
let pending = false
```
callbacks用来存放我们需要异步执行的函数队列，
pending用来标记是否已经命令callbacks在下个tick全部执行，防止多次调用。

### 入口
```js
export function nextTick (cb?: Function, ctx?: Object) {
  let _resolve
  callbacks.push(() => {
    if (cb) {
      try {
        cb.call(ctx)
      } catch (e) {
        handleError(e, ctx, 'nextTick')
      }
    } else if (_resolve) {
      _resolve(ctx)
    }
  })
  if (!pending) {
    pending = true
    if (useMacroTask) {
      macroTimerFunc()
    } else {
      microTimerFunc()
    }
  }
  // $flow-disable-line
  if (!cb && typeof Promise !== 'undefined') {
    return new Promise(resolve => {
      _resolve = resolve
    })
  }
}
```
我们在外部调用都是nextTick(() => { // doSth })
这样子去使用， 把一个cb函数传入nextTick函数中，
nextTick函数首先
```js
callbacks.push(() => {
    if (cb) {
      try {
        cb.call(ctx)
      } catch (e) {
        handleError(e, ctx, 'nextTick')
      }
    } else if (_resolve) {
      _resolve(ctx)
    }
  })
```
把我们的cb函数包装了一层，做了判断，这是为了nextTick可以用then方法，我们就暂且当做直接把cb函数push进callbacks队列吧。

我们需要知道的是microTask是在同步方法完成的末尾去执行， macroTask则是直接是到下一个task了，task之间又可能会包含浏览器的重渲染，setTimeout默认的4ms延迟等等...从性能和时效性来看都是microTask更为优先。

关于macroTask和microTask的区别不是本文的重点，如果有需要的小伙伴可以去查阅一下浏览器的eventLoop相关的知识点。

随后如果pending的标志位还没有置为true，就把pending置为true，
并且开始根据useMacroTask这个标志判断 nextTick是通过macroTask实现还是microTask实现，
并且去调用这个task，这样在下一个tick就会去把callbacks里的方法全部执行。
```js
  if (!pending) {
    pending = true
    if (useMacroTask) {
      macroTimerFunc()
    } else {
      microTimerFunc()
    }
  }
```

### 判断macroTask和microTask该用什么api

回到这个文件的上半部分 
```js
let microTimerFunc
let macroTimerFunc
let useMacroTask = false
```
首先定义了3个全局变量， 可以看到useMacroTask默认为false，接下来就要开始根据浏览器的api兼容性判断，用什么来实现microTimerFunc和macroTimerFunc

接下来vue开始判断如何实现macroTimerFunc
```js
if (typeof setImmediate !== 'undefined' && isNative(setImmediate)) {
  macroTimerFunc = () => {
    setImmediate(flushCallbacks)
  }
} else if (typeof MessageChannel !== 'undefined' && (
  isNative(MessageChannel) ||
  // PhantomJS
  MessageChannel.toString() === '[object MessageChannelConstructor]'
)) {
  const channel = new MessageChannel()
  const port = channel.port2
  channel.port1.onmessage = flushCallbacks
  macroTimerFunc = () => {
    port.postMessage(1)
  }
} else {
  /* istanbul ignore next */
  macroTimerFunc = () => {
    setTimeout(flushCallbacks, 0)
  }
}
```

这段方法就是判断macroTask优先去使用setImmediate， 其次是MessageChannel，最次是setTimeout。

接下来去判断microTask
```js
if (typeof Promise !== 'undefined' && isNative(Promise)) {
  const p = Promise.resolve()
  microTimerFunc = () => {
    p.then(flushCallbacks)
    if (isIOS) setTimeout(noop)
  }
} else {
  microTimerFunc = macroTimerFunc
}
```
microTask只有Promise一个选项，如果浏览器没有提供promise的api 就只能降级为上面判断的macroTimerFunc了。

### 在下个tick执行异步队列
无论是microTask还是macroTask 传入的方法都是flushCallbacks，那这个肯定就是执行callbacks的方法了，我们来看看这个方法的定义
```js
function flushCallbacks () {
  pending = false
  const copies = callbacks.slice(0)
  callbacks.length = 0
  for (let i = 0; i < copies.length; i++) {
    copies[i]()
  }
}
```

这个方法很简短， 
把pendding置为false，把callbacks拷贝一份并且把callbacks清空
这是为了在nextTick的方法里再次调用nextTick，能够新开一个异步队列，
然后循环这个拷贝callbacks里的函数， 一次性执行完毕，


vue的异步队列调度就是这样实现的，
希望在大家在工作中也能运用这种思想， 把影响性能而且能合并的方法异步合并执行。