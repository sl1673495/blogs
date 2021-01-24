---
title: 'React Core Team 成员开发的火焰图组件技术揭秘。'
date: '2021-01-24'
spoiler: ''
---

## 前言

最近在业务的开发中，业务方需要我们性能监控平台提供火焰图来展示函数堆栈以及相关的耗时信息。

根据 Brendan Gregg 在 [FlameGraph](http://www.brendangregg.com/flamegraphs.html) 主页中的定义：

> Flame graphs are a visualization of profiled software, allowing the most frequent code-paths to be identified quickly and accurately
>
> 火焰图是一种可视化分析软件，让我们可以快速准确的发现调用频繁的函数堆栈。

可以在这里查看[火焰图的示例](http://www.brendangregg.com/FlameGraphs/cpu-mysql-updated.svg)。

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/aeb03bd78dea469f845a922df5bde922~tplv-k3u1fbpfcp-watermark.image)

其实不光是调用频率，火焰图也同样适合描述函数调用的堆栈以及耗时频率，比如 Chrome DevTools 中的火焰图：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2efa3db5ca234327aac18adf439bdaea~tplv-k3u1fbpfcp-watermark.image)

其实根节点在顶部，叶子节点在底部的这种图形称为 Icicle charts（冰柱图）更合适，不过为了理解方便，下文还是统一称为火焰图。

本文想要分析的源码并不是上面的任意一种，而是 React 浏览器插件中使用的火焰图组件，它是由 React 官方成员 Brian Vaughn 开发的 [react-flame-graph](react-flame-graph)。

## 本地调试

这个库是由 rollup 负责构建，而 [react-flame-graph 的示例网站](https://react-flame-graph.now.sh/) 则是用 webpack 构建。

所以本地想要调试的话，clone 这个库以后：

1. 分别在根目录和 website 目录安装依赖。
2. 在根目录执行 `npm link` 链接到全局，再去 `website` 目录 `npm link react-flame-graph` 建立软链接。
3. 在根目录执行 `npm run start` 开启 rollup 的 watch 编译模式。
4. 在 website 目录执行 `npm run start` 开启 webpack dev 模式，进入示例网站调试。

由于这个库比较老，最好用 nrm 把 node 版本调整到 10.15.0，我是在这个版本下成功安装了依赖。

先来简单看一下火焰图的效果：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/95968bf94b864f92b4da3e5fdb8b241e~tplv-k3u1fbpfcp-watermark.image)

## 组件揭秘

### 使用
想要使用这个组件，必须传入的数据是 `width` 和 `data`，

`width` 是指整个火焰图容器的宽度，后续计算每个的宽度都需要用到。

`data` 格式则是树形结构：

```js
const simpleData = {
  name: 'foo',
  value: 5,
  children: [
    {
      name: 'custom tooltip',
      value: 1,
      tooltip: 'Custom tooltip shown on hover',
    },
    {
      name: 'custom background color',
      value: 3,
      backgroundColor: '#35f',
      color: '#fff',
      children: [
        {
          name: 'leaf',
          value: 2,
        },
      ],
    },
  ],
};
```

除了标准树的 `name`, `children` 外，这里还有一个必须的属性 `value`，根据每一层的 `value` 也就决定了每一个火焰图块的宽度。

比如这个数据的宽度树是
```
width: 5
 - width 1
 - width 3
  - width 2
```

那么生成的火焰图也会遵循这个宽度比例：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a32cae63e1454ce2bb017b1e590f4207~tplv-k3u1fbpfcp-watermark.image)

而在业务场景中，这里一般每个矩形块对应一次函数调用，它会统计到总耗时，这个值就可以用作为 `value`。

### 数据转换

这个组件的第一步，是把这份递归的数据转化为拉平的数组。

递归数据虽然比较直观的展示了层级，但是用作渲染却比较麻烦。

整个火焰图的渲染，其实就是每个**层级**对应的**所有矩形块**逐行渲染而已，所以平级的数组更适合。

