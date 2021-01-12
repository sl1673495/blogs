---
title: 'Vue3 的响应式和以前有什么区别，Proxy 无敌？'
date: '2020-04-13'
spoiler: ''
---

## 前言
大家都知道，Vue2 里的响应式其实有点像是一个半完全体，对于对象上新增的属性无能为力，对于数组则需要拦截它的原型方法来实现响应式。

举个例子：
```js
let vm = new Vue({
  data() {
    return {
        a: 1
    }
  }
})

// ❌  oops，没反应！
vm.b = 2 
```

```js
let vm = new Vue({
  data() {
    return {
        a: 1
    }
  },
  watch: {
    b() {
      console.log('change !!')
    }
  }
})

// ❌  oops，没反应！
vm.b = 2
```

这种时候，Vue 提供了一个 api：`this.$set`，来使得新增的属性也拥有响应式的效果。

但是对于很多新手来说，很多时候需要小心翼翼的去判断到底什么情况下需要用 `$set`，什么时候可以直接触发响应式。

总之，在 Vue3 中，这些都将成为过去。本篇文章会带你仔细讲解，proxy 到底会给 Vue3 带来怎么样的便利。并且会从源码级别，告诉你这些都是如何实现的。

## 响应式仓库
Vue3 不同于 Vue2 也体现在源码结构上，Vue3 把耦合性比较低的包分散在 `packages` 目录下单独发布成 `npm` 包。 这也是目前很流行的一种大型项目管理方式 `Monorepo`。

