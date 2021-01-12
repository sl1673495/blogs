---
title: 'Vue中的组件从初始化到挂载经历了什么'
date: '2020-01-04'
spoiler: ''
---

# 一个组件从初始化到挂载经历了什么

下面的所有解析都以这段代码为基准：

```js
new Vue({
  el: "#app",
  render: h => h(AppSon)
});
```

其中 AppSon 就是组件，它是一个对象：

```js
const AppSon = {
  name: "app-son",
  data() {
    return {
      msg: 123
    };
  },
  render(h) {
    return h("span", [this.msg]);
  }
};
```

这样一段代码，在 Vue 内部组件化的流程顺序：

1. `$createElement`，其实 render 接受的参数 h 就是`this.$createElement`的别名
2. `createElement`，做一下参数的整理，就进入下一步
3. `_createElement`，比较关键的一步，在这个方法里会判断组件是`span`这样的 html 标签，还是用户写的自定义组件。
4. `createComponent`，生成组件的 vnode，安装一些 vnode 的生命周期，返回 vnode

其实，render 函数最终返回的就是`vnode`。

## 流程解析

## \$createElement

调用`createElement`方法，第一个参数是 vm 实例自身，剩余的参数原封不动的透传。

```js
vm.$createElement = function(a, b, c, d) {
  return createElement(vm, a, b, c, d, true);
};
```

## createElement

```js
function createElement (
  // 上一步传进来的vm实例，在哪个组件的render里调用，context就是哪个组件的实例。
  context,
  // 在例子中，就是AppSon这个对象
  tag,
  // 可以传入props等交给子组件的选项
  data,
  // 子组件中间的内容
  children,
  ...
)
```

之后有一个判断

```js
if (typeof tag === "string") {
  // html标签流程
} else {
  // 组件化流程
  vnode = createComponent(tag, data, context, children);
}
```

`createComponent`接受的四个参数就是上文的方法传进去的

## createComponent

```js
function createComponent(
  // 还是上文中的tag，本文中是AppSon对象
  Ctor,
  // 下面的都一致
  data,
  context,
  children
) {
  if (isObject(Ctor)) {
    Ctor = baseCtor.extend(Ctor);
  }

  // 给vnode安装一些生命周期函数（注意这里是vnode的生命周期，而不是created那些组件声明周期）
  installComponentHooks(data);

  var vnode = new VNode(
    "vue-component-" + Ctor.cid + (name ? "-" + name : ""),
    data,
    undefined,
    undefined,
    undefined,
    context,
    {
      Ctor: Ctor,
      propsData: propsData,
      listeners: listeners,
      tag: tag,
      children: children
    },
    asyncFactory
  );

  return vnode;
}
```

下面有一个逻辑

```js
if (isObject(Ctor)) {
  Ctor = baseCtor.extend(Ctor);
}
```

其中`baseCtor.extend(Ctor)`就可以暂时理解为 Vue.extend，这是一个全局共用方法，从名字也可以看出它主要是做一些继承，让子组件的也拥有父组件的一些能力，这个方法返回的是一个新的构造函数。

**组件对象最终都会用 extend 这个 api 变成一个组件构造函数，这个构造函数继承了父构造函数 Vue 的一些属性**

extend 函数具体做了什么呢？

### createComponent / Vue.extend

```js
Vue.extend = function(extendOptions) {
  extendOptions = extendOptions || {};
  // this在这个例子其实就是Vue。
  var Super = this;

  // Appson这个组件的构造函数
  var Sub = function VueComponent(options) {
    // 这个_init就是调用的Vue.prototype._init
    this._init(options);
  };

  // 把Vue.prototype生成一个
  // { __proto__: Vue.prototype }这样的对象，
  // 直接赋值给子组件构造函数的prototype
  // 此时子组件构造函数的原型链上就可以拿到Vue的原型链的属性了
  Sub.prototype = Object.create(Super.prototype);
  Sub.prototype.constructor = Sub;

  // 合并Vue.option上的一些全局配置
  Sub.options = mergeOptions(Super.options, extendOptions);
  Sub["super"] = Super;

  // 拷贝静态函数
  Sub.extend = Super.extend;
  Sub.mixin = Super.mixin;
  Sub.use = Super.use;

  // 返回子组件的构造函数
  return Sub;
};
```

到了这一步，我们一开始定义的 Appson 组件对象，已经变成了一个函数，可以通过 new AppSon()来生成一个组件实例了，并且组件配置对象被合并到了`Sub.options`这个构造函数的静态属性上。

### createComponent / installComponentHooks

`installComponentHooks`这个方法是为了给 vnode 上加入一些生命周期函数，

其中有一个`init`生命周期，这个周期后面被调用的时候再讲解。

### createComponent / new VNode

可以看出，主要是生成 vnode 的实例，并且赋值给`vnode.componentInstance`，并且调用`$mount`方法挂载 dom 节点，注意这个`init`生命周期此时还没有调用。

到这为止`render`的流程就讲完了，现在我们拥有了一个`vnode`节点，它有一些关键的属性

1. vnode.componentOptions.Ctor: 上一步`extend`生成的子组件构造函数。
2. vnode.data.hook: 里面保存了`init`等 vnode 生命周期方法
3. vnode.context: 调用\$createElement 的是哪个实例，这个 context 就是谁。

## \$mount

最外层的组件调用了`$mount`后，组件在初次渲染的时候其实是递归去调用`createElm`的，而`createElm`中会去调用组件 vnode 的`init`钩子。

```js
if (isDef((i = i.hook)) && isDef((i = i.init))) {
  i(vnode);
}
```

然后就会走进 vnode 的`init`生命周期的逻辑

```js
const child = (vnode.componentInstance = createComponentInstanceForVnode(
  vnode,
  activeInstance
));
child.$mount(vnode.elm);
```

`createComponentInstanceForVnode`:

```js
createComponentInstanceForVnode (
  vnode: any,
  parent: any,
): Component {
  const options: InternalComponentOptions = {
    // 标记这是一个组件节点
    _isComponent: true,
    // Appson组件的vnode
    _parentVnode: vnode,
    // 当前正在活跃的父组件实例，在本例中就是根Vue实例
    // new Vue({
    //   el: "#app",
    //   render: h => h(AppSon)
    // });
    parent
  }

  return new vnode.componentOptions.Ctor(options)
}
```

可以看出，最终调用组件构造函数，然后调用`\_init` 方法，它接受到的 `options` 不再是

```js
{
  data() {

  },
  props: {

  },
  methods() {

  }
}
```

这样的传统 Vue 对象了，而是

```
{
    _isComponent: true,
    _parentVnode: vnode,
    parent,
  }
```

这样的一个对象，然后\_init 内部会针对这样特征的对象，调用`initInternalComponent`做一些特殊的处理，
这里有一个疑惑点，那刚刚子组件声明的 data 那些选项哪去了呢？
其实是被保存在`Ctor.options`里了。

然后在`initInternalComponent`中，把子组件构造函数上保存的 options 再转移到`vm.$options.__proto__`上。

```js
var opts = (vm.$options = Object.create(vm.constructor.options));
```

之后生成了子组件的实例后，又会调用`child.$mount(vnode.elm)`，继续的去递归这个初始化的过程。
