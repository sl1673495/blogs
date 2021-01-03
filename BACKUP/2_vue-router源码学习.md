# [vue-router源码学习](https://github.com/sl1673495/blogs/issues/2)

### 初始化
通过Vue.mixin混入beforeCreate方法执行初始化

根组件： 
把this._routerRoot定义为根实例
子组件：
通过Vue.util.defineReactive把_route作为响应式对象定义到Vue实例this下(指向this._router.history.current)，
并且把子组件的this._routerRoot指向根实例

通过Vue.component将router-view和router-link注册成全局组件

通过Object.defineProperty往Vue.prototype上挂上了
$router(指向this._routerCurrent._router)
$router(指向this._routerCurrent._route 之前被定义为响应式了)
所以每个Vue实例都可以拿到这俩个很重要的对象。

### hash路由模式
回退： 监听浏览器的popstate或hashchange事件，重新执行transitionTo方法。
改变： 调用window.history的pushState、replaceState api

this.$router.push 本质上调用了内部history实例的push方法，计算出带hash值的新路径，执行transitionTo切换路由。

### router-view：
funcitional component
在render函数的第二个参数可以解构出{props, children, parent, data}
通过 const h = parent.$createElement 拿到父组件的Vue实例的创建VNode方法。

初始化:
```js   
    data.routerView = true
    // directly use parent context's createElement() function
    // so that components rendered by router-view can resolve named slots
    // 这个注释值得注意，因为调用了父组件的createElement 所以context是父组件实例，
    // 之前在学习Vue源码的slot部分有注意到 命名slot只有在context正确的情况下才会渲染
    const h = parent.$createElement
    const name = props.name
    const route = parent.$route
    const cache = parent._routerViewCache || (parent._routerViewCache = {})
```

通过初始化时候定义的data.routerView = true网上寻找父组件的routerView
从而确定routerView的层级，这个层级可以用来匹配router配置里的层级，方便找到应该渲染的组件!
```js
    // determine current view depth, also check to see if the tree
    // has been toggled inactive but kept-alive.
    let depth = 0
    let inactive = false
    while (parent && parent._routerRoot !== parent) {
      // 父组件的data.routerView为true 说明是嵌套的router-view 将depth + 1
      if (parent.$vnode && parent.$vnode.data.routerView) {
        depth++
      }
      if (parent._inactive) {
        inactive = true
      }
      parent = parent.$parent
    }
    // 记录这个routerView的深度
    data.routerViewDepth = depth
```

通过depth 和route.matched这个records数组 找到对应的组件 并且cache下来
```js
   // render previous view if the tree is inactive and kept-alive
    if (inactive) {
      return h(cache[name], data, children)
    }

    const matched = route.matched[depth]
    // render empty node if no matched route
    if (!matched) {
      cache[name] = null
      return h()
    }

    const component = cache[name] = matched.components[name]
```
渲染组件。
```js
 return h(component, data, children)
```

另外来看 中间有一段给data上挂载registerRouteInstance方法
这个方法会在初始化的时候指定beforeCreate调用 registerInstance(this, this) 也就是注册为当前实例
并且destory调用 registerInstance(this) 也就是注册为空，销毁 
这个实例是给vue-router内部生成导航守卫时用的
```js
    // attach instance registration hook
    // this will be called in the instance's injected lifecycle hooks
    data.registerRouteInstance = (vm, val) => {
      // val could be undefined for unregistration
      const current = matched.instances[name]
      if (
        (val && current !== vm) ||
        (!val && current === vm)
      ) {
        matched.instances[name] = val
      }
    }
```

写到这里 为什么路径切换了 router-view会重新render还是个悬念，接下来我们揭晓：
在初始化的时候，_route被定义为响应式属性了。
router-view的render刚开始的
```js
    const route = parent.$route
```
这段代码访问了$route, 收集到了依赖,
在init中有一个监听, 对_route做了修改， 此时就会触发Watcher的重新渲染
```js
    history.listen(route => {
      this.apps.forEach((app) => {
        app._route = route
      })
    })
```
