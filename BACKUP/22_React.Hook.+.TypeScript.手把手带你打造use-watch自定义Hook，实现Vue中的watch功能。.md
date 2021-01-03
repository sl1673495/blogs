# [React Hook + TypeScript 手把手带你打造use-watch自定义Hook，实现Vue中的watch功能。](https://github.com/sl1673495/blogs/issues/22)

## 前言
在Vue中，我们经常需要用watch去观察一个值的变化，通过新旧值的对比去做一些事情。

但是React Hook中好像并没有提供类似的hook来让我们实现相同的事情

不过好在Hook的好处就在于它可以自由组合各种基础Hook从而实现强大的自定义Hook。

本篇文章就带你打造一个简单好用的use-watch hooks。

## 实现

### 实现雏形
首先分析一下Vue中watch的功能，就是一个响应式的值发生改变以后，会触发一个回调函数，那么在React中自然而然的就想到了useEffect这个hook，我们先来打造一个基础的代码雏形，把我们想要观察的值作为useEffect的依赖传入。
```js
type Callback<T> = (prev: T | undefined) => void;

function useWatch<T>(dep: T, callback: Callback<T>) {
  useEffect(() => {
   callback();
  }, [dep]);
}
```

现在我们使用的时候就可以
```js
const App: React.FC = () => {
  const [count, setCount] = useState(0);

  useWatch(count, () => {
    console.log('currentCount: ', count);
  })

  const add = () => setCount(prevCount => prevCount + 1)

  return (
    <div>
      <p> 当前的count是{count}</p>
      {count}
      <button onClick={add} className="btn">+</button>
    </div>
  )
}
```

### 实现oldValue
在每次count发生变化的时候，会执行传入的回调函数。

现在我们加入旧值的保存逻辑，以便于在每次调用传进去的回调函数的时候，可以在回调函数中拿到count上一次的值。  

什么东西可以在一个组件的生命周期中充当一个存储器的功能呢，当然是`useRef`啦。

```js
function useWatch<T>(dep: T, callback: Callback<T>) {
  const prev = useRef<T>();

  useEffect(() => {
    callback(prev.current);
    prev.current = dep;
  }, [dep]);

  return () => {
    stop.current = true;
  };
}
```

这样就在每一次更新prev里保存的值为最新的值之前，先调用callback函数把上一次保留的值给到外部。

现在外部使用的时候 就可以
```js
const App: React.FC = () => {
  const [count, setCount] = useState(0);

  useWatch(count, (oldCount) => {
    console.log('oldCount: ', oldCount);
    console.log('currentCount: ', count);
  })

  const add = () => setCount(prevCount => prevCount + 1)

  return (
    <div>
      <p> 当前的count是{count}</p>
      {count}
      <button onClick={add} className="btn">+</button>
    </div>
  )
}
```

### 实现immediate

其实到此为止，已经实现了Vue中watch的主要功能了，  

现在还有一个问题是`useEffect`会在组件初始化的时候就默认调用一次，而watch的默认行为不应该这样。  

现在需要在组件初始化的时候不要调用这个callback，还是利用`useRef`来做，利用一个标志位inited来保存组件是否初始化的标记。  

并且通过第三个参数config来允许用户改变这个默认行为。

```js
type Callback<T> = (prev: T | undefined) => void;
type Config = {
  immediate: boolean;
};

function useWatch<T>(dep: T, callback: Callback<T>, config: Config = { immediate: false }) {
  const { immediate } = config;

  const prev = useRef<T>();
  const inited = useRef(false);

  useEffect(() => {
    const execute = () => callback(prev.current);

    if (!inited.current) {
      inited.current = true;
      if (immediate) {
        execute();
      }
    } else {
      execute();
    }
    prev.current = dep;
  }, [dep]);
}

```

### 实现stop

还是通过`useRef`做，只是把控制ref标志的逻辑暴露给外部。
```js
type Callback<T> = (prev: T | undefined) => void;
type Config = {
  immediate: boolean;
};

function useWatch<T>(dep: T, callback: Callback<T>, config: Config = { immediate: false }) {
  const { immediate } = config;

  const prev = useRef<T>();
  const inited = useRef(false);
  const stop = useRef(false);

  useEffect(() => {
    const execute = () => callback(prev.current);

    if (!stop.current) {
      if (!inited.current) {
        inited.current = true;
        if (immediate) {
          execute();
        }
      } else {
        execute();
      }
      prev.current = dep;
    }
  }, [dep]);

  return () => {
    stop.current = true;
  };
}
```

这样在外部就可以这样去停止本次观察。
```js
const App: React.FC = () => {
  const [prev, setPrev] = useState()
  const [count, setCount] = useState(0);

  const stop = useWatch(count, (prevCount) => {
    console.log('prevCount: ', prevCount);
    console.log('currentCount: ', count);
    setPrev(prevCount)
  })

  const add = () => setCount(prevCount => prevCount + 1)

  return (
    <div>
      <p> 当前的count是{count}</p>
      <p> 前一次的count是{prev}</p>
      {count}
      <button onClick={add} className="btn">+</button>
      <button onClick={stop} className="btn">停止观察旧值</button>
    </div>
  )
}
```

## 源码地址：
https://github.com/sl1673495/use-watch-hook

## 文档地址：
文档是基于docz生成的，配合mdx还可以实现非常好用的功能预览：  
https://sl1673495.github.io/use-watch-hook