---
title: '如何编写神奇的「插件机制」，优化基于 Antd Table 封装表格的混乱代码'
date: '2021-03-02'
spoiler: ''
---

## 前言

最近在一个业务需求中，我通过在 Antd Table 提供的回调函数等机制中编写代码，实现了这些功能：

- ✨ 每个层级**缩进指示线**
- ✨ 远程**懒加载**子节点
- ✨ 每个层级支持**分页**

最后实现的效果大概是这样的：

![最终效果](https://images.gitee.com/uploads/images/2021/0301/181948_efc006a8_1087321.gif 'Kapture 2021-03-01 at 18.19.38.gif')

功能虽然已经实现了，也记录在了 [给 Antd Table 组件编写缩进指引线、子节点懒加载等功能](https://github.com/sl1673495/blogs/issues/77) 这篇文章中。不过我个人感觉意义不大，对功能代码不感兴趣的同学完全可以跳过。

这篇文章我想聊聊我在这个需求中，对**代码解耦**，为组件编写**插件机制**的一些思考。

代码已经发布在 [react-antd-treetable](https://github.com/sl1673495/react-antd-treetable)，欢迎 Star~

## 重构思路

随着编写功能的增多，逻辑被耦合在 Antd Table 的各个回调函数之中，

- **指引线**的逻辑分散在 `rewriteColumns`, `components`中。
- **分页**的逻辑被分散在 `rewriteColumns` 和 `rewriteTree` 中。
- **加载更多**的逻辑被分散在 `rewriteTree` 和 `onExpand` 中

至此，组件的代码行数也已经来到了 `300` 行，大概看一下代码的结构，已经是比较混乱了：

```js
export const TreeTable = rawProps => {
  function rewriteTree() {
    // 🎈加载更多逻辑
    // 🔖 分页逻辑
  }

  function rewriteColumns() {
    // 🔖 分页逻辑
    // 🏁 缩进线逻辑
  }

  const components = {
    // 🏁 缩进线逻辑
  };

  const onExpand = async (expanded, record) => {
    // 🎈 加载更多逻辑
  };

  return <Table />;
};
```

这时候缺点就暴露出来了，当我想要改动或者删减其中一个功能的时候变得异常痛苦，经常在各个函数之间跳转查找。

有没有一种机制，可以让代码**按照功能点聚合**，而不是散落在各个函数中？

```js
// 🔖 分页逻辑
const usePaginationPlugin = () => {};
// 🎈 加载更多逻辑
const useLazyloadPlugin = () => {};
// 🏁 缩进线逻辑
const useIndentLinePlugin = () => {};

export const TreeTable = rawProps => {
  usePaginationPlugin();

  useLazyloadPlugin();

  useIndentLinePlugin();

  return <Table />;
};
```

没错，就是很像 `VueCompositionAPI` 和 `React Hook` 在逻辑解耦方面所做的改进，但是在这个回调函数的写法形态下，好像不太容易做到？

这时候，我回想到社区中一些开源框架提供的**插件机制**，好像就可以在**不深入源码**的情况下注入各个**回调时机**的用户逻辑。

比如 [Vite 的插件](https://cn.vitejs.dev/guide/api-plugin.html)、[Webpack 的插件](https://webpack.docschina.org/concepts/plugins/) 甚至大家很熟悉的 [Vue.use()](https://cn.vuejs.org/v2/api/#Vue-use)，它们本质上就是对外暴露出一些内部的时机和属性，让用户去写一些代码来介入框架运行的各个时机之中。

那么，我们是否可以考虑把「处理每个节点、`column`、每次 `onExpand`」 的时机暴露出去，这样让用户也可以**介入这些流程**，去改写一些属性，调用一些内部方法，以此实现上面的几个功能呢？

我们设计插件机制，想要实现这两个目标：

1. **逻辑解耦**，把每个小功能的代码**整合**到插件文件中去，不和组件耦合起来，增加可维护性。
2. **用户共建**，内部使用的话方便**同事**共建，开源后方便**社区**共建，当然这要求你编写的插件机制足够完善，文档足够友好。

不过插件也会带来一些缺点，设计一套完善的插件机制也是非常复杂的，像 Webpack、Rollup、Redux 的插件机制都有设计的非常精良的地方可以参考学习。

接下来，我会试着实现的一个**最简化版**的插件系统。

## 源码

首先，设计一下插件的接口：

```ts
export interface TreeTablePlugin<T = any> {
  (props: ResolvedProps, context: TreeTablePluginContext): {
    /**
     * 可以访问到每一个 column 并修改
     */
    onColumn?(column: ColumnProps<T>): void;
    /**
     * 可以访问到每一个节点数据
     * 在初始化或者新增子节点以后都会执行
     */
    onRecord?(record): void;
    /**
     * 节点展开的回调函数
     */
    onExpand?(expanded, record): void;
    /**
     * 自定义 Table 组件
     */
    components?: TableProps<T>['components'];
  };
}

export interface TreeTablePluginContext {
  forceUpdate: React.DispatchWithoutAction;
  replaceChildList(record, childList): void;
  expandedRowKeys: TableProps<any>['expandedRowKeys'];
  setExpandedRowKeys: (v: string[] | number[] | undefined) => void;
}
```

我把插件设计成一个**函数**，这样每次执行都可以拿到最新的 `props` 和 `context`。

`context` 其实就是组件内一些依赖上下文的工具函数等等，比如 `forceUpdate`, `replaceChildList` 等函数都可以挂在上面。

接下来，由于插件可能有多个，而且内部可能会有一些解析流程，所以我设计一个运行插件的 hook 函数 `usePluginContainer`：

```ts
export const usePluginContainer = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { plugins: rawPlugins } = props;

  const plugins = rawPlugins.map(usePlugin => usePlugin?.(props, context));

  const container = {
    onColumn(column: ColumnProps<any>) {
      for (const plugin of plugins) {
        plugin?.onColumn?.(column);
      }
    },
    onRecord(record, parentRecord, level) {
      for (const plugin of plugins) {
        plugin?.onRecord?.(record, parentRecord, level);
      }
    },
    onExpand(expanded, record) {
      for (const plugin of plugins) {
        plugin?.onExpand?.(expanded, record);
      }
    },
    /**
     * 暂时只做 components 的 deepmerge
     * 不处理自定义组件的冲突 后定义的 Cell 会覆盖前者
     */
    mergeComponents() {
      let components: TableProps<any>['components'] = props.components || {};
      for (const plugin of plugins) {
        components = deepmerge.all([components, plugin.components || {}]);
      }
      return components;
    },
  };

  return container;
};
```

目前的流程很简单，只是把每个 `plugin` 函数调用一下，然后提供对外的包装接口。`mergeComponent` 使用[deepmerge](https://github.com/TehShrike/deepmerge) 这个库来合并用户传入的 `components` 和 插件中的 `components`，暂时不做冲突处理。

接着就可以在组件中调用这个函数，生成 `pluginContainer`：

```ts
export const TreeTable =  React.forwardRef((props， ref) => {
  const [_, forceUpdate] = useReducer((x) => x + 1, 0)

  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([])

  const pluginContext = {
    forceUpdate,
    replaceChildList,
    expandedRowKeys,
    setExpandedRowKeys
  }

  // 对外暴露工具方法给用户使用
  useImperativeHandle(ref, () => ({
    replaceChildList,
    setNodeLoading,
  }));

  // 这里拿到了 pluginContainer
  const pluginContainer = usePluginContainer(
    {
      ...props,
      plugins: [
        ...props.plugins,
        usePaginationPlugin,
        useLazyloadPlugin,
        useIndentLinePlugin,
      ],
    },
    pluginContext
  );
})
```

之后，在各个流程的相应位置，都通过 `pluginContainer` 执行相应的钩子函数即可：

```ts
export const TreeTable = React.forwardRef((props, ref) => {
  // 省略上一部分代码……

  // 这里拿到了 pluginContainer
  const pluginContainer = usePluginContainer(
    {
      ...props,
      plugins: [
        ...props.plugins,
        usePaginationPlugin,
        useLazyloadPlugin,
        useIndentLinePlugin,
      ],
    },
    pluginContext
  );

  // 递归遍历整个数据 调用钩子
  const rewriteTree = ({
    dataSource,
    // 在动态追加子树节点的时候 需要手动传入 parent 引用
    parentNode = null,
  }) => {
    pluginContainer.onRecord(parentNode);

    traverseTree(dataSource, childrenColumnName, (node, parent, level) => {
      // 这里执行插件的 onRecord 钩子
      pluginContainer.onRecord(node, parent, level);
    });
  }

  const rewrittenColumns = columns.map(rawColumn => {
    //  这里把浅拷贝过后的 column 暴露出去
    //  防止污染原始值
    const column = Object.assign({}, rawColumn);
    pluginContainer.onColumn(column);
    return column;
  });

  const onExpand = async (expanded, record) => {
    // 这里执行插件的 onExpand 钩子
    pluginContainer.onExpand(expanded, record);
  };

  // 这里获取合并后的 components 传递给 Table
  const components = pluginContainer.mergeComponents()
});
```

之后，我们就可以把之前**分页相关**的逻辑直接抽象成 `usePaginationPlugin`：

```ts
export const usePaginationPlugin: TreeTablePlugin = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { forceUpdate, replaceChildList } = context;
  const {
    childrenPagination,
    childrenColumnName,
    rowKey,
    indentLineDataIndex,
  } = props;

  const handlePagination = node => {
    // 先加入渲染分页器占位节点
  };

  const rewritePaginationRender = column => {
    // 改写 column 的 render
    // 渲染分页器
  };

  return {
    onRecord: handlePagination,
    onColumn: rewritePaginationRender,
  };
};
```

也许机智的你已经发现，这里的插件是以 `use` 开头的，这是**自定义 hook**的标志。

没错，它既是一个插件，同时也是一个 **自定义 Hook**。所以你可以使用 **React Hook 的一切能力**，同时也可以在插件中引入各种社区的第三方 Hook 来加强能力。

这是因为我们是在 `usePluginContainer` 中通过函数调用执行各个 `usePlugin`，完全符合 React Hook 的调用规则。

而**懒加载节点**相关的逻辑也可以抽象成 `useLazyloadPlugin`：

```ts
export const useLazyloadPlugin: TreeTablePlugin = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { childrenColumnName, rowKey, hasNextKey, onLoadMore } = props;
  const { replaceChildList, expandedRowKeys, setExpandedRowKeys } = context;

  // 处理懒加载占位节点逻辑
  const handleNextLevelLoader = node => {};

  const onExpand = async (expanded, record) => {
    if (expanded && record[hasNextKey] && onLoadMore) {
      // 处理懒加载逻辑
    }
  };

  return {
    onRecord: handleNextLevelLoader,
    onExpand: onExpand,
  };
};
```

而缩进线相关的逻辑则抽取成 `useIndentLinePlugin`：

```ts
export const useIndentLinePlugin: TreeTablePlugin = (
  props: ResolvedProps,
  context: TreeTablePluginContext
) => {
  const { expandedRowKeys } = context;
  const onColumn = column => {
    column.onCell = record => {
      return {
        record,
        ...column,
      };
    };
  };

  const components = {
    body: {
      cell: cellProps => (
        <IndentCell
          {...props}
          {...cellProps}
          expandedRowKeys={expandedRowKeys}
        />
      ),
    },
  };

  return {
    components,
    onColumn,
  };
};
```

至此，主函数被精简到 `150` 行左右，新功能相关的函数全部被移到插件目录中去了，无论是想要新增或者删减、开关功能都变的非常容易。

此时的目录结构：

![目录结构](https://images.gitee.com/uploads/images/2021/0302/202947_5e9f5a4f_1087321.png '屏幕截图.png')

## 总结

本系列通过讲述扩展 `Table` 组件的如下功能：

- ✨ 每个层级**缩进指示线**
- ✨ 远程**懒加载**子节点
- ✨ 每个层级支持**分页** 

以及开发过程中出现代码的耦合，难以维护问题，进而延伸探索**插件机制**在组件中的设计和使用，虽然本文设计的插件还是最简陋的版本，但是原理大致上如此，希望能够对你有所启发。

代码已经发布在 [react-antd-treetable](https://github.com/sl1673495/react-antd-treetable)，欢迎 Star~

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![image](https://user-images.githubusercontent.com/23615778/108619258-76929d80-745e-11eb-90bf-023abec85d80.png)
