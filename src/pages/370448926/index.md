---
title: 'Vue源码学习 响应式数据'
date: '2018-10-16'
spoiler: ''
---

本文内容摘录自vue-design项目。

从initState开始
```js
if (opts.data) {
  initData(vm)
} else {
  observe(vm._data = {}, true /* asRootData */)
}
```


我们找到 initData 函数，该函数与 initState 函数定义在同一个文件中，即 core/instance/state.js 文件，initData 函数的一开始是这样一段代码：
```js
let data = vm.$options.data
data = vm._data = typeof data === 'function'
  ? getData(data, vm)
  : data || {}
```
通过getData拿到我们定义的data方法里的对象后，

```js
else if (!isReserved(key)) {
  proxy(vm, `_data`, key)
}
```
!isReserved(key)，该条件的意思是判断定义在 data 中的 key 是否是保留键，
Vue 是不会代理那些键名以 $ 或 _ 开头的字段的，因为 Vue 自身的属性和方法都是以 $ 或 _ 开头的，所以这么做是为了避免与 Vue 自身的属性和方法相冲突。

proxy函数：
```js
export function proxy (target: Object, sourceKey: string, key: string) {
  sharedPropertyDefinition.get = function proxyGetter () {
    return this[sourceKey][key]
  }
  sharedPropertyDefinition.set = function proxySetter (val) {
    this[sourceKey][key] = val
  }
  Object.defineProperty(target, key, sharedPropertyDefinition)
}
```
其实就是把我们的this.xxx的get和set代理到this._data.xxx上去，这也是为什么我们写在data里的数据可以直接通过this访问和修改。（Vue2.0为了兼容性还是不敢用原生Proxy啊~）

接下来来到了一句很关键的代码
```js
// observe data
observe(data, true /* asRootData */)
```

调用 observe 函数将 data 数据对象转换成响应式的，可以说这句代码才是响应系统的开始，不过在讲解 observe 函数之前我们有必要总结一下 initData 函数所做的事情，通过前面的分析可知 initData 函数主要完成如下工作：

根据 vm.$options.data 选项获取真正想要的数据（注意：此时 vm.$options.data 是函数）
校验得到的数据是否是一个纯对象
检查数据对象 data 上的键是否与 props 对象上的键冲突
检查 methods 对象上的键是否与 data 对象上的键冲突
在 Vue 实例对象上添加代理访问数据对象的同名属性
最后调用 observe 函数开启响应式之路

```js
export function observe (value: any, asRootData: ?boolean): Observer | void {
  if (!isObject(value) || value instanceof VNode) {
    return
  }
  let ob: Observer | void
  if (hasOwn(value, '__ob__') && value.__ob__ instanceof Observer) {
    ob = value.__ob__
  } else if (
    shouldObserve &&
    !isServerRendering() &&
    (Array.isArray(value) || isPlainObject(value)) &&
    Object.isExtensible(value) &&
    !value._isVue
  ) {
    ob = new Observer(value)
  }
  if (asRootData && ob) {
    ob.vmCount++
  }
  return ob
}
```
函数开头首先判断如果value不是对象 或者是VNode实例 就什么也不做
接下来 如果value上已经有__ob__这个属性，就直接return value.__ob__，
这其实能看出 调用new Observer(value)最终会在value上定义一个__ob__属性。

在else if中 满足了几个条件进入的才是主流程，
先看这几个条件

- 第一个条件是 shouldObserve 必须为 true，
shouldObserve 变量也定义在 core/observer/index.js 文件内，如下：
```js
/**
 * In some cases we may want to disable observation inside a component's
 * update computation.
 */
export let shouldObserve: boolean = true

export function toggleObserving (value: boolean) {
  shouldObserve = value
}
```
变量的初始值为 true，在 shouldObserve 变量的下面定义了 toggleObserving 函数，该函数接收一个布尔值参数，用来切换 shouldObserve 变量的真假值，我们可以把 shouldObserve 想象成一个开关，为 true 时说明打开了开关，此时可以对数据进行观测，为 false 时可以理解为关闭了开关，此时数据对象将不会被观测。为什么这么设计呢？原因是有一些场景下确实需要这个开关从而达到一些目的，后面我们遇到的时候再仔细来说。

- 第二个条件是 !isServerRendering() 必须为真，我们讨论的环境非服务端渲染 肯定满足。

