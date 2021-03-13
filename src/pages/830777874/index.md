---
title: '打破 React Hook 必须按顺序、不能在条件语句中调用的枷锁'
date: '2021-03-13'
spoiler: ''
---

React 官网介绍了 Hook 的这样一个限制：

> **不要在循环，条件或嵌套函数中调用 Hook**， 确保总是在你的 React 函数的最顶层以及任何 return 之前调用他们。遵守这条规则，你就能确保 Hook 在每一次渲染中都按照同样的顺序被调用。这让 React 能够在多次的 `useState` 和 `useEffect` 调用之间保持 hook 状态的正确。(如果你对此感到好奇，我们在下面会有更深入的解释。)

这个限制在开发中也确实会时常影响到我们的开发体验，比如函数组件中出现 if 语句提前 return 了，后面又出现 Hook 调用的话，React 官方推的 eslint 规则也会给出警告。

```ts
function App(){
  if (xxx) {
    return null;
  }

  // ❌ React Hook "useState" is called conditionally. 
  // React Hooks must be called in the exact same order in every component render.
  useState();
  
  return 'Hello'
}
```

其实是个挺常见的用法，很多时候满足某个条件了我们就不希望组件继续渲染下去。但由于这个限制的存在，我们只能把所有 Hook 调用提升到函数的顶部，增加额外开销。

