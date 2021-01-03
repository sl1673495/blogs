# [通过实现一个最精简的响应式系统来学习Vue的data、computed、watch。](https://github.com/sl1673495/blogs/issues/20)

## 导读
记得初学Vue源码的时候，在`defineReactive`、`Observer`、`Dep`、`Watcher`等等内部设计源码之间跳来跳去，发现再也绕不出来了。Vue发展了很久，很多fix和feature的增加让内部源码越来越庞大，太多的边界情况和优化设计掩盖了原本精简的代码设计，让新手阅读源码变得越来越困难，但是面试的时候，Vue的响应式原理几乎成了Vue技术栈的公司面试中高级前端必问的点之一。

这篇文章通过自己实现一个响应式系统，尽量还原和Vue内部源码同样结构，但是剔除掉和渲染、优化等等相关的代码，来最低成本的学习Vue的响应式原理。

## 预览
源码地址：  
https://github.com/sl1673495/vue-reactive  

预览地址：  
https://sl1673495.github.io/vue-reactive/  


## reactive
Vue最常用的就是响应式的data了，通过在vue中定义 
```js
new Vue({
    data() {
        return {
            msg: 'Hello World'
        }
    }
})
```
在data发生改变的时候，视图也会更新，在这篇文章里我把对data部分的处理单独提取成一个api：`reactive`，下面来一起实现这个api。

要实现的效果：
```js
const data = reactive({
  msg: 'Hello World',
})

new Watcher(() => {
  document.getElementById('app').innerHTML = `msg is ${data.msg}`
})
```

在data.msg发生改变的时候，我们需要这个app节点的innerHTML同步更新，这里新增加了一个概念`Watcher`，这也是Vue源码内部的一个设计，想要实现响应式的系统，这个`Watcher`是必不可缺的。

在实现这两个api之前，我们先来理清他们之间的关系，reactive这个api定义了一个响应式的数据，其实大家都知道响应式的数据就是在它的属性某个属性（比如例中的`data.msg`）被读取的时候，记录下来这时候是谁在读取他，读取他的这个函数肯定依赖它。
在本例中，下面这段函数，因为读取了`data.msg`并且展示在页面上，所以可以说这段`渲染函数`依赖了`data.msg`。
```js
document.getElementById('app').innerHTML = `msg is ${data.msg}`
```

这也就解释清了，为什么我们需要用`new Watcher`来传入这段渲染函数，我们已经可以分析出来`Watcher`内部是需要记录下来这段渲染函数，并且在帮我们执行这段渲染函数的时候需要开启收集依赖的一个开关。  

在js引擎执行`渲染函数`的途中，突然读到了`data.msg`，`data`已经被定义成了响应式数据，读取`data.msg`时所触发的get函数已经被我们劫持，这个get函数中我们去记录下`data.msg`被这个`渲染函数`所依赖，然后再返回`data.msg`的值。

这样下次`data.msg`发生变化的时候，`Watcher`内部所做的一些逻辑就会通知到`渲染函数`去重新执行。这不就是响应式的原理嘛。

下面开始实现代码
```js
import Dep from './dep'
import { isObject } from '../utils'

// 将对象定义为响应式
export default function reactive(data) {
  if (isObject(data)) {
    Object.keys(data).forEach(key => {
      defineReactive(data, key)
    })
  }
  return data
}

function defineReactive(data, key) {
  let val = data[key]
  // 收集依赖
  const dep = new Dep()

  Object.defineProperty(data, key, {
    get() {
      dep.depend()
      return val
    },
    set(newVal) {
      val = newVal
      dep.notify()
    }
  })

  if (isObject(val)) {
    reactive(val)
  }
}

```

代码很简单，就是去遍历data的key，在`defineReactive`函数中对每个key进行get和set的劫持，`Dep`是一个新的概念，它主要用来做上面所说的`dep.depend()`去收集当前正在运行的渲染函数和`dep.notify()` 触发渲染函数重新执行。

可以把dep看成一个收集依赖的小筐，每当运行渲染函数读取到data的某个key的时候，就把这个渲染函数丢到这个key自己的小筐中，在这个key的值发生改变的时候，去key的筐中找到所有的渲染函数再执行一遍。

## Dep
```js
export default class Dep {
  constructor() {
    this.deps = new Set()
  }

  depend() {
    if (Dep.target) {
      this.deps.add(Dep.target)
    }
  }

  notify() {
    this.deps.forEach(watcher => watcher.update())
  }
}

// 正在运行的watcher
Dep.target = null
```

这个类很简单，利用Set去做存储，在depend的时候把Dep.target加入到deps集合里，在notify的时候遍历deps，触发每个watcher的update。  

没错Dep.target这个概念也是Vue中所引入的，它是一个挂在Dep类上的全局变量，js是单线程运行的，所以在渲染函数如：
```js
document.getElementById('app').innerHTML = `msg is ${data.msg}`
```
运行之前，先把全局的Dep.target设置为`存储了这个渲染函数的watcher`，也就是：
```js
new Watcher(() => {
  document.getElementById('app').innerHTML = `msg is ${data.msg}`
})
```
这样在运行途中data.msg就可以通过Dep.target找到当前是哪个渲染函数的`watcher`正在运行，这样也就可以把自身对应的依赖所收集起来了。  

