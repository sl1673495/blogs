# [使用React Hooks + 自定义Hook封装一步一步打造一个完善的小型应用。](https://github.com/sl1673495/blogs/issues/16)

## 前言
Reack Hooks自从16.8发布以来，社区已经有相当多的讨论和应用了，不知道各位在公司里有没有用上这个酷炫的特性~  

今天分享一下利用React Hooks实现一个功能相对完善的todolist。  

特点：
- 利用自定义hook管理请求
- 利用hooks做代码组织和逻辑分离


## 界面预览
![预览](https://user-images.githubusercontent.com/23615778/64005966-ee228d80-cb43-11e9-8c59-f494c8b52a6b.png)

## 体验地址
https://codesandbox.io/s/react-hooks-todo-dh3gx?fontsize=14

## 代码详解

### 界面
首先我们引入antd作为ui库，节省掉无关的一些逻辑，快速的构建出我们的页面骨架
```js

const TAB_ALL = "all";
const TAB_FINISHED = "finished";
const TAB_UNFINISHED = "unfinished";
const tabMap = {
  [TAB_ALL]: "全部",
  [TAB_FINISHED]: "已完成",
  [TAB_UNFINISHED]: "待完成"
};

function App() {
  const [activeTab, setActiveTab] = useState(TAB_ALL);
  
  return (
    <>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={tabMap[TAB_ALL]} key={TAB_ALL} />
        <TabPane tab={tabMap[TAB_FINISHED]} key={TAB_FINISHED} />
        <TabPane tab={tabMap[TAB_UNFINISHED]} key={TAB_UNFINISHED} />
      </Tabs>
      <div className="app-wrap">
        <h1 className="app-title">Todo List</h1>
        <Input />
        <TodoList />
      </div>
    </>
  );
}
```

### 数据获取
有了界面以后，接下来就要获取数据。

#### 模拟api
这里我新建了一个api.js专门用来模拟接口获取数据，这里面的逻辑大概看一下就好，不需要特别在意。
```js
const todos = [
  {
    id: 1,
    text: "todo1",
    finished: true
  },
  {
    id: 2,
    text: "todo2",
    finished: false
  },
  {
    id: 3,
    text: "todo3",
    finished: true
  },
  {
    id: 4,
    text: "todo4",
    finished: false
  },
  {
    id: 5,
    text: "todo5",
    finished: false
  }
];

const delay = time => new Promise(resolve => setTimeout(resolve, time));
// 将方法延迟1秒
const withDelay = fn => async (...args) => {
  await delay(1000);
  return fn(...args);
};

// 获取todos
export const fetchTodos = withDelay(params => {
  const { query, tab } = params;
  let result = todos;
  // tab页分类
  if (tab) {
    switch (tab) {
      case "finished":
        result = result.filter(todo => todo.finished === true);
        break;
      case "unfinished":
        result = result.filter(todo => todo.finished === false);
        break;
      default:
        break;
    }
  }

  // 带参数查询
  if (query) {
    result = result.filter(todo => todo.text.includes(query));
  }

  return Promise.resolve({
    tab,
    result
  });
});
```
这里我们封装了个withDelay方法用来包裹函数，模拟异步请求接口的延迟，这样方便我们后面演示loading功能。

#### 基础数据获取
获取数据，最传统的方式就是在组件中利用useEffect来完成请求，并且声明依赖值来在某些条件改变后重新获取数据，简单写一个：
```js
import { fetchTodos } from './api'

const TAB_ALL = "all";
const TAB_FINISHED = "finished";
const TAB_UNFINISHED = "unfinished";
const tabMap = {
  [TAB_ALL]: "全部",
  [TAB_FINISHED]: "已完成",
  [TAB_UNFINISHED]: "待完成"
};

function App() {
  const [activeTab, setActiveTab] = useState(TAB_ALL);
  
  
  // 获取数据
  const [loading, setLoading] = useState(false)
  const [todos, setTodos] = useState([])
  useEffect(() => {
    setLoading(true)
    fetchTodos({tab: activeTab})
        .then(result => {
            setTodos(todos)
        })
        .finally(() => {
            setLoading(false)
        })
  }, [])
  
  
  return (
    <>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={tabMap[TAB_ALL]} key={TAB_ALL} />
        <TabPane tab={tabMap[TAB_FINISHED]} key={TAB_FINISHED} />
        <TabPane tab={tabMap[TAB_UNFINISHED]} key={TAB_UNFINISHED} />
      </Tabs>
      <div className="app-wrap">
        <h1 className="app-title">Todo List</h1>
        <Input />
        <Spin spinning={loading} tip="稍等片刻~">
          <!--把todos传递给组件-->
          <TodoList todos={todos}/>
        </Spin>
      </div>
    </>
  );
}
```

这样很好，在公司内部新启动的项目里我的同事们也都是这么写的，但是这样的获取数据有几个小问题。
- 每次都要用useState建立loading的的状态
- 每次都要用useState建立请求结果的状态
- 对于请求如果有一些更高阶的封装的话，不太好操作。  

所以这里要封装一个专门用于请求的自定义hook。  

### 自定义hook（数据获取）

忘了在哪看到的说法，自定hook其实就是把useXXX方法执行以后，把方法体里的内容平铺到组件内部，我觉得这种说法对于理解自定义hook很友好。
```js
useTest() {
    const [test, setTest] = useState('')
    setInterval(() => {
        setTest(Math.random())
    }, 1000)
    return {test, setTest}
}

function App() {
    const {test, setTest} = useTest()
    
    return <span>{test}</span>
}

```
这段代码等价于：
```js
function App() {
    const [test, setTest] = useState('')
    setInterval(() => {
        setTest(Math.random())
    }, 1000)
    
    return <span>{test}</span>
}

```

是不是瞬间感觉自定hook很简单了~ 基于这个思路，我们来封装一下我们需要的useRequest方法。

```
export const useRequest = (fn, dependencies) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // 请求的方法 这个方法会自动管理loading
  const request = () => {
    setLoading(true);
    fn()
      .then(setData)
      .finally(() => {
        setLoading(false);
      });
  };

  // 根据传入的依赖项来执行请求
  useEffect(() => {
    request()
  }, dependencies);
    
  return {
      // 请求获取的数据
      data,
      // loading状态
      loading,
      // 请求的方法封装
      request
  };
};
```

有了这个自定义hook，我们组件内部的代码又可以精简很多。

```js
import { fetchTodos } from './api'
import { useRequest } from './hooks'

const TAB_ALL = "all";
const TAB_FINISHED = "finished";
const TAB_UNFINISHED = "unfinished";
const tabMap = {
  [TAB_ALL]: "全部",
  [TAB_FINISHED]: "已完成",
  [TAB_UNFINISHED]: "待完成"
};

function App() {
  const [activeTab, setActiveTab] = useState(TAB_ALL);
  
  // 获取数据
  const {loading, data: todos} = useRequest(() => {
      return fetchTodos({ tab: activeTab });
  }, [activeTab]) 
  
  return (
    <>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={tabMap[TAB_ALL]} key={TAB_ALL} />
        <TabPane tab={tabMap[TAB_FINISHED]} key={TAB_FINISHED} />
        <TabPane tab={tabMap[TAB_UNFINISHED]} key={TAB_UNFINISHED} />
      </Tabs>
      <div className="app-wrap">
        <h1 className="app-title">Todo List</h1>
        <Input />
        <Spin spinning={loading} tip="稍等片刻~">
          <!--把todos传递给组件-->
          <TodoList todos={todos}/>
        </Spin>
      </div>
    </>
  );
}
```

果然，样板代码少了很多，腰不酸了腿也不痛了，一口气能发5个请求了！


#### 消除tab频繁切换产生的脏数据

在真实开发中我们特别容易遇到的一个场景就是，tab切换并不改变视图，而是去重新请求新的列表数据，在这种情况下我们可能就会遇到一个问题，以这个todolist举例，我们从`全部`tab切换到`已完成`tab，会去请求数据，但是如果我们在`已完成`tab的数据还没请求完成时，就去点击`待完成`的tab页，这时候就要考虑一个问题，异步请求的响应时间是不确定的，很可能我们发起的第一个请求`已完成`最终耗时5s，第二个请求`待完成`最终耗时1s，这样第二个请求的数据返回，渲染完页面以后，过了几秒第一个请求的数据返回了，但是这个时候我们的tab是停留在对应第二个请求`待完成`上，这就造成了脏数据的bug。

这个问题其实我们可以利用useEffect的特性在useRequest封装解决。
```js

export const useRequest = (fn, dependencies, defaultValue = []) => {
  const [data, setData] = useState(defaultValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const request = () => {
    // 定义cancel标志位
    let cancel = false;
    setLoading(true);
    fn()
      .then(res => {
        if (!cancel) {
          setData(res);
        } else {
          // 在请求成功取消掉后，打印测试文本。
          const { tab } = res;
          console.log(`request with ${tab} canceled`);
        }
      })
      .catch(() => {
        if (!cancel) {
          setError(error);
        }
      })
      .finally(() => {
        if (!cancel) {
          setLoading(false);
        }
      });

    // 请求的方法返回一个 取消掉这次请求的方法
    return () => {
      cancel = true;
    };
  };

  // 重点看这段，在useEffect传入的函数，返回一个取消请求的函数
  // 这样在下一次调用这个useEffect时，会先取消掉上一次的请求。
  useEffect(() => {
    const cancelRequest = request();
    return () => {
      cancelRequest();
    };
    // eslint-disable-next-line
  }, dependencies);

  return { data, setData, loading, error, request };
};
```

其实这里request里实现的取消请求只是我们模拟出来的取消，真实情况下可以利用axios等请求库提供的方法做不一样的封装，这里主要是讲思路。
useEffect里返回的函数其实叫做清理函数，在每次新一次执行useEffect时，都会先执行清理函数，我们利用这个特性，就能成功的让useEffect永远只会用最新的请求结果去渲染页面。

可以去[预览地址](https://codesandbox.io/s/react-hooks-todo-dh3gx?fontsize=14)快速点击tab页切换，看一下控制台打印的结果。

### 主动请求的封装
现在需要加入一个功能，点击列表中的项目，切换完成状态，这时候`useRequest`好像就不太合适了，因为`useRequest`其实本质上是针对useEffect的封装，而useEffect的使用场景是初始化和依赖变更的时候发起请求，但是这个新需求其实是响应用户的点击而去主动发起请求，难道我们又要手动写setLoading之类的冗余代码了吗？答案当然是不。  
我们利用高阶函数的思想封装一个自定义hook：`useWithLoading`

#### useWithLoading代码实现
```js
export function useWithLoading(fn) {
  const [loading, setLoading] = useState(false);

  const func = (...args) => {
    setLoading(true);
    return fn(...args).finally(() => {
      setLoading(false);
    });
  };

  return { func, loading };
}
```
它本质上就是对传入的方法进行了一层包裹，在执行前后去更改loading状态。  
使用：
```js
 // 完成todo逻辑
  const { func: onToggleFinished, loading: toggleLoading } = useWithLoading(
    async id => {
      await toggleTodo(id);
    }
  );
  
<TodoList todos={todos} onToggleFinished={onToggleFinished} />
      
```

### 代码组织
加入一个新功能，input的placeholder根据tab页的切换去切换文案，注意，这里我们先提供一个错误的示例，这是刚从Vue2.x和React Class Component转过来的人很容易犯的一个错误。

❌错误示例
```js
import { fetchTodos } from './api'
import { useRequest } from './hooks'

const TAB_ALL = "all";
const TAB_FINISHED = "finished";
const TAB_UNFINISHED = "unfinished";
const tabMap = {
  [TAB_ALL]: "全部",
  [TAB_FINISHED]: "已完成",
  [TAB_UNFINISHED]: "待完成"
};

function App() {
  // state放在一起
  const [activeTab, setActiveTab] = useState(TAB_ALL);
  const [placeholder, setPlaceholder] = useState("");
  const [query, setQuery] = useState("");
  
  // 副作用放在一起
  const {loading, data: todos} = useRequest(() => {
      return fetchTodos({ tab: activeTab });
  }, [activeTab]) 
  useEffect(() => {
    setPlaceholder(`在${tabMap[activeTab]}内搜索`);
  }, [activeTab]);
  const { func: onToggleFinished, loading: toggleLoading } = useWithLoading(
    async id => {
      await toggleTodo(id);
    }
  );
  
  return (
    <>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={tabMap[TAB_ALL]} key={TAB_ALL} />
        <TabPane tab={tabMap[TAB_FINISHED]} key={TAB_FINISHED} />
        <TabPane tab={tabMap[TAB_UNFINISHED]} key={TAB_UNFINISHED} />
      </Tabs>
      <div className="app-wrap">
        <h1 className="app-title">Todo List</h1>
        <Input />
        <Spin spinning={loading} tip="稍等片刻~">
          <!--把todos传递给组件-->
          <TodoList todos={todos}/>
        </Spin>
      </div>
    </>
  );
}
```

注意，在之前的vue和react开发中，因为vue代码组织的方式都是 `based on options`（基于选项如data, methods, computed组织），  
React 也是state在一个地方统一初始化，然后class里定义一堆一堆的xxx方法，这会导致新接手代码的人阅读逻辑十分困难。  

所以hooks也解决了一个问题，就是我们的代码组织方式可以 `based on logical concerns`（基于逻辑关注点组织）了
不要再按照往常的思维把useState useEffect分门别类的组织起来，看起来整齐但是毫无用处 ！！  

这里上一张vue composition api介绍里对于@vue/ui库中一个组件的对比图

![对比图](https://user-gold-cdn.xitu.io/2019/8/29/16cdc53829fba3a5?w=1200&h=1201&f=png&s=266251)
颜色是用来区分功能点的，哪种代码组织方式更利于维护，一目了然了吧。

Vue composition api 推崇的代码组织方式是把逻辑拆分成一个一个的自定hook function，这点和react hook的思路是一致的。
```js
export default {
  setup() { // ...
  }
}

function useCurrentFolderData(nextworkState) { // ...
}

function useFolderNavigation({ nextworkState, currentFolderData }) { // ...
}

function useFavoriteFolder(currentFolderData) { // ...
}

function useHiddenFolders() { // ...
}

function useCreateFolder(openFolder) { // ...
}
```



✔️正确示例

```js
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import TodoInput from "./todo-input";
import TodoList from "./todo-list";
import { Spin, Tabs } from "antd";
import { fetchTodos, toggleTodo } from "./api";
import { useRequest, useWithLoading } from "./hook";

import "antd/dist/antd.css";
import "./styles/styles.css";
import "./styles/reset.css";

const { TabPane } = Tabs;

const TAB_ALL = "all";
const TAB_FINISHED = "finished";
const TAB_UNFINISHED = "unfinished";
const tabMap = {
  [TAB_ALL]: "全部",
  [TAB_FINISHED]: "已完成",
  [TAB_UNFINISHED]: "待完成"
};

function App() {
  const [activeTab, setActiveTab] = useState(TAB_ALL);

  // 数据获取逻辑
  const [query, setQuery] = useState("");
  const {
    data: { result: todos = [] },
    loading: listLoading
  } = useRequest(() => {
    return fetchTodos({ query, tab: activeTab });
  }, [query, activeTab]);

  // placeHolder
  const [placeholder, setPlaceholder] = useState("");
  useEffect(() => {
    setPlaceholder(`在${tabMap[activeTab]}内搜索`);
  }, [activeTab]);

  // 完成todo逻辑
  const { func: onToggleFinished, loading: toggleLoading } = useWithLoading(
    async id => {
      await toggleTodo(id);
    }
  );

  const loading = !!listLoading || !!toggleLoading;
  return (
    <>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={tabMap[TAB_ALL]} key={TAB_ALL} />
        <TabPane tab={tabMap[TAB_FINISHED]} key={TAB_FINISHED} />
        <TabPane tab={tabMap[TAB_UNFINISHED]} key={TAB_UNFINISHED} />
      </Tabs>
      <div className="app-wrap">
        <h1 className="app-title">Todo List</h1>
        <TodoInput placeholder={placeholder} onSetQuery={setQuery} />
        <Spin spinning={loading} tip="稍等片刻~">
          <TodoList todos={todos} onToggleFinished={onToggleFinished} />
        </Spin>
      </div>
    </>
  );
}
const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
```


## 总结
React Hook提供了一种新思路让我们去更好的组织组件内部的逻辑代码，使得功能复杂的大型组件更加易于维护。并且自定义Hook功能十分强大，在公司的项目中我也已经封装了很多好用的自定义Hook比如UseTable, useTreeSearch, useTabs等，可以结合各自公司使用的组件库和ui交互需求把一些逻辑更细粒度的封装起来，发挥你的想象力！useYourImagination!
