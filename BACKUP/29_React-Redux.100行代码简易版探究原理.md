# [React-Redux 100行代码简易版探究原理](https://github.com/sl1673495/blogs/issues/29)

 ## 前言
 各位使用react技术栈的小伙伴都不可避免的接触过`redux` + `react-redux`的这套组合，众所周知redux是一个非常精简的库，它和react是没有做任何结合的，甚至可以在vue项目中使用。
 
 redux的核心状态管理实现其实就几行代码
 ```ts
 function createStore(reducer) {
  let currentState
  let subscribers = []

  function dispatch(action) {
    currentState = reducer(currentState, action);
    subscribers.forEach(s => s())
  }

  function getState() {
    return currentState;
  }
  
  function subscribe(subscriber) {
      subscribers.push(subscriber)
      return function unsubscribe() {
          ...
      }
  }

  dispatch({ type: 'INIT' });

  return {
    dispatch,
    getState,
  };
}

```
 
 它就是利用闭包管理了state等变量，然后在dispatch的时候通过用户定义reducer拿到新状态赋值给state，再把外部通过subscribe的订阅给触发一下。  
 
 那redux的实现简单了，react-redux的实现肯定就需要相对复杂，它需要考虑如何和react的渲染结合起来，如何优化性能。 
 
## 目标  

1. 本文目标是尽可能简短的实现`react-redux`v7中的hook用法部分`Provider`, `useSelector`, `useDispatch`方法。（不实现`connect`方法）
2. 可能会和官方版本的一些复杂实现不一样，但是保证主要的流程一致。  
3. 用TypeScript实现，并且能获得完善的类型提示。

