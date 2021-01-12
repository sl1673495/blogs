---
title: 'Vue3 TypeScript 之 Ref 类型从零实现'
date: '2020-04-13'
spoiler: ''
---

Vue3 中，`ref` 是一个新出现的 api，不太了解这个 api 的小伙伴可以先看 [官方api文档](https://vue-composition-api-rfc.netlify.com/api.html#ref)。

简单介绍来说，响应式的属性依赖一个复杂类型的`载体`，想象一下这样的场景，你有一个数字 `count` 需要响应式的改变。

```ts
const count = reactive(2)

// ❌ 什么鬼
count = 3
```

这样肯定是无法触发响应式的，因为 Proxy 需要对一个复杂类型上的某个属性的访问进行拦截，而不是直接拦截一个变量的改变。

于是就有了 `ref` 这个函数，它会为简单类型的值生成一个形为 `{ value: T }` 的包装，这样在修改的时候就可以通过 `count.value = 3` 去触发响应式的更新了。

```ts
const count = ref(2)

// ✅ (*^▽^*) 完全可以
count.value = 3
```

那么，`ref` 函数所返回的类型 `Ref`，就是本文要讲解的重点了。

为什么说 `Ref` 是个比较复杂的类型呢？假如 `ref` 函数中又接受了一个 `Ref` 类型的参数呢？Vue3 内部其实是会帮我们层层解包，只剩下最里层的那个 `Ref` 类型。

它是支持嵌套后解包的，最后只会剩下 `{ value: number }` 这个类型。

```js
const count = ref(ref(ref(ref(2))))
```

这是一个好几层的嵌套，按理来说应该是 `count.value.value.value.value` 才会是 `number`，但是在 vscode 中，鼠标指向 `count.value` 这个变量后，提示出的类型就是 number，这是怎么做到的呢？

本文尝试给出一种捷径，通过逐步实现这个复杂需求，来倒推出 TS 的高级技巧需要学习哪些知识点。

1. 泛型的反向推导。
2. 索引签名
3. 条件类型
4. keyof
5. infer

先逐个拆解这些知识点吧，注意，如果本文中的这些知识点还有所不熟，一定要在代码编辑器中反复敲击调试，刻意练习，也可以在 [typescript-playground](https://www.typescriptlang.org/play) 中尽情玩耍。

## 泛型的反向推导

泛型的正向用法很多人都知道了。

```ts
type Value<T> = T

type NumberValue = Value<number>
```

这样，`NumberValue` 解析出的类型就是 number，其实就类似于类型系统里的传参。

那么反向推导呢？

```js
function create<T>(val: T): T

let num: number

const c= create(num)
```
[在线调试](https://www.typescriptlang.org/play?#code/GYVwdgxgLglg9mABBATgUwIZTQHgCoB8AFAG4YA2AXIngJTV4BQj5aUiYIAttZ1wEZoUzCAgDO7CAF5k6LGiJ9aQA)

这里泛型没有传入，居然也能推断出 `value` 的类型是 number。

因为 `create<T>` 这里的泛型 T 被分配给了传入的参数 `value: T`，然后又用这个 T 直接作为返回的类型，

简单来说，这里的三个 T 被**关联起来**了，并且在传入 `create(2)` 的那一刻，这个 T 被统一推断成了 number。

```js
function create<2>(value: 2): 2
```

### 阅读资料
具体可以看文档里的[泛型章节](https://www.tslang.cn/docs/handbook/generics.html)。

## 索引签名
假设我们有一个这样的类型：
```js
type Test = {
  foo: number;
  bar: string
}

type N = Test['foo'] // number
```

可以通过类似 JavaScript 中的对象属性查找的语法来找出对应的类型。

具体可以看[这里的介绍](https://jkchao.github.io/typescript-book-chinese/typings/indexSignatures.html)，有比较详细的例子。

## 条件类型
假设我们有一个这样的类型：
```ts
type IsNumber<T> = T extends number ? 'yes' : 'no';

type A = IsNumber<2> // yes
type B = isNumber<'3'> // no
```

[在线调试](https://www.typescriptlang.org/play?#code/C4TwDgpgBAkgzgOQK4FsBGEBOAeAKgPigF4pcoIAPYCAOwBM4obUNMoB+KAchAji6gAubjQD2XANwAoKaEhQAgsViIWWbACZCAem1RecWeGgAhZfGTp1XAMxcdesUA)

这就是一个典型的条件类型，用 `extends` 关键字配合三元运算符来判断传入的泛型是否可分配给 `extends` 后面的类型。

同时也支持多层的三元运算符（后面会用到）：

```ts
type TypeName<T> = T extends string
  ? "string"
  : T extends boolean
      ? "boolean"
      : "object";

type T0 = TypeName<string>; // "string"
type T1 = TypeName<"a">; // "string"
type T2 = TypeName<true>; // "boolean"
```

### 阅读资料
具体讲解可以看文档中的 [conditional types](https://www.typescriptlang.org/docs/handbook/advanced-types.html#conditional-types) 部分。

## keyof

`keyof` 操作符是 TS 中用来获取对象的 key 值集合的，比如：
```ts
type Obj = {
  foo: number;
  bar: string;
}

type Keys = keyof Obj // "foo" | "bar"
```

这样就轻松获取到了对象 key 值的联合类型：`"foo" | "bar"`。

它也可以用在遍历中：

```ts
type Obj = {
  foo: number;
  bar: string;
}

type Copy = {
  [K in keyof Obj]: Obj[K]
}

// Copy 得到和 Obj 一模一样的类型
```
[在线调试](https://www.typescriptlang.org/play/index.html?ssl=1&ssc=1&pln=2&pc=22#code/C4TwDgpgBA8gRgKygXigbwFBSgMwPZ4BcUAdgK4C2cEATgNxZRwCGNxAzsDQJYkDmDAL4YMoSFADCeMCBTpGAbQDSUXlADWEEHhyxEAXWLwEy-RkFA)

可以看出，遍历的过程中右侧也可以通过索引直接访问到原类型 `Obj` 中对应 key 的类型。

### 阅读资料
[index-types](https://www.typescriptlang.org/docs/handbook/advanced-types.html#index-types)

## infer

这是一个比较难的点，文档中对它的描述是 **条件类型中的类型推断**。

它的出现使得 `ReturnType`、 `Parameters` 等一众工具类型的支持都成为可能，是 TypeScript 进阶必须掌握的一个知识点了。

注意前置条件，它一定是出现在条件类型中的。

```ts
type Get<T> = T extends infer R ? R: never
```

注意，`infer R` 的位置代表了一个未知的类型，可以理解为在条件类型中给了它一个占位符，然后就可以在后面的三元运算符中使用它。

```ts
type T = Get<number>

// 经过计算
type Get<number> = number extends infer number ? number: never

// 得到
number
```

它的使用非常灵活，它也可以出现在泛型位置：
```ts
type Unpack<T> = T extends Array<infer R> ? R : T
```

```ts
type NumArr = Array<number>
type U = Unpack<NumArr>

// 经过计算
type Unpack<Array<number>> = Array<number> extends Array<infer R> ? R : T

// 得到
number
```

[在线调试](https://www.typescriptlang.org/play?#code/C4TwDgpgBAqgdmAhgYwNYB4AqA+KBeKTKCAD2AjgBMBnKAQQCcHER0BLOAMwgagCVcAfn5QAXIQBQE0JCgA5AK4BbRrwKqW6OMoBGPbFJnQY+WAhQZFKprgD0tqNqV6GQA)

仔细看看，是不是有那么点感觉了，它就是对于 `extends` 后面未知的某些类型进行一个占位 `infer R`，后续就可以使用推断出来的 `R` 这个类型。

### 阅读资料
[官网文档](https://www.typescriptlang.org/docs/handbook/advanced-types.html#conditional-types)

[巧用 TypeScript（五）-- infer](https://jkchao.cn/article/5c8a4d99e53a054fad647c15)


## 简化实现
好了，有了这么多的前置知识，我们来摩拳擦掌尝试实现一下这个 `Ref` 类型。

我们已经了解到，`ref` 这个函数就是把一个值包裹成 `{value: T}` 这样的结构：

我们的目的是，让 `ref(ref(ref(2)))` 这种嵌套用法，也能顺利的提示出 number 类型。

### ref
```ts
// 这里用到了泛型的默认值语法 <T = any>
type Ref<T = any> = {
  value: T
}

function ref<T>(value: T): Ref<T>

const count = ref(2)

count.value // number
```

默认情况很简单，结合了我们上面提到的几个小知识点很快就能做出来。

如果传入给函数的 value 也是一个 `Ref` 类型呢？是不是很快就想到 `extends` 关键字了。

```ts
function ref<T>(value: T): T extends Ref 
  ? T 
  : Ref<UnwarpRef<T>>
```

先解读 `T extends Ref` 的情况，如果 `value` 是 `Ref` 类型，函数的返回值就原封不动的是这个 `Ref` 类型。

那么对于 `ref(ref(2))` 这种类型来说，内层的 `ref(2)` 返回的是 `Ref<number>` 类型，

外层的 `ref` 读取到 `ref(Ref<number>)` 这个类型以后，

由于此时的 `value` 符合 `extends Ref` 的定义，

所以 `Ref<number>` 又被原封不动的返回了，这就形成了解包。

那么关键点就在于后半段逻辑，`Ref<UnwarpRef<T>>` 是怎么实现的，

它用来决定 `ref(2)` 返回的是 `Ref<number>`，

并且嵌套的对象 `ref({ a: 1 })`，返回 `Ref<{ a: number }>`

并且嵌套的对象中包含 `Ref` 类型也会被解包：
```ts
const count = ref({
  foo: ref('1'),
  bar: ref(2)
})

// 推断出
const count: Ref<{
  foo: string;
  bar: number;
}>
```

那么其实本文的关键也就在于，应该如何实现这个 `UnwarpRef` 解包函数了。

根据我们刚刚学到的 `infer` 知识，从 `Ref` 的泛型中提取出它的泛型类型并不难：

### UnwarpRef

```ts
type UnwarpRef<T> = T extends Ref<infer R> ? R : T

UnwarpRef<Ref<number>> // number
```

但这只是单层解包，如果 `infer R` 中的 `R` 还是 `Ref` 类型呢？

我们自然的想到了递归声明这个 `UnwarpRef` 类型：

```ts
// X！ Type alias 'UnwarpRef' circularly references itself.ts(2456)
type UnwarpRef<T> = T extends Ref<infer R> 
    ? UnwarpRef<R> 
    : T
```

报错了，不允许循环引用自己！

### 递归 UnwarpRef
但是到此为止了吗？当然没有，有一种机制可以绕过这个递归限制，那就是配合 **索引签名**，并且增加其他的能够终止递归的条件，在本例中就是 `other` 这个索引，它原样返回 `T` 类型。 

```ts
type UnwarpRef<T> = {
  ref: T extends Ref<infer R> ? UnwarpRef<R> : T
  other: T
}[T extends Ref ? 'ref' : 'other']
```

### 支持字符串和数字
拆解开来看这个类型，首先假设我们调用了 `ref(ref(2))` 我们其实会传给 `UnwarpRef` 一个泛型：

```ts
UnwarpRef<Ref<Ref<number>>>
```

那么第一次走入 `[T extends Ref ? 'ref' : 'other']` 这个索引的时候，匹配到的是 `ref` 这个字符串，然后它去
```ts
type UnwarpRef<Ref<Ref<number>>> = {
  // 注意这里和 infer R 对应位置的匹配 得到的是 Ref<number>
  ref: Ref<Ref<number>> extends Ref<infer R> ? UnwarpRef<R> : T
}['ref']
```

匹配到了 `ref` 这个索引，然后通过用 `Ref<Ref<number>>` 去匹配 `Ref<infer R>` 拿到 `R` 也就是解包了一层过后的 `Ref<number>`。

再次传给 `UnwarpRef<Ref<number>>` ，又经过同样的逻辑解包后，这次只剩下 `number` 类型传递了。

也就是 `UnwarpRef<number>`，那么这次就不太一样了，索引签名计算出来是 `['other']`，

也就是
```ts
type UnwarpRef<number> = {
  other: number
}['other']
```

自然就解包得到了 `number` 这个类型，终止了递归。

### 支持对象
考虑一下这种场景：

```ts
const count = ref({
  foo: ref(1),
  bar: ref(2)
})
```
那么，`count.value.foo` 推断的类型应该是 `number`，这需要我们用刚刚的遍历索引和 `keyof` 的知识来做，并且在索引签名中再增加对 `object` 类型的支持：

```ts
type UnwarpRef<T> = {
  ref: T extends Ref<infer R> ? UnwarpRef<R> : T
  // 注意这里
  object: { [K in keyof T]: UnwarpRef<T[K]> }
  other: T
}[T extends Ref 
  ? 'ref' 
  : T extends object 
    ? 'object' 
    : 'other']
```

这里在遍历 `K in keyof T` 的时候，只要对值类型 `T[K]` 再进行解包 `UnwarpRef<T[K]>` 即可，如果 `T[K]` 是个 `Ref` 类型，则会拿到 `Ref` 的 `value` 的原始类型。

## 简化版完整代码
```js
type Ref<T = any> = {
  value: T
}

type UnwarpRef<T> = {
  ref: T extends Ref<infer R> ? UnwarpRef<R> : T
  object: { [K in keyof T]: UnwarpRef<T[K]> }
  other: T
}[T extends Ref 
  ? 'ref' 
  : T extends object 
    ? 'object' 
    : 'other']

function ref<T>(value: T): T extends Ref ? T : Ref<UnwarpRef<T>>
```

[在线调戏最终版](https://www.typescriptlang.org/play/?ssl=1&ssc=1&pln=14&pc=22#code/C4TwDgpgBAShBmAeAKlAvFAhgOxAPnSgG8BYAKCigDdMAbAVwgC4plyBfc80SKAVWwB3TACcwcJMgIZSFKCIQtUEAB7AI2ACYBnWAkQBLbPAgjYBAPz8ho8fpgEl5SgHsARgCsIAY2AsiUADaANJQRlAA1hAgLvCsALosAsJiEigh8QScci7AABamTmTsgcpqGjp6cc5QVgDkCvB1UDVKUKrqWrruXr4tcpT1PT7AzTWULHW5BSJ18Vxk8PTYvgYu2PL6UgAUNAzMrACUbR0VuhK1rFAsacm2aVJ4C97r2sBQL8vvGI3bspTwFwuFi-OoARjqhwANDU3KIQQhtgAmQ4cVFkcifbDAAB0e0YOMBLigAHoSVBsPQALZuUzkIA)

## 源码

这里还是放一下 Vue3 里的源码，在源码中对于数组、对象和计算属性的 `ref` 也做了相应的处理，但是相信经过了上面简化版的实现后，你对于这个复杂版的原理也可以进一步的掌握了吧。

```ts
export interface Ref<T = any> {
  [isRefSymbol]: true
  value: T
}

export function ref<T>(value: T): T extends Ref ? T : Ref<UnwrapRef<T>>

export type UnwrapRef<T> = {
  cRef: T extends ComputedRef<infer V> ? UnwrapRef<V> : T
  ref: T extends Ref<infer V> ? UnwrapRef<V> : T
  array: T
  object: { [K in keyof T]: UnwrapRef<T[K]> }
}[T extends ComputedRef<any>
  ? 'cRef'
  : T extends Array<any>
    ? 'array'
    : T extends Ref | Function | CollectionTypes | BaseTypes
      ? 'ref' // bail out on types that shouldn't be unwrapped
      : T extends object ? 'object' : 'ref']
```

乍一看很劝退，没错，我一开始也被这段代码所激励，开始了为期几个月的 TypeScript 恶补生涯。资料真的很难找，这里面涉及的一些高级技巧需要经过反复的练习和实践，才能学下来并且自如的运用出来。

## 总结

跟着尤小右学源码只是一个噱头，这个递归类型其实是一位外国人提的一个 [pr](https://github.com/vuejs/vue-next/commit/c6b7afcc23faefd8c504c3c5705ecb5b0f4be0fd#diff-2751769c8b46d7bef1f06b254c0257f1) 去实现的，一开始 TypeScript 不支持递归的时候，尤大写了 9 层手动解包，非常的吓人，可以去这个 pr 里看看，茫茫的一片红。

当然，这也可以看出 TypeScript 是在不断的进步和优化中的，非常期待未来它能够越来越强大。

相信看完本文的你，一定会对上文中提到的一些高级特性有了进一步的掌握。在 Vue3 到来之前，提前学点 TypeScript ，未雨绸缪总是没错的！

关于 TypeScript 的学习路径，我也总结在了我之前的文章 [写给初中级前端的高级进阶指南-TypeScript](https://juejin.im/post/5e7c08bde51d455c4c66ddad#heading-26) 中给出了很好的资料，大家一起加油吧！

## 求点赞
如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我持续进行创作的动力，让我知道你喜欢看我的文章吧~

## ❤️感谢大家

关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)