- 第三个条件是 (Array.isArray(value) || isPlainObject(value)) 必须为真
这个条件很好理解，只有当数据对象是数组或纯对象的时候，才有必要对其进行观测。

- 第四个条件是 Object.isExtensible(value) 必须为真
也就是说要被观测的数据对象必须是可扩展的。一个普通的对象默认就是可扩展的，以下三个方法都可以使得一个对象变得不可扩展：Object.preventExtensions()、Object.freeze() 以及 Object.seal()

- 第五个条件是 !value._isVue 必须为真
我们知道 Vue 实例对象拥有 _isVue 属性，所以这个条件用来避免 Vue 实例对象被观测。

当一个对象满足了以上五个条件时，就会执行 else...if 语句块的代码，即创建一个 Observer 实例：

```js
ob = new Observer(value)
```

#### Observer 构造函数
其实真正将数据对象转换成响应式数据的是 Observer 函数，它是一个构造函数，同样定义在 core/observer/index.js 文件下，如下是简化后的代码：
```js
export class Observer {
  value: any;
  dep: Dep;
  vmCount: number; // number of vms that has this object as root $data

  constructor (value: any) {
    // 省略...
  }

  walk (obj: Object) {
    // 省略...
  }
  
  observeArray (items: Array<any>) {
    // 省略...
  }
}
```

以清晰的看到 Observer 类的实例对象将拥有三个实例属性，分别是 value、dep 和 vmCount 以及两个实例方法 walk 和 observeArray。Observer 类的构造函数接收一个参数，即数据对象。下面我们就从 constructor 方法开始，研究实例化一个 Observer 类时都做了哪些事情。


如下是 constructor 方法的全部代码：
```js
constructor (value: any) {
  this.value = value
  this.dep = new Dep()
  this.vmCount = 0
  def(value, '__ob__', this)
  if (Array.isArray(value)) {
    const augment = hasProto
      ? protoAugment
      : copyAugment
    augment(value, arrayMethods, arrayKeys)
    this.observeArray(value)
  } else {
    this.walk(value)
  }
}
```

constructor 方法的参数就是在实例化 Observer 实例时传递的参数，即数据对象本身，可以发现，实例对象的 value 属性引用了数据对象：
```js
this.value = value
```

实例对象的 dep 属性，保存了一个新创建的 Dep 实例对象：
```js
this.dep = new Dep()
```

那么这里的 Dep 是什么呢？它就是一个收集依赖的“筐”。但这个“筐”并不属于某一个字段，后面我们会发现，这个筐是属于某一个对象或数组的。

实例对象的 vmCount 属性被设置为 0：this.vmCount = 0。

初始化完成三个实例属性之后，使用 def 函数，为数据对象定义了一个 __ob__ 属性，这个属性的值就是当前 Observer 实例对象。其中 def 函数其实就是 Object.defineProperty 函数的简单封装，之所以这里使用 def 函数定义 __ob__ 属性是因为这样可以定义不可枚举的属性，这样后面遍历数据对象的时候就能够防止遍历到 __ob__ 属性。

假设我们的数据对象如下：
```js
const data = {
  a: 1
}
```
那么经过 def 函数处理之后，data 对象应该变成如下这个样子：
```js
const data = {
  a: 1,
  // __ob__ 是不可枚举的属性
  __ob__: {
    value: data, // value 属性指向 data 数据对象本身，这是一个循环引用
    dep: dep实例对象, // new Dep()
    vmCount: 0
  }
}
```

#### 响应式数据之纯对象的处理
```js
if (Array.isArray(value)) {
  const augment = hasProto
    ? protoAugment
    : copyAugment
  augment(value, arrayMethods, arrayKeys)
  this.observeArray(value)
} else {
  this.walk(value)
}
```
该判断用来区分数据对象到底是数组还是一个纯对象，因为对于数组和纯对象的处理方式是不同的，为了更好地理解我们先看数据对象是一个纯对象的情况，这个时候代码会走 else 分支，即执行 this.walk(value) 函数，我们知道这个函数实例对象方法，找到这个方法：
```js
walk (obj: Object) {
  const keys = Object.keys(obj)
  for (let i = 0; i < keys.length; i++) {
    defineReactive(obj, keys[i])
  }
}
```
walk 方法很简单，首先使用 Object.keys(obj) 获取对象属性所有可枚举的属性，然后使用 for 循环遍历这些属性，同时为每个属性调用了 defineReactive 函数。