其中负责响应式部分的仓库就是 [@vue/rectivity](https://github.com/vuejs/vue-next/tree/master/packages/reactivity)，它不涉及 Vue 的其他的任何部分，是非常非常 「正交」 的一种实现方式。

甚至可以[轻松的集成进 React](https://juejin.im/post/5e70970af265da576429aada)。

这也使得本篇的分析可以更加聚焦的分析这一个仓库，排除其他无关部分。

## 区别
Proxy 和 Object.defineProperty 的使用方法看似很相似，其实 Proxy 是在 「更高维度」 上去拦截属性的修改的，怎么理解呢？

Vue2 中，对于给定的 data，如 `{ count: 1 }`，是需要根据具体的 key 也就是 `count`，去对「修改 data.count 」 和 「读取 data.count」进行拦截，也就是
```js
Object.defineProperty(data, 'count', {
  get() {},
  set() {},
})
```
必须预先知道要拦截的 key 是什么，这也就是为什么 Vue2 里对于对象上的新增属性无能为力。

而 Vue3 所使用的 Proxy，则是这样拦截的：
```js
new Proxy(data, {
  get(key) { },
  set(key, value) { },
})
```
可以看到，根本不需要关心具体的 key，它去拦截的是 「修改 data 上的任意 key」 和 「读取 data 上的任意 key」。

所以，不管是已有的 key  还是新增的 key，都逃不过它的魔爪。

但是 Proxy 更加强大的地方还在于 Proxy 除了 get 和 set，还可以拦截更多的操作符。

## 简单的例子🌰
先写一个 Vue3 响应式的最小案例，本文的相关案例都只会用 `reactive` 和 `effect` 这两个 api。如果你了解过 React 中的 `useEffect`，相信你会对这个概念秒懂，Vue3 的 `effect` 不过就是去掉了手动声明依赖的「进化版」的 `useEffect`。

React 中手动声明 `[data.count]` 这个依赖的步骤被 Vue3 内部直接做掉了，在 `effect` 函数内部读取到 `data.count` 的时候，它就已经被收集作为依赖了。

Vue3：
```js
// 响应式数据
const data = reactive({ 
  count: 1
})

// 观测变化
effect(() => console.log('count changed', data.count))

// 触发 console.log('count changed', data.count) 重新执行
data.count = 2
```

React：
```js
// 数据
const [data, setData] = useState({
  count: 1
})

// 观测变化 需要手动声明依赖
useEffect(() => {
  console.log('count changed', data.count)
}, [data.count])

// 触发 console.log('count changed', data.count) 重新执行
setData(({
  count: 2
}))
```

其实看到这个案例，聪明的你也可以把 `effect` 中的回调函数联想到视图的重新渲染、 watch 的回调函数等等…… 它们是同样基于这套响应式机制的。

而本文的核心目的，就是探究这个基于 Proxy 的 reactive api，到底能强大到什么程度，能监听到用户对于什么程度的修改。

## 先讲讲原理
先最小化的讲解一下响应式的原理，其实就是在 Proxy 第二个参数 `handler` 也就是[陷阱操作符](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy/handler)中，拦截各种取值、赋值操作，依托 `track` 和 `trigger` 两个函数进行依赖收集和派发更新。

`track` 用来在读取时收集依赖。

`trigger` 用来在更新时触发依赖。

### track
```ts
function track(target: object, type: TrackOpTypes, key: unknown) {
  const depsMap = targetMap.get(target);
  // 收集依赖时 通过 key 建立一个 set
  let dep = new Set()
  targetMap.set(ITERATE_KEY, dep)
  // 这个 effect 可以先理解为更新函数 存放在 dep 里
  dep.add(effect)    
}
```

`target` 是原对象。

`type` 是本次收集的类型，也就是收集依赖的时候用来标识是什么类型的操作，比如上文依赖中的类型就是 `get`，这个后续会详细讲解。

`key` 是指本次访问的是数据中的哪个 key，比如上文例子中收集依赖的 key 就是 `count`

首先全局会存在一个 `targetMap`，它用来建立 `数据 -> 依赖` 的映射，它是一个 WeakMap 数据结构。

而 `targetMap` 通过数据 `target`，可以获取到 `depsMap`，它用来存放这个数据对应的所有响应式依赖。

`depsMap` 的每一项则是一个 Set 数据结构，而这个 Set 就存放着对应 key 的更新函数。

是不是有点绕？我们用一个具体的例子来举例吧。

```js
const target = { count: 1}
const data = reactive(target)

const effection = effect(() => {
  console.log(data.count)
})
```

对于这个例子的依赖关系，

1. 全局的 `targetMap` 是：
```js
targetMap: {
  { count: 1 }: dep    
}
```

2. dep 则是
```js
dep: {
  count: Set { effection }
}
```

这样一层层的下去，就可以通过 `target` 找到 `count` 对应的更新函数 `effection` 了。

### trigger
这里是最小化的实现，仅仅为了便于理解原理，实际上要复杂很多，

其实 `type` 的作用很关键，先记住，后面会详细讲。
```js
export function trigger(
  target: object,
  type: TriggerOpTypes,
  key?: unknown,
) {
  // 简化来说 就是通过 key 找到所有更新函数 依次执行
  const dep = targetMap.get(target)
  dep.get(key).forEach(effect => effect())
}
```

## 新增属性

这个上文已经讲了，由于 Proxy 完全不关心具体的 key，所以没问题。
```js
// 响应式数据
const data = reactive({ 
  count: 1
})

// 观测变化
effect(() => console.log('newCount changed', data.newCount))

// ✅ 触发响应
data.newCount = 2
```

数组新增索引：
```js
// 响应式数据
const data = reactive([])

// 观测变化
effect(() => console.log('data[1] changed', data[1]))

// ✅ 触发响应
data[1] = 5
```

数组调用原生方法：
```js
const data = reactive([])
effect(() => console.log('c', data[1]))

// 没反应
data.push(1)

// ✅ 触发响应 因为修改了下标为 1 的值
data.push(2)
```

其实这一个案例就比较有意思了，我们仅仅是在调用 push，但是等到数组的第二项被 push的时候，我们之前关注 `data[1]` 为依赖的回调函数也执行了，这是什么原理呢？写个简单的 Proxy 就知道了。

```js
const raw = []
const arr = new Proxy(raw, {
  get(target, key) {
    console.log('get', key)
    return Reflect.get(target, key)
  },
  set(target, key, value) {
    console.log('set', key)
    return Reflect.set(target, key, value)
  }
})

arr.push(1)
```

在这个案例中，我们只是打印出了对于 `raw` 这个数组上的所有 get、set 操作，并且调用 [Reflect](https://es6.ruanyifeng.com/?search=reflect&x=0&y=0#docs/reflect) 这个 api 原样处理取值和赋值操作后返回。看看 `arr.push(1)` 后控制台打印出了什么？

```
get push
get length
set 0
set length
```

原来一个小小的 push，会触发两对 get 和 set，我们来想象一下流程：
1. 读取 push 方法
2. 读取 arr 原有的 length 属性
3. 对于数组第 0 项赋值
4. 对于 length 属性赋值

这里的重点是第三步，对于第 index 项的赋值，那么下次再 push，可以想象也就是对于第 1 项触发 set 操作。

而我们在例子中读取 `data[1]`，是一定会把对于 `1` 这个下标的依赖收集起来的，这也就清楚的解释了为什么 push 的时候也能精准的触发响应式依赖的执行。

对了，记住这个对于 length 的 set 操作，后面也会用到，很重要。

## 遍历后新增
```js
// 响应式数据
const data = reactive([])

// 观测变化
effect(() => console.log('data map +1', data.map(item => item + 1))

// ✅ 触发响应 打印出 [2]
data.push(1)
```

这个拦截很神奇，但是也很合理，转化成现实里的一个例子来看，

假设我们要根据学生 id 的集合 `ids`， 去请求学生详细信息，那么仅仅是需要这样写即可：

```js
const state = reactive({})
const ids = reactive([1])

effect(async () => {
  state.students = await axios.get('students/batch', ids.map(id => ({ id })))
})

// ✅ 触发响应 
ids.push(2)
```

这样，每次调用各种 api 改变 ids 数组，都会重新发送请求获取最新的学生列表。

如果我在监听函数中调用了 map、forEach 等 api，

说明我关心这个数组的长度变化，那么 push 的时候触发响应是完全正确的。

但是它是如何实现的呢？感觉似乎很复杂啊。

因为 effect 第一次执行的时候， `data` 还是个空数组，怎么会 push 的时候能触发更新呢？

还是用刚刚的小测试，看看 map 的时候会发生什么事情。

```js
const raw = [1, 2]
const arr = new Proxy(raw, {
  get(target, key) {
    console.log('get', key)
    return Reflect.get(target, key)
  },
  set(target, key, value) {
    console.log('set', key)
    return Reflect.set(target, key, value)
  }
})

arr.map(v => v + 1)
```

```js
get map
get length
get constructor
get 0
get 1
```

和 push 的部分有什么相同的？找一下线索，我们发现 map 的时候会触发 `get length`，而在触发更新的时候， Vue3 内部会对 「新增 key」 的操作进行特殊处理，这里是新增了 `0` 这个下标的值，会走到 `trigger`  中这样的一段逻辑里去：

[源码地址](https://github.com/vuejs/vue-next/blob/0764c33d3da8c06d472893a4e451e33394726a42/packages/reactivity/src/effect.ts#L214-L219)
```js
// 简化版
if (isAddOrDelete) {
  add(depsMap.get('length'))
}
```

把之前读取 length 时收集到的依赖拿到，然后触发函数。

这就一目了然了，我们在 `effect` 里 map 操作读取了 length，收集了 length 的依赖。

在新增 key 的时候， 触发 length 收集到的依赖，触发回调函数即可。

对了，对于 `for of` 操作，也一样可行：
```js
// 响应式数据
const data = reactive([])

// 观测变化
effect(() => {
  for (const val of data) {
    console.log('val', val)
  }
})

// ✅ 触发响应 打印出 val 1
data.push(1)
```

可以按我们刚刚的小试验自己跑一下拦截, `for of` 也会触发 `length` 的读取。

`length` 真是个好同志…… 帮了大忙了。

## 遍历后删除或者清空

注意上面的源码里的判断条件是 `isAddOrDelete`，所以删除的时候也是同理，借助了 `length` 上收集到的依赖。

```js
// 简化版
if (isAddOrDelete) {
  add(depsMap.get('length'))
}
```

```js
const arr = reactive([1])
  
effect(() => {
  console.log('arr', arr.map(v => v))
})

// ✅ 触发响应 
arr.length = 0

// ✅ 触发响应 
arr.splice(0, 1)
```

真的是什么操作都能响应，爱了爱了。

## 获取 keys
```js
const obj = reactive({ a: 1 })
  
effect(() => {
  console.log('keys', Reflect.ownKeys(obj))
})

effect(() => {
  console.log('keys', Object.keys(obj))
})

effect(() => {
  for (let key in obj) {
    console.log(key)
  }
})

// ✅ 触发所有响应 
obj.b = 2
```

这几种获取 key 的方式都能成功的拦截，其实这是因为 Vue 内部拦截了 `ownKeys` 操作符。

```js
const ITERATE_KEY = Symbol( 'iterate' );

function ownKeys(target) {
    track(target, "iterate", ITERATE_KEY);
    return Reflect.ownKeys(target);
}
```


`ITERATE_KEY` 就作为一个特殊的标识符，表示这是读取 key 的时候收集到的依赖。它会被作为依赖收集的 key。

那么在触发更新时，其实就对应这段源码：
```js
if (isAddOrDelete) {
    add(depsMap.get(isArray(target) ? 'length' : ITERATE_KEY));
}
```

其实就是我们聊数组的时候，代码简化掉的那部分。判断非数组，则触发 `ITERATE_KEY` 对应的依赖。

小彩蛋：

`Reflect.ownKeys`、 `Object.keys` 和 `for in` 其实行为是不同的，

`Reflect.ownKeys` 可以收集到 `Symbol` 类型的 key，不可枚举的 key。

举例来说:
```js
var a = {
  [Symbol(2)]: 2,
}

Object.defineProperty(a, 'b', {
  enumerable: false,
})

Reflect.ownKeys(a) // [Symbol(2), 'b']
Object.keys(a) // []
```

回看刚刚提到的 `ownKeys` 拦截，

```js
function ownKeys(target) {
    track(target, "iterate", ITERATE_KEY);
    // 这里直接返回 Reflect.ownKeys(target)
    return  Reflect.ownKeys(target);
}
```

内部直接之间返回了 `Reflect.ownKeys(target)`，按理来说这个时候 `Object.keys` 的操作经过了这个拦截，也会按照 `Reflect.ownKeys` 的行为去返回值。

然而最后返回的结果却还是 `Object.keys` 的结果，这是比较神奇的一点。

## 删除对象属性
有了上面 `ownKeys` 的基础，我们再来看看这个例子
```js
const obj = reactive({ a: 1, b: 2})
  
effect(() => {
  console.log(Object.keys(obj))
})

// ✅ 触发响应 
delete obj['b']
```

这也是个神奇的操作，原理在于对于 `deleteProperty` 操作符的拦截：

```js
function deleteProperty(target: object, key: string | symbol): boolean {
  const result = Reflect.deleteProperty(target, key)
  trigger(target, TriggerOpTypes.DELETE, key)
  return result
}
```

这里又用到了 `TriggerOpTypes.DELETE` 的类型，根据上面的经验，一定对它有一些特殊的处理。

其实还是 `trigger` 中的那段逻辑：
```js
const isAddOrDelete = type === TriggerOpTypes.ADD || type === TriggerOpTypes.DELETE
if (isAddOrDelete) {
  add(depsMap.get(isArray(target) ? 'length' : ITERATE_KEY))
}
```

这里的 target 不是数组，所以还是会去触发 `ITERATE_KEY` 收集的依赖，也就是上面例子中刚提到的对于 key 的读取收集到的依赖。

## 判断属性是否存在
```js
const obj = reactive({})

effect(() => {
  console.log('has', Reflect.has(obj, 'a'))
})

effect(() => {
  console.log('has', 'a' in obj)
})

// ✅ 触发两次响应 
obj.a = 1
```

这个就很简单了，就是利用了 `has` 操作符的拦截。

```js
function has(target, key) {
  const result = Reflect.has(target, key);
  track(target, "has", key);
  return result;
}
```

## Map 和 Set
其实 Vue3 对于这两种数据类型也是完全支持响应式的，对于它们的原型方法也都做了完善的拦截，限于篇幅原因本文不再赘述。

说实话 Vue3 的响应式部分代码逻辑分支还是有点过多，对于代码理解不是很友好，因为它还会涉及到 `readonly` 等只读化的操作，如果看完这篇文章你对于 Vue3 的响应式原理非常感兴趣的话，建议从简化版的库入手去读源码。

这里我推荐 [observer-util](https://github.com/nx-js/observer-util)，我解读过这个库的源码，和 Vue3 的实现原理基本上是一模一样！但是简单了很多。麻雀虽小，五脏俱全。里面的注释也很齐全。

当然，如果你的英文不是很熟练，也可以看我精心用 TypeScript + 中文注释基于 `observer-util` 重写的这套代码：
[typescript-proxy-reactive](https://github.com/sl1673495/typescript-proxy-reactive)

对于这个库的解读，可以看我之前的两篇文章：

[带你彻底搞懂Vue3的Proxy响应式原理！TypeScript从零实现基于Proxy的响应式库。](https://juejin.im/post/5e21196fe51d454d523be084)

[带你彻底搞懂Vue3的Proxy响应式原理！基于函数劫持实现Map和Set的响应式](https://juejin.im/post/5e23b20f51882510073eb571)

在第二篇文章里，你也可以对于 Map 和 Set 可以做什么拦截操作，获得源码级别的理解。

## 总结
Vue3 的 Proxy 真的很强大，把 Vue2 里我认为心智负担很大的一部分给解决掉了。（在我刚上手 Vue 的时候，我是真的不知道什么情况下该用 `$set`），它的 `composition-api` 又可以完美对标 `React Hook`，并且得益于响应式系统的强大，在某些方面是优胜于它的。[精读《Vue3.0 Function API》](https://juejin.im/post/5d1955e3e51d4556d86c7b09)

希望这篇文章能在 Vue3 正式到来之前，提前带你熟悉 Vue3 的一些新特性。

## 扩展阅读
Proxy 的拦截器里有个 receiver 参数，在本文中为了简化没有体现出来，它是用来做什么的？国内的网站比较少能找到这个资料：
```js
new Proxy(raw, {
  get(target, key, receiver) {
    return Reflect.get(target, key, receiver)
  }
})
```
可以看 StackOverflow 上的问答：[what-is-a-receiver-in-javascript](https://stackoverflow.com/questions/37563495/what-is-a-receiver-in-javascript/37565299#37565299)

也可以看我的总结
[Proxy 和 Reflect 中的 receiver 到底是什么？](https://github.com/sl1673495/notes/issues/52)

## 求点赞
如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我持续进行创作的动力，让我知道你喜欢看我的文章吧~

## ❤️感谢大家

关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)