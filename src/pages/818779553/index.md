---
title: '给 antd 的 Table 编写缩进线、懒加载等功能，以及插件机制在组件中的探索'
date: '2021-03-01'
spoiler: ''
---

在业务需求中，有时候我们需要基于 antd 之类的组件库定制很多功能，本文就以我自己遇到的业务需求为例，一步步实现和优化一个树状表格组件，这个组件会支持：

- ✨ 每个层级**缩进指示线**
- ✨ 远程**懒加载**子节点
- ✨ 每个层级支持**分页**

如果仅仅是这些相对常见业务功能，其实我也不想啰嗦的写成一篇文章。

在这个组件写到后面功能越来越多臃肿的时候，我发现已经各个功能所需要的代码东一堆、西一堆，组件已经变得很难维护了。

一个函数里可能既有懒加载需要的逻辑，又有分页需要的逻辑，更不敢想象再继续加功能时候的痛苦。

这时候我就想，社区知名的框架都是怎么解决耦合机制的呢？**插件**这个词进入了我的脑海，没错，正是插件机制把各种各样逻辑从主框架中**解耦**出来。

所以本文我想重点讲的是，怎么给**组件**也设计一套简单的**插件机制**，来解决代码耦合，难以维护的问题。

业务功能实现的部分作为引子，简单看看即可。

## 功能实现

### 层级缩进线

