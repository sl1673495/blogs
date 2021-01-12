---
title: '一道蚂蚁金服异步串行面试题'
date: '2020-08-13'
spoiler: ''
---

## 前言

朋友去面试蚂蚁金服，遇到了一道面试题，乍一看感觉挺简单的，但是实现起来发现内部值得一提的点还是挺多的。

先看题目：

```js
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const subFlow = createFlow([() => delay(1000).then(() => log("c"))]);

createFlow([
  () => log("a"),
  () => log("b"),
  subFlow,
  [() => delay(1000).then(() => log("d")), () => log("e")],
]).run(() => {
  console.log("done");
});

// 需要按照 a,b,延迟1秒,c,延迟1秒,d,e, done 的顺序打印
```

按照上面的测试用例，实现 `createFlow`：

- `flow` 是指一系列 `effects` 组成的逻辑片段。
- `flow` 支持嵌套。
- `effects` 的执行只需要支持串行。

## 分析

先以入参分析，`createFlow` 接受一个数组作为参数（按照题意里面的每一项应该叫做 `effect`)，排除掉一些重复的项，我们把参数数组中的每一项整理归类一下，总共有如下几种类型：

1. 普通函数：

```js
() => log("a");
```

2. 延迟函数（Promise）：

```js
() => delay(1000).then(() => log("d"));
```

3. 另一个 `flow`：

```js
const subFlow = createFlow([() => delay(1000).then(() => log("c"))]);
```

4. 用数组包裹的上述三项。

## 实现

先把参数浅拷贝一份（编写库函数，尽量不要影响用户传入的参数是个原则），再简单的扁平化 `flat` 一下。（处理情况 4）

```js
function createFlow(effects = []) {
  let sources = effects.slice().flat();
}
```

观察题意，`createFlow` 并不会让方法开始执行，需要 `.run()` 之后才会开始执行，所以先定义好这个函数：

```js
function createFlow(effects = []) {
  let sources = effects.slice().flat();
  function run(callback) {
    while (sources.length) {
      const task = sources.shift();
    }
    callback?.();
  }
}
```

这里我选择用 `while` 循环依次处理数组中的每个 `effect`，便于随时中断。

对于函数类型的 `effect`，直接执行它：

```js
function createFlow(effects = []) {
  let sources = effects.slice().flat();
  function run(callback) {
    while (sources.length) {
      const task = sources.shift();
      if (typeof task === "function") {
        const res = task();
      }
    }
    // 在所有任务执行完毕后 执行传入的回调函数
    callback?.();
  }

  return {
    run,
    isFlow: true,
  };
}
```

这里拿到了函数的返回值 `res`，有一个情况别忘了，就是 `effect` 返回的是一个 `Promise`，比如这种情况：

```js
() => delay(1000).then(() => log("d"));
```

那么拿到返回值后，这里直接简化判断，看返回值是否有 then 属性来判断它是否是一个 Promise（生产环境请选择更加严谨的方法）。

```js
if (res?.then) {
  res.then(createFlow(sources).run);
  return;
}
```

这里我选择中断本次的 `flow` 执行，并且用剩下的 `sources` 去建立一个新的 `flow`，并且在上一个 Promise 的 then 方法里再去异步的开启新的 `flow` 的 `run`。

这样，上面延迟 1s 后的 Promise 被 resolve 之后，剩下的 `sources` 任务数组会被新的 `flow.run()` 驱动，继续执行。

接下来再处理 `effect` 是另一个 `flow` 的情况，注意上面编写的大致函数体，我们已经让 `createFlow` 这个函数返回值带上 `isFlow` 这个标记，用来判断它是否是一个 `flow`。

```js
// 把callback放到下一个flow的callback时机里执行
const next = () => createFlow(sources).run(callback)
if (typeof task === "function") {
  const res = task();
  if (res?.then) {
    res.then(next);
    return;
  }
} else if (task?.isFlow) {
  task.run(next);
  return;
}
```

看 `else if` 的部分，直接调用传入的 `flow` 的 `run`，把剩下的 `sources` 创建的新的 `flow`，并且把这一轮的 `callback` 放入到新的 `flow` 的 `callback` 位置。在所有的任务都结束后再执行。

定义一个 `next` 方法，用来在遇到异步任务或者另一个 `flow` 的时候

这样，参数中传入的 `flow` 执行完毕后，才会继续执行剩下的任务，并且在最后执行 `callback`。

## 完整代码

```js
function createFlow(effects = []) {
  let sources = effects.slice().flat();
  function run(callback) {
    while (sources.length) {
      const task = sources.shift();
      // 把callback放到下一个flow的callback时机里执行
      const next = () => createFlow(sources).run(callback)
      if (typeof task === "function") {
        const res = task();
        if (res?.then) {
          res.then(next);
          return;
        }
      } else if (task?.isFlow) {
        task.run(next);
        return;
      }
    }
    callback?.();
  }
  return {
    run,
    isFlow: true,
  };
}
const delay = () => new Promise((resolve) => setTimeout(resolve, 1000));
createFlow([
  () => console.log("a"),
  () => console.log("b"),
  createFlow([() => console.log("c")]),
  [() => delay().then(() => console.log("d")), () => console.log("e")],
]).run();
```

## 总结

这道面试题主要的目的是考察对于异步串行流的控制，巧妙的利用自身的递归设计来处理传入的参数也是一个 `flow`的情况，在编写题目的过程中展示你对 Promise 的熟练运用，一定会让面试官对你刮目相看的~

祝大家在大环境不好的情况下，都能拿到自己满意的 offer，加油。


---

> 或许更好的解决方案：
> 
> * 使用 async await 控制串行
> * 使用生成器将嵌套结构的 flow 展平为 effects 迭代器

是的 async 一定是更简洁的 也许是我想怀旧一下了 XD