## 预览
![redux gif.gif](https://user-gold-cdn.xitu.io/2020/1/11/16f946f6c4fd8955?w=706&h=380&f=gif&s=188883)  
预览地址：https://sl1673495.github.io/tiny-react-redux  

## 性能
 说到性能这个点，自从React Hook推出以后，有了`useContext`和`useReducer`这些方便的api，新的状态管理库如同雨后春笋版的冒了出来，其中的很多就是利用了`Context`做状态的向下传递。  
 
 举一个最简单的状态管理的例子
 ```js
export const StoreContext = React.createContext();

function App({ children }) {
  const [state, setState] = useState({});
  return <StoreContext.Provider value={{ state, setState }}>{children}</StoreContext.Provider>;
}

function Son() {
  const { state } = useContext(StoreContext);
  return <div>state是{state.xxx}</div>;
}

 ```
 
利用useState或者useContext，可以很轻松的在所有组件之间通过Context共享状态。 

但是这种模式的缺点在于Context会带来一定的性能问题，下面是React官方文档中的描述：


![Context性能问题](https://user-gold-cdn.xitu.io/2020/1/11/16f9412b5f3f10b2?w=1576&h=528&f=png&s=282752)  

想像这样一个场景，在刚刚所描述的Context状态管理模式下，我们的全局状态中有`count`和`message`两个状态分别给通过`StoreContext.Provider`向下传递  

1. `Counter`计数器组件使用了`count`
2. `Chatroom`聊天室组件使用了`message`

而在计数器组件通过Context中拿到的setState触发了`count`改变的时候，  

由于聊天室组件也利用`useContext`消费了用于状态管理的StoreContext，所以聊天室组件也会被强制重新渲染，这就造成了性能浪费。  

虽然这种情况可以用`useMemo`进行优化，但是手动优化和管理依赖必然会带来一定程度的心智负担，而在不手动优化的情况下，肯定无法达到上面动图中的重渲染优化。  

那么`react-redux`作为社区知名的状态管理库，肯定被很多大型项目所使用，大型项目里的状态可能分散在各个模块下，它是怎么解决上述的性能缺陷的呢？接着往下看吧。  
## 缺陷示例    
在我之前写的类vuex语法的状态管理库[react-vuex-hook](https://github.com/sl1673495/react-vuex-hook)中，就会有这样的问题。因为它就是用了`Context` + `useReducer`的模式。  

你可以直接在 [在线示例](https://sl1673495.github.io/react-vuex-hook) 这里，在左侧菜单栏选择`需要优化的场景`，即可看到上述性能问题的重现，优化方案也已经写在文档底部。  

这也是为什么我觉得`Context` + `useReducer`的模式更适合在小型模块之间共享状态，而不是在全局。   

## 实现
### 介绍  
本文的项目就上述性能场景提炼而成，由
1. `聊天室`组件，用了store中的`count`
2. `计数器`组件，用了store中的`message`
3. `控制台`组件，用来监控组件的重新渲染。  

用最简短的方式实现代码，探究react-redux为什么能在`count`发生改变的时候不让使用了`message`的组件重新渲染。  

### redux的定义
redux的使用很传统，跟着官方文档对于TypeScript的指导走起来，并且把类型定义和store都export出去。  

```jsx
import { createStore } from 'redux';

type AddAction = {
  type: 'add';
};

type ChatAction = {
  type: 'chat';
  payload: string;
};

type LogAction = {
  type: 'log';
  payload: string;
};

const initState = {
  message: 'Hello',
  logs: [] as string[],
};

export type ActionType = AddAction | ChatAction | LogAction;
export type State = typeof initState;

function reducer(state: State, action: ActionType): State {
  switch (action.type) {
    case 'add':
      return {
        ...state,
        count: state.count + 1,
      };
    case 'chat':
      return {
        ...state,
        message: action.payload,
      };
    case 'log':
      return {
        ...state,
        logs: [action.payload, ...state.logs],
      };
    default:
      return initState;
  }
}

export const store = createStore(reducer);
```

### 在项目中使用
```jsx
import React, { useState, useCallback } from 'react';
import { Card, Button, Input } from 'antd';
import { Provider, useSelector, useDispatch } from '../src';
import { store, State, ActionType } from './store';
import './index.css';
import 'antd/dist/antd.css';

function Count() {
  const count = useSelector((state: State) => state.count);
  const dispatch = useDispatch<ActionType>();
  // 同步的add
  const add = useCallback(() => dispatch({ type: 'add' }), []);

  dispatch({
    type: 'log',
    payload: '计数器组件重新渲染🚀',
  });
  return (
    <Card hoverable style={{ marginBottom: 24 }}>
      <h1>计数器</h1>
      <div className="chunk">
        <div className="chunk">store中的count现在是 {count}</div>
        <Button onClick={add}>add</Button>
      </div>
    </Card>
  );
}

export default () => {
  return (
    <Provider store={store}>
      <Count />
    </Provider>
  );
};

```

可以看到，我们用`Provider`组件里包裹了`Count`组件，并且把redux的store传递了下去  

在子组件里，通过`useDispatch`可以拿到redux的dispatch， 通过`useSelector`可以访问到store，拿到其中任意的返回值。  

### 构建Context  

利用官方api构建context，并且提供一个自定义hook: `useReduxContext`去访问这个context，对于忘了用Provider包裹的情况进行一些错误提示：  

对于不熟悉自定义hook的小伙伴，可以看我之前写的这篇文章：  
[使用React Hooks + 自定义Hook封装一步一步打造一个完善的小型应用。](https://juejin.im/post/5d6771375188257573636cf9)

```jsx
import React, { useContext } from 'react';
import { Store } from 'redux';

interface ContextType {
  store: Store;
}
export const Context = React.createContext<ContextType | null>(null);

export function useReduxContext() {
  const contextValue = useContext(Context);

  if (!contextValue) {
    throw new Error(
      'could not find react-redux context value; please ensure the component is wrapped in a <Provider>',
    );
  }

  return contextValue;
}
```


### 实现Provider  
```jsx
import React, { FC } from 'react';
import { Store } from 'redux';
import { Context } from './Context';

interface ProviderProps {
  store: Store;
}

export const Provider: FC<ProviderProps> = ({ store, children }) => {
  return <Context.Provider value={{ store }}>{children}</Context.Provider>;
};
```

### 实现useDispatch  
这里就是简单的把dispatch返回出去，通过泛型传递让外部使用的时候可以获得类型提示。  

泛型推导不熟悉的小伙伴可以看一下之前这篇：  
[进阶实现智能类型推导的简化版Vuex](https://juejin.im/post/5e1684b65188253a8c26468b)
```jsx
import { useReduxContext } from './Context';
import { Dispatch, Action } from 'redux';

export function useDispatch<A extends Action>() {
  const { store } = useReduxContext();
  return store.dispatch as Dispatch<A>;
}
```

### 实现useSelector  
这里才是重点，这个api有两个参数。
1. `selector`: 定义如何从state中取值，如`state => state.count`
2. `equalityFn`: 定义如何判断渲染之间值是否有改变。  

在性能章节也提到过，大型应用中必须做到只有自己使用的状态改变了，才去重新渲染，那么`equalityFn`就是判断是否渲染的关键了。  

关键流程（初始化）：  
1. 根据传入的selector从redux的store中取值。
2. 定义一个`latestSelectedState`保存上一次selector返回的值。
2. 定义一个`checkForceUpdate`方法用来控制当状态发生改变的时候，让当前组件的强制渲染。
3. 利用`store.subscribe`订阅一次redux的store，下次redux的store发生变化执行`checkForceUpdate`。

关键流程（更新）  

1. 当用户使用`dispatch`触发了redux store的变动后，store会触发`checkForceUpdate`方法。  
2. `checkForceUpdate`中，从`latestSelectedState`拿到上一次selector的返回值，再利用selector(store)拿到最新的值，两者利用`equalityFn`进行比较。
3. 根据比较，判断是否需要强制渲染组件。  

有了这个思路，就来实现代码吧：

```jsx
import { useReducer, useRef, useEffect } from 'react';
import { useReduxContext } from './Context';

type Selector<State, Selected> = (state: State) => Selected;
type EqualityFn<Selected> = (a: Selected, b: Selected) => boolean;

// 默认比较的方法
const defaultEqualityFn = <T>(a: T, b: T) => a === b;
export function useSelector<State, Selected>(
  selector: Selector<State, Selected>,
  equalityFn: EqualityFn<Selected> = defaultEqualityFn,
) {
  const { store } = useReduxContext();
  // 强制让当前组件渲染的方法。
  const [, forceRender] = useReducer(s => s + 1, 0);

  // 存储上一次selector的返回值。
  const latestSelectedState = useRef<Selected>();
  // 根据用户传入的selector，从store中拿到用户想要的值。
  const selectedState = selector(store.getState());

  // 检查是否需要强制更新
  function checkForUpdates() {
    // 从store中拿到最新的值
    const newSelectedState = selector(store.getState());

    // 如果比较相等，就啥也不做
    if (equalityFn(newSelectedState, latestSelectedState.current)) {
      return;
    }
    // 否则更新ref中保存的上一次渲染的值
    // 然后强制渲染
    latestSelectedState.current = newSelectedState;
    forceRender();
  }
  
  // 组件第一次渲染后 执行订阅store的逻辑
  useEffect(() => {
  
    // 🚀重点，去订阅redux store的变化
    // 在用户调用了dispatch后，执行checkForUpdates
    const unsubscribe = store.subscribe(checkForUpdates);
    
    // 组件被销毁后 需要调用unsubscribe停止订阅
    return unsubscribe;
  }, []);
  
  return selectedState;
}

```

## 总结  
本文涉及到的源码地址：  
https://github.com/sl1673495/tiny-react-redux  

原版的react-redux的实现肯定比这里的简化版要复杂的多，它要考虑class组件的使用，以及更多的优化以及边界情况。  

从简化版的实现入手，我们可以更清晰的得到整个流程脉络，如果你想进一步的学习源码，也可以考虑多花点时间去看官方源码并且单步调试。  