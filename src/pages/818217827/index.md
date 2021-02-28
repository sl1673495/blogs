---
title: 'TypeScript 中你不一定知道的 top types，在用 any 之前先试试 unknown？'
date: '2021-02-28'
spoiler: ''
---

## 来源
最近发现了一本 TS 相关的电子书，[Tackling TypeScript](https://exploringjs.com/tackling-ts/ch_any-unknown.html#typescripts-two-top-types)。随便翻看了一下，就发现了自己很感兴趣的一个问题，并且也经常听说在国内面试中出现。

加上国内的相关资料确实不多，花了点时间翻译了下这一章节。

英文基础好的同学可以直接去电子书地址阅读，如果觉得有帮助的话，可以买下这本书，或者捐助作者。

![输入图片说明](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/92fcc564764d4f8a8bfdd145c06d44b9~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

## 前言

在 TypeScript 中，`any` 和 `unknown` 是包含了所有值的类型。

本文会详细介绍它们是什么，用在哪儿。

## TS 中的两个 top types

`any` 和 `unknown` 是 TypeScript 中欧所谓的 `top types`，详见 [Wikipedia](https://en.wikipedia.org/wiki/Top_type)：

> The top type […] is the universal type, sometimes called the universal supertype as all other types in any given type system are subtypes […]. In most cases it is the type which contains every possible [value] in the type system of interest.

简单翻译过来就是说，`top type` 又称作通用父类型，基本上涵盖了类型系统中所有可能的值。

![输入图片说明](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/519b8b7f671748108ad5c7fc9f927c88~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

## top type `any`


如果一个值是 any 类型，几乎对它做任何操作都没问题。
```ts

function func(value: any) {
  // 可以做数字操作
  5 * value;

  // 可以假设一定有 propName 属性
  value.propName;

  // 可以假设数字索引存在
  value[123];
}
```

每种类型都可赋值给any类型:

```ts
let storageLocation: any;

storageLocation = null;
storageLocation = true;
storageLocation = {};
```

any类型也可赋值给任何类型：

```ts
function func(value: any) {
  const a: null = value;
  const b: boolean = value;
  const c: object = value;
}
```

一旦用了 any，我们就失去了 TypeScript 静态类型系统提供的所有保护。

更好的选择是：

1. 使用更具体的类型
2. 使用 unknown

总而言之，使用 any 是最下策。

### 例子：`JSON.parse()`

`JSON.parse()` 的结果根据输入而动态的改变，所以只能用 any 类型（我从类型签名中移除了参数 `reviver`）

```ts
JSON.parse(text: string): any;
```

`JSON.parse()` 是在 unknown 类型出现之前被添加到 TypeScript 系统中的，否则它的返回类型应该是 unknown。

### 例子：`String()`

函数 `String()` 可以将任意类型的值转为字符串，所以具有以下类型签名：

```ts
interface StringConstructor {
  (value?: any): string;
  // ···
}
```

## Top type `unknown`

unknown 类型是安全版本的 any，每当你想用 any 的时候，先试试用 unknown。

any 允许你做几乎所有操作，unknown 的限制性则更多。

当我们对 unknown 类型的值做任何操作之前，我们必须先这样缩窄它的类型：

- [Type assertions](https://exploringjs.com/tackling-ts/ch_type-assertions.html):

```ts
function func(value: unknown) {
  // @ts-expect-error: Object is of type 'unknown'.
  value.toFixed(2);

  // Type assertion:
  (value as number).toFixed(2); // OK
}
```

- Equality:

```ts
function func(value: unknown) {
  // @ts-expect-error: 
  // Object is of type 'unknown'.
  value * 5;

  if (value === 123) { // equality
    // 推断出类型: 123
    value;

    value * 5; // OK
  }
}
```

- [Type guards](https://exploringjs.com/tackling-ts/ch_type-guards-assertion-functions.html):

```ts
function func(value: unknown) {
  // @ts-expect-error:
  // Object is of type 'unknown'.
  value.length;
  
  // type guard
  if (typeof value === 'string') { 
    // 推断出类型: string
    value;

    value.length; // OK
  }
}
```

- [Assertion functions](https://exploringjs.com/tackling-ts/ch_type-guards-assertion-functions.html):

```ts
function func(value: unknown) {
  // @ts-expect-error: 
  // Object is of type 'unknown'.
  value.test('abc');

  assertIsRegExp(value);

  // 推断出类型: RegExp
  value;

  value.test('abc'); // OK
}

/** An assertion function */
function assertIsRegExp(arg: unknown): asserts arg is RegExp {
  if (! (arg instanceof RegExp)) {
    throw new TypeError('Not a RegExp: ' + arg);
  }
}
```