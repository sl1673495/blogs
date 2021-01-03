# [Vue 进阶必学之高阶组件实战](https://github.com/sl1673495/blogs/issues/41)

## 前言

高阶组件这个概念在 React 中一度非常流行，但是在 Vue 的社区里讨论的不多，本篇文章就真正的带你来玩一个进阶的骚操作。

先和大家说好，本篇文章的核心是学会这样的思想，也就是 `智能组件` 和 `木偶组件` 的解耦合，没听过这个概念没关系，下面会详细说明。

这可以有很多方式，比如 `slot-scopes`，比如未来的`composition-api`。本篇所写的代码也不推荐用到生产环境，生产环境有更成熟的库去使用，这篇强调的是 `思想`，顺便把 React 社区的玩法移植过来皮一下。

**不要喷我，不要喷我，不要喷我！！**，此篇只为演示高阶组件的思路，如果实际业务中想要简化文中所提到的异步状态管理，请使用基于 `slot-scopes` 的开源库 [vue-promised](https://github.com/posva/vue-promised)

## 例子
本文就以平常开发中最常见的需求，也就是`异步数据的请求`为例，先来个普通玩家的写法：

```xml
<template>
    <div v-if="error">failed to load</div>
    <div v-else-if="loading">loading...</div>
    <div v-else>hello {{result.name}}!</div>
</template>

<script>
export default {
  data() {
    return {
        result: {
          name: '',
        },
        loading: false,
        error: false,
    },
  },
  async created() {
      try {
        // 管理loading
        this.loading = true
        // 取数据
        const data = await this.$axios('/api/user')  
        this.data = data
      } catch (e) {
        // 管理error
        this.error = true  
      } finally {
        // 管理loading
        this.loading = false
      }
  },
}
</script>
```

一般我们都这样写，平常也没感觉有啥问题，但是其实我们每次在写异步请求的时候都要有 `loading`、 `error` 状态，都需要有 `取数据` 的逻辑，并且要管理这些状态。

那么想个办法抽象它？好像特别好的办法也不多，React 社区在 Hook 流行之前，经常用 `HOC`（high order component） 也就是高阶组件来处理这样的抽象。

## 高阶组件是什么？
说到这里，我们就要思考一下高阶组件到底是什么概念，其实说到底，高阶组件就是：

`一个函数接受一个组件为参数，返回一个包装后的组件`。

## 在 React 中

在 React 里，组件是 `Class`，所以高阶组件有时候会用 `装饰器` 语法来实现，因为 `装饰器` 的本质也是接受一个 `Class` 返回一个新的 `Class`。

在 React 的世界里，高阶组件就是 `f(Class) -> 新的Class`。

## 在 Vue 中

在 Vue 的世界里，组件是一个对象，所以高阶组件就是一个函数接受一个对象，返回一个新的包装好的对象。

类比到 Vue 的世界里，高阶组件就是 `f(object) -> 新的object`。


## 智能组件和木偶组件
如果你还不知道 `木偶` 组件和 `智能` 组件的概念，我来给你简单的讲一下，这是 React 社区里一个很成熟的概念了。

`木偶` 组件： 就像一个牵线木偶一样，只根据外部传入的 `props` 去渲染相应的视图，而不管这个数据是从哪里来的。

`智能` 组件： 一般包在 `木偶` 组件的外部，通过请求等方式获取到数据，传入给 `木偶` 组件，控制它的渲染。

一般来说，它们的结构关系是这样的：

```xml
<智能组件>
  <木偶组件 />
</智能组件>
```

它们还有另一个别名，就是 `容器组件` 和 `ui组件`，是不是很形象。

## 实现

具体到上面这个例子中（如果你忘了，赶紧回去看看，哈哈），我们的思路是这样的，

1. 高阶组件接受 `木偶组件` 和 `请求的方法` 作为参数
2. 在 `mounted` 生命周期中请求到数据
3. 把请求的数据通过 `props` 传递给 `木偶组件`。

接下来就实现这个思路，首先上文提到了，`HOC` 是个函数，本次我们的需求是实现请求管理的 `HOC`，那么先定义它接受两个参数，我们把这个 `HOC` 叫做 `withPromise`。

并且 `loading`、`error` 等状态，还有 `加载中`、`加载错误` 等对应的视图，我们都要在 `新返回的包装组件` ，也就是下面的函数中 `return 的那个新的对象` 中定义好。

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    name: "with-promise",
    data() {
      return {
        loading: false,
        error: false,
        result: null,
      };
    },
    async mounted() {
      this.loading = true;
      const result = await promiseFn().finally(() => {
        this.loading = false;
      });
      this.result = result;
    },
  };
};
```
在参数中：
1. `wrapped` 也就是需要被包裹的组件对象。
2. `promiseFunc` 也就是请求对应的函数，需要返回一个 Promise

看起来不错了，但是函数里我们好像不能像在 `.vue` 单文件里去书写 `template` 那样书写模板了，

但是我们又知道模板最终还是被编译成组件对象上的 `render` 函数，那我们就直接写这个 `render` 函数。（注意，本例子是因为便于演示才使用的原始语法，脚手架创建的项目可以直接用 `jsx` 语法。）

在这个 `render` 函数中，我们把传入的 `wrapped` 也就是木偶组件给包裹起来。

这样就形成了 `智能组件获取数据` -> `木偶组件消费数据`，这样的数据流动了。

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    data() { ... },
    async mounted() { ... },
    render(h) {
      return h(wrapped, {
        props: {
          result: this.result,
          loading: this.loading,
        },
      });
    },
  };
};
```

