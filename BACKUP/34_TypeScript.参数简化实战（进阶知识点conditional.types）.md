---
title: 'TypeScript 参数简化实战（进阶知识点conditional types）'
date: '2020-02-05'
spoiler: ''
---

TypeScript中有一项相当重要的进阶特性：`conditional types`，这个功能出现以后，很多积压已久的TypeScript功能都可以轻而易举的实现了。  

那么本篇文章就会通过一个简单的功能：把
```js
distribute({
    type: 'LOGIN',
    email: string
})
```
这样的函数调用方式给简化为：
```js
distribute('LOGIN', {
    email: string
})
```

没错，它只是节省了几个字符串，但是却是一个非常适合我们深入学习条件类型的实战。

## 通过这篇文章，你可以学到以下特性在实战中是如何使用的：
1. 🎉TypeScript的高级类型（[Advanced Type](https://www.typescriptlang.org/docs/handbook/advanced-types.html)）
2. 🎉Conditional Types (条件类型)
3. 🎉Distributive conditional types (分布条件类型)
4. 🎉Mapped types（映射类型）
5. 🎉函数重载  

## conditional types的第一次使用
先简单的看一个条件类型的示例：  

```js
function process<T extends string | null>(
  text: T
): T extends string ? string : null {
  ...
}
```

```ts
A extends B ? C : D
```
这样的语法就叫做条件类型，`A`, `B`, `C`和`D`可以是任何类型表达式。  

## 可分配性
这个`extends`关键字是条件类型的核心。 `A extends B`恰好意味着可以将类型A的任何值安全地分配给类型B的变量。在类型系统术语中，我们可以说“ A可分配给B”。

从结构上来讲，我们可以说`A extends B`，就像“ A是B的超集”，或者更确切地说，“ A具有B的所有特性，也许更多”。  

举个例子来说 `{ foo: number, bar: string } extends { foo: number }`是成立的，因为前者显然是后者的超集，比后者拥有更具体的类型。  

## 分布条件类型

官方文档中，介绍了一种操作，叫 `Distributive conditional types`  

简单来说，传入给`T extends U`中的`T`如果是一个联合类型`A | B | C`，则这个表达式会被展开成

```
(A extends U ? X : Y) | (B extends U ? X : Y) | (C extends U ? X : Y)
```  
条件类型让你可以过滤联合类型的特定成员。 为了说明这一点，假设我们有一个称为Animal的联合类型：

```
type Animal = Lion | Zebra | Tiger | Shark
```

再假设我们要编写一个类型，来过滤出Animal中属于“猫”的那些类型  

```
type ExtractCat<A> = A extends { meow(): void } ? A : never

type Cat = ExtractCat<Animal>
// => Lion | Tiger
```
接下来，Cat的计算过程会是这样子的：
```
type Cat =
  | ExtractCat<Lion>
  | ExtractCat<Zebra>
  | ExtractCat<Tiger>
  | ExtractCat<Shark>
```

然后，它被计算成联合类型
```
type Cat = Lion | never | Tiger | never
```

然后，联合类型中的never没什么意义，所以最后的结果的出来了：
```
type Cat = Lion | Tiger
```  

记住这样的计算过程，记住ts这个把联合类型如何分配给条件类型，接下来的实战中会很有用。  

## 分布条件类型的真实用例  

举一个类似`redux`中的`dispatch`的例子。  

首先，我们有一个联合类型`Action`，用来表示所有可以被dispatch接受的参数类型：

```js
type Action =
  | {
      type: "INIT"
    }
  | {
      type: "SYNC"
    }
  | {
      type: "LOG_IN"
      emailAddress: string
    }
  | {
      type: "LOG_IN_SUCCESS"
      accessToken: string
    }
```

然后我们定义这个dispatch方法：

```js
declare function dispatch(action: Action): void

// ok
dispatch({
  type: "INIT"
})

// ok
dispatch({
  type: "LOG_IN",
  emailAddress: "david.sheldrick@artsy.net"
})

// ok
dispatch({
  type: "LOG_IN_SUCCESS",
  accessToken: "038fh239h923908h"
})
```  

这个API是类型安全的，当TS识别到type为`LOG_IN`的时候，它会要求你在参数中传入`emailAddress`这个参数，这样才能完全满足联合类型中的其中一项。  

到此为止，我们可以去和女朋友约会了，此文完结。  

等等，我们好像可以让这个api变得更简单一点：
```js
dispatch("LOG_IN_SUCCESS", {
  accessToken: "038fh239h923908h"
})
```  

好，推掉我们的约会，打电话给我们的女朋友！取消！  

## 参数简化实现

首先，利用方括号选择出`Action`中的所有`type`，这个技巧很有用。
```js
type ActionType = Action["type"]
// => "INIT" | "SYNC" | "LOG_IN" | "LOG_IN_SUCCESS"
```

但是第二个参数的类型取决于第一个参数。 我们可以使用类型变量来对该依赖关系建模。

```js
declare function dispatch<T extends ActionType>(
  type: T,
  args: ExtractActionParameters<Action, T>
): void
```

注意，这里就用到了`extends`语法，规定了我们的入参`type`必须是`ActionType`中一部分。  

注意这里的第二个参数args，用`ExtractActionParameters<Action, T>`这个类型来把type和args做了关联，  

来看看`ExtractActionParameters`是如何实现的：  

```js
type ExtractActionParameters<A, T> = A extends { type: T } ? A : never
```
在这次实战中，我们第一次运用到了条件类型，`ExtractActionParameters<Action, T>`会按照我们上文提到的`分布条件类型`，把Action中的4项依次去和`{ type: T }`进行比对，找出符合的那一项。  

来看看如何使用它：

```js
type Test = ExtractActionParameters<Action, "LOG_IN">
// => { type: "LOG_IN", emailAddress: string }
```  

这样就筛选出了type匹配的一项。  

接下来我们要把type去掉，第一个参数已经是type了，因此我们不想再额外声明type了。  

```js
// 把类型中key为"type"去掉
type ExcludeTypeField<A> = { [K in Exclude<keyof A, "type">]: A[K] }
```
这里利用了`keyof`语法，并且利用内置类型`Exclude`把`type`这个key去掉，因此只会留下额外的参数。

```js
type Test = ExcludeTypeField<{ type: "LOG_IN", emailAddress: string }>
// { emailAddress: string }
```  

到此为止，我们就可以实现上文中提到的参数简化功能：  

```js
// ok
dispatch({
  type: "LOG_IN",
  emailAddress: "david.sheldrick@artsy.net"
})
```


## 利用重载进一步优化

到了这一步为止，虽然带参数的Action可以完美支持了，但是对于"INIT"这种不需要传参的Action，我们依然要写下面这样代码： 

```js
dispatch("INIT", {})
```

这肯定是不能接受的！所以我们要利用TypeScript的函数重载功能。  

```ts
// 简单参数类型
function dispatch<T extends SimpleActionType>(type: T): void

// 复杂参数类型
function dispatch<T extends ComplexActionType>(
  type: T,
  args: ExtractActionParameters<Action, T>,
): void

// 实现
function dispatch(arg: any, payload?: any) {}
```

那么关键点就在于`SimpleActionType`和`ComplexActionType`要如何实现了，  

`SimpleActionType`顾名思义就是除了type以外不需要额外参数的Action类型，  

```js
type SimpleAction = ExtractSimpleAction<Action>
```
我们如何定义这个`ExtractSimpleAction`条件类型？  

如果我们从这个Action中删除`type`字段，并且结果是一个空的接口，  

那么这就是一个`SimpleAction`。 所以我们可能会凭直觉写出这样的代码：  

```
type ExtractSimpleAction<A> = ExcludeTypeField<A> extends {} ? A : never
```  

但这样是行不通的，几乎所有的类型都可以extends {}，因为{}太宽泛了。  

我们应该反过来写：  

```
type ExtractSimpleAction<A> = {} extends ExcludeTypeField<A> ? A : never
```

现在，如果`ExcludeTypeField <A>`为空，则extends表达式为true，否则为false。  

但这仍然行不通！ 因为`分布条件类型`仅在extends关键字左侧是**类型变量**时发生。  

分布条件件类型仅发生在如下场景：
```
type Blah<Var> = Var extends Whatever ? A : B
```

而不是：  
```
type Blah<Var> = Foo<Var> extends Whatever ? A : B
type Blah<Var> = Whatever extends Var ? A : B
```

但是我们可以通过一些小技巧绕过这个限制：  

```
type ExtractSimpleAction<A> = A extends any
  ? {} extends ExcludeTypeField<A>
    ? A
    : never
  : never
```

`A extends any`是一定成立的，这只是用来绕过ts对于分布条件类型的限制，而我们真正想要做的条件判断被放在了中间，因此Action联合类型中的每一项又能够分布的去匹配了。

那么我们就可以简单的筛选出所有不需要额外参数的type
```
type SimpleAction = ExtractSimpleAction<Action>
type SimpleActionType = SimpleAction['type']
```

再利用Exclude取反，找到复杂类型：
```
type ComplexActionType = Exclude<ActionType, SimpleActionType>
```

到此为止，我们所需要的功能就完美实现了：

```js
// 简单参数类型
function dispatch<T extends SimpleActionType>(type: T): void
// 复杂参数类型
function dispatch<T extends ComplexActionType>(
  type: T,
  args: ExtractActionParameters<Action, T>,
): void
// 实现
function dispatch(arg: any, payload?: any) {}

// ok
dispatch("SYNC")

// ok
dispatch({
  type: "LOG_IN",
  emailAddress: "david.sheldrick@artsy.net"
})
```

## 总结
本文的实战示例来自国外大佬的博客，我结合个人的理解整理成了这篇文章。  

中间涉及到的一些进阶的知识点，如果小伙伴们不太熟悉的话，可以参考各类文档中的定义去反复研究，相信你会对TypeScript有更深一步的了解。

## 参考资料
https://artsy.github.io/blog/2018/11/21/conditional-types-in-typescript/

## 源码
https://github.com/sl1673495/typescript-codes/blob/master/src/dispatch-conditional-types-with-builtin-types.ts