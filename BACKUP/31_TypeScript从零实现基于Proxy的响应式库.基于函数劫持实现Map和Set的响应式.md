# [TypeScript从零实现基于Proxy的响应式库 基于函数劫持实现Map和Set的响应式](https://github.com/sl1673495/blogs/issues/31)

## 前言
在本系列的上一篇文章  

[带你彻底搞懂Vue3的响应式原理！TypeScript从零实现基于Proxy的响应式库。](https://juejin.im/post/5e21196fe51d454d523be084)中，  

我们详细的讲解了普通对象和数组实现响应式的原理，但是Proxy可以做的远不止于此，对于es6中新增的`Map`、`Set`、`WeakMap`、`WeakSet`也一样可以实现响应式的支持。  

但是对于这部分的劫持，代码中的逻辑是完全独立的一套，这篇文章就来看一下如何基于函数劫持实现实现这个需求。  

阅读本篇需要的一些前置知识：  
[Proxy](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy)  
[WeakMap](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WeakMap)  
[Reflect](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Reflect)  
[Symbol.iterator](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Symbol/iterator) (会讲解)

## 为什么特殊
在上一篇文章中，假设我们通过`data.a`去读取响应式数据`data`的属性，则会触发Proxy的劫持中的`get(target, key)`

target就是`data对应的原始对象`，key就是`a`  

我们可以在这时候给key: `a`注册依赖，然后通过Reflect.get(data, key)去读到原始数据返回出去。

回顾一下：  
```js
/** 劫持get访问 收集依赖 */
function get(target: Raw, key: Key, receiver: ReactiveProxy) {
  const result = Reflect.get(target, key, receiver)
  
  // 收集依赖
  registerRunningReaction({ target, key, receiver, type: "get" })

  return result
}
```  

而当我们的响应式对象是一个`Map`数据类型的时候，想象一下这个场景：
```js
const data = reactive(new Map([['a', 1]]))

observe(() => data.get('a'))

data.set('a', 2)
```

读取数据的方式变成了`data.get('a')`这种形式，如果还是用上一篇文章中的get，会发生什么情况呢？

`get(target, key)`中的target是`map原始对象`，key是`get`，  

通过Reflect.get返回的是`map.get`这个方法，注册的依赖也是通过`get`这个key注册的，而我们想要的效果是通过`a`这个key来注册依赖。

所以这里的办法就是`函数劫持`，就是把对于`Map`和`Set`的所有api的访问（比如`has`, `get`, `set`, `add`）全部替换成我们自己写的方法，让用户无感知的使用这些api，但是内部却已经被我们自己的代码劫持了。  

## 实现
我们把上篇文章中的目录结构调整成这样：
```ts
src/handlers
// 数组和对象的handlers
├── base.ts
// map和set的handlers
├── collections.ts
// 统一导出
└── index.ts
```

### 入口
首先看一下handlers/index.ts入口的改造
```js
import { collectionHandlers } from "./collections"
import { baseHandlers } from "./base"
import { Raw } from "types"

// @ts-ignore
// 根据对象的类型 获取Proxy的handlers
export const handlers = new Map([
  [Map, collectionHandlers],
  [Set, collectionHandlers],
  [WeakMap, collectionHandlers],
  [WeakSet, collectionHandlers],
  [Object, baseHandlers],
  [Array, baseHandlers],
  [Int8Array, baseHandlers],
  [Uint8Array, baseHandlers],
  [Uint8ClampedArray, baseHandlers],
  [Int16Array, baseHandlers],
  [Uint16Array, baseHandlers],
  [Int32Array, baseHandlers],
  [Uint32Array, baseHandlers],
  [Float32Array, baseHandlers],
  [Float64Array, baseHandlers],
])

/** 获取Proxy的handlers */
export function getHandlers(obj: Raw) {
  return handlers.get(obj.constructor)
}

```

这里定义了一个Map: `handlers`，导出了一个`getHandlers`方法，根据传入数据的类型获取Proxy的第二个参数`handlers`，  

`baseHandlers`在第一篇中已经进行了详细讲解。  

这篇文章主要是讲解`collectionHandlers`。

### collections
先看一下`collections`的入口：  
```js
// 真正交给Proxy第二个参数的handlers只有一个get
// 把用户对于map的get、set这些api的访问全部移交给上面的劫持函数
export const collectionHandlers = {
  get(target: Raw, key: Key, receiver: ReactiveProxy) {
    // 返回上面被劫持的api
    target = hasOwnProperty.call(instrumentations, key)
      ? instrumentations
      : target
    return Reflect.get(target, key, receiver)
  },
}
```

我们所有的handlers只有一个`get`，也就是用户对于map或者set上所有api的访问（比如`has`, `get`, `set`, `add`），都会被转移到我们自己定义的api上，这其实就是函数劫持的一种应用。

那关键就在于`instrumentations`这个对象上，我们对于这些api的自己的实现。  

### 劫持api的实现

#### get和set
```js
export const instrumentations = {
  get(key: Key) {
    // 获取原始数据
    const target = proxyToRaw.get(this)
    // 获取原始数据的__proto__ 拿到原型链上的方法
    const proto: any = Reflect.getPrototypeOf(this)
    // 注册get类型的依赖
    registerRunningReaction({ target, key, type: "get" })
    // 调用原型链上的get方法求值 然后对于复杂类型继续定义成响应式
    return findReactive(proto.get.apply(target, arguments))
  },
  set(key: Key, value: any) {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    // 是否是新增的key
    const hadKey = proto.has.call(target, key)
    // 拿到旧值
    const oldValue = proto.get.call(target, key)
    // 求出结果
    const result = proto.set.apply(target, arguments)
    if (!hadKey) {
      // 新增key值时以type: add触发观察函数
      queueReactionsForOperation({ target, key, value, type: "add" })
    } else if (value !== oldValue) {
      // 已存在的key的值发生变化时以type: set触发观察函数
      queueReactionsForOperation({ target, key, value, oldValue, type: "set" })
    }
    return result
  },
}

/** 对于返回值 如果是复杂类型 再进一步的定义为响应式 */
function findReactive(obj: Raw) {
  const reactiveObj = rawToProxy.get(obj)
  // 只有正在运行观察函数的时候才去定义响应式
  if (hasRunningReaction() && isObject(obj)) {
    if (reactiveObj) {
      return reactiveObj
    }
    return reactive(obj)
  }
  return reactiveObj || obj
}
```

核心的`get`和`set`方法和上一篇文章中的实现就几乎一样了，`get`返回的值通过`findReactive`确保进一步定义响应式数据，从而实现深度响应。  

至此，这样的用例就可以跑通了：

```js
const data = reactive(new Map([['a', 1]]))
observe(() => console.log('a', data.get('a')))

data.set('a', 5)
// 重新打印出a 5
```

接下来再针对一些特有的api进行实现：
#### has
```js
  has (key) {
    const target = proxyToRaw.get(this)
    const proto = Reflect.getPrototypeOf(this)
    registerRunningReactionForOperation({ target, key, type: 'has' })
    return proto.has.apply(target, arguments)
  },
```

#### add
add就是典型的新增key的流程，会触发循环相关的观察函数。
```js
  add (key: Key) {
    const target = proxyToRaw.get(this)
    const proto: any  = Reflect.getPrototypeOf(this)
    const hadKey = proto.has.call(target, key)
    const result = proto.add.apply(target, arguments)
    if (!hadKey) {
      queueReactionsForOperation({ target, key, value: key, type: 'add' })
    }
    return result
  },
```

#### delete
delete也和上一篇中的deleteProperty的实现大致相同，会触发循环相关的观察函数。
```js
  delete (key: Key) {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    const hadKey = proto.has.call(target, key)
    const result = proto.delete.apply(target, arguments)
    if (hadKey) {
      queueReactionsForOperation({ target, key, type: 'delete' })
    }
    return result
  },
```

#### clear
```js
  clear () {
    const target: any = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    const hadItems = target.size !== 0
    const result = proto.clear.apply(target, arguments)
    if (hadItems) {
      queueReactionsForOperation({ target, type: 'clear' })
    }
    return result
  },
```

在触发观察函数的时候，针对clear这个type做了一些特殊处理，也是触发循环相关的观察函数。  

```diff
export function getReactionsForOperation ({ target, key, type }) {
  const reactionsForTarget = connectionStore.get(target)
  const reactionsForKey = new Set()

+  if (type === 'clear') {
+    reactionsForTarget.forEach((_, key) => {
+      addReactionsForKey(reactionsForKey, reactionsForTarget, key)
+    })
  } else {
    addReactionsForKey(reactionsForKey, reactionsForTarget, key)
  }

 if (
    type === 'add' 
    || type === 'delete' 
+   || type === 'clear'
) {
    const iterationKey = Array.isArray(target) ? 'length' : ITERATION_KEY
    addReactionsForKey(reactionsForKey, reactionsForTarget, iterationKey)
  }

  return reactionsForKey
}
```  

`clear`的时候，把每一个key收集到的观察函数都给拿到，并且把循环的观察函数也拿到，可以说是触发最全的了。  

逻辑也很容易理解，`clear`的行为每一个key都需要关心，只要在observe函数中读取了任意的key，clear的时候也需要重新执行这个observe的函数。  


#### forEach 


```js
  forEach (cb, ...args) {
    const target = proxyToRaw.get(this)
    const proto = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    const wrappedCb = (value, ...rest) => cb(findObservable(value), ...rest)
    return proto.forEach.call(target, wrappedCb, ...args)
  },
```

到了forEach的劫持 就稍微有点难度了。

首先`registerRunningReaction`注册依赖的时候，用的key是`iterate`，这个很容易理解，因为这是遍历的操作。  

这样用户后续对集合数据进行`新增`或者`删除`、或者使用`clear`操作的时候，会重新触发内部调用了`forEach`的观察函数

重点看下接下来这两段代码：
```js
const wrappedCb = (value, ...rest) => cb(findObservable(value), ...rest)
return proto.forEach.call(target, wrappedCb, ...args)
```  

wrappedCb包裹了用户自己传给forEach的cb函数，然后传给了集合对象原型链上的forEach，这又是一个函数劫持。用户传入的是map.forEach(cb)，而我们最终调用的是map.forEach(wrappedCb)。  

在这个wrappedCb中，我们把cb中本应该获得的原始值value通过`findObservable`定义成响应式数据交给用户，这样用户在forEach中进行的响应式操作一样可以收集到依赖了，不得不赞叹这个设计的巧妙。  

#### keys && size
```js
  get size () {
    const target = proxyToRaw.get(this)
    const proto = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    return Reflect.get(proto, 'size', target)
  },
  keys () {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    return proto.keys.apply(target, arguments)
  },
```
由于`keys`和`size`返回的值不需要定义成响应式，所以直接返回原值就可以了。

#### values
再来看一个需要做特殊处理的典型
```js
  values () {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    const iterator = proto.values.apply(target, arguments)
    return patchIterator(iterator, false)
  },
```

这里有一个知识点需要注意一下，就是集合对象的values方法返回的是一个迭代器对象[Map.values](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Map/values)，  

这个迭代器对象每一次调用`next()`都会返回Map中的下一个值  

，为了让next()得到的值也可以变成`响应式proxy`，我们需要用`patchIterator`劫持`iterator`

```js
// 把iterator劫持成响应式的iterator
function patchIterator (iterator) {
  const originalNext = iterator.next
  iterator.next = () => {
    let { done, value } = originalNext.call(iterator)
    if (!done) {
      value = findReactive(value)
    }
    return { done, value }
  }
  return iterator
}
```

也是经典的函数劫持逻辑，把原有的`{ done, value }`值拿到，把value值定义成`响应式proxy`。  

理解了这个概念以后，剩下相关几个handler也好理解了

#### entries
```js
  entries () {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    const iterator = proto.entries.apply(target, arguments)
    return patchIterator(iterator, true)
  },
```


对应`entries`也有特殊处理，把迭代器传给`patchIterator`的时候需要特殊标记一下这是`entries`，看一下`patchIterator`的改动：

```diff
/** 把iterator劫持成响应式的iterator */ 
function patchIterator (iterator, isEntries) {
  const originalNext = iterator.next
  iterator.next = () => {
    let { done, value } = originalNext.call(iterator)
    if (!done) {
+      if (isEntries) {
+        value[1] = findReactive(value[1])
      } else {
        value = findReactive(value)
      }
    }
    return { done, value }
  }
  return iterator
}
```

entries操作的每一项是一个[key, val]的数组，所以通过下标[1]，只把值定义成响应式，key不需要特殊处理。  

#### Symbol.iterator
```js
  [Symbol.iterator] () {
    const target = proxyToRaw.get(this)
    const proto: any = Reflect.getPrototypeOf(this)
    registerRunningReaction({ target, type: 'iterate' })
    const iterator = proto[Symbol.iterator].apply(target, arguments)
    return patchIterator(iterator, target instanceof Map)
  },
```

这里又是一个比较特殊的处理了，`[Symbol.iterator]`这个内置对象会在`for of`操作的时候被触发，具体可以看本文开头给出的mdn文档。所以也要用上面的迭代器劫持的思路。  

patchIterator的第二个参数，是因为对`Map`数据结构使用`for of`操作的时候，返回的是entries结构，所以也需要进行特殊处理。  

## 总结
本文的代码都在这个仓库里  
https://github.com/sl1673495/proxy-reactive  

函数劫持的思路在各种各样的前端库中都有出现，这几乎是进阶必学的一种技巧了，希望通过本文的学习，你可以理解函数劫持的一些强大的作用。也可以想象Vue3里用proxy来实现响应式能力有多么强。