#### defineReactive 函数

那我们就看一看 defineReactive 函数都做了什么，该函数也定义在 core/observer/index.js 文件，内容如下：
```js
export function defineReactive (
  obj: Object,
  key: string,
  val: any,
  customSetter?: ?Function,
  shallow?: boolean
) {
  const dep = new Dep()

  const property = Object.getOwnPropertyDescriptor(obj, key)
  if (property && property.configurable === false) {
    return
  }

  // cater for pre-defined getter/setters
  const getter = property && property.get
  const setter = property && property.set
  if ((!getter || setter) && arguments.length === 2) {
    val = obj[key]
  }

  let childOb = !shallow && observe(val)
  Object.defineProperty(obj, key, {
    enumerable: true,
    configurable: true,
    get: function reactiveGetter () {
      const value = getter ? getter.call(obj) : val
      if (Dep.target) {
        // 这里闭包引用了上面的 dep 常量
        dep.depend()
        // 省略...
      }
      return value
    },
    set: function reactiveSetter (newVal) {
      // 省略...

      // 这里闭包引用了上面的 dep 常量
      dep.notify()
    }
  })
}
```

首先可以看到 方法的开头又有一个dep筐子，这个筐是为对象的每个key建立的一个依赖收集筐，
这个筐被get和set方法闭包引用，

这里大家要明确一件事情，即 **每一个数据字段都通过闭包引用着属于自己的 dep 常量**。

```js
let childOb = !shallow && observe(val)
```
如果函数的参数shallow字段为假，则递归观测子对象（val是否是对象这个判断observe函数会做）。

#### 被观测后的数据对象的样子

现在我们需要明确一件事情，那就是一个数据对象经过了 observe 函数处理之后变成了什么样子，假设我们有如下数据对象：
```js
const data = {
  a: {
    b: 1
  }
}

observe(data)
```

数据对象 data 拥有一个叫做 a 的属性，且属性 a 的值是另外一个对象，该对象拥有一个叫做 b 的属性。那么经过 observe 处理之后， data 和 data.a 这两个对象都被定义了 __ob__ 属性，并且访问器属性 a 和 b 的 setter/getter 都通过闭包引用着属于自己的 Dep 实例对象和 childOb 对象：

```
const data = {
  // 属性 a 通过 setter/getter 通过闭包引用着 dep 和 childOb
  a: {
    // 属性 b 通过 setter/getter 通过闭包引用着 dep 和 childOb
    b: 1
    __ob__: {a, dep, vmCount}
  }
  __ob__: {data, dep, vmCount}
}
```

需要注意的是，属性 a 闭包引用的 childOb 实际上就是 data.a.__ob__。而属性 b 闭包引用的 childOb 是 undefined，因为属性 b 是基本类型值，并不是对象也不是数组。

#### 在 get 函数中如何收集依赖
我们回过头来继续查看 defineReactive 函数的代码，接下来是 defineReactive 函数的关键代码，即使用 Object.defineProperty 函数定义访问器属性：
```js
Object.defineProperty(obj, key, {
  enumerable: true,
  configurable: true,
  get: function reactiveGetter () {
    // 省略...
  },
  set: function reactiveSetter (newVal) {
    // 省略...
})
```

get 函数如下：
```
get: function reactiveGetter () {
  const value = getter ? getter.call(obj) : val
  if (Dep.target) {
    dep.depend()
    if (childOb) {
      childOb.dep.depend()
      if (Array.isArray(value)) {
        dependArray(value)
      }
    }
  }
  return value
}
```
首先判断 Dep.target 是否存在，那么 Dep.target 是什么呢？其实 Dep.target 与我们在中保存的值就是要被收集的依赖(观察者)。所以如果 Dep.target 存在的话说明有依赖需要被收集，这个时候才需要执行 if 语句块内的代码，如果 Dep.target 不存在就意味着没有需要被收集的依赖，所以当然就不需要执行 if 语句块内的代码了。

在 if 语句块内第一句执行的代码就是：dep.depend()，执行 dep 对象的 depend 方法将依赖收集到 dep 这个“筐”中，这里的 dep 对象就是属性的 getter/setter 通过闭包引用的“筐”。

