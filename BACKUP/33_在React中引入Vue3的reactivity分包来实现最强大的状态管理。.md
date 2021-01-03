# [在React中引入Vue3的reactivity分包来实现最强大的状态管理。](https://github.com/sl1673495/blogs/issues/33)

## 前言
React的状态管理是一个缤纷繁杂的大世界，光我知道的就不下数十种，其中有最出名immutable阵营的`redux`，有mutable阵营的`mobx`，`react-easy-state`，在hooks诞生后还有极简主义的`unstated-next`，有蚂蚁金服的大佬出品的`hox`、`hoox`。  

其实社区诞生这么多种状态管理框架，也说明状态管理库之间都有一些让人不满足的地方。  

`rxv`是我依据这些痛点，并且直接引入了Vue3的package: `@vue/reactivity`去做的一个React状态管理框架，下面先看一个简单的示例：

## 示例

```ts
// store.ts
import { reactive, computed, effect } from '@vue/reactivity';

export const state = reactive({
  count: 0,
});

const plusOne = computed(() => state.count + 1);

effect(() => {
  console.log('plusOne changed: ', plusOne);
});

const add = () => (state.count += 1);

export const mutations = {
  // mutation
  add,
};

export const store = {
  state,
  computed: {
    plusOne,
  },
};

export type Store = typeof store;
```
```js
// Index.tsx
import { Provider, useStore } from 'rxv'
import { mutations, store, Store } from './store.ts'
function Count() {
  const countState = useStore((store: Store) => {
    const { state, computed } = store;
    const { count } = state;
    const { plusOne } = computed;

    return {
      count,
      plusOne,
    };
  });

  return (
    <Card hoverable style={{ marginBottom: 24 }}>
      <h1>计数器</h1>
      <div className="chunk">
        <div className="chunk">store中的count现在是 {countState.count}</div>
        <div className="chunk">computed值中的plusOne现在是 {countState.plusOne.value}</div>
         <Button onClick={mutations.add}>add</Button>
      </div>
    </Card>
  );
}

export default () => {
  return (
    <Provider value={store}>
       <Count />
    </Provider>
  );
};
```
可以看出，`store`的定义只用到了`@vue/reactivity`，而`rxv`只是在组件中做了一层桥接，连通了Vue3和React，正如它名字的含义：React x Vue。

## 一些痛点
根据我自己的看法，我先简单的总结一下现有的状态管理库中或多或少存在的一些不足之处：  
1. 以`redux`为代表的，语法比较冗余，样板文件比较多。
2. `mobx`很好，但是也需要单独的学一套api，对于react组件的侵入性较强，装饰器语法不稳定。
3. `unstated-next`是一个极简的框架，对于React Hook做了一层较浅的封装。
4. `react-easy-state`引入了`observe-util`，这个库对于响应式的处理很接近Vue3，我想要的了。

下面展开来讲：

