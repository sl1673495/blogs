# [React + TypeScript + Hook 带你手把手打造类型安全的应用。](https://github.com/sl1673495/blogs/issues/21)

## 前言
TypeScript可以说是今年的一大流行点，虽然Angular早就开始把TypeScript作为内置支持了，但是真正在中文社区火起来据我观察也就是没多久的事情，尤其是在Vue3官方宣布采用TypeScript开发以后达到了一个顶点。  

社区里有很多TypeScript比较基础的分享，但是关于React实战的还是相对少一些，这篇文章就带大家用React从头开始搭建一个TypeScript的todolist，我们的目标是实现类型安全，杜绝开发时可能出现的任何错误！

本文所使用的所有代码全部整理在了 [ts-react-todo](https://github.com/sl1673495/ts-react-todo) 这个仓库里。

本文默认你对于TypeScript的基础应用没有问题，对于泛型的使用也大概理解，如果对于TS的基础还没有熟悉的话，可以看我在上面github仓库的Readme的文末附上的几篇推荐。
## 实战

### 创建应用
首先使用的脚手架是create-react-app，根据  
https://www.html.cn/create-react-app/docs/adding-typescript/  
的流程可以很轻松的创建一个开箱即用的typescript-react-app。  

创建后的结构大概是这样的：
```
my-app/
  README.md
  node_modules/
  package.json
  public/
    index.html
    favicon.ico
  src/
    App.css
    App.ts
    App.test.ts
    index.css
    index.ts
    logo.svg
```

在src/App.ts中开始编写我们的基础代码
```js
import React, { useState, useEffect } from "react";
import classNames from "classnames";
import TodoForm from "./TodoForm";
import axios from "../api/axios";
import "../styles/App.css";

type Todo = {
  id: number;
  // 名字
  name: string;
  // 是否完成
  done: boolean;
};

type Todos = Todo[];

const App: React.FC = () => {
  const [todos, setTodos] = useState<Todos>([]);
  
  return (
    <div className="App">
      <header className="App-header">
        <ul>
          <TodoForm />
          {todos.map((todo, index) => {
            return (
              <li
                onClick={() => onToggleTodo(todo)}
                key={index}
                className={classNames({
                  done: todo.done,
                })}
              >
                {todo.name}
              </li>
            );
          })}
        </ul>
      </header>
    </div>
  );
};

export default App;
```
### useState
代码很简单，利用type关键字来定义Todo这个类型，然后顺便生成Todos这个类型，用来给React的useState作为`泛型约束`使用，这样在上下文中，todos这个变量就会被约束为Todos这个类型，setTodos也只能去传入Todos类型的变量。
```js
  const [todos, setTodos] = useState<Todos>([]);
```

![Todos](https://user-gold-cdn.xitu.io/2019/11/27/16eaab9638955295?w=387&h=55&f=png&s=29172)

当然，useState也是具有泛型推导的能力的，但是这要求你传入的初始值已经是你想要的类型了，而不是空数组。

```js
const [todos, setTodos] = useState({
    id: 1,
    name: 'ssh',
    done: false
  });
```
![](https://user-gold-cdn.xitu.io/2019/11/27/16eaabcfc1df56a8?w=292&h=184&f=png&s=55346)


### 模拟axios（简单版）
有了基本的骨架以后，就要想办法去拿到数据了，这里我选择自己模拟编写一个axios去返回想要的数据。

```js
  const refreshTodos = () => {
    // 这边必须手动声明axios的返回类型。
    axios<Todos>("/api/todos").then(setTodos);
  };

  useEffect(() => {
    refreshTodos();
  }, []);
```

注意这里的axios也要在使用时手动传入泛型，因为我们现在还不能根据"/api/todos"这个字符串来推导出返回值的类型，接下来看一下axios的实现。

```js
let todos = [
  {
    id: 1,
    name: '待办1',
    done: false
  },
  {
    id: 2,
    name: '待办2',
    done: false
  },
  {
    id: 3,
    name: '待办3',
    done: false
  }
]

// 使用联合类型来约束url
type Url = '/api/todos' | '/api/toggle' | '/api/add'

const axios = <T>(url: Url, payload?: any): Promise<T> | never => {
  let data
  switch (url) {
    case '/api/todos': {
      data = todos.slice()
      break
    }
  }
 default: {
    throw new Error('Unknown api')
 }

  return Promise.resolve(data as any)
}

export default axios
```

重点看一下axios的类型描述
```js
const axios = <T>(url: Url, payload?: any): Promise<T> | never
```
泛型T被原封不动的交给了返回值的Promise<T>，
```js
promise.then((data) => data.xxx)
```
所以外部axios调用时传入的Todos泛型就被交给了Promise，Ts就可以推断出这个promise去resolve的值的类型是Todos，然后我们把switch-case逻辑中拿到的值用Promise.resolve(data)返回出去。

接下来回到src/App.ts 继续补充点击todo，更改完成状态时候的事件，
```js

const App: React.FC = () => {
  const [todos, setTodos] = useState<Todos>([]);
  const refreshTodos = () => {
    // FIXME 这边必须手动声明axios的返回类型。
    axios<Todos>("/api/todos").then(setTodos);
  };

  useEffect(() => {
    refreshTodos();
  }, []);

  const onToggleTodo = async (todo: Todo) => {
    await axios("/api/toggle", todo.id);
    refreshTodos();
  };

  return (
    <div className="App">
      <header className="App-header">
        <ul>
          <TodoForm refreshTodos={refreshTodos} />
          {todos.map((todo, index) => {
            return (
              <li
                onClick={() => onToggleTodo(todo)}
                key={index}
                className={classNames({
                  done: todo.done,
                })}
              >
                {todo.name}
              </li>
            );
          })}
        </ul>
      </header>
    </div>
  );
};
```

再来看一下src/TodoForm组件的实现:
```js
import React from "react";
import axios from "../api/axios";

interface Props {
  refreshTodos: () => void;
}

const TodoForm: React.FC<Props> = ({ refreshTodos }) => {
  const [name, setName] = React.useState("");

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const newTodo = {
      id: Math.random(),
      name,
      done: false,
    };

    if (name.trim()) {
      // FIXME 这边第二个参数没有做类型约束
      axios("/api/add", newTodo);
      refreshTodos();
      setName("");
    }
  };

  return (
    <form className="todo-form" onSubmit={onSubmit}>
      <input
        className="todo-input"
        value={name}
        onChange={onChange}
        placeholder="请输入待办事项"
      />
      <button type="submit">新增</button>
    </form>
  );
};

export default TodoForm;
```

在axios里加入/api/toggle和/api/add的处理：
```js
  switch (url) {
    case '/api/todos': {
      data = todos.slice()
      break
    }
    case '/api/toggle': {
      const todo = todos.find(({ id }) => id === payload)
      if (todo) {
        todo.done = !todo.done
      }
      break
    }
    case '/api/add': {
      todos.push(payload)
      break
    }
    default: {
      throw new Error('Unknown api')
    }
  }
```

其实写到这里，一个简单的todolist已经实现了，功能是完全可用的，但是你说它类型安全吗，其实一点也不安全。

再回头看一下axios的类型签名：
```js
const axios = <T>(url: Url, payload?: any): Promise<T> | never
```
payload这个参数被加上了?可选符，这是因为有的接口需要传参而有的接口不需要，这就会带来一些问题。

这里编写axios只约束了传入的url的限制，但是并没有约束入参的类型，返回值的类型，其实基本也就是anyscript了，举例来说，在src/TodoForm里的提交事件中，我们在FIXME的下面一行稍微改动，把axios的第二个参数去掉，如果以现实情况来说的话，一个add接口不传值，基本上报错没跑了，而且这个错误只有运行时才能发现。
```js
  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const newTodo = {
      id: Math.random(),
      name,
      done: false,
    };

    if (name.trim()) {
      // ERROR！！ 这边的第二个参数被去掉了
      axios("/api/add");
      refreshTodos();
      setName("");
    }
  };

```

在src/App.ts的onToggleTodo事件里也有着同样的问题
```js
 const onToggleTodo = async (todo: Todo) => {
    // ERROR！！ 这边的第二个参数被去掉了
    await axios("/api/toggle");
    refreshTodos();
  };
```

另外在获取数据时候axios，必须要手动用泛型来定义好返回类型，这个也很冗余。
```js
axios<Todos>("/api/todos").then(setTodos);
```

接下来我们用一个严格类型版本的axios函数来解决这个问题。

```ts
// axios.strict.ts
let todos = [
  {
    id: 1,
    name: '待办1',
    done: false
  },
  {
    id: 2,
    name: '待办2',
    done: false
  },
  {
    id: 3,
    name: '待办3',
    done: false
  }
]


export enum Urls {
  TODOS = '/api/todos',
  TOGGLE = '/api/toggle',
  ADD = '/api/add',
}

type Todo = typeof todos[0]
type Todos = typeof todos

```

首先我们用enum枚举定义好我们所有的接口url，方便后续复用，
然后我们用ts的typeof操作符从todos数据倒推出类型。  

接下来用泛型条件类型来定义一个工具类型，根据泛型传入的值来返回一个自定义的key 
```ts
type Key<U> =
  U extends Urls.TOGGLE ? 'toggle': 
  U extends Urls.ADD ? 'add': 
  U extends Urls.TODOS ? 'todos': 
  'other'
```

这个Key的作用就是，假设我们传入
```ts
type K = Key<Urls.TODOS>
```
会返回`todos`这个字符串类型，它有什么用呢，接着看就知道了。

现在需要把axios的函数类型声明的更加严格，我们需要把入参payload的类型和返回值的类型都通过传入的url推断出来，这里要利用泛型推导：
```ts
function axios <U extends Urls>(url: U, payload?: Payload<U>): Promise<Result<U>> | never
```

不要被这长串吓到，先一步步来分解它，  
1. `<U extends Urls>`首先泛型U用extends关键字做了类型约束，它必须是Urls枚举中的一个，
2. `(url: U, payload?: Payload<U>)`参数中，url参数和泛型U建立了关联，这样我们在调用axios函数时，就会动态的根据传入的url来确定上下文中U的类型，接下来用`Payload<U>`把U传入Payload工具类型中。
3. 最后返回值用`Promise<Result<U>>`，还是一样的原理，把U交给Result工具类型进行推导。

接下来重要的就是看Payload和Result的实现了。

```ts

type Payload<U> = {
  toggle: number
  add: Todo,
  todos: any,
  other: any
}[Key<U>]

```
刚刚定义的Key\<U\>工具类型就派上用场了，假设我们调用axios(Urls.TOGGLE),那么U被推断Urls.TOGGLE，传给Payload的就是`Payload<Urls.TOGGLE>`，那么Key\<U\>返回的结果就是Key\<Urls.TOGGLE\>，即为`toggle`，

那么此时推断的结果是
```ts
Payload<Urls.TOGGLE> = {
  toggle: number
  add: Todo,
  todos: any,
  other: any
}['toggle']
```
此时todos命中的就是前面定义的类型集合中第一个`toggle: number`，
所以此时`Payload<Urls.TOGGLE>`就这样被推断成了number 类型。

Result也是类似的实现：
```ts
type Result<U> = {
  toggle: boolean
  add: boolean,
  todos: Todos
  other: any
}[Key<U>]
```

这时候再回头来看函数类型
```ts
function axios <U extends Urls>(url: U, payload?: Payload<U>): Promise<Result<U>> | never 
```
是不是就清楚很多了，传入不同的参数会推断出不同的payload入参，以及返回值类型。

此时在来到app.ts里，看新版refreshTodos函数
```js
  const refreshTodos = () => {
    axios(Urls.TODOS).then((todos) => {
      setTodos(todos)
    })
  }
```
axios后面的泛型约束被去掉了，then里面的todos依然被成功的推断为Todos类型。

![todos](https://user-gold-cdn.xitu.io/2019/11/27/16eaba8268f9222d?w=405&h=183&f=png&s=70512)

这时候就完美了吗？并没有，还有最后一点优化。

## 函数重载

写到这里，类型基本上是比较严格了，但是还有一个问题，就是在调用呢`axios(Urls.TOGGLE)`这个接口的时候，我们其实是一定要传递第二个参数的，但是因为`axios(Urls.TODOS)`是不需要传参的，所以我们只能在axios的函数签名把payload?设置为可选，这就导致了一个问题，就是ts不能明确的知道哪些接口需要传参，哪些接口不需要传参。

注意下图中的payload是带?的。
![toggle](https://user-gold-cdn.xitu.io/2019/11/27/16eaba932b3f795a?w=678&h=103&f=png&s=43151)

要解决这个问题，需要用到ts中的函数重载。

首先把需要传参的接口和不需要传参的接口列出来。

```ts
type UrlNoPayload =  Urls.TODOS
type UrlWithPayload = Exclude<Urls, UrlNoPayload>
```

这里用到了TypeScript的内置类型Exclude，用来在传入的类型中排除某些类型，这里我们就有了两份类型，`需要传参的Url集合`和`无需传参的Url集合`。

接着开始写重载
```ts
function axios <U extends UrlNoPayload>(url: U): Promise<Result<U>>
function axios <U extends UrlWithPayload>(url: U, payload: Payload<U>): Promise<Result<U>> | never
function axios <U extends Urls>(url: U, payload?: Payload<U>): Promise<Result<U>> | never {
  // 具体实现
}
```

根据extends约束到的不同类型，来重写函数的入参形式，最后用一个最全的函数签名（一定是要能兼容之前所有的函数签名的，所以最后一个签名的payload需要写成可选）来进行函数的实现。

此时如果再空参数调用toggle，就会直接报错，因为只有在请求todos的情况下才可以不传参数。
![toggle严格](https://user-gold-cdn.xitu.io/2019/11/27/16eabaec64ac4c0a?w=553&h=165&f=png&s=81097)


## 后记
到此我们就实现了一个严格类型的React应用，写这篇文章的目的不是让大家都要在公司的项目里去把类型推断做到极致，毕竟一切的技术还是为业务服务的。  

但是就算是写宽松版本的TypeScript，带来的收益也远远比裸写JavaScript要高很多，尤其是在别人需要复用你写的工具函数或者组件时。   

而且TypeScript也可以在开发时就避免很多粗心导致的错误，详见：  
TypeScript 解决了什么痛点？ - justjavac的回答 - 知乎
https://www.zhihu.com/question/308844713/answer/574423626

本文涉及到的所有代码都在  
https://github.com/sl1673495/ts-react-todo 中，有兴趣的同学可以拉下来自己看看。