接着又判断了 childOb 是否存在，如果存在那么就执行 childOb.dep.depend()，这段代码是什么意思呢？要想搞清楚这段代码的作用，你需要知道 childOb 是什么，前面我们分析过，假设有如下数据对象：
```
const data = {
  a: {
    b: 1
  }
}
```

该数据对象经过观测处理之后，将被添加 __ob__ 属性，如下：
```js
const data = {
  a: {
    b: 1,
    __ob__: {value, dep, vmCount}
  },
  __ob__: {value, dep, vmCount}
}
```

对于属性 a 来讲，访问器属性 a 的 setter/getter 通过闭包引用了一个 Dep 实例对象，即属性 a 用来收集依赖的“筐”。除此之外访问器属性 a 的 setter/getter 还通过闭包引用着 childOb，且 childOb === data.a.__ob__ 所以 childOb.dep === data.a.__ob__.dep。也就是说 childOb.dep.depend() 这句话的执行说明除了要将依赖收集到属性 a 自己的“筐”里之外，还要将同样的依赖收集到 data.a.__ob__.dep 这里”筐“里，为什么要将同样的依赖分别收集到这两个不同的”筐“里呢？其实答案就在于这两个”筐“里收集的依赖的触发时机是不同的，即作用不同，两个”筐“如下：

第一个”筐“是 dep
第二个”筐“是 childOb.dep
第一个”筐“里收集的依赖的触发时机是当属性值被修改时触发，即在 set 函数中触发：dep.notify()。而第二个”筐“里收集的依赖的触发时机是在使用 $set 或 Vue.set 给数据对象添加新属性时触发，我们知道由于 js 语言的限制，在没有 Proxy 之前 Vue 没办法拦截到给对象添加属性的操作。所以 Vue 才提供了 $set 和 Vue.set 等方法让我们有能力给对象添加新属性的同时触发依赖，那么触发依赖是怎么做到的呢？就是通过数据对象的 __ob__ 属性做到的。因为 __ob__.dep 这个”筐“里收集了与 dep 这个”筐“同样的依赖。假设 Vue.set 函数代码如下：

```
Vue.set = function (obj, key, val) {
  defineReactive(obj, key, val)
  obj.__ob__.dep.notify()
}
```
如上代码所示，当我们使用上面的代码给 data.a 对象添加新的属性：
```
Vue.set(data.a, 'c', 1)
```

上面的代码之所以能够触发依赖，就是因为 Vue.set 函数中触发了收集在 data.a.__ob__.dep 这个”筐“中的依赖：
```
Vue.set = function (obj, key, val) {
  defineReactive(obj, key, val)
  obj.__ob__.dep.notify() // 相当于 data.a.__ob__.dep.notify()
}

Vue.set(data.a, 'c', 1)
```

所以 __ob__ 属性以及 __ob__.dep 的主要作用是为了添加、删除属性时有能力触发依赖，而这就是 Vue.set 或 Vue.delete 的原理。

在 childOb.dep.depend() 这句话的下面还有一个 if 条件语句，如下：
```js
if (Array.isArray(value)) {
  dependArray(value)
}
```
如果读取的属性值是数组，那么需要调用 dependArray 函数逐个触发数组每个元素的依赖收集，为什么这么做呢？那是因为 Observer 类在定义响应式属性时对于纯对象和数组的处理方式是不同，对于上面这段 if 语句的目的等到我们讲解到对于数组的处理时，会详细说明。

#### 在 set 函数中如何触发依赖

在 get 函数中收集了依赖之后，接下来我们就要看一下在 set 函数中是如何触发依赖的，即当属性被修改的时候如何触发依赖。set 函数如下：
```js
set: function reactiveSetter (newVal) {
  const value = getter ? getter.call(obj) : val
  /* eslint-disable no-self-compare */
  if (newVal === value || (newVal !== newVal && value !== value)) {
    return
  }
  /* eslint-enable no-self-compare */
  if (process.env.NODE_ENV !== 'production' && customSetter) {
    customSetter()
  }
  if (setter) {
    setter.call(obj, newVal)
  } else {
    val = newVal
  }
  childOb = !shallow && observe(newVal)
  dep.notify()
}
```

我们知道 get 函数主要完成了两部分重要的工作，一个是返回正确的属性值，另一个是收集依赖。与 get 函数类似， set 函数也要完成两个重要的事情，第一正确地为属性设置新值，第二是能够触发相应的依赖。