这里划重点：Dep.target一定是一个`Watcher`的实例。  

又因为渲染函数可以是嵌套运行的，比如在Vue中每个`组件`都会有自己用来存放渲染函数的一个watcher，那么在下面这种组件嵌套组件的情况下：
```
// Parent组件

<template>
  <div>
    <Son组件 />
  </div>
</template>
```

watcher的运行路径就是： 开始 -> ParentWatcher -> SonWatcher -> ParentWatcher -> 结束。

是不是特别像函数运行中的入栈出栈，没错，Vue内部就是用了栈的数据结构来记录watcher的运行轨迹。
```js
// watcher栈
const targetStack = []

// 将上一个watcher推到栈里，更新Dep.target为传入的_target变量。
export function pushTarget(_target) {
  if (Dep.target) targetStack.push(Dep.target)
  Dep.target = _target
}

// 取回上一个watcher作为Dep.target，并且栈里要弹出上一个watcher。
export function popTarget() {
  Dep.target = targetStack.pop()
}
```

有了这些辅助的工具，就可以来看看`Watcher`的具体实现了

```js
import Dep, { pushTarget, popTarget } from './dep'

export default class Watcher {
  constructor(getter) {
    this.getter = getter
    this.get()
  }

  get() {
    pushTarget(this)
    this.value = this.getter()
    popTarget()
    return this.value
  }

  update() {
     this.get()
  }
}

```

回顾一下开头示例中Watcher的使用。
```js
const data = reactive({
  msg: 'Hello World',
})

new Watcher(() => {
  document.getElementById('app').innerHTML = `msg is ${data.msg}`
})
```

传入的getter函数就是
```js
() => {
  document.getElementById('app').innerHTML = `msg is ${data.msg}`
}
```

在构造函数中，记录下getter函数，并且执行了一遍get
```js
  get() {
    pushTarget(this)
    this.value = this.getter()
    popTarget()
    return this.value
  }
```

在这个函数中,`this`就是这个watcher实例，在执行get的开头先把这个存储了渲染函数的watcher设置为当前的Dep.target，然后执行this.getter()也就是渲染函数  

在执行渲染函数的途中读取到了`data.msg`，就触发了`defineReactive`函数中劫持的get:
```js
Object.defineProperty(data, key, {
    get() {
      dep.depend()
      return val
    }
  })
```

这时候的`dep.depend`函数：
```js
  depend() {
    if (Dep.target) {
      this.deps.add(Dep.target)
    }
  }

```
所收集到的`Dep.target`，就是在get函数开头中`pushTarget(this)`所收集的
```js
new Watcher(() => {
  document.getElementById('app').innerHTML = `msg is ${data.msg}`
})
```
这个watcher实例了。

此时我们假如执行了这样一段赋值代码：
```js
data.msg = 'ssh'
```
就会运行到劫持的set函数里：
```js
  Object.defineProperty(data, key, {
    set(newVal) {
      val = newVal
      dep.notify()
    }
  })
```