我们的目标是把数据整理成这样的结构：
```js
levels: [
  ["_0"],
  ["_1", "_2"],
  ["_3"],
],
nodes: {
  _0: { width: 1, depth: 0, left: 0, name: "foo", …}
  _1: { width: 0.2, depth: 1, left: 0, name: "custom tooltip", …}
  _2: { width: 0.6, depth: 1, left: 0.2, name: "custom background color", …}
  _3: { width: 0.4, depth: 2, left: 0.2, name: "leaf", …}
}
```

一目了然，`levels` 对应层级关系和每层的节点 id，`nodes` 则是 id 所对应的节点数据。

其实这一步很关键，这个数据基本把渲染的层级和样式决定好了。

这里的 `nodes` 中的 `width` 经过了 `width: value / maxValue` 这样的处理，而 `maxValue` 其实就是根节点定义的那个 `width`，本例中对应数值为 `5`，所以：

- 第一层的节点宽度是 `5 / 5 = 1`
- 第二层的节点的宽度自然就是 `1 / 5 = 0.2`， `3 / 5 = 0.6`。

在这里处理的好处是渲染的时候可以直接通过和火焰图容器的宽度，也就是真实 dom 节点的宽度相乘，得到矩形块真实宽度。

转换部分其实就是一次递归，代码如下：

```js
export function transformChartData(rawData: RawData): ChartData {
  let uidCounter = 0;

  const maxValue = rawData.value;

  const nodes = {};
  const levels = [];

  function convertNode(
    sourceNode: RawData,
    depth: number,
    leftOffset: number
  ): ChartNode {
    const {
      backgroundColor,
      children,
      color,
      id,
      name,
      tooltip,
      value,
    } = sourceNode;

    const uidOrCounter = id || `_${uidCounter}`;

    // 把这个 node 放到 map 中
    const targetNode = (nodes[uidOrCounter] = {
      backgroundColor:
        backgroundColor || getNodeBackgroundColor(value, maxValue),
      color: color || getNodeColor(value, maxValue),
      depth,
      left: leftOffset,
      name,
      source: sourceNode,
      tooltip,
      // width 属性是（当前节点 value / 根元素的 value）
      width: value / maxValue,
    });

    // 记录每个 level 对应的 uid 列表
    if (levels.length <= depth) {
      levels.push([]);
    }
    levels[depth].push(uidOrCounter);

    // 把全局的 UID 计数器 + 1
    uidCounter++;

    if (Array.isArray(children)) {
      children.forEach(sourceChildNode => {
        // 进一步递归
        const targetChildNode = convertNode(
          sourceChildNode,
          depth + 1,
          leftOffset
        );
        leftOffset += targetChildNode.width;
      });
    }

    return targetNode;
  }

  convertNode(rawData, 0, 0);

  const rootUid = rawData.id || '_0';

  return {
    height: levels.length,
    levels,
    nodes,
    root: rootUid,
  };
}
```

## 渲染列表

转换好数据结构后，就要开始渲染部分了。这里作者 Brian Vaughn 用了他写的 React 虚拟滚动库 [react-window](https://github.com/bvaughn/react-window) 去优化长列表的性能。

```js
// FlamGraph.js
const itemData = this.getItemData(
  data,
  focusedNode,
  ...,
  width
);
    
<List
  height={height}
  innerTagName="svg"
  itemCount={data.height}
  itemData={itemData}
  itemSize={rowHeight}
  width={width}
>
  {ItemRenderer}
</List>;
```

这里需要注意的是把外部传入的一些数据整合成了虚拟列表组件所需要的 itemData，方法如下：

```js
import memoize from 'memoize-one';

getItemData = memoize(
  (
    data: ChartData,
    disableDefaultTooltips: boolean,
    focusedNode: ChartNode,
    focusNode: (uid: any) => void,
    handleMouseEnter: (event: SyntheticMouseEvent<*>, node: RawData) => void,
    handleMouseLeave: (event: SyntheticMouseEvent<*>, node: RawData) => void,
    handleMouseMove: (event: SyntheticMouseEvent<*>, node: RawData) => void,
    width: number
  ) =>
    ({
      data,
      disableDefaultTooltips,
      focusedNode,
      focusNode,
      handleMouseEnter,
      handleMouseLeave,
      handleMouseMove,
      scale: (value) => (value / focusedNode.width) * width,
    }: ItemData)
);
```

`memoize-one` 是一个用来做函数缓存的库，它的作用是传入的参数不发生改变的情况下，直接返回上一次计算的值。

对于新版的 React 来说，直接用 `useMemo` 配合依赖也可以达到类似的效果。

这里就是简单的把数据保存了一下，唯一不同的就是新定义了一个方法 `scale`：

```js
scale: value => (value / focusedNode.width) * width,
```

它是负责计算真实 DOM 宽度的，所有节点的宽度都会参照 `focuesdNode` 的宽度再乘以火焰图容易的真实 DOM 宽度来计算。

所以点击了某个节点**聚焦它**后，它的子节点宽度也会发生变化。

`focuesdNode`为根节点时：

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4e6a2d63600b47ae8e1e76ffd57ca10e~tplv-k3u1fbpfcp-watermark.image)