首先 set 函数接收一个参数 newVal，即该属性被设置的新值。在函数体内，先执行了这样一句话：
```js
const value = getter ? getter.call(obj) : val
```

这句话与 get 函数体的第一句话相同，即取得属性原有的值，为什么要取得属性原来的值呢？很简单，因为我们需要拿到原有的值与新的值作比较，并且只有在原有值与新设置的值不相等的情况下才需要触发依赖和重新设置属性值，否则意味着属性值并没有改变，当然不需要做额外的处理。如下代码：
```js
/* eslint-disable no-self-compare */
if (newVal === value || (newVal !== newVal && value !== value)) {
  return
}
```

这里就对比了新值和旧值：newVal === value。如果新旧值全等，那么函数直接 return，不做任何处理。但是除了对比新旧值之外，我们还注意到，另外一个条件：
```js
(newVal !== newVal && value !== value)
```
如果满足该条件，同样不做任何处理，那么这个条件什么意思呢？newVal !== newVal 说明新值与新值自身都不全等，同时旧值与旧值自身也不全等，大家想一下在 js 中什么时候会出现一个值与自身都不全等的？答案就是 NaN：
```js
NaN === NaN // false
```

所以我们现在重新分析一下这个条件，首先 value !== value 成立那说明该属性的原有值就是 NaN，同时 newVal !== newVal 说明为该属性设置的新值也是 NaN，所以这个时候新旧值都是 NaN，等价于属性的值没有变化，所以自然不需要做额外的处理了，set 函数直接 return 。

再往下又是一个 if 语句块：

```js
if (setter) {
  setter.call(obj, newVal)
} else {
  val = newVal
}
```
上面这段代码的意图很明显，即正确地设置属性值，首先判断 setter 是否存在，我们知道 setter 常量存储的是属性原有的 set 函数。即如果属性原来拥有自身的 set 函数，那么应该继续使用该函数来设置属性的值，从而保证属性原有的设置操作不受影响。如果属性原本就没有 set 函数，那么就设置 val 的值：val = newVal。

接下来就是 set 函数的最后两句代码，如下：
childOb = !shallow && observe(newVal)
dep.notify()

我们知道，由于属性被设置了新的值，那么假如我们为属性设置的新值是一个数组或者纯对象，那么该数组或纯对象是未被观测的，所以需要对新值进行观测，这就是第一句代码的作用，同时使用新的观测对象重写 childOb 的值。当然了，这些操作都是在 !shallow 为真的情况下，即需要深度观测的时候才会执行。最后是时候触发依赖了，我们知道 dep 是属性用来收集依赖的”筐“，现在我们需要把”筐“里的依赖都执行一下，而这就是 dep.notify() 的作用。

至此 set 函数我们就讲解完毕了。

#### 响应式数据之数组的处理
以上就是响应式数据对于纯对象的处理方式，接下来我们将会对数组展开详细的讨论。回到 Observer 类的 constructor 函数，找到如下代码：
```js
if (Array.isArray(value)) {
  const augment = hasProto
    ? protoAugment
    : copyAugment
  augment(value, arrayMethods, arrayKeys)
  this.observeArray(value)
} else {
  this.walk(value)
}
```

在 if 条件语句中，使用 Array.isArray 函数检测被观测的值 value 是否是数组，如果是数组则会执行 if 语句块内的代码，从而实现对数组的观测。处理数组的方式与纯对象不同，我们知道数组是一个特殊的数据结构，它有很多实例方法，并且有些方法会改变数组自身的值，我们称其为变异方法，这些方法有：push、pop、shift、unshift、splice、sort 以及 reverse 等。这个时候我们就要考虑一件事，即当用户调用这些变异方法改变数组时需要触发依赖。换句话说我们需要知道开发者何时调用了这些变异方法，只有这样我们才有可能在这些方法被调用时做出反应。

#### 拦截数组变异方法的思路
缓存Array.prototype.push这个函数 然后定义newPush = function() {
    ...doSomething(),
    调用缓存的push函数...
}
这其实是一个很通用也很常见的技巧，而 Vue 正是通过这个技巧实现了对数据变异方法的拦截，即保持数组变异方法原有功能不变的前提下对其进行功能扩展。

