---
title: '用jsx封装Vue中的复杂组件（网易云音乐实战项目需求）'
date: '2019-07-31'
spoiler: ''
---

## 背景介绍
最近在做vue高仿[网易云音乐](https://juejin.im/post/5d3c0765f265da1b60294b78)的项目，在做的过程中发现音乐表格这个组件会被非常多的地方复用，而且需求比较复杂的和灵活。
### [预览地址](http://47.99.213.231:8001/)
### [源码地址](https://github.com/sl1673495/vue-netease-music) 


## 图片预览

* 歌单详情
![歌单详情](https://user-gold-cdn.xitu.io/2019/7/31/16c45d24774d06bf?w=1209&h=481&f=png&s=154844)
* 播放列表
![播放列表](https://user-gold-cdn.xitu.io/2019/7/31/16c45d2920dc1634?w=391&h=358&f=png&s=53326)
* 搜索高亮
![搜索高亮](https://user-gold-cdn.xitu.io/2019/7/31/16c46085f7a4c70c?w=1210&h=363&f=png&s=135056)


## 需求分析

它需要支持：

* hideColumns参数， 自定义需要隐藏哪些列。

* highLightText，传入字符串，数据中命中的字符串高亮。


首先 看一下我们平常的table写法。
```javascript
  <el-table
      :data="tableData"
      style="width: 100%">
      <el-table-column
        prop="index"
        label=" "
        width="180">
      </el-table-column>
      <el-table-column
        prop="name"
        label="音乐标题"
        width="180">
      </el-table-column>
      <el-table-column
        prop="artistsText"
        label="歌手">
      </el-table-column>
    </el-table>
```

这是官网的写法，假设我们传入了 hideColumns: ['index', 'name']，我们需要在模板里隐藏的话```
  ```javascript
    <el-table
      :data="tableData"
      style="width: 100%">
      <el-table-column
    +++ v-if="!hideColumns.includes('index')"
        prop="index"
        label=" "
        width="180">
      </el-table-column>
      <el-table-column
    +++ v-if="!hideColumns.includes('name')"
        prop="name"
        label="音乐标题"
        width="180">
      </el-table-column>
      <el-table-column
    +++ v-if="!hideColumns.includes('address')"
        prop="artistsText"
        label="歌手">
      </el-table-column>
    </el-table>
```

这种代码非常笨，所以我们肯定是接受不了的，我们很自然的联想到平常用v-for循环，能不能套用在这个需求上呢。
首先在data里定义columns

```javascript
data() {
    return {
      columns: [{
        prop: 'index',
        label: '',
        width: '50'
      }, {
        prop: 'artistsText',
        label: '歌手'
      }, {
        prop: 'albumName',
        label: '专辑'
      }, {
        prop: 'durationSecond',
        label: '时长',
        width: '100',
      }]
    }
}
```

然后我们在computed中计算hideColumns做一次合并
```javascript
  computed: {
    showColumns() {
      const { hideColumns } = this
      return this.columns.filter(column => {
        return !this.hideColumns.find((prop) => prop === column.prop)
      })
    },
  },
```

那么模板里我们就可以简写成
```javascript
<el-table
    :data="songs"
  >
    <template v-for="(column, index) in showColumns">
      <el-table-column
        :key="index"
        // 混入属性
        v-bind="column"
      >
      </el-table-column>
    </template>
  </el-table>
```

注意```  v-bind="column" ```这行， 相当于把column中的所有属性混入到table-column中去，是一个非常简便的方法。


## script配合template的解决方案
这样需求看似解决了，很美好。
</br>
但是我们忘了非常重要的一点，`slotScopes`这个东西！

比如音乐时长我们需要format一下，
```javascript
 <el-table-column>
     <template>
        <span>{{ $utils.formatTime(scope.row.durationSecond) }}</span>
     </template>
 </el-table-column>
```
但是我们现在把columns都写到script里了，和template分离开来了，我暂时还不知道有什么方法能把`sciprt`里写的模板放到`template`里用，所以先想到一个可以解决问题的方法。就是在template里加一些判断。

```javascript
<el-table
    v-bind="$attrs"
    v-if="songs.length"
    :data="songs"
    @row-click="onRowClick"
    :cell-class-name="tableCellClassName"
    style="width: 99.9%"
  >
    <template v-for="(column, index) in showColumns">
      <!-- 需要自定义渲染的列 -->
      <el-table-column
        v-if="['durationSecond'].includes(column.prop)"
        :key="index"
        v-bind="column"
      >
          <!-- 时长 -->
          <template v-else-if="column.prop === 'durationSecond'">
            <span>{{ $utils.formatTime(scope.row.durationSecond) }}</span>
          </template>
      </el-table-column>

      <!-- 普通列 -->
      <el-table-column
        v-else
        :key="index"
        v-bind="column"
      >
      </el-table-column>
    </template>
  </el-table>
```

又一次的需求看似解决了，很美好。 

## 高亮文字匹配需求分析
</br>
但是新需求又来了！！根据传入的 highLightText 去高亮某些文字，我们分析一下需求
</br>

`鸡你太美`这个歌名，我们在搜索框输入`鸡你`
我们需要把
```
<span>鸡你太美</span>
```

转化为
```
  <span>
    <span class="high-light">鸡你</span>
    太美
 </span>
```

我们在template里找到音乐标题这行，写下这端代码：
```javascript
<template v-else-if="column.prop === 'name'">
  <span>{{this.genHighlight(scope.row.name)}}</span>
</template>
```

```javascript
methods: {
    genHighlight(text) {
       return <span>xxx</span>
    }
}
```

我发现无从下手了, 因为jsx最终编译成的是return vnode的方法，genHighlight执行以后返回的是vnode，但是你不能直接把vnode放到template里去。

## jsx终极解决方案
所以我们要统一环境，直接使用jsx渲染我们的组件，文档可以参照
</br>
[babel-plugin-transform-vue-jsx](https://github.com/vuejs/babel-plugin-transform-vue-jsx)
<br>
[vuejs/jsx](https://github.com/vuejs/jsx)
```javascript
import ElTable from 'element-ui/lib/table'

data() {
    const commonHighLightSlotScopes = {
      scopedSlots: {
        default: (scope) => {
          return (
            <span>{this.genHighlight(scope.row[scope.column.property])}</span>
          )
        }
      }
    }
    return {
      columns: [{
        prop: 'name',
        label: '音乐标题',
        ...commonHighLightSlotScopes
      }, {
        prop: 'artistsText',
        label: '歌手',
         ...commonHighLightSlotScopes
      }, {
        prop: 'albumName',
        label: '专辑',
        ...commonHighLightSlotScopes
      }, {
        prop: 'durationSecond',
        label: '时长',
        width: '100',
        scopedSlots: {
          default: (scope) => {
            return (
              <span>{this.$utils.formatTime(scope.row.durationSecond)}</span>
            )
          }
        }
      }]
    }
  },
  methods: {
    genHighlight(title = '') {
      ...省去一些细节
      const titleSpan = matchIndex > -1 ? (
        <span>
          {beforeStr}
          <span class="high-light-text">{hitStr}</span>
          {afterStr}
        </span>
      ) : title;
      return titleSpan;
    },
  },
 render() {
    const elTableProps = ElTable.props
    // 从$attrs里提取作为prop的值
    // 这里要注意的点是驼峰命名法(camelCase)和短横线命名法(kebab-case)
    // 都是可以被组件接受的，虽然elTable里的prop定义的属性叫cellClassName
    // 但是我们要把cell-class-name也解析进prop里
    const { props, attrs } = genPropsAndAttrs(this.$attrs, elTableProps)
    
    const tableAttrs = {
      attrs,
      on: {
        ...this.$listeners,
        ['row-click']: this.onRowClick,
      },
      props: {
        ...props,
        cellClassName: this.tableCellClassName,
        data: this.songs,
      },
      style: { width: '99.9%' }
    }
    return this.songs.length ? (
      <el-table
        {...tableAttrs}
      >
        {this.showColumns.map((column, index) => {
          const { scopedSlots, ...columnProps } = column
          return (
            <el-table-column key={index} props={columnProps} scopedSlots={scopedSlots} >
            </el-table-column>
          )
        })}
      </el-table>
    ) : null
  }
```
`attrs: this.$attrs` 注意这句话，我们在template里可以通过
`v-bind="$attrs"`去透传外部传进来的所有属性，  
但是在jsx中我们必须分类清楚传给el-table的`attrs`和`props`  
比如el-table接受`data`这个prop，如果你放在attrs里传进去，那么就失效了。 

这个我暂时也没找到特别好的解决方法，只能先引用去拿elTable上的props去进行比对$attrs，取交集。
```javascript
import ElTable from 'element-ui/lib/table'
// 从$attrs里提取作为prop的值
// 这里要注意的点是驼峰命名法(camelCase)和短横线命名法(kebab-case)
// 都是可以被组件接受的，虽然elTable里的prop定义的属性叫cellClassName
// 但是我们要把cell-class-name也解析进prop里
const { props, attrs } = genPropsAndAttrs(this.$attrs, elTableProps)
```
可以看到代码中模板的部分少了很多重复的判断，维护性和扩展性都更强了，jsx可以说是复杂组件的终极解决方案，但是要真正的封装好一个高阶组件，要做的还非常多。

