# [手写async await的最简实现（20行）](https://github.com/sl1673495/blogs/issues/59)

## 前言
如果让你手写async函数的实现，你是不是会觉得很复杂？这篇文章带你用20行搞定它的核心。  

经常有人说async函数是generator函数的语法糖，那么到底是怎么样一个糖呢？让我们来一层层的剥开它的糖衣。  

有的同学想说，既然用了generator函数何必还要实现async呢？  

这篇文章的目的就是带大家理解清楚async和generator之间到底是如何相互协作，管理异步的。

## 示例
```js
const getData = () => new Promise(resolve => setTimeout(() => resolve("data"), 1000))

async function test() {
  const data = await getData()
  console.log('data: ', data);
  const data2 = await getData()
  console.log('data2: ', data2);
  return 'success'
}

// 这样的一个函数 应该再1秒后打印data 再过一秒打印data2 最后打印success
test().then(res => console.log(res))
```

## 思路
对于这个简单的案例来说，如果我们把它用generator函数表达，会是怎么样的呢？
```js
function* testG() {
  // await被编译成了yield
  const data = yield getData()
  console.log('data: ', data);
  const data2 = yield getData()
  console.log('data2: ', data2);
  return 'success'
}
```

我们知道，generator函数是不会自动执行的，每一次调用它的next方法，会停留在下一个yield的位置。  

利用这个特性，我们只要编写一个自动执行的函数，就可以让这个generator函数完全实现async函数的功能。  

```js
const getData = () => new Promise(resolve => setTimeout(() => resolve("data"), 1000))
  
var test = asyncToGenerator(
    function* testG() {
      // await被编译成了yield
      const data = yield getData()
      console.log('data: ', data);
      const data2 = yield getData()
      console.log('data2: ', data2);
      return 'success'
    }
)

test().then(res => console.log(res))
```

那么大体上的思路已经确定了，  

`asyncToGenerator`接受一个`generator`函数，返回一个`promise`，  

关键就在于，里面用`yield`来划分的异步流程，应该如何自动执行。  

## 如果是手动执行
在编写这个函数之前，我们先模拟手动去调用这个`generator`函数去一步步的把流程走完，有助于后面的思考。
```js
function* testG() {
  // await被编译成了yield
  const data = yield getData()
  console.log('data: ', data);
  const data2 = yield getData()
  console.log('data2: ', data2);
  return 'success'
}
```
我们先调用`testG`生成一个迭代器
```js
// 返回了一个迭代器
var gen = testG()
```

然后开始执行第一次`next`

```js
// 第一次调用next 停留在第一个yield的位置
// 返回的promise里 包含了data需要的数据
var dataPromise = gen.next()
```

这里返回了一个`promise`，就是第一次`getData()`所返回的`promise`，注意

```js
const data = yield getData()
```
这段代码要切割成左右两部分来看，第一次调用`next`，其实只是停留在了`yield getData()`这里，  

`data`的值并没有被确定。

那么什么时候data的值会被确定呢？

**下一次调用next的时候，传的参数会被作为上一个yield前面接受的值**

也就是说，我们再次调用`gen.next('这个参数才会被赋给data变量')`的时候  

`data`的值才会被确定为`'这个参数才会被赋给data变量'`  

```js
gen.next('这个参数才会被赋给data变量')

// 然后这里的data才有值
const data = yield getData()

// 然后打印出data
console.log('data: ', data);

// 然后继续走到下一个yield
const data2 = yield getData()
```
然后往下执行，直到遇到下一个`yield`，继续这样的流程...

这是generator函数设计的一个比较难理解的点，但是为了实现我们的目标，还是得去学习它~  

借助这个特性，如果我们这样去控制yield的流程，是不是就能实现异步串行了？

```js
function* testG() {
  // await被编译成了yield
  const data = yield getData()
  console.log('data: ', data);
  const data2 = yield getData()
  console.log('data2: ', data2);
  return 'success'
}

var gen = testG()

var dataPromise = gen.next()

dataPromise.then((value1) => {
    // data1的value被拿到了 继续调用next并且传递给data
    var data2Promise = gen.next(value1)
    
    // console.log('data: ', data);
    // 此时就会打印出data
    
    data2Promise.value.then((value2) => {
        // data2的value拿到了 继续调用next并且传递value2
         gen.next(value2)
         
        // console.log('data2: ', data2);
        // 此时就会打印出data2
    })
})
```