到了这一步，已经是一个勉强可用的雏形了，我们来声明一下 `木偶` 组件。

这其实是 `逻辑和视图分离` 的一种思路。

```js
const view = {
  template: `
    <span>
      <span>{{result?.name}}</span>
    </span>
  `,
  props: ["result", "loading"],
};
```
注意这里的组件就可以是任意 `.vue` 文件了，我这里只是为了简化而采用这种写法。

然后用神奇的事情发生了，别眨眼，我们用 `withPromise` 包裹这个 `view` 组件。

```js
// 假装这是一个 axios 请求函数
const request = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ name: "ssh" });
    }, 1000);
  });
};

const hoc = withPromise(view, request)
```

然后在父组件中渲染它：
```xml
<div id="app">
  <hoc />
</div>

<script>
 const hoc = withPromise(view, request)

 new Vue({
    el: 'app',
    components: {
      hoc
    }
 })
</script>
```

此时，组件在空白了一秒后，渲染出了我的大名 `ssh`，整个异步数据流就跑通了。

现在在加上 `加载中` 和 `加载失败` 视图，让交互更友好点。

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    data() { ... },
    async mounted() { ... },
    render(h) {
      const args = {
        props: {
          result: this.result,
          loading: this.loading,
        },
      };

      const wrapper = h("div", [
        h(wrapped, args),
        this.loading ? h("span", ["加载中……"]) : null,
        this.error ? h("span", ["加载错误"]) : null,
      ]);

      return wrapper;
    },
  };
};