此时在控制台中打印出dep这个变量，它内部的deps属性果然存储了一个Watcher的实例。
![dep](https://user-gold-cdn.xitu.io/2019/10/28/16e103b795abacf6?w=684&h=596&f=png&s=122287)

运行了`dep.notify`以后，就会触发这个watcher的update方法，也就会再去重新执行一遍渲染函数了，这个时候视图就刷新了。

## computed

在实现了reactive这个基础api以后，就要开始实现computed这个api了，这个api的用法是这样：

```js
const data = reactive({
  number: 1
})

const numberPlusOne = computed(() => data.number + 1)

// 渲染函数watcher
new Watcher(() => {
  document.getElementById('app2').innerHTML = `
    computed: 1 + number 是 ${numberPlusOne.value}
  `
})
```
vue内部是把computed属性定义在vm实例上的，这里我们没有实例，所以就用一个对象来存储computed的返回值，用`.value`来拿computed的真实值。  

这里computed传入的其实还是一个函数，这里我们回想一下Watcher的本质，其实就是存储了一个`需要在特定时机触发的函数`，在Vue内部，每个computed属性也有自己的一个对应的`watcher`实例，下文中叫它`computedWatcher`


先看渲染函数：
```js
// 渲染函数watcher
new Watcher(() => {
  document.getElementById('app2').innerHTML = `
    computed: 1 + number 是 ${numberPlusOne.value}
  `
})
```
这段渲染函数执行过程中，读取到numberPlusOne的值的时候  

首先会把Dep.target设置为numberPlusOne所对应的`computedWatcher`

`computedWatcher`的特殊之处在于
1. 渲染watcher只能作为依赖被收集到其他的dep筐子里，而`computedWatcher`实例上有属于自己的dep，它可以收集别的`watcher`作为自己的依赖。
2. 惰性求值，初始化的时候先不去运行getter。

```js
export default class Watcher {
  constructor(getter, options = {}) {
    const { computed } = options
    this.getter = getter
    this.computed = computed

    if (computed) {
      this.dep = new Dep()
    } else {
      this.get()
    }
  }
}
```

其实computed实现的本质就是，computed在读取value之前，Dep.target肯定此时是正在运行的`渲染函数的watcher`。

先把当前正在运行的`渲染函数的watcher`作为依赖收集到`computedWatcher`内部的dep筐子里。

把自身`computedWatcher`设置为 全局Dep.target，然后开始求值：

求值函数会在运行
```js
() => data.number + 1
```
的途中遇到data.number的读取，这时又会触发'number'这个key的劫持get函数，这时全局的Dep.target是`computedWatcher`，data.number的dep依赖筐子里丢进去了`computedWatcher`。

此时的依赖关系是 data.number的dep筐子里装着`computedWatcher`，`computedWatcher`的dep筐子里装着`渲染watcher`。

此时如果更新data.number的话，会一级一级往上触发更新。会触发`computedWatcher`的`update`，我们肯定会对被设置为`computed`特性的watcher做特殊的处理，这个watcher的筐子里装着`渲染watcher`，所以只需要触发 this.dep.notify()，就会触发`渲染watcher`的update方法，从而更新视图。

下面来改造代码：
```js
// Watcher
import Dep, { pushTarget, popTarget } from './dep'

export default class Watcher {
  constructor(getter, options = {}) {
    const { computed } = options
    this.getter = getter
    this.computed = computed

    if (computed) {
      this.dep = new Dep()
    } else {
      this.get()
    }
  }

  get() {
    pushTarget(this)
    this.value = this.getter()
    popTarget()
    return this.value
  }

  // 仅为computed使用
  depend() {
    this.dep.depend()
  }

  update() {
    if (this.computed) {
      this.get()
      this.dep.notify()
    } else {
      this.get()
    }
  }
}
```

computed初始化：
```js
// computed
import Watcher from './watcher'

export default function computed(getter) {
  let def = {}
  const computedWatcher = new Watcher(getter, { computed: true })
  Object.defineProperty(def, 'value', {
    get() {
      // 先让computedWatcher收集渲染watcher作为自己的依赖。
      computedWatcher.depend()
      return computedWatcher.get()
    }
  })
  return def
}
```

这里的逻辑比较绕，如果没理清楚的话可以把代码下载下来一步步断点调试，`data.number`被劫持的set触发以后，可以看一下number的dep到底存了什么。

![dep](https://user-gold-cdn.xitu.io/2019/10/28/16e10729f72347a3?w=1120&h=866&f=png&s=554656)

## watch
watch的使用方式是这样的：
```js
watch(
  () => data.msg,
  (newVal, oldVal) => {
    console.log('newVal: ', newVal)
    console.log('old: ', oldVal)
  }
)
```
传入的第一个参数是个函数，里面需要读取到响应式的属性，确保依赖能被收集到，这样下次这个响应式的属性发生改变后，就会打印出对饮的新值和旧值。

分析一下watch的实现原理，这里依然是利用Watcher类去实现，我们把用于watch的watcher叫做`watchWatcher`，传入的getter函数也就是`() => data.msg`，`Watcher`在执行它之前还是一样会把自身（也就是`watchWatcher`）设为`Dep.target`，这时读到data.msg，就会把`watchWatcher`丢进`data.msg`的依赖筐子里。  

如果data.msg更新了，则就会触发`watchWatcher`的`update`方法

直接上代码：
```js
// watch
import Watcher from './watcher'

export default function watch(getter, callback) {
  new Watcher(getter, { watch: true, callback })
}

```

没错又是直接用了getter，只是这次传入的选项是`{ watch: true, callback }`，接下来看看Watcher内部进行了什么处理：
```js
export default class Watcher {
  constructor(getter, options = {}) {
    const { computed, watch, callback } = options
    this.getter = getter
    this.computed = computed
    this.watch = watch
    this.callback = callback
    this.value = undefined

    if (computed) {
      this.dep = new Dep()
    } else {
      this.get()
    }
  }
}
```
首先是构造函数中，对watch选项和callback进行了保存，其他没变。

然后在`update`方法中。
```js
  update() {
    if (this.computed) {
     ...
    } else if (this.watch) {
      const oldValue = this.value
      this.get()
      this.callback(oldValue, this.value)
    } else {
      ...
    }
  }
```

在调用`this.get`去更新值之前，先把旧值保存起来，然后把新值和旧值一起通过调用callback函数交给外部，就这么简单。 

我们仅仅是改动寥寥几行代码，就轻松实现了非常重要的api：`watch`。

## 总结。
有了精妙的Watcher和Dep的设计，Vue内部的响应式api实现的非常简单，不得不再次感叹一下尤大真是厉害啊！