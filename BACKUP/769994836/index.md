---
title: '🔖TypeScript 备忘录：如何在 React 中完美运用？'
date: '2020-12-17'
spoiler: ''
---

## 前言
一直以来，ssh 身边都有很多小伙伴对 TS 如何在 React 中运用有很多困惑，他们开始慢慢讨厌 TS，觉得各种莫名其妙的问题**降低了开发的效率**。

其实如果运用熟练的话，TS 只是在**第一次开发**的时候稍微多花一些时间去编写类型，后续维护、重构的时候就会发挥它神奇的作用了，还是非常推荐**长期维护的项目**使用它的。

其实我一直知道**英文版**有个不错的备忘录，本来想直接推荐给小伙伴，奈何很多人对英文比较头痛，而它中文翻译的版本点进去**竟然是这个景象**：

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a43e7a47a4634ef194ec8c92d301c025~tplv-k3u1fbpfcp-watermark.image)

既然如此，就自己动手。结合英文原版里的一些示例进行一些扩展，总结成这篇备忘录。

## 前置基础
阅读本文的前提条件是：

- 熟悉 React 的使用。
- 熟悉 TypeScript 中的类型知识。
- 本文会侧重使用 React Hook 作为示例，当然大部分类型知识都是通用的。

也就是说，这篇文章侧重点在于 **「React 和 TypeScript 的结合」**，而不是基础知识，基础知识阅读文档即可学习。