```

到此为止的代码可以在 [效果预览](https://sl1673495.github.io/vue-hoc-codes/hoc-promise-easy.html) 里查看，控制台的 source 里也可以直接预览源代码。

## 完善
到此为止的高阶组件虽然可以演示，但是并不是完整的，它还缺少一些功能，比如

1. 要拿到子组件上定义的参数，作为初始化发送请求的参数。
2. 要监听子组件中请求参数的变化，并且重新发送请求。
3. 外部组件传递给 `hoc` 组件的参数现在没有透传下去。

第一点很好理解，我们请求的场景的参数是很灵活的。

第二点也是实际场景中常见的一个需求。

第三点为了避免有的同学不理解，这里再啰嗦下，比如我们在最外层使用 `hoc` 组件的时候，可能希望传递一些 额外的`props` 或者 `attrs` 甚至是 `插槽slot` 给最内层的 `木偶` 组件。那么 `hoc` 组件作为桥梁，就要承担起将它透传下去的责任。

为了实现第一点，我们约定好 `view` 组件上需要挂载某个特定 `key` 的字段作为请求参数，比如这里我们约定它叫做 `requestParams`。

```js
const view = {
  template: `
    <span>
      <span>{{result?.name}}</span>
    </span>
  `,
  data() {
    // 发送请求的时候要带上它
    requestParams: {
      name: 'ssh'
    }  
  },
  props: ["result", "loading"],
};
```

改写下我们的 `request` 函数，让它为接受参数做好准备，

并且让它的 `响应数据` 原样返回 `请求参数`。
```js
// 假装这是一个 axios 请求函数
const request = (params) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(params);
    }, 1000);
  });
};
```

那么问题现在就在于我们如何在 `hoc` 组件中拿到 `view` 组件的值了，

平常我们怎么拿子组件实例的？ 没错就是 `ref`，这里也用它：

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    data() { ... },
    async mounted() {
      this.loading = true;
      // 从子组件实例里拿到数据
      const { requestParams } = this.$refs.wrapped
      // 传递给请求函数
      const result = await promiseFn(requestParams).finally(() => {
        this.loading = false;
      });
      this.result = result;
    },
    render(h) {
      const args = {
        props: {
          result: this.result,
          loading: this.loading,
        },
        // 这里传个 ref，就能拿到子组件实例了，和平常模板中的用法一样。
        ref: 'wrapped'
      };

      const wrapper = h("div", [
        this.loading ? h("span", ["加载中……"]) : null,
        this.error ? h("span", ["加载错误"]) : null,
        h(wrapped, args),
      ]);

      return wrapper;
    },
  };
};
```

再来完成第二点，子组件的请求参数发生变化时，父组件也要`响应式`的重新发送请求，并且把新数据带给子组件。

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    data() { ... },
    methods: {
      // 请求抽象成方法
      async request() {
        this.loading = true;
        // 从子组件实例里拿到数据
        const { requestParams } = this.$refs.wrapped;
        // 传递给请求函数
        const result = await promiseFn(requestParams).finally(() => {
          this.loading = false;
        });
        this.result = result;
      },
    },
    async mounted() {
      // 立刻发送请求，并且监听参数变化重新请求
      this.$refs.wrapped.$watch("requestParams", this.request.bind(this), {
        immediate: true,
      });
    },
    render(h) { ... },
  };
};
```

第二个问题，我们只要在渲染子组件的时候把 `$attrs`、`$listeners`、`$scopedSlots` 传递下去即可，

此处的 `$attrs` 就是外部模板上声明的属性，`$listeners` 就是外部模板上声明的监听函数，

以这个例子来说：

```xml
<my-input value="ssh" @change="onChange" />
```

组件内部就能拿到这样的结构：
```js
{
  $attrs: {
    value: 'ssh'
  },
  $listeners: {
    change: onChange
  }
}
```

注意，传递 `$attrs`、`$listeners` 的需求不仅发生在高阶组件中，平常我们假如要对 `el-input` 这种组件封装一层变成 `my-input` 的话，如果要一个个声明 `el-input` 接受的 `props`，那得累死，直接透传 `$attrs` 、`$listeners` 即可，这样 `el-input` 内部还是可以照样处理传进去的所有参数。

```xml
// my-input 内部
<template>
  <el-input v-bind="$attrs" v-on="$listeners" />
