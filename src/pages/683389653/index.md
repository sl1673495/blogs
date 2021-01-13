---
title: 'Vue3 + TypeScript 实现递归菜单组件'
date: '2020-08-21'
spoiler: ''
---

## 前言

小伙伴们好久不见，最近刚入职新公司，需求排的很满，平常是实在没时间写文章了，更新频率会变得比较慢。

周末在家闲着无聊，突然小弟过来紧急求助，说是面试的时候，对方给了个 Vue 的递归菜单要求实现，回来找我复盘。

正好这周是小周，没想着出去玩，就在家写写代码吧，我看了一下需求，确实是比较复杂，需要利用好递归组件，正好趁着这个机会总结一篇 Vue3 + TS 实现递归组件的文章。

## 需求

可以先在 [Github Pages](https://sl1673495.github.io/vue-nested-menu/) 中预览一下效果。

需求是这样的，后端会返回一串可能有无限层级的菜单，格式如下：

```js
[
  {
    id: 1,
    father_id: 0,
    status: 1,
    name: '生命科学竞赛',
    _child: [
      {
        id: 2,
        father_id: 1,
        status: 1,
        name: '野外实习类',
        _child: [{ id: 3, father_id: 2, status: 1, name: '植物学' }],
      },
      {
        id: 7,
        father_id: 1,
        status: 1,
        name: '科学研究类',
        _child: [
          { id: 8, father_id: 7, status: 1, name: '植物学与植物生理学' },
          { id: 9, father_id: 7, status: 1, name: '动物学与动物生理学' },
          { id: 10, father_id: 7, status: 1, name: '微生物学' },
          { id: 11, father_id: 7, status: 1, name: '生态学' },
        ],
      },
      { id: 71, father_id: 1, status: 1, name: '添加' },
    ],
  },
  {
    id: 56,
    father_id: 0,
    status: 1,
    name: '考研相关',
    _child: [
      { id: 57, father_id: 56, status: 1, name: '政治' },
      { id: 58, father_id: 56, status: 1, name: '外国语' },
    ],
  },
]
```

1. 每一层的菜单元素如果有 `_child` 属性，**这一项菜单被选中**以后就要继续展示这一项的所有子菜单，预览一下动图：

![Kapture 2020-08-21 at 18 49 46](https://user-images.githubusercontent.com/23615778/90882867-4438b280-e3df-11ea-8f65-196e81f6c98d.gif)

2. 并且点击其中的任意一个层级，都需要把菜单的 **完整的 `id` 链路** 传递到最外层，给父组件请求数据用。比如点击了 `科学研究类`。那么向外 `emit` 的时候还需要带上它的第一个子菜单 `植物学与植物生理学` 的 `id`，以及它的父级菜单 `生命科学竞赛` 的 id，也就是 `[1, 7, 8]`。

3. 每一层的样式还可以自己定制。

## 实现

这很显然是一个递归组件的需求，在设计递归组件的时候，我们要先想清楚数据到视图的映射。

在后端返回的数据中，数组的每一层可以分别对应一个菜单项，那么数组的层则就对应视图中的一行，当前这层的菜单中，**被点击选中** 的那一项菜单的 `child` 就会被作为子菜单数据，交给递归的 `NestMenu` 组件，直到某一层的高亮菜单不再有 `child`，则递归终止。

![image](https://user-images.githubusercontent.com/23615778/90954698-2d5e9280-e4a9-11ea-90ba-73093daea276.png)

由于需求要求每一层的样式可能是不同的，所以再每次调用递归组件的时候，我们都需要从父组件的 `props` 中拿到一个 `depth` 代表层级，并且把这个 `depth + 1` 继续传递给递归的 `NestMenu` 组件。

重点主要就是这些，接下来编码实现。

先看 `NestMenu` 组件的 `template` 部分的大致结构：

```xml
<template>
  <div class="wrap">
    <div class="menu-wrap">
      <div
        class="menu-item"
        v-for="menuItem in data"
      >{{menuItem.name}}</div>
    </div>
    <nest-menu
      :key="activeId"
      :data="subMenu"
      :depth="depth + 1"
    ></nest-menu>
  </div>
</template>
```

和我们预想设计中的一样， `menu-wrap` 代表当前菜单层， `nest-menu` 则就是组件本身，它负责递归的渲染子组件。

### 首次渲染

在第一次获取到整个菜单的数据的时候，我们需要先把每层菜单的选中项默认设置为第一个子菜单，由于它很可能是异步获取的，所以我们最好是 `watch` 这个数据来做这个操作。

```js
// 菜单数据源发生变化的时候 默认选中当前层级的第一项
const activeId =  ref<number | null>(null)

watch(
  () => props.data,
  (newData) => {
    if (!activeId.value) {
      if (newData && newData.length) {
        activeId.value = newData[0].id
      }
    }
  },
  {
    immediate: true,
  }
)
```

现在我们从最上层开始讲起，第一层的 `activeId` 被设置成了 `生命科学竞赛` 的 id，注意我们传递给递归子组件的 `data` ，也就是 `生命科学竞赛` 的 `child`，是通过 `subMenu` 获取到的，它是一个计算属性：

```js
const getActiveSubMenu = () => {
  return data.find(({ id }) => id === activeId.value)._child
}
const subMenu = computed(getActiveSubMenu)
```

这样，就拿到了 `生命科学竞赛` 的 `child`，作为子组件的数据传递下去了。

### 点击菜单项

回到之前的需求设计，在点击了菜单项后，无论点击的是哪层，都需要把完整的 `id` 链路通过 `emit` 传递到最外层去，所以这里我们需要多做一些处理：

```js
/**
 * 递归收集子菜单第一项的 id
 */
const getSubIds = (child) => {
  const subIds = []
  const traverse = (data) => {
    if (data && data.length) {
      const first = data[0]
      subIds.push(first.id)
      traverse(first._child)
    }
  }
  traverse(child)
  return subIds
}

const onMenuItemClick = (menuItem) => {
  const newActiveId = menuItem.id
  if (newActiveId !== activeId.value) {
    activeId.value = newActiveId
    const child = getActiveSubMenu()
    const subIds = getSubIds(child)
    // 把子菜单的默认第一项 ids 也拼接起来 向父组件 emit
    context.emit('change', [newActiveId, ...subIds])
  }
}
```

由于我们之前定的规则是，点击了新的菜单以后默认选中子菜单的第一项，所以这里我们也递归去找子菜单数据里的第一项，放到 `subIds` 中，直到最底层。

注意这里的 `context.emit("change", [newId, ...subIds]);`，这里是把事件向上 `emit`，如果这个菜单是中间层级的菜单，那么它的父组件也是 `NestMenu`，我们需要在父层级递归调用 `NestMenu` 组件的时候监听这个 `change` 事件。

```xml
<nest-menu
    :key="activeId"
    v-if="activeId !== null"
    :data="getActiveSubMenu()"
    :depth="depth + 1"
    @change="onSubActiveIdChange"
></nest-menu>
```

在父层级的菜单接受到了子层级的菜单的 `change` 事件后，需要怎么做呢？没错，需要进一步的再向上传递：

```js
const onSubActiveIdChange = (ids) => {
  context.emit('change', [activeId.value].concat(ids))
}
```

这里就只需要简单的把自己当前的 `activeId` 拼接到数组的最前面，再继续向上传递即可。

这样，任意一层的组件点击了菜单后，都会先用自己的 `activeId` 拼接好所有子层级的默认 `activeId`，再一层层向上 `emit`。并且向上的每一层父菜单都会把自己的 `activeId` 拼在前面，就像接力一样。

最后，我们在应用层级的组件里，就可以轻松的拿到完整的 `id` 链路：

```xml
<template>
  <nest-menu :data="menu" @change="activeIdsChange" />
</template>

export default {
  methods: {
    activeIdsChange(ids) {
      this.ids = ids;
      console.log("当前选中的id路径", ids);
  },
},
```

### 样式区分

由于我们每次调用递归组件的时候，都会把 `depth + 1`，那么就可以通过把这个数字拼接到类名后面来实现样式区分了。

```xml
<template>
  <div class="wrap">
    <div class="menu-wrap" :class="`menu-wrap-${depth}`">
      <div class="menu-item">{{menuItem.name}}</div>
    </div>
    <nest-menu />
  </div>
</template>

<style>
.menu-wrap-0 {
  background: #ffccc7;
}

.menu-wrap-1 {
  background: #fff7e6;
}

.menu-wrap-2 {
  background: #fcffe6;
}
</style>
```

### 默认高亮

上面的代码写完后，应对没有默认值时的需求已经足够了，这时候面试官说，产品要求这个组件能通过传入任意一个层级的 `id` 来默认展示高亮。

其实这也难不倒我们，稍微改造一下代码，在父组件里假设我们通过 url 参数或者任意方式拿到了一个 `activeId`，先通过深度优先遍历的方式查找到这个 `id` 的所有父级。

```js
const activeId = 7

const findPath = (menus, targetId) => {
  let ids

  const traverse = (subMenus, prev) => {
    if (ids) {
      return
    }
    if (!subMenus) {
      return
    }
    subMenus.forEach((subMenu) => {
      if (subMenu.id === activeId) {
        ids = [...prev, activeId]
        return
      }
      traverse(subMenu._child, [...prev, subMenu.id])
    })
  }

  traverse(menus, [])

  return ids
}

const ids = findPath(data, activeId)
```

这里我选择在递归的时候带上上一层的 `id`，在找到了目标 `id` 以后就能轻松的拼接处完整的父子 id 数组。

然后我们把构造好的 `ids` 作为 `activeIds` 传递给 `NestMenu`，此时这时候 `NestMenu` 就要改变一下设计，成为一个「受控组件」，它的渲染状态是受我们外层传递的数据控制的。

所以我们需要在初始化参数的时候改变一下取值逻辑，优先取 `activeIds[depth]` ，并且在点击菜单项的时候，要在最外层的页面组件中，接收到 `change` 事件时，把 `activeIds` 的数据同步改变。这样继续传递下去才不会导致 `NestMenu` 接收到的数据混乱。

```xml
<template>
  <nest-menu :data="data" :defaultActiveIds="ids" @change="activeIdsChange" />
</template>
```

`NestMenu` 初始化的时候，对有默认值的情况做一下处理，优先使用数组中取到的 `id` 值。

```js
setup(props: IProps, context) {
  const { depth = 0, activeIds } = props;

  /**
   * 这里 activeIds 也可能是异步获取到的 所以用 watch 保证初始化
   */
  const activeId = ref<number | null | undefined>(null);
  watch(
    () => activeIds,
    (newActiveIds) => {
      if (newActiveIds) {
        const newActiveId = newActiveIds[depth];
        if (newActiveId) {
          activeId.value = newActiveId;
        }
      }
    },
    {
      immediate: true,
    }
  );
}
```

这样，如果 `activeIds` 数组中取不到的话，默认还是 `null`，在 `watch` 到菜单数据变化的逻辑中，如果 `activeId` 是 `null` 的话，会被初始化为第一个子菜单的 `id`。

```js
watch(
  () => props.data,
  (newData) => {
    if (!activeId.value) {
      if (newData && newData.length) {
        activeId.value = newData[0].id
      }
    }
  },
  {
    immediate: true,
  }
)
```

在最外层页面容器监听到 `change` 事件的时候，要把数据源同步一下：

```js
<template>
  <nest-menu :data="data" :activeIds="ids" @change="activeIdsChange" />
</template>

<script>
import { ref } from "vue";

export default {
  name: "App",
  setup() {
    const activeIdsChange = (newIds) => {
      ids.value = newIds;
    };

    return {
      ids,
      activeIdsChange,
    };
  },
};
</script>
```

如此一来，外部传入 `activeIds` 的时候，就可以控制整个 `NestMenu` 的高亮选中逻辑了。

### 数据源变动引发的 bug。

这时候，面试官对着你的 App 文件稍作改动，然后演示了这样一个 bug：

App.vue 的 `setup` 函数中加了这样的一段逻辑：

```js
onMounted(() => {
  setTimeout(() => {
    menu.value = [data[0]].slice()
  }, 1000)
})
```

也就是说，组件渲染完成后过了一秒，菜单的最外层只剩下一项了，这时候面试官在一秒之内点击了最外层的第二项，这个组件在数据源改变之后，会报错：

![Kapture 2020-08-23 at 18 30 44](https://user-images.githubusercontent.com/23615778/90976345-cacfca00-e56e-11ea-805d-443bc66af362.gif)

这是因为数据源已经改变了，但是组件内部的 `activeId` 状态依然停留在了一个已经不存在了的 `id` 上。

这会导致 `subMenu` 这个 `computed` 属性在计算时出错。

我们对 `watch data` 观测数据源的这段逻辑稍加改动：

```js
watch(
  () => props.data,
  (newData) => {
    if (!activeId.value) {
      if (newData && newData.length) {
        activeId.value = newData[0].id
      }
    }
    // 如果当前层级的 data 中遍历无法找到 `activeId` 的值 说明这个值失效了
    // 把它调整成数据源中第一个子菜单项的 id
    if (!props.data.find(({ id }) => id === activeId.value)) {
      activeId.value = props.data?.[0].id
    }
  },
  {
    immediate: true,
    // 在观测到数据变动之后 同步执行 这样会防止渲染发生错乱
    flush: 'sync',
  }
)
```

![Kapture 2020-08-23 at 18 34 35](https://user-images.githubusercontent.com/23615778/90976400-521d3d80-e56f-11ea-9e03-379c3ba3b994.gif)

注意这里的 `flush: "sync"` 很关键，Vue3 对于 `watch` 到数据源变动之后触发 `callback` 这一行为，默认是以 `post` 也就是渲染之后再执行的，但是在当前的需求下，如果我们用错误的 `activeId` 去渲染，就会直接导致报错了，所以我们需要手动把这个 `watch` 变成一个同步行为。

这下再也不用担心数据源变动导致渲染错乱了。

## 完整代码

### App.vue
```js
<template>
  <nest-menu :data="data" :activeIds="ids" @change="activeIdsChange" />
</template>

<script>
import { ref } from "vue";
import NestMenu from "./components/NestMenu.vue";
import data from "./menu.js";
import { getSubIds } from "./util";

export default {
  name: "App",
  setup() {
    // 假设默认选中 id 为 7
    const activeId = 7;

    const findPath = (menus, targetId) => {
      let ids;

      const traverse = (subMenus, prev) => {
        if (ids) {
          return;
        }
        if (!subMenus) {
          return;
        }
        subMenus.forEach((subMenu) => {
          if (subMenu.id === activeId) {
            ids = [...prev, activeId];
            return;
          }
          traverse(subMenu._child, [...prev, subMenu.id]);
        });
      };

      traverse(menus, []);

      return ids;
    };

    const ids = ref(findPath(data, activeId));

    const activeIdsChange = (newIds) => {
      ids.value = newIds;
      console.log("当前选中的id路径", newIds);
    };

    return {
      ids,
      activeIdsChange,
      data,
    };
  },
  components: {
    NestMenu,
  },
};
</script>
```

### NestMenu.vue

```js
<template>
  <div class="wrap">
    <div class="menu-wrap" :class="`menu-wrap-${depth}`">
      <div
        class="menu-item"
        v-for="menuItem in data"
        :class="getActiveClass(menuItem.id)"
        @click="onMenuItemClick(menuItem)"
        :key="menuItem.id"
      >{{menuItem.name}}</div>
    </div>
    <nest-menu
      :key="activeId"
      v-if="subMenu && subMenu.length"
      :data="subMenu"
      :depth="depth + 1"
      :activeIds="activeIds"
      @change="onSubActiveIdChange"
    ></nest-menu>
  </div>
</template>

<script lang="ts">
import { watch, ref, onMounted, computed } from "vue";
import data from "../menu";

interface IProps {
  data: typeof data;
  depth: number;
  activeIds?: number[];
}

export default {
  name: "NestMenu",
  props: ["data", "depth", "activeIds"],
  setup(props: IProps, context) {
    const { depth = 0, activeIds, data } = props;

    /**
     * 这里 activeIds 也可能是异步获取到的 所以用 watch 保证初始化
     */
    const activeId = ref<number | null | undefined>(null);
    watch(
      () => activeIds,
      (newActiveIds) => {
        if (newActiveIds) {
          const newActiveId = newActiveIds[depth];
          if (newActiveId) {
            activeId.value = newActiveId;
          }
        }
      },
      {
        immediate: true,
        flush: 'sync'
      }
    );

    /**
     * 菜单数据源发生变化的时候 默认选中当前层级的第一项
     */
    watch(
      () => props.data,
      (newData) => {
        if (!activeId.value) {
          if (newData && newData.length) {
            activeId.value = newData[0].id;
          }
        }
        // 如果当前层级的 data 中遍历无法找到 `activeId` 的值 说明这个值失效了
        // 把它调整成数据源中第一个子菜单项的 id
        if (!props.data.find(({ id }) => id === activeId.value)) {
          activeId.value = props.data?.[0].id;
        }
      },
      {
        immediate: true,
        // 在观测到数据变动之后 同步执行 这样会防止渲染发生错乱
        flush: "sync",
      }
    );

    const onMenuItemClick = (menuItem) => {
      const newActiveId = menuItem.id;
      if (newActiveId !== activeId.value) {
        activeId.value = newActiveId;
        const child = getActiveSubMenu();
        const subIds = getSubIds(child);
        // 把子菜单的默认第一项 ids 也拼接起来 向父组件 emit
        context.emit("change", [newActiveId, ...subIds]);
      }
    };
    /**
     * 接受到子组件更新 activeId 的同时
     * 需要作为一个中介告知父组件 activeId 更新了
     */
    const onSubActiveIdChange = (ids) => {
      context.emit("change", [activeId.value].concat(ids));
    };
    const getActiveSubMenu = () => {
      return props.data?.find(({ id }) => id === activeId.value)._child;
    };
    const subMenu = computed(getActiveSubMenu);

    /**
     * 样式相关
     */
    const getActiveClass = (id) => {
      if (id === activeId.value) {
        return "menu-active";
      }
      return "";
    };

    /**
     * 递归收集子菜单第一项的 id
     */
    const getSubIds = (child) => {
      const subIds = [];
      const traverse = (data) => {
        if (data && data.length) {
          const first = data[0];
          subIds.push(first.id);
          traverse(first._child);
        }
      };
      traverse(child);
      return subIds;
    };

    return {
      depth,
      activeId,
      subMenu,
      onMenuItemClick,
      onSubActiveIdChange,
      getActiveClass,
    };
  },
};
</script>

<style>
.wrap {
  padding: 12px 0;
}

.menu-wrap {
  display: flex;
  flex-wrap: wrap;
}

.menu-wrap-0 {
  background: #ffccc7;
}

.menu-wrap-1 {
  background: #fff7e6;
}

.menu-wrap-2 {
  background: #fcffe6;
}

.menu-item {
  margin-left: 16px;
  cursor: pointer;
  white-space: nowrap;
}

.menu-active {
  color: #f5222d;
}
</style>
```

## 源码地址

https://github.com/sl1673495/vue-nested-menu

## 总结

一个递归的菜单组件，说简单也简单，说难也有它的难点。如果我们不理解 Vue 的异步渲染和观察策略，可能中间的 bug 就会困扰我们许久。所以适当学习原理还是挺有必要的。

在开发通用组件的时候，一定要注意数据源的传入时机（同步、异步），对于异步传入的数据，要利用好 `watch` 这个 API 去观测变动，做相应的操作。并且要考虑数据源的变化是否会和组件内原来保存的状态冲突，在适当的时机要做好清理操作。

另外留下一个小问题，我在 `NestMenu` 组件 `watch` 数据源的时候，选择这样去做：

```js
watch((() => props.data);
```

而不是解构后再去观测：

```js
const { data } = props;
watch(() => data);
```

这两者之间有区别吗？这又是一道考察深度的面试题。

开发优秀组件的路还是很漫长的，欢迎各位也在评论区留下你的看法~

## 招聘

字节跳动内推啦，Client Infrastructure是字节跳动终端基础架构团队，面向字节跳动全业务线的移动端、Web、Desktop等终端业务的基础架构部门，为公司业务的高效迭代、质量保证、研发效率和体验提供平台、工具、框架和专项技术能力支撑。
研发领域包括但不限于APP框架和基础组件、研发体系、自动化测试、APM、跨平台框架、端智能解决方案、Web开发引擎、Node.js基建以及下一代移动开发技术的预研等，目前在北上广深杭五地均设有研发中心。

上海的同学点这里一键投递，来我们部门和我做同事吧~ 

https://job.toutiao.com/s/JhRtmQv

其他地区（北上广深杭）也可以自己搜索你想要的业务线和工作地点，通过我的下方内推链接直接投递即可。

https://job.toutiao.com/s/JhRDWep

校招的同学看这里：

投递链接: https://job.toutiao.com/s/JhRV7nC