### options-based的痛点
Vuex和dva的`options-based`的模式现在看来弊端多多。具体的可以看尤大在[vue-composition-api文档](https://vue-composition-api-rfc.netlify.com/#logical-concerns-vs-option-types)中总结的。  

简单来说就是一个组件有好几个功能点，但是这几个功能点在分散在`data`,`methods`,`computed`中，形成了一个杂乱无章的结构。  

当你想维护一个功能，你不得不先完整的看完这个配置对象的全貌。  

心惊胆战的去掉几行，改掉几行，说不定会遗留一些没用的代码，也或者隐藏在computed选项里的某个相关的函数悄悄的坑了你...

而hook带来的好处是更加灵活的代码组织方式。

### redux
直接引入dan自己的吐槽吧，要学的概念太多，写一个简单的功能要在五个文件之间跳来跳去，好头疼。redux的弊端在社区被讨论也不是一天两天了，相信写过redux的你也是深有同感。  
![redux](https://user-gold-cdn.xitu.io/2020/1/26/16fe015af0db87d6?w=720&h=1558&f=png&s=446860)  

### unstated-next
unstated-next其实很不错了，源码就40来行。最大程度的利用了React Hook的能力，写一个model就是写一个自定义hook。但是极简也带来了一些问题：
1. 模块之间没有相互访问的能力。
2. Context的性能问题，让你需要关注模块的划分。（具体可以看我这篇文章的[性能章节](https://juejin.im/post/5e1995a66fb9a02fdc3a44b4#heading-3)）
2. 模块划分的问题，如果全放在一个Provider，那么更新的粒度太大，所有用了useContext的组件都会重复渲染。如果放在多个Provider里，那么就会回到第一条痛点，这些模块之间是相互独立的，没法互相访问。 
3. hook带来的一些心智负担的问题。[React Hooks 你真的用对了吗？
](https://zhuanlan.zhihu.com/p/85969406)

### react-easy-state
这个库引入的`observe-util`其实和Vue3 reactivity部分的核心实现很相似，关于原理解析也可以看我之前写的两篇文章：  
[带你彻底搞懂Vue3的Proxy响应式原理！TypeScript从零实现基于Proxy的响应式库。](https://juejin.im/post/5e21196fe51d454d523be084)  
[带你彻底搞懂Vue3的Proxy响应式原理！基于函数劫持实现Map和Set的响应式。](https://juejin.im/post/5e23b20f51882510073eb571)  

那其实转而一想，Vue3 reactivity其实是`observe-util`的强化版，它拥有了更多的定制能力，如果我们能把这部分直接接入到状态管理库中，岂不是完全拥有了Vue3的响应式能力。  



## 原理分析
`vue-next`是Vue3的源码仓库，Vue3采用lerna做package的划分，而响应式能力`@vue/reactivity`被划分到了单独的一个package中  

从这个包提供的几个核心api来分析：  

### effect  
effect其实是响应式库中一个通用的概念：`观察函数`，就像Vue2中的`Watcher`，mobx中的`autorun`，`observer`一样，它的作用是`收集依赖`。  

它接受的是一个函数，这个函数内部对于响应式数据的访问都可以收集依赖，那么在响应式数据更新后，就会触发响应的更新事件。  

### reactive  
响应式数据的核心api，这个api返回的是一个`proxy`，对上面所有属性的访问都会被劫持，从而在get的时候收集依赖（也就是正在运行的`effect`），在set的时候触发更新。  

### ref
对于简单数据类型比如`number`，我们不可能像这样去做：
```js
let data = reactive(2)
// 😭oops
data = 5
```
这是不符合响应式的拦截规则的，没有办法能拦截到`data`本身的改变，只能拦截到`data`身上的属性的改变，所以有了ref。  
```js
const data = ref(2)
// 💕ok
data.value= 5
```

### computed
计算属性，依赖值更新以后，它的值也会随之自动更新。其实computed内部也是一个effect。

拥有在computed中观察另一个computed数据、effect观察computed改变之类的高级特性。  

## 实现
从这几个核心api来看，只要effect能接入到React系统中，那么其他的api都没什么问题，因为它们只是去收集effect的毅力，去通知effect触发更新。  

effect接受的是一个函数，而且effect还支持通过传入`schedule`参数来自定义依赖更新的时候需要触发什么函数，

而`rxv`的核心api: `useStore`接受的也是一个函数`selector`，它会让用户自己选择在组件中需要访问的数据。

那么思路就显而易见了：

1. 把`selector`包装在effect中执行，去收集依赖。
2. 指定依赖发生更新时，需要调用的函数是`当前正在使用useStore`的这个组件的`forceUpdate`强制渲染函数。 

这样不就实现了数据变化，组件自动更新吗？  

简单的看一下核心实现

```js
export const useStore = <T, S>(selector: Selector<T, S>): S => {
  const forceUpdate = useForceUpdate();
  const store = useStoreContext();

  const effection = useEffection(() => selector(store), {
    scheduler: forceUpdate,
    lazy: true,
  });

  const value = effection();
  return value;
};
```

1. 先通过useForceUpdate在当前组件中注册一个强制更新的函数。  
2. 通过useContext读取用户从Provider中传入的store。
3. 再通过Vue的effect去帮我们执行selector(store)，并且指定scheduler为forceUpdate，这样就完成了依赖收集。 

就简单的几行代码，就实现了在React中使用`@vue/reactivity`中的所有能力。  

## 优点：
1. 直接引入@vue/reacivity，完全使用Vue3的reactivity能力，拥有computed, effect等各种能力，并且对于Set和Map也提供了响应式的能力。后续也会随着这个库的更新变得更加完善的和强大。
2. vue-next仓库内部完整的测试用例。
3. 完善的TypeScript类型支持。
4. 完全复用@vue/reacivity实现超强的全局状态管理能力。
5. 状态管理中组件级别的精确更新。
6. Vue3总是要学的嘛，提前学习防止失业！  

## 缺点：
1. 由于需要精确的收集依赖全靠`useStore`，所以`selector`函数一定要精确的访问到你关心的数据。甚至如果你需要触发数组内部某个值的更新，那你在useStore中就不能只返回这个对象本身。  

## 源码地址
https://github.com/sl1673495/react-composition-api

如果你喜欢这个库，欢迎给出你的star✨，你的支持就是我最大的动力~
