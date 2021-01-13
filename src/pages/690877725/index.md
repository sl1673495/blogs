---
title: '最简实现Promise，支持异步链式调用（20行）'
date: '2020-09-02'
spoiler: ''
---

## 前言

在面试的时候，经常会有面试官让你实现一个 Promise，如果参照 A+规范来实现的话，可能面到天黑都结束不了。

说到 Promise，我们首先想到的最核心的功能就是异步链式调用，本篇文章就带你用 20 行代码实现一个可以异步链式调用的 Promise。

这个 Promise 的实现不考虑任何异常情况，只考虑代码最简短，从而便于读者理解核心的异步链式调用原理。

## 代码

先给代码吧，真就 20 行。

```js
function Promise(fn) {
  this.cbs = [];

  const resolve = (value) => {
    setTimeout(() => {
      this.data = value;
      this.cbs.forEach((cb) => cb(value));
    });
  }

  fn(resolve);
}

Promise.prototype.then = function (onResolved) {
  return new Promise((resolve) => {
    this.cbs.push(() => {
      const res = onResolved(this.data);
      if (res instanceof Promise) {
        res.then(resolve);
      } else {
        resolve(res);
      }
    });
  });
};
```

## 核心案例

```js
new Promise((resolve) => {
  setTimeout(() => {
    resolve(1);
  }, 500);
})
  .then((res) => {
    console.log(res);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(2);
      }, 500);
    });
  })
  .then(console.log);
```

本文将围绕这个最核心的案例来讲，这段代码的表现如下：

1. 500ms 后输出 1
2. 500ms 后输出 2

## 实现

### 构造函数

首先来实现 Promise 构造函数

```js
function Promise(fn) {
  // Promise resolve时的回调函数集
  this.cbs = [];

  // 传递给Promise处理函数的resolve
  // 这里直接往实例上挂个data
  // 然后把onResolvedCallback数组里的函数依次执行一遍就可以
  const resolve = (value) => {
    // 注意promise的then函数需要异步执行
    setTimeout(() => {
      this.data = value;
      this.cbs.forEach((cb) => cb(value));
    });
  }

  // 执行用户传入的函数 
  // 并且把resolve方法交给用户执行
  fn(resolve);
}
```

好，写到这里先回过头来看案例

```js
const fn = (resolve) => {
  setTimeout(() => {
    resolve(1);
  }, 500);
};

new Promise(fn);
```

分开来看，`fn` 就是用户传的函数，这个函数内部调用了 `resolve` 函数后，就会把 `promise` 实例上的 `cbs` 全部执行一遍。

到此为止我们还不知道 `cbs` 这个数组里的函数是从哪里来的，接着往下看。

### then

这里是最重要的 then 实现，链式调用全靠它：

```js
Promise.prototype.then = function (onResolved) {
  // 这里叫做promise2
  return new Promise((resolve) => {
    this.cbs.push(() => {
      const res = onResolved(this.data);
      if (res instanceof Promise) {
        // resolve的权力被交给了user promise
        res.then(resolve);
      } else {
        // 如果是普通值 就直接resolve
        // 依次执行cbs里的函数 并且把值传递给cbs
        resolve(res);
      }
    });
  });
};
```

再回到案例里

```js
const fn = (resolve) => {
  setTimeout(() => {
    resolve(1);
  }, 500);
};

const promise1 = new Promise(fn);

promise1.then((res) => {
  console.log(res);
  // user promise
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(2);
    }, 500);
  });
});
```

注意这里的命名：

1. 我们把 `new Promise` 返回的实例叫做`promise1`

2. 在 `Promise.prototype.then` 的实现中，我们构造了一个新的 promise 返回，叫它`promise2`

3. 在用户调用 `then` 方法的时候，用户手动构造了一个 promise 并且返回，用来做异步的操作，叫它`user promise`

那么在 `then` 的实现中，内部的 this 其实就指向`promise1`

而`promise2`的传入的`fn` 函数执行了一个 `this.cbs.push()`，其实是往 **`promise1`** 的`cbs`数组中 push 了一个函数，等待后续执行。

```js
Promise.prototype.then = function (onResolved) {
  // 这里叫做promise2
  return new Promise((resolve) => {
    // 这里的this其实是promise1
    this.cbs.push(() => {});
  });
};
```

那么重点看这个 push 的函数，注意，这个函数在 `promise1` 被 resolve 了以后才会执行。

```js
// promise2
return new Promise((resolve) => {
  this.cbs.push(() => {
    // onResolved就对应then传入的函数
    const res = onResolved(this.data)
    // 例子中的情况 用户自己返回了一个user promise
    if (res instanceof Promise) {
      // user promise的情况
      // 用户会自己决定何时resolve promise2
      // 只有promise2被resolve以后
      // then下面的链式调用函数才会继续执行
      res.then(resolve)
    } else {
      resolve(res)
    }
  })
})
```

如果用户传入给 then 的 onResolved 方法返回的是个 `user promise`，那么这个`user promise`里用户会自己去在合适的时机 `resolve promise2`，那么进而这里的 `res.then(resolve)` 中的 resolve 就会被执行：

```js
if (res instanceof Promise) {
    res.then(resolve)
}
```

结合下面这个例子来看：
```js
new Promise((resolve) => {
  setTimeout(() => {
    // resolve1
    resolve(1);
  }, 500);
})
  // then1
  .then((res) => {
    console.log(res);
    // user promise
    return new Promise((resolve) => {
      setTimeout(() => {
        // resolve2
        resolve(2);
      }, 500);
    });
  })
  // then2
  .then(console.log);
```

`then1`这一整块其实返回的是 `promise2`，那么 `then2` 其实本质上是 `promise2.then(console.log)`，

也就是说 `then2`注册的回调函数，其实进入了`promise2`的 `cbs` 回调数组里，又因为我们刚刚知道，`resolve2` 调用了之后，`user promise` 会被 resolve，进而触发 `promise2` 被 resolve，进而 `promise2` 里的 `cbs` 数组被依次触发。

这样就实现了用户自己写的 `resolve2` 执行完毕后，`then2` 里的逻辑才会继续执行，也就是**异步链式调用**。

## 文章总结

本文只是简单实现一个可以异步链式调用的 promise，而真正的 promise 比它复杂很多很多，涉及到各种异常情况、边界情况的处理。

promise A+规范还是值得每一个合格的前端开发去阅读的。

希望这篇文章可以对你有所帮助！