点击 `custom background color` 这个节点后：

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/dfef3b6facce484594e064c6567f227a~tplv-k3u1fbpfcp-watermark.image)

这里 children 的位置用花括号的方式放了一个组件引用 `ItemRenderer`，其实这是 render props 的用法，相当于：

```js
<List>
  {props => <ItemRenderer {...props} />}
</List>
```

而 `ItemRenderer` 组件其实就负责通过数据来渲染每一行的矩形块，由于数据中有 3 层 `level`，所以这个组件会被调用 3 次。

每一次都可以拿到对应层级的 `uids`，通过 `uid` 又可以拿到 `node` 相关的信息，完成渲染。

```jsx
// ItemRenderer
const focusedNodeLeft = scale(focusedNode.left);
const focusedNodeWidth = scale(focusedNode.width);

const top = parseInt(style.top, 10);

const uids = data.levels[index];

return uids.map((uid) => {
  const node = data.nodes[uid];
  const nodeLeft = scale(node.left);
  const nodeWidth = scale(node.width);

  // 太小的矩形块不渲染
  if (nodeWidth < minWidthToDisplay) {
    return null;
  }

  // 超出视图的部分就直接不渲染了
  if (
    nodeLeft + nodeWidth < focusedNodeLeft ||
    nodeLeft > focusedNodeLeft + focusedNodeWidth
  ) {
    return null;
  }

  return (
    <LabeledRect
      ...
      onClick={() => itemData.focusNode(uid)}
      x={nodeLeft - focusedNodeLeft}
      y={top}
    />
  );
});
```

这里所有的数值量都是通过 `scale` 根据容器宽度算出来的真实 DOM 宽度。

这里计算偏移量比较巧妙的点在于，最终传递给矩形块组件`LabeledRect`的 `x` 也就是横轴的偏移量，是根据 `focusedNode` 的 `left` 值计算出来的。

如果父节点被 `focus` 后，它是占据整行的，子节点的 `x` 也会紧随父节点偏移到最左边去。

比如这个图中聚焦的节点是 `foo`，那么最底下的 `leaf` 节点计算偏移量时，`focusedNodeLeft` 就是 0，它的偏移量就保持自身的 `left` 不变。

![](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4e6a2d63600b47ae8e1e76ffd57ca10e~tplv-k3u1fbpfcp-watermark.image)

而聚焦的节点变成 `custom background color` 时，由于聚焦节点的 left 是 200，所以 `leaf` 节点也会左移 200 像素。

![](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/dfef3b6facce484594e064c6567f227a~tplv-k3u1fbpfcp-watermark.image)

也许有同学会疑惑，在 `custom background color` 聚焦时，它的父节点 `foo` 节点本身偏移量就是 0 了，再减去 200，不是成负数了嘛，那能父节点的矩形块保证占据一整行吗？

这里再回顾 `scale` 的逻辑：`value => (value / focusedNode.width) * width`，计算父节点的宽度时是 `scale(父节点的宽度)`，而此时父节点的 `width` 是大于聚焦的节点的，所以最终的宽度能保证在偏移一定程度的负数时，父节点还是占满整行。

最后 `LabeledRect` 就是用 svg 渲染出矩形，没什么特殊的。

## 总结

看似复杂的火焰图，在设计了良好的数据结构以及组件结构以后，一层层梳理下来，其实也并不难。