</template>
```

那么在 `render` 函数中，可以这样透传：

```js
const withPromise = (wrapped, promiseFn) => {
  return {
    ...,
    render(h) {
      const args = {
        props: {
          // 混入 $attrs
          ...this.$attrs,
          result: this.result,
          loading: this.loading,
        },

        // 传递事件
        on: this.$listeners,

        // 传递 $scopedSlots
        scopedSlots: this.$scopedSlots,
        ref: "wrapped",
      };

      const wrapper = h("div", [
        this.loading ? h("span", ["加载中……"]) : null,
        this.error ? h("span", ["加载错误"]) : null,
        h(wrapped, args),
      ]);

      return wrapper;
    },
  };
};
```

至此为止，完整的代码也就实现了：

```xml
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>hoc-promise</title>
  </head>
  <body>
    <div id="app">
      <hoc msg="msg" @change="onChange">
        <template>
          <div>I am slot</div>
        </template>
        <template v-slot:named>
          <div>I am named slot</div>
        </template>
      </hoc>
    </div>
    <script src="./vue.js"></script>
    <script>
      var view = {
        props: ["result"],
        data() {
          return {
            requestParams: {
              name: "ssh",
            },
          };
        },
        methods: {
          reload() {
            this.requestParams = {
              name: "changed!!",
            };
          },
        },
        template: `
          <span>
            <span>{{result?.name}}</span>
            <slot></slot>
            <slot name="named"></slot>
            <button @click="reload">重新加载数据</button>
          </span>
        `,
      };

      const withPromise = (wrapped, promiseFn) => {
        return {
          data() {
            return {
              loading: false,
              error: false,
              result: null,
            };
          },
          methods: {
            async request() {
              this.loading = true;
              // 从子组件实例里拿到数据
              const { requestParams } = this.$refs.wrapped;
              // 传递给请求函数
              const result = await promiseFn(requestParams).finally(() => {
                this.loading = false;
              });
              this.result = result;
            },
          },
          async mounted() {
            // 立刻发送请求，并且监听参数变化重新请求
            this.$refs.wrapped.$watch(
              "requestParams",
              this.request.bind(this),
              {
                immediate: true,
              }
            );
          },
          render(h) {
            const args = {
              props: {
                // 混入 $attrs
                ...this.$attrs,
                result: this.result,
                loading: this.loading,
              },

              // 传递事件
              on: this.$listeners,

              // 传递 $scopedSlots
              scopedSlots: this.$scopedSlots,
              ref: "wrapped",
            };

            const wrapper = h("div", [
              this.loading ? h("span", ["加载中……"]) : null,
              this.error ? h("span", ["加载错误"]) : null,
              h(wrapped, args),
            ]);

            return wrapper;
          },
        };
      };

      const request = (data) => {
        return new Promise((r) => {
          setTimeout(() => {
            r(data);
          }, 1000);
        });
      };

      var hoc = withPromise(view, request);

      new Vue({
        el: "#app",
        components: {
          hoc,
        },
        methods: {
          onChange() {},
        },
      });
    </script>
  </body>
</html>
```

可以在 [这里](https://sl1673495.github.io/vue-hoc-codes/hoc-promise.html) 预览代码效果。

我们开发新的组件，只要拿 `hoc` 过来复用即可，它的业务价值就体现出来了，代码被精简到不敢想象。
```js
import { getListData } from 'api'
import { withPromise } from 'hoc'

const listView = {
  props: ["result"],
  template: `
    <ul v-if="result>
      <li v-for="item in result">
        {{ item }}
      </li>
    </ul>
  `,
};