也推荐看我 [初中级前端的高级进阶指南](https://mp.weixin.qq.com/s?__biz=MzI3NTM5NDgzOA==&amp;mid=2247484321&amp;idx=1&amp;sn=e5fb9256ce7887b314e69c17f3d3b872&amp;chksm=eb043bd8dc73b2cebc529089df47e12100144f936090c8e97eaa9450c3d4a6f72351b416a35b&token=962173348&lang=zh_CN#rd) 这篇文章中的 React 和 TypeScript 章节，这里不多赘述。

## 工具

- [TypeScript Playground with React](https://www.typescriptlang.org/play?#code/JYWwDg9gTgLgBAKjgQwM5wEoFNkGN4BmUEIcA5FDvmQNwCwAUKJLHAN5wCuqWAyjMhhYANFx4BRAgSz44AXzhES5Snhi1GjLAA8W8XBAB2qeAGEInQ0KjjtycABsscALxwAFAEpXAPnaM4OANjeABtA0sYUR4Yc0iAXVcxPgEhdwAGT3oGAOTJaXx3L19-BkDAgBMIXE4QLCsAOhhgGCckgAMATQsgh2BcAGssCrgAEjYIqwVmutR27MC5LM0yuEoYTihDD1zAgB4K4AA3H13yvbAfbs5e-qGRiYspuBmsVD2Aekuz-YAjThgMCMcCMpj6gxcbGKLj8MTiVnck3gAGo4ABGTxyU6rcrlMF3OB1H5wT7-QFGbG4z6HE65ZYMOSMIA)：可以在线调试 React + TypeScript，只能调试类型，并不能运行代码
- [Stackblitz](https://stackblitz.com/edit/react-typescript-base)：云开发工具，可以直接运行 React 代码并且预览
- [Create React App TypeScript](https://create-react-app.dev/docs/adding-typescript/): 本地用脚手架生成 React + TS 的项目

选择你觉得比较中意的调试工具即可。

## 组件 Props
先看几种定义 Props 经常用到的类型：

### 基础类型

```ts
type BasicProps = {
  message: string;
  count: number;
  disabled: boolean;
  /** 数组类型 */
  names: string[];
  /** 用「联合类型」限制为下面两种「字符串字面量」类型 */
  status: "waiting" | "success";
};
```

### 对象类型
```ts
type ObjectOrArrayProps = {
  /** 如果你不需要用到具体的属性 可以这样模糊规定是个对象 ❌ 不推荐 */
  obj: object;
  obj2: {}; // 同上
  /** 拥有具体属性的对象类型 ✅ 推荐 */
  obj3: {
    id: string;
    title: string;
  };
  /** 对象数组 😁 常用 */
  objArr: {
    id: string;
    title: string;
  }[];
  /** key 可以为任意 string，值限制为 MyTypeHere 类型 */
  dict1: {
    [key: string]: MyTypeHere;
  };
  dict2: Record<string, MyTypeHere>; // 基本上和 dict1 相同，用了 TS 内置的 Record 类型。
}
```

### 函数类型
```ts
type FunctionProps = {
  /** 任意的函数类型 ❌ 不推荐 不能规定参数以及返回值类型 */
  onSomething: Function;
  /** 没有参数的函数 不需要返回值 😁 常用 */
  onClick: () => void;
  /** 带函数的参数 😁 非常常用 */
  onChange: (id: number) => void;
  /** 另一种函数语法 参数是 React 的按钮事件 😁 非常常用 */
  onClick(event: React.MouseEvent<HTMLButtonElement>): void;
  /** 可选参数类型 😁 非常常用 */
  optional?: OptionalType;
}
```

### React 相关类型

```ts
export declare interface AppProps {
  children1: JSX.Element; // ❌ 不推荐 没有考虑数组
  children2: JSX.Element | JSX.Element[]; // ❌ 不推荐 没有考虑字符串 children
  children4: React.ReactChild[]; // 稍微好点 但是没考虑 null
  children: React.ReactNode; // ✅ 包含所有 children 情况
  functionChildren: (name: string) => React.ReactNode; // ✅ 返回 React 节点的函数
  style?: React.CSSProperties; // ✅ 推荐 在内联 style 时使用
  // ✅ 推荐原生 button 标签自带的所有 props 类型
  // 也可以在泛型的位置传入组件 提取组件的 Props 类型
  props: React.ComponentProps<"button">;
  // ✅ 推荐 利用上一步的做法 再进一步的提取出原生的 onClick 函数类型 
  // 此时函数的第一个参数会自动推断为 React 的点击事件类型
  onClickButton：React.ComponentProps<"button">["onClick"]
}
```

## 函数式组件

最简单的：

```ts
interface AppProps = { message: string };

const App = ({ message }: AppProps) => <div>{message}</div>;
```

包含 children 的：

利用 `React.FC` 内置类型的话，不光会包含你定义的 `AppProps` 还会自动加上一个 children 类型，以及其他组件上会出现的类型：

```ts
// 等同于
AppProps & { 
  children: React.ReactNode 
  propTypes?: WeakValidationMap<P>;
  contextTypes?: ValidationMap<any>;
  defaultProps?: Partial<P>;
  displayName?: string;
}

// 使用
interface AppProps = { message: string };

const App: React.FC<AppProps> = ({ message, children }) => {
  return (
    <>
     {children}
     <div>{message}</div>
    </>
  )
};
```

## Hooks

`@types/react` 包在 16.8 以上的版本开始对 Hooks 的支持。

### useState

如果你的默认值已经可以说明类型，那么不用手动声明类型，交给 TS 自动推断即可：

```ts
// val: boolean
const [val, toggle] = React.useState(false);

toggle(false)
toggle(true)
```

如果初始值是 null 或 undefined，那就要通过泛型手动传入你期望的类型。

```ts
const [user, setUser] = React.useState<IUser | null>(null);

// later...
setUser(newUser);
```

这样也可以保证在你直接访问 `user` 上的属性时，提示你它有可能是 null。

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/89f3eb300d824bafb544494b8e92d9ac~tplv-k3u1fbpfcp-watermark.image)

通过 `optional-chaining` 语法（TS 3.7 以上支持），可以避免这个错误。

```ts
// ✅ ok
const name = user?.name
```

### useReducer

需要用 [Discriminated Unions](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes-func.html#discriminated-unions) 来标注 Action 的类型。

```ts
const initialState = { count: 0 };

type ACTIONTYPE =
  | { type: "increment"; payload: number }
  | { type: "decrement"; payload: string };

function reducer(state: typeof initialState, action: ACTIONTYPE) {
  switch (action.type) {
    case "increment":
      return { count: state.count + action.payload };
    case "decrement":
      return { count: state.count - Number(action.payload) };
    default:
      throw new Error();
  }
}

function Counter() {
  const [state, dispatch] = React.useReducer(reducer, initialState);
  return (
    <>
      Count: {state.count}
      <button onClick={() => dispatch({ type: "decrement", payload: "5" })}>
        -
      </button>
      <button onClick={() => dispatch({ type: "increment", payload: 5 })}>
        +
      </button>
    </>
  );
}
```
「Discriminated Unions」一般是一个联合类型，其中每一个类型都需要通过类似 `type` 这种特定的字段来区分，当你传入特定的 `type` 时，剩下的类型 `payload` 就会自动匹配推断。

这样：

- 当你写入的 `type` 匹配到 `decrement` 的时候，TS 会自动推断出相应的 `payload` 应该是 `string` 类型。
- 当你写入的 `type` 匹配到 `increment` 的时候，则 `payload` 应该是 `number` 类型。

这样在你 `dispatch` 的时候，输入对应的 `type`，就自动提示你剩余的参数类型啦。

### useEffect

这里主要需要注意的是，useEffect 传入的函数，它的返回值要么是一个**方法**（清理函数），要么就是**undefined**，其他情况都会报错。

比较常见的一个情况是，我们的 useEffect 需要执行一个 async 函数，比如：

```ts
// ❌ 
// Type 'Promise<void>' provides no match 
// for the signature '(): void | undefined'
useEffect(async () => {
  const user = await getUser()
  setUser(user)
}, [])
```

虽然没有在 async 函数里显式的返回值，但是 async 函数默认会返回一个 Promise，这会导致 TS 的报错。

推荐这样改写：
```ts
useEffect(() => {
  const getUser = async () => {
    const user = await getUser()
    setUser(user)
  }
  getUser()
}, [])
```

或者用自执行函数？不推荐，可读性不好。

```ts
useEffect(() => {
  (async () => {
    const user = await getUser()
    setUser(user)
  })()
}, [])
```

### useRef

这个 Hook 在很多时候是没有初始值的，这样可以声明返回对象中 `current` 属性的类型：

```ts
const ref2 = useRef<HTMLElement>(null);
```

以一个按钮场景为例：

```ts
function TextInputWithFocusButton() {
  const inputEl = React.useRef<HTMLInputElement>(null);
  const onButtonClick = () => {
    if (inputEl && inputEl.current) {
      inputEl.current.focus();
    }
  };
  return (
    <>
      <input ref={inputEl} type="text" />
      <button onClick={onButtonClick}>Focus the input</button>
    </>
  );
}
```

当 `onButtonClick` 事件触发时，可以肯定 `inputEl` 也是有值的，因为组件是同级别渲染的，但是还是依然要做冗余的非空判断。

有一种办法可以绕过去。

```ts
const ref1 = useRef<HTMLElement>(null!);

```

`null!` 这种语法是非空断言，跟在一个值后面表示你断定它是有值的，所以在你使用 `inputEl.current.focus()` 的时候，TS 不会给出报错。

但是这种语法比较危险，需要尽量减少使用。

在绝大部分情况下，`inputEl.current?.focus()` 是个更安全的选择，除非这个值**真的不可能**为空。（比如在使用之前就赋值了）

### useImperativeHandle

推荐使用一个自定义的 `innerRef` 来代替原生的 `ref`，否则要用到 `forwardRef` 会搞的类型很复杂。

```ts
type ListProps = {
  innerRef?: React.Ref<{ scrollToTop(): void }>
}

function List(props: ListProps) {
  useImperativeHandle(props.innerRef, () => ({
    scrollToTop() { }
  }))
  return null
}
```

结合刚刚 `useRef` 的知识，使用是这样的：

```ts
function Use() {
  const listRef = useRef<{ scrollToTop(): void }>(null!)

  useEffect(() => {
    listRef.current.scrollToTop()
  }, [])

  return (
    <List innerRef={listRef} />
  )
}
```

很完美，是不是？

可以在线调试 [useImperativeHandle 的例子](https://www.typescriptlang.org/play?#code/JYWwDg9gTgLgBAKjgQwM5wEoFNkGN4BmUEIcA5FDvmQNwCwAUKJLHAN5wCuqWAyjMhhYANFx4BRAgSz5R3LNgJyeASXBYog4ADcsACWQA7ACYAbLHAC+cIiXKU8MWo0YwAnmAsAZYKhgAFYjB0AF52Rjg4YENDDUUAfgAuTCoYADpFAB4OVFxiU1MAFQhisAAKAEpk7QhgYysAPkZLFwYCTkN8YAhDOB8-MrAg1GT+gOGK8IZI+TVPTRgdfSMzLEHhtOjYqEVRSrgQhrgytgjIuFz8opKIcsmOFumrCoqzyhhOKF7DTgLm1vanUWPTgAFUePtTk9cD0-HBTL4YIoDmIFFgCNkLnkIAViqVKtVavVLA0yj8CgBCV4MM7ySTSfBlfaHKbneGIxRpXCfSiGdKXHHXfHUyKWUQAbQAutS3lgPl9jmdIpkxlEYnF0SE2Ai-IprAB6JpPamWIA)。

也可以查看这个[useImperativeHandle 讨论 Issue](https://github.com/typescript-cheatsheets/react/issues/106)，里面有很多有意思的想法，也有使用 React.forwardRef 的复杂例子。

### 自定义 Hook

如果你想仿照 useState 的形式，返回一个数组给用户使用，一定要记得在适当的时候使用 `as const`，标记这个返回值是个常量，告诉 TS 数组里的值不会删除，改变顺序等等……

否则，你的每一项都会被推断成是「所有类型可能性的联合类型」，这会影响用户使用。

```ts
export function useLoading() {
  const [isLoading, setState] = React.useState(false);
  const load = (aPromise: Promise<any>) => {
    setState(true);
    return aPromise.finally(() => setState(false));
  };
  // ✅ 加了 as const 会推断出 [boolean, typeof load]
  // ❌ 否则会是 (boolean | typeof load)[]
  return [isLoading, load] as const;[]
}
```

对了，如果你在用 React Hook 写一个库，别忘了把类型也导出给用户使用。

## React API

### forwardRef

函数式组件默认不可以加 ref，它不像类组件那样有自己的实例。这个 API 一般是函数式组件用来接收父组件传来的 ref。

所以需要标注好实例类型，也就是父组件通过 ref 可以拿到什么样类型的值。

```ts
type Props = { };
export type Ref = HTMLButtonElement;
export const FancyButton = React.forwardRef<Ref, Props>((props, ref) => (
  <button ref={ref} className="MyClassName">
    {props.children}
  </button>
));
```

由于这个例子里直接把 ref 转发给 button 了，所以直接把类型标注为 `HTMLButtonElement` 即可。

父组件这样调用，就可以拿到正确类型：

```ts
export const App = () => {
  const ref = useRef<HTMLButtonElement>()
  return (
    <FancyButton ref={ref} />
  )
}
```

## 鸣谢

本文大量使用 [react-typescript-cheatsheets](https://github.com/typescript-cheatsheets/react) 中的例子，加上自己的润色和例子补充，英文好的同学也可以读这个原文扩展学习。

> 欢迎关注「[前端从进阶到入院](https://ssh-1300257814.cos.ap-shanghai.myqcloud.com/public_qrcode)」，如果这篇文章**点赞**的人数还不错的话，我会继续更新本系列。