由于 React 的源码太复杂，接下来本文会以原理类似但精简很多的 [Preact](https://github.com/preactjs/preact) 的源码为切入点来调试、讲解。

## 限制的原因

这个限制并不是 React 团队凭空造出来的，的确是由于 React Hook 的实现设计而不得已为之。

以 Preact 的 Hook 的实现为例，它用**数组和下标**来实现 Hook 的查找（React 使用链表，但是原理类似）。

```ts
// 当前正在运行的组件
let currentComponent

// 当前 hook 的全局索引
let currentIndex

// 第一次调用 currentIndex 为 0
useState('first') 

// 第二次调用 currentIndex 为 1
useState('second')
```

可以看出，每次 Hook 的调用都对应一个全局的 index 索引，通过这个索引去当前运行组件 `currentComponent` 上的 `_hooks` 数组中查找保存的值，也就是 Hook 返回的 `[state, useState]`

那么假如条件调用的话，比如第一个 `useState` 只有 0.5 的概率被调用：

```js
// 当前正在运行的组件
let currentComponent

// 当前 hook 的全局索引
let currentIndex

// 第一次调用 currentIndex 为 0
if (Math.random() > 0.5) {
  useState('first')
}

// 第二次调用 currentIndex 为 1
useState('second')
```

在 Preact 第一次渲染组件的时候，假设 `Math.random()` 返回的随机值是 `0.6`，那么第一个 Hook 会被执行，此时组件上保存的 `_hooks` 状态是：

```js
_hooks: [
  { value: 'first', update: function },
  { value: 'second', update: function },
]
```

用图来标识这个查找过程是这样的：

![第一次渲染](https://images.gitee.com/uploads/images/2021/0312/205942_86865f67_1087321.png "屏幕截图.png")

假设第二次渲染的时候，`Math.random()` 返回的随机值是 `0.3`，此时只有第二个 useState 被执行了，那么它对应的全局 `currentIndex` 会是 0，这时候去 `_hooks[0]` 中拿到的确是 `first` 所对应的状态，这就会造成渲染混乱。本应该渲染出 `second` 的地方渲染出了 `first`。

![第二次渲染](https://images.gitee.com/uploads/images/2021/0312/210043_bd1e68e8_1087321.png "屏幕截图.png")

没错，本应该值为 `second` 的 value，莫名其妙的被指向了 `first`，渲染完全错误！

以这个例子来看：

```jsx
export default function App() {
  if (Math.random() > 0.5) {
    useState(10000)
  }
  const [value, setValue] = useState(0)

  return (
    <div>
      <button onClick={() => setValue(value + 1)}>+</button>
      {value}
    </div>
  )
}
```

结果是这样：

![chaos](https://images.gitee.com/uploads/images/2021/0312/122331_329604b3_1087321.gif "chaos.gif")

## 破解限制

有没有办法破解限制呢？

如果要破解全局索引递增导致的 bug，那么我们可以考虑换种方式存储 Hook 状态。

如果不用下标存储，是否可以考虑用一个**全局唯一的 key** 来保存 Hook，这样不是就可以绕过下标导致的混乱了吗？

比如 `useState` 这个 API 改造成这样：

```jsx
export default function App() {
  if (Math.random() > 0.5) {
    useState(10000, 'key1');
  }
  const [value, setValue] = useState(0, "key2");

  return (
    <div>
      <button onClick={() => setValue(value + 1)}>+</button>
      {value}
    </div>
  );
}
```

这样，通过 `_hooks['key']` 来查找，就无所谓前序的 Hook 出现的任何意外情况了。

也就是说，原本的存储方式是：

```js
_hooks: [
  { value: 'first', update: function },
  { value: 'second', update: function },
]
```

改造后：

```js
_hooks: [
  key1: { value: 'first', update: function },
  key2: { value: 'second', update: function },
]
```

注意，数组本身就支持对象的 key 值特性，不需要改造 `_hooks` 的结构。

## 改造源码

来试着改造一下 Preact 源码，它的 Hook 包的位置在 [hooks/src/index.js](https://github.com/preactjs/preact/blob/master/hooks/src/index.js) 下，找到 `useState` 方法：

```js
export function useState(initialState) {
  currentHook = 1;
  return useReducer(invokeOrReturn, initialState, undefined);
}
```

它的底层调用了 `useReducer`，所以新增加一个 `key` 参数透传下去：

```diff
+ export function useState(initialState, key) {
  currentHook = 1;
+ return useReducer(invokeOrReturn, initialState, undefined, key);
}
```

`useReducer` 原本是通过全局索引去获取 Hook state：

```js
// 全局索引
let currentIndex

export function useReducer(reducer, initialState, init) {
  const hookState = getHookState(currentIndex++, 2);
  hookState._reducer = reducer;

  return hookState._value;
}
```

改造成兼容版本，有 key 的时候优先传入 key 值：

```diff
// 全局索引
let currentIndex

+ export function useReducer(reducer, initialState, init, key) {
+  const hookState = getHookState(key || currentIndex++, 2);
   hookState._reducer = reducer;

   return hookState._value;
}
```

最后改造一下 `getHookState` 方法：

```diff
function getHookState(index, type) {
  const hooks =
    currentComponent.__hooks ||
    (currentComponent.__hooks = {
      _list: [],
      _pendingEffects: [],
    });

// 传入 key 值是 string 或 symbol 都可以
+  if (typeof index !== 'number') {
+    if (!hooks._list[index]) {
+      hooks._list[index] = {};
+    }
+  } else {
    if (index >= hooks._list.length) {
      hooks._list.push({});
    }
  }
  // 这里天然支持 key 值取用的方式
  return hooks._list[index];
}
```

这里设计成传入 `key` 值的时候，初始化就不往数组里 `push` 新状态，而是直接通过下标写入即可，原本的取状态的写法 `hooks._list[index]` 本身就支持通过 `key` 从数组上取值，不用改动。

至此，改造就完成了。

来试试新用法：

```jsx
export default function App() {
  if (Math.random() > 0.5) {
    useState(10000, 'key1');
  }
  const [value, setValue] = useState(0, 'key2');

  return (
    <div>
      <button onClick={() => setValue(value + 1)}>+</button>
      {value}
    </div>
  );
}
```

![ok](https://images.gitee.com/uploads/images/2021/0312/124253_cb5b5892_1087321.gif "ok.gif")

## 自动编译

事实上 React 团队也考虑过给每次调用加一个 `key` 值的设计，在 Dan Abramov 的 [为什么顺序调用对 React Hooks 很重要？](https://overreacted.io/zh-hans/why-do-hooks-rely-on-call-order/#%E7%BC%BA%E9%99%B7-2-%E5%91%BD%E5%90%8D%E5%86%B2%E7%AA%81) 中已经详细解释过这个提案。

多重的缺陷导致这个提案被否决了，尤其是在遇到自定义 Hook 的时候，比如你提取了一个 `useFormInput`：

```js
const valueKey = Symbol();
 
function useFormInput() {
  const [value, setValue] = useState(valueKey);
  return {
    value,
    onChange(e) {
      setValue(e.target.value);
    },
  };
}
```

然后在组件中多次调用它：

```jsx
function Form() {
  // 使用 Symbol
  const name = useFormInput(); 
  // 又一次使用了同一个 Symbol
  const surname = useFormInput(); 
  // ...
  return (
    <>
      <input {...name} />
      <input {...surname} />
      {/* ... */}
    </>    
  )
}
```

此时这个通过 `key` 寻找 Hook state 的方式就会发生冲突。

但我的想法是，能不能借助 **babel 插件的编译能力**，实现编译期自动为每一次 **Hook 调用**都注入一个 `key`，
伪代码如下：

```js
traverse(node) {
  if (isReactHookInvoking(node)) {
    addFunctionParameter(node, getUniqKey(node))
  }
}
```

生成这样的代码：

```diff
function Form() {
+  const name = useFormInput('key_1'); 
+  const surname = useFormInput('key_2'); 
  // ...
  return (
    <>
      <input {...name} />
      <input {...surname} />
      {/* ... */}
    </>    
  )
}

+ function useFormInput(key) {
+  const [value, setValue] = useState(key);
  return {
    value,
    onChange(e) {
      setValue(e.target.value);
    },
  };
}
```

key 的生成策略可以是随机值，也可以是注入一个 Symbol，这个无所谓，保证运行时期不会改变即可。也许有一些我没有考虑周到的地方，对此有任何想法的同学都欢迎加我微信 [sshsunlight](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/017d568dc1d14cd883cc3238350a39ec~tplv-k3u1fbpfcp-watermark.image) 讨论，当然单纯的交个朋友也没问题，大佬或者萌新都欢迎。

## 总结

本文只是一篇**探索性质**的文章：

- 介绍 Hook 实现的大概原理以及限制
- 探索出修改源码机制绕过限制的方法

其实本意是**帮助大家更好的理解 Hook**。

我并不希望 React 取消掉这些限制，我觉得这也是设计的取舍。

如果任何子函数，任何条件表达式中都可以调用 Hook，代码也会变得更加**难以理解和维护**。

如果你真的希望更加灵活的使用类似的 Hook 能力，Vue3 底层**响应式收集依赖**的原理就可以完美的绕过这些限制，但更加灵活的同时也一定会无法避免的增加更多维护风险。

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![image](https://user-images.githubusercontent.com/23615778/108619258-76929d80-745e-11eb-90bf-023abec85d80.png)