export default withPromise(listView, getListData)
```

一切变得简洁而又优雅。

## 组合
注意，这一章节对于没有接触过 React 开发的同学可能很困难，可以先适当看一下或者跳过。

有一天，我们突然又很开心，写了个高阶组件叫 `withLog`，它很简单，就是在 `mounted` 声明周期帮忙打印一下日志。

```js
const withLog = (wrapped) => {
  return {
    mounted() {
      console.log("I am mounted!")
    },
    render(h) {
      return h(wrapped)
    },
  }
}
```

这里我们发现，又要把`on`、`scopedSlots` 等属性提取并且透传下去，其实挺麻烦的，我们封装一个从 `this` 上整合需要透传属性的函数：

```js
function normalizeProps(vm) {
  return {
    on: vm.$listeners,
    attr: vm.$attrs,
    // 传递 $scopedSlots
    scopedSlots: vm.$scopedSlots,
  }
}
```

然后在 `h` 的第二个参数提取并传递即可。
```js
const withLog = (wrapped) => {
  return {
    mounted() {
      console.log("I am mounted!")
    },
    render(h) {
      return h(wrapped, normalizeProps(this))
    },
  }
}
```

然后再包在刚刚的 `hoc` 之外：

```js
var hoc = withLog(withPromise(view, request));
```

可以看出，这样的嵌套是比较让人头疼的，我们把 `redux` 这个库里的 `compose` 函数给搬过来，这个 `compose` 函数，其实就是不断的把函数给高阶化，返回一个新的函数。

```js
function compose(...funcs) {
  return funcs.reduce((a, b) => (...args) => a(b(...args)))
}
```

`compose(a, b, c)` 返回的是一个新的函数，这个函数会把传入的几个函数 `嵌套执行`

返回的函数签名：`(...args) => a(b(c(...args)))`

这个函数对于第一次接触的同学来说可能需要很长时间来理解，因为它确实非常复杂，但是一旦理解了，你的函数式思想又更上一层楼了。

但是这也说明我们要改造 `withPromise` 高阶函数了，因为仔细观察这个 `compose`，它会包装函数，让它接受一个参数，并且把第一个函数的`返回值` 传递给下一个函数作为参数。

比如 `compose(a, b)` 来说，`b(arg)` 返回的值就会作为 `a` 的参数，进一步调用 `a(b(args))`

这需要保证参数只有一个。

那么按照这个思路，我们改造 `withPromise`，其实就是要进一步高阶化它，让它返回一个只接受一个参数的函数：

```js
const withPromise = (promiseFn) => {
  // 返回的这一层函数 wrap，就符合我们的要求，只接受一个参数
  return function wrap(wrapped) {
    // 再往里一层 才返回组件
    return {
      mounted() {},
      render() {},
    }
  }
}
```

有了它以后，就可以更优雅的组合高阶组件了：
```js
const compsosed = compose(
    withPromise(request),
    withLog,
)

const hoc = compsosed(view)
```

以上 `compose` 章节的完整代码 [在这](https://github.com/sl1673495/vue-hoc-codes/blob/master/hoc-promise-compose.html)。

注意，这一节如果第一次接触这些概念看不懂很正常，这些在 React 社区里很流行，但是在 Vue 社区里很少有人讨论！关于这个 `compose` 函数，第一次在 React 社区接触到它的时候我完全看不懂，先知道它的用法，慢慢理解也不迟。

## 真实业务场景
可能很多人觉得上面的代码实用价值不大，但是 `vue-router` 的 [高级用法文档](https://github.com/vuejs/vue-router/blob/8975db3659401ef5831ebf2eae5558f2bf3075e1/docs/en/advanced/lazy-loading.md) 里就真实的出现了一个用高阶组件去解决问题的场景。

先简单的描述下场景，我们知道 `vue-router` 可以配置异步路由，但是在网速很慢的情况下，这个异步路由对应的 `chunk` 也就是组件代码，要等到下载完成后才会进行跳转。

这段`下载异步组件`的时间我们想让页面展示一个 `Loading` 组件，让交互更加友好。

在 [Vue 文档-异步组件](https://cn.vuejs.org/v2/guide/components-dynamic-async.html#%E5%A4%84%E7%90%86%E5%8A%A0%E8%BD%BD%E7%8A%B6%E6%80%81) 这一章节，可以明确的看出 Vue 是支持异步组件声明 `loading` 对应的渲染组件的：

```js
const AsyncComponent = () => ({
  // 需要加载的组件 (应该是一个 `Promise` 对象)
  component: import('./MyComponent.vue'),
  // 异步组件加载时使用的组件
  loading: LoadingComponent,
  // 加载失败时使用的组件
  error: ErrorComponent,
  // 展示加载时组件的延时时间。默认值是 200 (毫秒)
  delay: 200,
  // 如果提供了超时时间且组件加载也超时了，
  // 则使用加载失败时使用的组件。默认值是：`Infinity`
  timeout: 3000
})
```

我们试着把这段代码写到 `vue-router` 里，改写原先的异步路由：
```diff
new VueRouter({
    routes: [{
        path: '/',
-        component: () => import('./MyComponent.vue')
+        component: AsyncComponent
    }]
})
```

会发现根本不支持，深入调试了一下 `vue-router` 的源码发现，`vue-router` 内部对于异步组件的解析和 `vue` 的处理完全是两套不同的逻辑，在 `vue-router` 的实现中不会去帮你渲染 `Loading` 组件。

这个肯定难不倒机智的社区大佬们，我们转变一个思路，让 `vue-router` 先跳转到一个 `容器组件`，这个 `容器组件` 帮我们利用 Vue 内部的渲染机制去渲染 `AsyncComponent` ，不就可以渲染出 `loading` 状态了？具体代码如下：

由于 vue-router 的 `component` 字段接受一个 `Promise`，因此我们把组件用 `Promise.resolve` 包裹一层。
```js
function lazyLoadView (AsyncView) {
  const AsyncHandler = () => ({
    component: AsyncView,
    loading: require('./Loading.vue').default,
    error: require('./Timeout.vue').default,
    delay: 400,
    timeout: 10000
  })

  return Promise.resolve({
    functional: true,
    render (h, { data, children }) {
      // 这里用 vue 内部的渲染机制去渲染真正的异步组件
      return h(AsyncHandler, data, children)
    }
  })
}
  