```
/*
 * not type checking this file because flow doesn't play well with
 * dynamically accessing methods on Array prototype
 */

import { def } from '../util/index'

const arrayProto = Array.prototype
export const arrayMethods = Object.create(arrayProto)

const methodsToPatch = [
  'push',
  'pop',
  'shift',
  'unshift',
  'splice',
  'sort',
  'reverse'
]

/**
 * Intercept mutating methods and emit events
 */
methodsToPatch.forEach(function (method) {
  // cache original method
  const original = arrayProto[method]
  def(arrayMethods, method, function mutator (...args) {
    const result = original.apply(this, args)
    const ob = this.__ob__
    let inserted
    switch (method) {
      case 'push':
      case 'unshift':
        inserted = args
        break
      case 'splice':
        inserted = args.slice(2)
        break
    }
    if (inserted) ob.observeArray(inserted)
    // notify change
    ob.dep.notify()
    return result
  })
})
```

methodsToPatch 常量是一个数组，包含了所有需要拦截的数组变异方法的名字。再往下是一个 forEach 循环，用来遍历 methodsToPatch 数组。该循环的主要目的就是使用 def 函数在 arrayMethods 对象上定义与数组变异方法同名的函数，从而做到拦截的目的，如下是简化后的代码：
```js
methodsToPatch.forEach(function (method) {
  // cache original method
  const original = arrayProto[method]
  def(arrayMethods, method, function mutator (...args) {
    const result = original.apply(this, args)
    const ob = this.__ob__

    // 省略中间部分...

    // notify change
    ob.dep.notify()
    return result
  })
})
```

上面的代码中，首先缓存了数组原本的变异方法：
```js
const original = arrayProto[method]
```
然后使用 def 函数在 arrayMethods 上定义与数组变异方法同名的函数，在函数体内优先调用了缓存下来的数组变异方法：
```js
const result = original.apply(this, args)
```
并将数组原本变异方法的返回值赋值给 result 常量，并且我们发现函数体的最后一行代码将 result 作为返回值返回。这就保证了拦截函数的功能与数组原本变异方法的功能是一致的。

关键要注意这两句代码：
```js
const ob = this.__ob__

// 省略中间部分...

// notify change
ob.dep.notify()
```

定义了 ob 常量，它是 this.__ob__ 的引用，其中 this 其实就是数组实例本身，我们知道无论是数组还是对象，都将会被定义一个 __ob__ 属性，并且 __ob__.dep 中收集了所有该对象(或数组)的依赖(观察者)。所以上面两句代码的目的其实很简单，当调用数组变异方法时，必然修改了数组，所以这个时候需要将该数组的所有依赖(观察者)全部拿出来执行，即：ob.dep.notify()。

注意上面的讲解中我们省略了中间部分，那么这部分代码的作用是什么呢？如下：
```js
def(arrayMethods, method, function mutator (...args) {
  // 省略...
  let inserted
  switch (method) {
    case 'push':
    case 'unshift':
      inserted = args
      break
    case 'splice':
      inserted = args.slice(2)
      break
  }
  if (inserted) ob.observeArray(inserted)
  // 省略...
})
```

首先我们需要思考一下数组变异方法对数组的影响是什么？无非是 增加元素、删除元素 以及 变更元素顺序。有的同学可能会说还有 替换元素，实际上替换可以理解为删除和增加的复合操作。那么在这些变更中，我们需要重点关注的是 增加元素 的操作，即 push、unshift 和 splice，这三个变异方法都可以为数组添加新的元素，那么为什么要重点关注呢？原因很简单，因为新增加的元素是非响应式的，所以我们需要获取到这些新元素，并将其变为响应式数据才行，而这就是上面代码的目的。下面我们看一下具体实现，首先定义了 inserted 变量，这个变量用来保存那些被新添加进来的数组元素：let inserted。接着是一个 switch 语句，在 switch 语句中，当遇到 push 和 unshift 操作时，那么新增的元素实际上就是传递给这两个方法的参数，所以可以直接将 inserted 的值设置为 args：inserted = args。当遇到 splice 操作时，我们知道 splice 函数从第三个参数开始到最后一个参数都是数组的新增元素，所以直接使用 args.slice(2) 作为 inserted 的值即可。最后 inserted 变量中所保存的就是新增的数组元素，我们只需要调用 observeArray 函数对其进行观测即可：
```js
if (inserted) ob.observeArray(inserted)
```