这样的一个看着像`callback hell`的调用，就可以让我们的generator函数把异步安排的明明白白。
## 实现

有了这样的思路，实现这个高阶函数就变得很简单了。

先整体看一下结构，有个印象，然后我们逐行注释讲解。

```js
function asyncToGenerator(generatorFunc) {
    return function() {
      const gen = generatorFunc.apply(this, arguments)
      return new Promise((resolve, reject) => {
        function step(key, arg) {
          let generatorResult
          try {
            generatorResult = gen[key](arg)
          } catch (error) {
            return reject(error)
          }
          const { value, done } = generatorResult
          if (done) {
            return resolve(value)
          } else {
            return Promise.resolve(value).then(val => step('next', val), err => step('throw', err))
          }
        }
        step("next")
      })
    }
}
```

不多不少，22行。  

接下来逐行讲解。
```js
function asyncToGenerator(generatorFunc) {
  // 返回的是一个新的函数
  return function() {
  
    // 先调用generator函数 生成迭代器
    // 对应 var gen = testG()
    const gen = generatorFunc.apply(this, arguments)

    // 返回一个promise 因为外部是用.then的方式 或者await的方式去使用这个函数的返回值的
    // var test = asyncToGenerator(testG)
    // test().then(res => console.log(res))
    return new Promise((resolve, reject) => {
    
      // 内部定义一个step函数 用来一步一步的跨过yield的阻碍
      // key有next和throw两种取值，分别对应了gen的next和throw方法
      // arg参数则是用来把promise resolve出来的值交给下一个yield
      function step(key, arg) {
        let generatorResult
        
        // 这个方法需要包裹在try catch中
        // 如果报错了 就把promise给reject掉 外部通过.catch可以获取到错误
        try {
          generatorResult = gen[key](arg)
        } catch (error) {
          return reject(error)
        }

        // gen.next() 得到的结果是一个 { value, done } 的结构
        const { value, done } = generatorResult

        if (done) {
          // 如果已经完成了 就直接resolve这个promise
          // 这个done是在最后一次调用next后才会为true
          // 以本文的例子来说 此时的结果是 { done: true, value: 'success' }
          // 这个value也就是generator函数最后的返回值
          return resolve(value)
        } else {
          // 除了最后结束的时候外，每次调用gen.next()
          // 其实是返回 { value: Promise, done: false } 的结构，
          // 这里要注意的是Promise.resolve可以接受一个promise为参数
          // 并且这个promise参数被resolve的时候，这个then才会被调用
          return Promise.resolve(
            // 这个value对应的是yield后面的promise
            value
          ).then(
            // value这个promise被resove的时候，就会执行next
            // 并且只要done不是true的时候 就会递归的往下解开promise
            // 对应gen.next().value.then(value => {
            //    gen.next(value).value.then(value2 => {
            //       gen.next() 
            //
            //      // 此时done为true了 整个promise被resolve了 
            //      // 最外部的test().then(res => console.log(res))的then就开始执行了
            //    })
            // })
            function onResolve(val) {
              step("next", val)
            },
            // 如果promise被reject了 就再次进入step函数
            // 不同的是，这次的try catch中调用的是gen.throw(err)
            // 那么自然就被catch到 然后把promise给reject掉啦
            function onReject(err) {
              step("throw", err)
            },
          )
        }
      }
      step("next")
    })
  }
}
```


## 源码地址
这个 [js文件](https://github.com/sl1673495/javascript-codes/blob/master/async.js) 的代码可以直接放进浏览器里运行，欢迎调戏。  


## 总结
本文用最简单的方式实现了asyncToGenerator这个函数，这是babel编译async函数的核心，当然在babel中，generator函数也被编译成了一个很原始的形式，本文我们直接以generator替代。  

这也是实现promise串行的一个很棒的模式，如果本篇文章对你有帮助，点个赞就好啦。  

## ❤️感谢大家
1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/6/28/172f8f7d642a6c86?w=910&h=436&f=png&s=250863)