const router = new VueRouter({
  routes: [
    {
      path: '/foo',
      component: () => lazyLoadView(import('./Foo.vue'))
    }
  ]
})
```

这样，在跳转的时候下载代码的间隙，一个漂亮的 `Loading` 组件就渲染在页面上了。

## compose 拆解原理
这一章来一步步拆解 `compose` 函数，看看它到底做了什么样的事情，比较脑壳痛。

**第一次接触这个函数的小伙伴还是酌情跳过吧。**

假设现在是三个高阶组件的组合：
```js
const compsosed = compose(
    withA,
    withB,
    withC
)

const hoc = compsosed(view)
```

1. 首先在 `reduce` 的第一次循环里，`a` 是 `withA`，`b` 是 `withB`，然后 return 了：
```js
(...args) => withA(withB(...args))
```

这个 return 的值就会作为 `reduce` 中下次循环的 `a`

2. 下一次循环，那么此时的`b` 是我们假设的另一个高阶组件 `withC`，那么就 return 了
```js
(...args2) => (...args) => withA(withB(...args))(withC(...args2))
              ↑ 这里是a                          ↑这里是(b(args))
```

3. 此时我们如果外部传入了 `view`，上一步中的 `args2` 就会被消除，这个函数会先归约成这样：

```js
(...args) => withA(withB(...args))(withC(view))
```

此时 `withC(view)` 又进一步的作为`...args`去执行这个函数，进一步归约：

```js
withA(withB(withC(view)))
```

可以看到，`compose` 函数不断的把函数高阶包裹，在执行的时候又一层一层的解包，非常巧妙的构思。


## 总结
本篇文章的所有代码都保存在 [Github仓库](https://github.com/sl1673495/vue-hoc-codes) 中，并且提供[预览](https://sl1673495.github.io/vue-hoc-codes)。

谨以此文献给在我源码学习道路上给了我很大帮助的 《Vue技术内幕》 作者 `hcysun` 大佬，虽然我还没和他说过话，但是在我还是一个工作几个月的小白的时候，一次业务需求的思考就让我找到了这篇文章：[探索Vue高阶组件 | HcySunYang](https://segmentfault.com/p/1210000012743259/read)

当时的我还不能看懂这篇文章中涉及到的源码问题和修复方案，然后改用了另一种方式实现了业务，但是这篇文章里提到的东西一直在我的心头萦绕，我在忙碌的工作之余努力学习源码，期望有朝一日能彻底看懂这篇文章。

时至今日我终于能理解文章中说到的 `$vnode` 和 `context` 代表什么含义，但是这个 bug 在 Vue 2.6 版本由于 `slot` 的实现方式被重写，也顺带修复掉了，现在在 Vue 中使用最新的 `slot` 语法配合高阶函数，已经不会遇到这篇文章中提到的 bug 了。


## ❤️感谢大家
1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)