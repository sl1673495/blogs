# [TypeScript进阶实现智能类型推导的简化版Vuex](https://github.com/sl1673495/blogs/issues/28)

之前几篇讲TypeScript的文章中，我带来了在React中的一些小实践  

[React + TypeScript + Hook 带你手把手打造类型安全的应用。](https://juejin.im/post/5dddde68e51d4541c24658c1)  

[React Hook + TypeScript 手把手带你打造use-watch自定义Hook，实现Vue中的watch功能。](https://juejin.im/post/5df1ede4f265da33ec7db049)

这篇文章我决定更进一步，直接用TypeScript实现一个类型安全的简易版的Vuex。  

## 这篇文章适合谁：
1. 已经学习TypeScript基础，需要一点进阶玩法的你。
2. 自己喜欢写一些开源的小工具，需要进阶学习TypeScript类型推导。（在项目中一般ts运用的比较浅层，大部分情况在写表面的interface）。
3. 单纯的想要进阶学习TypeScript。


## 通过这篇文章，你可以学到以下特性在实战中是如何使用的：
1. 🎉TypeScript的高级类型（[Advanced Type](https://www.typescriptlang.org/docs/handbook/advanced-types.html)）
1. 🎉TypeScript中利用泛型进行反向类型推导。([Generics](https://www.typescriptlang.org/docs/handbook/generics.html))
2. 🎉Mapped types（映射类型）
3. 🎉Distributive Conditional Types（条件类型分配）
4. 🎉TypeScript中Infer的实战应用（[Vue3源码里infer的一个很重要的使用](https://github.com/vuejs/vue-next/blob/985f4c91d9d3f47e1314d230c249b3faf79c6b90/packages/reactivity/src/ref.ts#L89)）  

希望通过这篇文章，你可以对TypeScript的高级类型实战应用得心应手，对于未来想学习Vue3源码的小伙伴来说，类型推断和`infer`的用法也是必须熟悉的。 

## 写在前面：
本文实现的Vuex只有很简单的`state`，`action`和`subscribeAction`功能，因为Vuex当前的组织模式非常不适合类型推导（Vuex官方的type库目前推断的也很简陋），所以本文中会有一些和官方不一致的地方，这些是刻意的为了类型安全而做的，本文的主要目标是学习TypeScript，而不是学习Vuex，所以请小伙伴们不要嫌弃它代码啰嗦或者和Vuex不一致。 🚀


## vuex骨架
首先定义我们Vuex的骨架。

```ts
export default class Vuex<S, A> {
  state: S

  action: Actions<S, A>

  constructor({ state, action }: { state: S; action: Actions<S, A> }) {
    this.state = state;
    this.action = action;
  }

  dispatch(action: any) {
  }
}
```

首先这个Vuex构造函数定了两个泛型`S`和`A`，这是因为我们需要推出`state`和`action`的类型，由于subscribeAction的参数中需要用到state和action的类型，dispatch中则需要用到`action`的key的类型（比如`dispatch({type: "ADD"})`中的type需要由对应 `actions: { ADD() {} }`）的key值推断。  

然后在构造函数中，把S和state对应，把Actions<S, A>和传入的action对应。
```ts
constructor({ state, action }: { state: S; action: Actions<S, A> }) {
  this.state = state;
  this.action = action;
}
```  

Actions这里用到了映射类型，它等于是遍历了传入的A的key值，然后定义每一项实际上的结构，
```ts
export type Actions<S, A> = {
  [K in keyof A]: (state: S, payload: any) => Promise<any>;
};
```
看看我们传入的actions
```ts
const store = new Vuex({
  state: {
    count: 0,
    message: '',
  },
  action: {
    async ADD(state, payload) {
      state.count += payload;
    },
    async CHAT(state, message) {
      state.message = message;
    },
  },
});
```

是不是类型正好对应上了？此时ADD函数的形参里的state就有了类型推断，它就是我们传入的state的类型。

![state](https://user-gold-cdn.xitu.io/2020/1/9/16f880d77a929b47?w=463&h=250&f=png&s=106982)  

这是因为我们给Vuex的构造函数传入state的时候，S就被反向推导为了state的类型，也就是`{count: number, message: string}`，这时S又被传给了`Actions<S, A>`， 自然也可以在action里获得state的类型了。 

现在有个问题，我们现在的写法里没有任何地方能体现出`payload`的类型，（这也是Vuex设计所带来的一些缺陷）所以我们也只能写成any，但是我们本文的目标是类型安全。  

## dispatch的类型安全
下面先想点办法实现`store.dispatch`的类型安全：
1. type需要自动提示。
2. type填写了以后，需要提示对应的payload的type。

所以参考`redux`的玩法，我们手动定义一个Action Types的联合类型。

```ts
const ADD = 'ADD';
const CHAT = 'CHAT';

type AddType = typeof ADD;
type ChatType = typeof CHAT;

type ActionTypes =
  | {
      type: AddType;
      payload: number;
    }
  | {
      type: ChatType;
      payload: string;
    };

```  

在`Vuex`中，我们新增一个辅助Ts推断的方法，这个方法原封不动的返回dispatch函数，但是用了`as`关键字改写它的类型，我们需要把ActionTypes作为泛型传入：
```
export default class Vuex<S, A> {
  ... 
  
  createDispatch<A>() {
    return this.dispatch.bind(this) as Dispatch<A>;
  }
}
```

Dispatch类型的实现相当简单，直接把泛型A交给第一个形参action就好了，由于ActionTypes是联合类型，Ts会严格限制我们填写的action的类型必须是AddType或者ChatType中的一种，并且填写了AddType后，payload的类型也必须是number了。  


```ts
export interface Dispatch<A> {
  (action: A): any;
}
```

然后使用它构造dispatch
```ts
// for TypeScript support
const dispatch = store.createDispatch<ActionTypes>();
```  

 目标达成：

![type](https://user-gold-cdn.xitu.io/2020/1/9/16f881771ec7ca80?w=715&h=85&f=png&s=23458)

![payload](https://user-gold-cdn.xitu.io/2020/1/9/16f8817d3a2346ab?w=713&h=107&f=png&s=33185)  

## action形参中payload的类型安全  

此时虽然store.diaptch完全做到了类型安全，但是在声明action传入vuex构造函数的时候，我不想像这样手动声明，  

```ts
const store = new Vuex({
  state: {
    count: 0,
    message: '',
  },
  action: {
    async [ADD](state, payload: number) {
      state.count += payload;
    },
    async [CHAT](state, message: string) {
      state.message = message;
    },
  },
});  
```

因为这个类型在刚刚定义的ActionTypes中已经有了，秉着`DRY`的原则，我们继续折腾吧。  

首先现在我们有这些佐料：
```ts
const ADD = 'ADD';
const CHAT = 'CHAT';

type AddType = typeof ADD;
type ChatType = typeof CHAT;

type ActionTypes =
  | {
      type: AddType;
      payload: number;
    }
  | {
      type: ChatType;
      payload: string;
    };

```  

所以我想通过一个类型工具，能够传入AddType给我返回number，传入ChatType给我返回message：  

它大概是这个样子的：
```
type AddPayload = PickPayload<ActionTypes, AddType> // number
type ChatPayload = PickPayload<ActionTypes, ChatType> // string
```

为了实现它，我们需要用到[distributive-conditional-types](https://mariusschulz.com/blog/conditional-types-in-typescript#distributive-conditional-types)，不熟悉的同学可以好好看看这篇文章。

简单的来说，如果我们把一个联合类型
```ts
type A = string | number
```
传递给一个用了extends关键字的类型工具：
```ts
type PickString<T> = T extends string ? T: never

type T1 = PickString<A> // string
```

它并不是像我们想象中的直接去用string | number直接匹配是否extends，而是把联合类型拆分开来，一个个去匹配。
```
type PickString<T> = 
| string extends string ? T: never 
| number extends string ? T: never
```  

所以返回的类型是`string | never`，由由于never在联合类型中没什么意义，所以就被过滤成`string`了

借由这个特性，我们就有思路了，这里用到了`infer`这个关键字，Vue3中也有很多推断是借助它实现的，它只能用在extends的后面，代表一个还未出现的类型，关于infer的玩法，详细可以看这篇文章：[巧用 TypeScript（五）---- infer](https://segmentfault.com/a/1190000018514540?utm_source=tag-newest)

```
export type PickPayload<Types, Type> = Types extends {
  type: Type;
  payload: infer P;
}
  ? P
  : never;
```

我们用Type这个字符串类型，让ActionTypes中的每一个类型一个个去过滤匹配，比如传入的是AddType:
```
PickPayload<ActionTypes, AddType>
```

则会被分布成：
```ts
type A = 
  | { type: AddType;payload: number;} extends { type: AddType; payload: infer P }
  ? P
  : never 
  | 
  { type: ChatType; payload: string } extends { type: AddType; payload: infer P }
  ? P
  : never;
```

注意infer P的位置，被放在了payload的位置上，所以第一项的type在命中后, P也被自动推断为了number，而三元运算符的 ? 后，我们正是返回了P，也就推断出了number这个类型。  

这时候就可以完成我们之前的目标了，也就是根据AddType这个类型推断出payload参数的类型，`PickPayload`这个工具类型应该定位成vuex官方仓库里提供的辅助工具，而在项目中，由于ActionType已经确定，所以我们可以进一步的提前固定参数。（有点类似于函数柯里化）
```ts
type PickStorePayload<T> = PickPayload<ActionTypes, T>;
```
此时，我们定义一个类型安全的Vuex实例所需要的所有辅助类型都定义完毕：

```ts
const ADD = 'ADD';
const CHAT = 'CHAT';

type AddType = typeof ADD;
type ChatType = typeof CHAT;

type ActionTypes =
  | {
      type: AddType;
      payload: number;
    }
  | {
      type: ChatType;
      payload: string;
    };

type PickStorePayload<T> = PickPayload<ActionTypes, T>;
```

使用起来就很简单了：  

```ts
const store = new Vuex({
  state: {
    count: 0,
    message: '',
  },
  action: {
    async [ADD](state, payload: PickStorePayload<AddType>) {
      state.count += payload;
    },
    async [CHAT](state, message: PickStorePayload<ChatType>) {
      state.message = message;
    },
  },
});

// for TypeScript support
const dispatch = store.createDispatch<ActionTypes>();

dispatch({
  type: ADD,
  payload: 3,
});

dispatch({
  type: CHAT,
  payload: 'Hello World',
});
```

## 总结
本文的所有代码都在  
https://github.com/sl1673495/tiny-middlewares/blob/master/vuex.ts  
仓库里，里面还加上了getters的实现和类型推导。

通过本文的学习，相信你会对高级类型的用法有进一步的理解，也会对TypeScript的强大更加叹服，本文有很多例子都是为了教学而刻意深究，复杂化的，请不要骂我（XD）。  

在实际的项目运用中，首先我们应该避免Vuex这种集中化的类型定义，而尽量去拥抱函数（函数对于TypeScript是天然支持），这也是Vue3往函数化api方向走的原因之一。  


## 参考文章
React + Typescript 工程化治理实践（蚂蚁金服的大佬实践总结总是这么靠谱）
https://juejin.im/post/5dccc9b8e51d4510840165e2#comment  

TS 学习总结：编译选项 && 类型相关技巧
http://zxc0328.github.io/diary/2019/10/2019-10-05.html  

Conditional types in TypeScript（据说比Ts官网讲的好）
https://mariusschulz.com/blog/conditional-types-in-typescript#distributive-conditional-types  

Conditional Types in TypeScript（文风幽默，代码非常硬核）
https://artsy.github.io/blog/2018/11/21/conditional-types-in-typescript/
