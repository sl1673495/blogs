---
title: 'TypeScript从零实现基于Proxy的响应式库 普通数据类型'
date: '2020-01-17'
spoiler: ''
---

## 前言
笔者最近在浏览React状态管理库的时候，发现了一些响应式的状态管理库如
`hodux`,`react-easy-state`，内部有一个基于proxy实现响应式的基础仓库`observer-util`，它的代码实现和Vue3中的响应式原理非常相似，这篇文章就从这个仓库入手，一步一步带你剖析响应式的实现。  

本文的代码是我参考`observer-util`用ts的重写的，并且会加上非常详细的注释。  

阅读本文可能需要的一些前置知识：

[Proxy](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy)  
[WeakMap](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WeakMap)  
[Reflect](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Reflect)  

首先看一下`observer-util`给出的代码示例：  
```js
import { observable, observe } from '@nx-js/observer-util';

const counter = observable({ num: 0 });

// 会在控制台打印出0
const countLogger = observe(() => console.log(counter.num));

// 会在控制台打印出1
counter.num++;
```
这就是一个最精简的响应式模型了，乍一看好像和Vue2里的响应式系统也没啥区别，那么还是先看一下Vue2和Vue3响应式系统之间的差异吧。  

## 和Vue2的差异

关于Vue2的响应式原理，感兴趣的也可以去看我之前的一篇文章：  
[实现一个最精简的响应式系统来学习Vue的data、computed、watch源码](https://juejin.im/post/5db6433b51882564912fc30f)  

其实这个问题本质上就是基于Proxy和基于Object.defineProperty之间的差异，来看Vue2中的一个案例：  

### Object.defineProperty
```xml
<template>
  {{ obj.c }}
</template>
<script>
   export default {
       data: {
           obj: { a: 1 }
       },
       mounted() {
           this.obj.c = 3
       }
   }
</script>
```

这个例子中，我们对obj上原本不存在的`c`属性进行了一个赋值，但是在Vue2中，这是不会触发响应式的。  

这是因为Object.defineProperty必须对于确定的`key`值进行响应式的定义，  

这就导致了如果data在初始化的时候没有`c`属性，那么后续对于`c`属性的赋值都不会触发Object.defineProperty中的劫持。  

在Vue2中，这里只能用一个额外的api `Vue.set`来解决。    

### Proxy
再看一下`Proxy`的api，
```js
const raw = {}
const data = new Proxy(raw, {
    get(target, key) { },
    set(target, key, value) { }
})
```  

可以看出来，Proxy在定义的时候并不用关心key值，  

只要你定义了get方法，那么后续对于data上任何属性的访问（哪怕是不存在的），  

都会触发`get`的劫持，`set`也是同理。  

这样Vue3中，对于需要定义响应式的值，初始化时候的要求就没那么高了，只要保证它是个可以被Proxy接受的对象或者数组类型即可。  

当然，Proxy对于数据拦截带来的便利还不止于此，往下看就知道。  

## 实现
接下来就一步步实现这个基于Proxy的响应式系统：  

### 类型描述
本仓库基于TypeScript重构，所以会有一个类型定义的文件，可以当做接口先大致看一下  

https://github.com/sl1673495/typescript-proxy-reactive/blob/master/types/index.ts  

### 思路
首先响应式的思路无外乎这样一个模型：  

1. 定义某个数据为`响应式数据`，它会拥有收集`访问它的函数`的能力。
2. 定义观察函数，在这个函数内部去访问`响应式数据`。

以开头的例子来说
```js
// 响应式数据
const counter = observable({ num: 0 });

// 观察函数
observe(() => console.log(counter.num));
```
这已经一目了然了，
- 用`observable`包裹的数据叫做响应式数据，
- 在`observe`内部执行的函数叫`观察函数`。  

观察函数首先开启某个开关，  
 
#### 访问时 

observe函数会帮你去执行`console.log(counter.num)`，  

这时候`proxy`的`get`拦截到了对于`counter.num`的访问，  

这时候又可以知道访问者是`() =>  console.log(counter.num)`这个函数，  

那么就把这个函数作为`num`这个key值的`观察函数`收集在一个地方。  

#### 修改时
下次对于`counter.num`修改的时候，去找`num`这个key下所有的`观察函数`，轮流执行一遍。  

这样就实现了响应式模型。  

## reactive的实现（定义响应式数据）

上文中关于`observable`的api，我换了个名字: `reactive`，感觉更好理解一些。  


```js
// 需要定义响应式的原值
export type Raw = object
// 定义成响应式后的proxy
export type ReactiveProxy = object

export const proxyToRaw = new WeakMap<ReactiveProxy, Raw>()
export const rawToProxy = new WeakMap<Raw, ReactiveProxy>()

function createReactive<T extends Raw>(raw: T): T {
  const reactive = new Proxy(raw, baseHandlers)

  // 双向存储原始值和响应式proxy的映射
  rawToProxy.set(raw, reactive)
  proxyToRaw.set(reactive, raw)

  // 建立一个映射
  // 原始值 -> 存储这个原始值的各个key收集到的依赖函数的Map
  storeObservable(raw)

  // 返回响应式proxy
  return reactive as T
}
```

首先是定义proxy
```js
const reactive = new Proxy(raw, baseHandlers)
```
这个baseHandlers里就是对于数据的`get`、`set`之类的劫持，

这里有两个WeakMap： `proxyToRaw`和`rawToProxy`，  

可以看到在定义响应式数据为一个Proxy的时候，会进行一个双向的存储，  

这样后续无论是拿到原始对象还是拿到响应式proxy，都可以很容易的拿到它们的`另一半`。

之后`storeObservable`，是用原始对象建立一个map：  
```js
const connectionStore = new WeakMap<Raw, ReactionForRaw>()

function storeObservable(value: object) {
  // 存储对象和它内部的key -> reaction的映射
  connectionStore.set(value, new Map() as ReactionForRaw)
}
```

通过connectionStore的泛型也可以知道，  

这是一个`Raw` -> `ReactionForRaw`的map。  

也就是`原始数据` -> `这个数据收集到的观察函数依赖`  

更清晰的描述可以看Type定义：  
```js
// 收集响应依赖的的函数
export type ReactionFunction = Function & {
  cleaners?: ReactionForKey[]
  unobserved?: boolean
}

// reactionForRaw的key为对象key值 value为这个key值收集到的Reaction集合
export type ReactionForRaw = Map<Key, ReactionForKey>

// key值收集到的Reaction集合
export type ReactionForKey = Set<ReactionFunction>

// 收集响应依赖的的函数
export type ReactionFunction = Function & {
  cleaners?: ReactionForKey[]
  unobserved?: boolean
}
```

那接下来的重点就是proxy的第二个参数`baseHandler`里的`get`和`set`了  

## proxy的get  
```js
/** 劫持get访问 收集依赖 */
function get(target: Raw, key: Key, receiver: ReactiveProxy) {
  const result = Reflect.get(target, key, receiver)
  
  // 收集依赖
  registerRunningReaction({ target, key, receiver, type: "get" })

  return result
}

```
关于receiver这个参数，这里可以先简单理解为`响应式proxy`本身，不影响流程。  

这里就是简单的做了一个求值，然后进入了`registerRunningReaction`函数，  

### 注册依赖  
```js
// 收集响应依赖的的函数
type ReactionFunction = Function & {
  cleaners?: ReactionForKey[]
  unobserved?: boolean
}

// 操作符 用来做依赖收集和触发依赖更新
interface Operation {
  type: "get" | "iterate" | "add" | "set" | "delete" | "clear"
  target: object
  key?: Key
  receiver?: any
  value?: any
  oldValue?: any
}

/** 依赖收集栈 */
const reactionStack: ReactionFunction[] = []

/** 依赖收集 在get操作的时候要调用 */
export function registerRunningReaction(operation: Operation) {
  const runningReaction = getRunningReaction()
  if (runningReaction) {
      // 拿到原始对象 -> 观察者的map
      const reactionsForRaw = connectionStore.get(target)
      // 拿到key -> 观察者的set
      let reactionsForKey = reactionsForRaw.get(key)
    
      if (!reactionsForKey) {
        // 如果这个key之前没有收集过观察函数 就新建一个
        reactionsForKey = new Set()
        // set到整个value的存储里去
        reactionsForRaw.set(key, reactionsForKey)
      }
    
      if (!reactionsForKey.has(reaction)) {
        // 把这个key对应的观察函数收集起来
        reactionsForKey.add(reaction)
        // 把key收集的观察函数集合 加到cleaners队列中 便于后续取消观察
        reaction.cleaners.push(reactionsForKey)
      }
  }
}

/** 从栈的末尾取到正在运行的observe包裹的函数 */
function getRunningReaction() {
  const [runningReaction] = reactionStack.slice(-1)
  return runningReaction
}
```

这里做的一系列操作，就是把用`原始数据`从`connectionStore`里拿到依赖收集的map，然后在`reaction`观察函数把对于某个`key`访问的时候，把`reaction`观察函数本身增加到这个`key`的观察函数集合里。  

那么这个`runningReaction`正在运行的观察函数是哪来的呢，剧透一下，当然是`observe`这个api内部开启观察模式后去做的。  

```js
// 此时 () => console.log(counter.num) 会被包装成reaction函数
observe(() => console.log(counter.num));
```

### set
```js
/** 劫持set访问 触发收集到的观察函数 */
function set(target: Raw, key: Key, value: any, receiver: ReactiveProxy) {
  // 拿到旧值
  const oldValue = target[key]
  // 设置新值
  const result = Reflect.set(target, key, value, receiver)
  
  queueReactionsForOperation({
      target,
      key,
      value,
      oldValue,
      receiver,
      type: 'set'
  })

  return result
}

/** 值更新时触发观察函数 */
export function queueReactionsForOperation(operation: Operation) {
  getReactionsForOperation(operation).forEach(reaction => reaction())
}

/**
 *  根据key,type和原始对象 拿到需要触发的所有观察函数
 */
export function getReactionsForOperation({ target, key, type }: Operation) {
  // 拿到原始对象 -> 观察者的map
  const reactionsForTarget = connectionStore.get(target)
  const reactionsForKey: ReactionForKey = new Set()

  // 把所有需要触发的观察函数都收集到新的set里
  addReactionsForKey(reactionsForKey, reactionsForTarget, key)

  return reactionsForKey
}
```
`set`赋值操作的时候，本质上就是去检查这个`key`收集到了哪些`reaction`观察函数，然后依次触发。  

## observe 观察函数  

`observe`这个api接受一个用户传入的函数，在这个函数内访问响应式数据才会去收集观察函数作为自己的依赖。  

```js
/** 
 * 观察函数
 * 在传入的函数里去访问响应式的proxy 会收集传入的函数作为依赖
 * 下次访问的key发生变化的时候 就会重新运行这个函数
 */
export function observe(fn: Function): ReactionFunction {
  // reaction是包装了原始函数只后的观察函数
  // 在runReactionWrap的上下文中执行原始函数 可以收集到依赖。
  const reaction: ReactionFunction = (...args: any[]) => {
    return runReactionWrap(reaction, fn, this, args)
  }

  // 先执行一遍reaction
  reaction()

  // 返回出去 让外部也可以手动调用
  return reaction
}
```  

核心的逻辑在`runReactionWrap`里，
```js

/** 把函数包裹为观察函数 */
export function runReactionWrap(
  reaction: ReactionFunction,
  fn: Function,
  context: any,
  args: any[],
) {
  try {
    // 把当前的观察函数推入栈内 开始观察响应式proxy
    reactionStack.push(reaction)
    // 运行用户传入的函数 这个函数里访问proxy就会收集reaction函数作为依赖了
    return Reflect.apply(fn, context, args)
  } finally {
    // 运行完了永远要出栈
    reactionStack.pop()
  }
}
```  

简化后的核心逻辑很简单，  

把`reaction`推入`reactionStack`后开始执行用户传入的函数，  

在函数内访问`响应式proxy`的属性，又会触发`get`的拦截，  

这时候`get`去`reactionStack`找当前正在运行的`reaction`，就可以成功的收集到依赖了。  
  
下一次用户进行赋值的时候
```js
const counter = reactive({ num: 0 });

// 会在控制台打印出0
const counterReaction = observe(() => console.log(counter.num));

// 会在控制台打印出1
counter.num = 1;
```
以这个示例来说，observe内部对于counter的key值`num的`访问，会收集`counterReaction`作为`num`的依赖。  

`counter.num = 1`的操作，会触发对于counter的`set`劫持，此时就会从`key`值的依赖收集里面找到`counterReaction`，再重新执行一遍。  

## 边界情况
以上实现只是一个最基础的响应式模型，还没有实现的点有：

- 深层数据的劫持
- 数组和对象新增、删除项的响应

接下来在上面的代码的基础上来实现这两种情况： 

### 深层数据的劫持
在刚刚的代码实现中，我们只对Proxy的第一层属性做了拦截，假设有这样的一个场景
```js
const counter = reactive({ data: { num: 0 } });

// 会在控制台打印出0
const counterReaction = observe(() => console.log(counter.data.num));

counter.data.num = 1;
```

这种场景就不能实能触发`counterReaction`自动执行了。  

因为counter.data.num其实是对`data`上的`num`属性进行赋值，而counter虽然是一个`响应式proxy`，但`counter.data`却只是一个普通的对象，回想一下刚刚的proxy`get`的拦截函数：  

```js
/** 劫持get访问 收集依赖 */
function get(target: Raw, key: Key, receiver: ReactiveProxy) {
  const result = Reflect.get(target, key, receiver)
  
  // 收集依赖
  registerRunningReaction({ target, key, receiver, type: "get" })

  return result
}
```
`counter.data`只是通过Reflect.get拿到了原始的 { data: {number } }对象，然后对这个对象的赋值不会被proxy拦截到。  

那么思路其实也有了，就是在深层访问的时候，如果访问的数据是个对象，就把这个对象也用`reactive`包装成proxy再返回，这样在进行`counter.data.num = 1;`赋值的时候，其实也是针对一个`响应式proxy`赋值了。  

```diff
/** 劫持get访问 收集依赖 */
function get(target: Raw, key: Key, receiver: ReactiveProxy) {
  const result = Reflect.get(target, key, receiver)
  // 收集依赖
  registerRunningReaction({ target, key, receiver, type: "get" })

+  // 如果访问的是对象 则返回这个对象的响应式proxy
+  if (isObject(result)) {
+    return reactive(result)
+  }

  return result
}

```  

### 数组和对象新增、删除项的响应
以这样一个场景为例  

```js
const data: any = reactive({ a: 1, b: 2})

observe(() => console.log( Object.keys(data)))

data.c = 5
```  

其实在用Object.keys访问data的时候，后续不管是data上的key发生了新增或者删除，都应该触发这个观察函数，那么这是怎么实现的呢？  

首先我们需要知道，Object.keys(data)访问proxy的时候，会触发proxy的`ownKeys`拦截。  

那么我们在`baseHandler`中先新增对于`ownKeys`的访问拦截：
```diff
/** 劫持get访问 收集依赖 */
function get() {}

/** 劫持set访问 触发收集到的观察函数 */
function set() {
}

/** 劫持一些遍历访问 比如Object.keys */
+ function ownKeys (target: Raw) {
+   registerRunningReaction({ target, type: 'iterate' })
+   return Reflect.ownKeys(target)
+ }
```

还是和get方法一样，调用`registerRunningReaction`方法注册依赖，但是type我们需要定义成`iterate`，这个type怎么用呢。我们继续改造`registerRunningReaction`函数：  

```diff
+ const ITERATION_KEY = Symbol("iteration key")

export function registerRunningReaction(operation: Operation) {
  const runningReaction = getRunningReaction()
  if (runningReaction) {
+      if (type === "iterate") {
+        key = ITERATION_KEY
+      }
      // 拿到原始对象 -> 观察者的map
      const reactionsForRaw = connectionStore.get(target)
      // 拿到key -> 观察者的set
      let reactionsForKey = reactionsForRaw.get(key)
    
      if (!reactionsForKey) {
        // 如果这个key之前没有收集过观察函数 就新建一个
        reactionsForKey = new Set()
        // set到整个value的存储里去
        reactionsForRaw.set(key, reactionsForKey)
      }
    
      if (!reactionsForKey.has(reaction)) {
        // 把这个key对应的观察函数收集起来
        reactionsForKey.add(reaction)
        // 把key收集的观察函数集合 加到cleaners队列中 便于后续取消观察
        reaction.cleaners.push(reactionsForKey)
      }
  }
}
```

也就是`type: iterate`触发的依赖收集，我们会放在key为`ITERATION_KEY`的一个特殊的set里，那么再来看看触发更新时的`set`改造：  

```diff
/** 劫持set访问 触发收集到的观察函数 */
function set(target: Raw, key: Key, value: any, receiver: ReactiveProxy) {
  // 拿到旧值
  const oldValue = target[key]
  // 设置新值
  const result = Reflect.set(target, key, value, receiver)
+  // 先检查一下这个key是不是新增的
+  const hadKey = hasOwnProperty.call(target, key)

+  if (!hadKey) {
+    // 新增key值时触发观察函数
+    queueReactionsForOperation({ target, key, value, receiver, type: 'add' })
  } else if (value !== oldValue) {
    // 已存在的key的值发生变化时触发观察函数
    queueReactionsForOperation({
      target,
      key,
      value,
      oldValue,
      receiver,
      type: 'set'
    })
  }

  return result
}

```

这里对新增的key也进行了的判断，传入`queueReactionsForOperation`的type变成了`add`

```diff

/** 值更新时触发观察函数 */
export function queueReactionsForOperation(operation: Operation) {
  getReactionsForOperation(operation).forEach(reaction => reaction())
}

/**
 *  根据key,type和原始对象 拿到需要触发的所有观察函数
 */
export function getReactionsForOperation({ target, key, type }: Operation) {
  // 拿到原始对象 -> 观察者的map
  const reactionsForTarget = connectionStore.get(target)
  const reactionsForKey: ReactionForKey = new Set()

  // 把所有需要触发的观察函数都收集到新的set里
  addReactionsForKey(reactionsForKey, reactionsForTarget, key)

  // add和delete的操作 需要触发某些由循环触发的观察函数收集
  // observer(() => rectiveProxy.forEach(() => proxy.foo))
+  if (type === "add" || type === "delete") {
+    const iterationKey = Array.isArray(target) ? "length" : ITERATION_KEY
+    addReactionsForKey(reactionsForKey, reactionsForTarget, iterationKey)
  }
  return reactionsForKey
}
```

这里需要注意的是，对于数组新增和删除项来说，如果我们在观察函数中做了遍历操作，也需要触发它的更新，  

这里又有一个知识点，对于数组遍历的操作，都会触发它对`length`的读取，然后把观察函数收集到`length`这个key的依赖中，比如
```js
observe(() => proxyArray.forEach(() => {}))
// 会访问proxyArray的length。
```

所以在触发更新的时候，
1. 如果目标是个数组，那就从`length`的依赖里收集，
2. 如果目标是对象，就从`ITERATION_KEY`的依赖里收集。（也就是对于对象做Object.keys读取时，由`ownKeys`拦截收集的依赖）。

## 源码地址
https://github.com/sl1673495/typescript-proxy-reactive  

## 总结
由于篇幅原因，有一些优化的操作我没有在文中写出来，在仓库里做了几乎是逐行注释，而且也可以用`npm run dev`对example文件夹中的例子进行调试。感兴趣的同学可以自己看一下。  

如果读完了还觉得有兴致，也可以直接去看`observe-util`这个库的源码，里面对于更多的边界情况做了处理，代码也写的非常优雅，值得学习。  

从本文里讲解的一些边界情况也可以看出，基于Proxy的响应式方案比Object.defineProperty要强大很多，希望大家尽情的享受Vue3带来的快落吧。  