antd 的 [Table 组件](https://3x.ant.design/components/table-cn/#components-table-demo-dynamic-settings) 默认是没有提供这个功能的，它只是支持了树状结构：

```js
const treeData = [
  {
    function_name: `React Tree Reconciliation`,
    count: 100,
    children: [
      {
        function_name: `React Tree Reconciliation2`,
        count: 100
      }
    ]
  }
]
```

展示效果如下：

![antd-table](https://images.gitee.com/uploads/images/2021/0301/164843_ed628f6e_1087321.png '屏幕截图.png')

可以看出，在展示**大量的函数堆栈**的时候，没有缩进线就会很难受了，业务方也确实和我提过这个需求，可惜之前太忙了，就暂时放一边了。😁

参考 VSCode 中的缩进线效果，可以发现，缩进线是和节点的层级紧密相关的。

![vscode](https://images.gitee.com/uploads/images/2021/0301/165157_dd33ae27_1087321.png '屏幕截图.png')

比如 `src` 目录对应的是第一级，那么它的子级 `client` 和 `node` 就只需要在 td 前面绘制一条垂直线，而 `node` 下的三个目录则绘制两条垂直线。

```
第 1 层： | text
第 2 层： | | text
第 3 层： | | | text
```

只需要在自定义渲染单元格元素的时候，得到以下两个信息。

1. 当前节点的层级信息。
2. 当前节点的父节点是否是展开状态。

所以思路就是对数据进行一次递归处理，把层级标记在节点上，并且要把父节点的引用也标记上，之后再通过传给 `Table` 的 `expandedRowKeys` 属性来维护表格的展开行数据。

```js
function rewriteTree({ dataSource }) {
  traverseTree(dataSource, childrenColumnName, (node, parent, level) => {
    // 记录节点的层级
    node[INTERNAL_LEVEL] = level
    // 记录节点的父节点
    node[INTERNAL_PARENT] = parent
  })
}
```

之后利用 Table 组件提供的 `components` 属性，自定义渲染 `Cell` 组件，也就是 td 元素。

```js
const components = {
  body: {
    cell: (cellProps) => (
      <TreeTableCell
        {...props}
        {...cellProps}
        expandedRowKeys={expandedRowKeys}
      />
    )
  }
}
```

之后，在自定义渲染的 Cell 中，只需要获取两个信息，只需要根据层级和父节点的展开状态，来决定绘制几条垂直线即可。

```js
const isParentExpanded = expandedRowKeys.includes(
  record?.[INTERNAL_PARENT]?.[rowKey]
)
// 只有当前是展示指引线的列 且父节点是展开节点 才会展示缩进指引线
if (dataIndex !== indentLineDataIndex || !isParentExpanded) {
  return <td className={className}>{children}</td>
}

// 只要知道层级 就知道要在 td 中绘制几条垂直指引线 举例来说：
// 第 2 层： | | text
// 第 3 层： | | | text
const level = record[INTERNAL_LEVEL]

const indentLines = renderIndentLines(level)
```

这里的实现就不再赘述，直接通过绝对定位画几条垂直线，再通过对 `level` 进行循环时的下标 `index` 决定 `left` 的偏移值即可。

效果如图所示：

![缩进线](https://images.gitee.com/uploads/images/2021/0301/170832_0c4380cd_1087321.png '屏幕截图.png')

### 远程懒加载子节点

这个需求就需要用比较 hack 的手段实现了，首先观察了一下 Table 组件的逻辑，只有在有 `children` 的子节点上才会展示「展开更多」的图标。

所以思路就是，和后端约定一个字段比如 `has_next`，之后预处理数据的时候先遍历这些节点，加上一个假的占位 `children`。

之后在点击展开的时候，把节点上的这个假 `children` 删除掉，并且把通过改写节点上一个特殊的 `is_loading` 字段，在自定义渲染 Icon 的代码中判断，并且展示 `Loading Icon`。

又来到递归树的逻辑中，我们加入这样的一段代码：

```js
if (node[hasNextKey]) {
  // 树表格组件要求 next 必须是非空数组才会渲染「展开按钮」
  // 所以这里手动添加一个占位节点数组
  // 后续在 onExpand 的时候再加载更多节点 并且替换这个数组
  node[childrenColumnName] = [generateInternalLoadingNode(rowKey)]
}
```

之后我们要实现一个 `forceUpdate` 函数，驱动组件强制渲染：

```js
const [_, forceUpdate] = useReducer((x) => x + 1, 0)
```

再来到 `onExpand` 的逻辑中：

```js
const onExpand = async (expanded, record) => {
  if (expanded && record[hasNextKey] && onLoadMore) {
    // 标识节点的 loading
    record[INTERNAL_IS_LOADING] = true
    // 移除用来展示展开箭头的假 children
    record[childrenColumnName] = null
    forceUpdate()
    const childList = await onLoadMore(record)
    record[hasNextKey] = false
    addChildList(record, childList)
  }
  onExpandProp?.(expanded, record)
}

function addChildList(record, childList) {
  record[childrenColumnName] = childList
  record[INTERNAL_IS_LOADING] = false
  rewriteTree({
    dataSource: childList,
    parentNode: record
  })
  forceUpdate()
}
```

这里 `onLoadMore` 是用户传入的获取更多子节点的方法，
这里比较容易 hack 的地方在于，组件进行展开先给节点写入一个正在加载的标志，然后强制渲染，在加载完成后赋值了新的子节点 `record[childrenColumnName] = childList` 后，我们又通过 `forceUpdate` 去强制组件重渲染，展示出新的子节点。

需要注意，我们递归树加入逻辑的所有逻辑都在 `rewriteTree` 中，所以对于加入的新的子节点，也需要通过这个函数递归一遍，加入 `level`, `parent` 等信息。

新加入的节点的 `level` 需要根据父节点的 `level` 相加得出，不能从 1 开始，否则渲染的缩进线就乱掉了，所以这个函数需要改写，加入 `parentNode` 父节点参数。

```js
function rewriteTree({
  dataSource,
  // 在动态追加子树节点的时候 需要手动传入 parent 引用
  parentNode = null
}) {
  // 在动态追加子树节点的时候 需要手动传入父节点的 level 否则 level 会从 1 开始计算
  const startLevel = parentNode?.[INTERNAL_LEVEL] || 0

  traverseTree(dataSource, childrenColumnName, (node, parent, level) => {
    // 记录节点的层级
    node[INTERNAL_LEVEL] = level + startLevel
    // 记录节点的父节点
    node[INTERNAL_PARENT] = parent || parentNode

    if (node[hasNextKey]) {
      // 树表格组件要求 next 必须是非空数组才会渲染「展开按钮」
      // 所以这里手动添加一个占位节点数组
      // 后续在 onExpand 的时候再加载更多节点 并且替换这个数组
      node[childrenColumnName] = [generateInternalLoadingNode(rowKey)]
    }
  })
}
```

自定义渲染 `Loading Icon` 就很简单了：

```js
// 传入给 Table 组件的 expandIcon 属性即可
export const TreeTableExpandIcon = ({
  expanded,
  expandable,
  onExpand,
  record
}) => {
  if (record[INTERNAL_IS_LOADING]) {
    return <IconLoading style={iconStyle} />
  }
}
```

功能完成，看一下效果：

![远程懒加载](https://images.gitee.com/uploads/images/2021/0301/174811_ef09a28c_1087321.gif 'Kapture 2021-03-01 at 17.47.56.gif')

## 每个层级支持分页

这个功能和上一个功能也有点类似，需要在 `rewriteTree` 的时候根据外部传入的是否开启分页的字段，在符合条件的时候往子节点数组的末尾加入一个**占位 Pagination 节点**。

之后在 `column` 的 `render` 中改写这个节点的渲染逻辑。

改写节点：

```js
function rewriteTree({
  dataSource,
  // 在动态追加子树节点的时候 需要手动传入 parent 引用
  parentNode = null
}) {
  // 在动态追加子树节点的时候 需要手动传入父节点的 level 否则 level 会从 1 开始计算
  const startLevel = parentNode?.[INTERNAL_LEVEL] || 0

  traverseTree(dataSource, childrenColumnName, (node, parent, level) => {
    // ……之前的逻辑省略

    // 分页逻辑
    if (childrenPagination) {
      const { totalKey } = childrenPagination
      const nodeChildren = node[childrenColumnName]
      // 渲染分页器，先加入占位节点
      if (
        node[totalKey] > nodeChildren?.length &&
        // 防止重复添加分页器占位符
        !isInternalPaginationNode(nodeChildren[nodeChildren.length - 1], rowKey)
      ) {
        nodeChildren?.push?.(generateInternalPaginationNode(rowKey))
      }
    }
  })
}
```

改写 `columns`：

```js
function rewriteColumns() {
  /**
   * 根据占位符 渲染分页组件
   */
  const rewritePaginationRender = (column) => {
    column.render = function ColumnRender(text, record) {
      if (
        isInternalPaginationNode(record, rowKey) &&
        dataIndex === indentLineDataIndex
      ) {
        return <Pagination />
      }
      return render?.(text, record) ?? text
    }
  }

  columns.forEach((column) => {
    rewritePaginationRender(column)
  })
}
```

来看一下实现的分页效果：
![分页](https://images.gitee.com/uploads/images/2021/0301/181948_efc006a8_1087321.gif 'Kapture 2021-03-01 at 18.19.38.gif')

## 利用插件机制重构

到这里我们已经可以发现，分页相关的逻辑被分散在 `rewriteTree` 和 `rewriteColumns` 中，而加载更多的逻辑被分散在 `rewriteTree` 和 `onExpand` 中，组件的代码行数也已经来到了 `300` 行。

大概看一下代码的结构，已经是比较混乱了：

```js
export const TreeTable = (rawProps) => {
  function rewriteTree() {
    // 加载更多逻辑
    // 分页逻辑
  }

  function rewriteColumns() {
    // 分页逻辑
  }

  const onExpand = async (expanded, record) => {
    // 加载更多逻辑
  }

  return <Table />
}
```

回忆一下 Vite 等构建工具提供的插件机制，就是对外提供一些时机的钩子，还有一些工具方法，让用户去写一些配置代码，以此介入框架运行的各个时机之中。

那么，我们是否可以考虑把「处理每个节点、`column`、每次 `onExpand`」 的时机暴露出去。

这样让用户也可以介入这些流程，去改写一些属性，调用一些内部方法，以此实现上面的几个功能呢？

我们设计插件机制，想要实现这两个目标：

1. **逻辑解耦**，把每个小功能的代码收缩到插件文件中去，不和组件耦合起来，增加可维护性。
2. **用户共建**，内部使用的话同事方便共建，开源后社区方便共建，当然这要求你编写的插件机制足够完善，文档足够友好。

当然插件也会带来一些缺点，设计一套完善的插件机制也是非常复杂的，像 webpack、rollup、redux 的插件机制都有设计的非常精良的地方可以参考学习。

不过回到本文，我只是实现的一个最简化版的插件系统。

首先，设计一下插件的接口：

```ts
export interface TreeTablePlugin<T = any> {
  (props: ResolvedProps, context: TreeTablePluginContext): {
    /**
     * 可以访问到每一个 column 并修改
     */
    onColumn?(column: ColumnProps<T>): void
    /**
     * 可以访问到每一个节点数据
     * 在初始化或者新增子节点以后都会执行
     */
    onRecord?(record): void
    /**
     * 节点展开的回调函数
     */
    onExpand?(expanded, record): void
  }
}
```

我把插件设计成一个**函数**，这样每次执行都可以拿到最新的 `props` 和 `context`。

`context` 其实就是组件内一些依赖上下文的工具函数等等，比如 `forceUpdate`, `addChildList` 等函数都可以挂在上面。

接下来，由于插件可能有多个，而且内部可能会有一些解析流程，所以我设计一个插件的包装函数 `usePluginContainer`：

```ts
export const usePluginContainer = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { plugins: rawPlugins } = props

  const plugins = rawPlugins.map((plugin) => plugin?.(props, context))

  const container = {
    onColumn(column: ColumnProps<any>) {
      for (const plugin of plugins) {
        plugin?.onColumn?.(column)
      }
    },
    onRecord(record) {
      for (const plugin of plugins) {
        plugin?.onRecord?.(record)
      }
    },
    onExpand(expanded, record) {
      for (const plugin of plugins) {
        plugin?.onExpand?.(expanded, record)
      }
    }
  }

  return container
}
```

目前的流程很简单，只是把每个 `plugin` 函数调用一下，然后提供对外的包装接口。

接着就可以在组件中调用这个工具函数：

```ts
export const TreeTable: React.FC<ITreeTableProps> = (props) => {
  const [_, forceUpdate] = useReducer((x) => x + 1, 0)

  const [expandedRowKeys, setExpandedRowKeys] = useControllableValue<
    TableProps<any>['expandedRowKeys']
  >(props, {
    defaultValue: [],
    valuePropName: 'expandedRowKeys',
    trigger: 'onExpandedRowsChange'
  })

  const pluginContext = {
    forceUpdate,
    addChildList,
    expandedRowKeys,
    setExpandedRowKeys
  }

  // 这里拿到了 pluginContainer
  const pluginContainer = usePluginContainer(props, pluginContext)
}
```

之后，在各个流程的相应位置，都通过这个插件包装来执行相应的函数即可：

```ts
export const TreeTable: React.FC<ITreeTableProps> = props => {
  ...

  // 这里拿到了 pluginContainer
  const pluginContainer = usePluginContainer(props, pluginContext);

  /**
   *  需要对 dataSource 进行一些改写 增加层级、父节点、loading 节点、分页等信息
   */
  function rewriteTree({
    dataSource,
    // 在动态追加子树节点的时候 需要手动传入 parent 引用
    parentNode = null,
  }) {
    pluginContainer.onRecord(parentNode);

    traverseTree(dataSource, childrenColumnName, (node, parent, level) => {
      pluginContainer.onRecord(node);
    });
  }

  function rewriteColumns() {
    columns.forEach(column => {
      pluginContainer.onColumn(column);
    });
  }

  const onExpand = async (expanded, record) => {
    pluginContainer.onExpand(expanded, record);
  };
}
```

之后，我们就可以把之前**分页相关**的逻辑直接抽象成 `pagination-plugin`：

```ts
export const paginationPlugin: TreeTablePlugin = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { forceUpdate, addChildList } = context
  const {
    childrenPagination,
    childrenColumnName,
    rowKey,
    indentLineDataIndex
  } = props

  const handlePagination = (node) => {
    // 先加入渲染分页器占位节点
  }

  const rewritePaginationRender = (column) => {
    // 改写 column 的 render
    // 渲染分页器
  }

  return {
    onRecord: handlePagination,
    onColumn: rewritePaginationRender
  }
}
```

而**懒加载节点**相关的逻辑也可以抽象成 `lazyload-plugin`：

```ts
export const lazyloadPlugin: TreeTablePlugin = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { childrenColumnName, rowKey, hasNextKey, onLoadMore } = props
  const { addChildList, expandedRowKeys, setExpandedRowKeys } = context

  // 处理懒加载占位节点逻辑
  const handleNextLevelLoader = (node) => {}

  const onExpand = async (expanded, record) => {
    if (expanded && record[hasNextKey] && onLoadMore) {
      // 处理懒加载逻辑
    }
  }

  return {
    onRecord: handleNextLevelLoader,
    onExpand: onExpand
  }
}
```

至此，主函数被精简到 `150` 行左右，新功能相关的函数全部被移到插件目录中去了，无论是想要新增或者删减、开关功能都变的非常容易。

此时的目录结构：

![目录结构](https://images.gitee.com/uploads/images/2021/0301/193435_38e8a9ba_1087321.png '屏幕截图.png')

## 总结

本文通过讲述扩展 `Table` 组件的如下功能：

- ✨ 每个层级**缩进指示线**
- ✨ 远程**懒加载**子节点
- ✨ 每个层级支持**分页**

以及开发过程中出现代码的耦合，难以维护问题，进而延伸探索**插件机制**在组件中的设计和使用，虽然本文设计的插件还是最简陋的版本，但是原理大致上如此，希望能够对你有所启发。
