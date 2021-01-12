---
title: 'React Hook + TypeScript 深入浅出实现一个购物车（陷阱、性能优化、自定义hook）'
date: '2020-03-19'
spoiler: ''
---

## 前言
本文由一个基础的购物车需求展开，一步一步带你深入理解React Hook中的坑和优化

通过本篇文章你可以学到：  

✨React Hook + TypeScript编写`业务组件`的实践

✨如何利用React.memo`优化性能`

✨如何避免Hook带来的`闭包陷阱  `

✨如何抽象出简单好用的`自定义hook`

## 预览地址
https://sl1673495.github.io/react-cart

## 代码仓库
本文涉及到的代码已经整理到github仓库中，用cra搭建了一个示例工程，关于性能优化的部分可以打开控制台查看重渲染的情况。  

https://github.com/sl1673495/react-cart

## 需求分解
作为一个购物车需求，那么它必然涉及到几个需求点：
1. 勾选、全选与反选。
2. 根据选中项计算总价。

![gif1](https://user-gold-cdn.xitu.io/2020/3/3/1709e44da6578aa9?w=794&h=1036&f=gif&s=63288)

## 需求实现

### 获取数据
首先我们请求到购物车数据，这里并不是本文的重点，可以通过自定义请求hook实现，也可以通过普通的useState + useEffect实现。

```js
const getCart = () => {
  return axios('/api/cart')
}
const { 
  // 购物车数据
  cartData,
  // 重新请求数据的方法
  refresh 
} = useRequest<CartResponse>(getCart)
```

### 勾选逻辑实现
我们考虑用一个对象作为映射表，通过`checkedMap`这个变量来记录所有被勾选的商品id：
```js
type CheckedMap = {
  [id: number]: boolean
}
// 商品勾选
const [checkedMap, setCheckedMap] = useState<CheckedMap>({})
const onCheckedChange: OnCheckedChange = (cartItem, checked) => {
  const { id } = cartItem
  const newCheckedMap = Object.assign({}, checkedMap, {
    [id]: checked,
  })
  setCheckedMap(newCheckedMap)
}
```

### 计算勾选总价
再用reduce来实现一个计算价格总和的函数
```js
  // cartItems的积分总和
 const sumPrice = (cartItems: CartItem[]) => {
    return cartItems.reduce((sum, cur) => sum + cur.price, 0)
 }
```

那么此时就需要一个过滤出所有选中商品的函数
```js
// 返回已选中的所有cartItems
const filterChecked = () => {
  return (
    Object.entries(checkedMap)
      // 通过这个filter 筛选出所有checked状态为true的项
      .filter(entries => Boolean(entries[1]))
      // 再从cartData中根据id来map出选中列表
      .map(([checkedId]) => cartData.find(({ id }) => id === Number(checkedId)))
  )
}
```

最后把这俩函数一组合，价格就出来了：
```js
  // 计算礼享积分
  const calcPrice = () => {
    return sumPrice(filterChecked())
  }
```

有人可能疑惑，为什么一个简单的逻辑要抽出这么几个函数，这里我要解释一下，为了保证文章的易读性，我把真实需求做了简化。  

在真实需求中，可能会对不同类型的商品分别做总价计算，因此`filterChecked`这个函数就不可或缺了，filterChecked可以传入一个额外的过滤参数，去返回勾选中的商品的`子集`，这里就不再赘述。

### 全选反选逻辑
有了`filterChecked`函数以后，我们也可以轻松的计算出派生状态`checkedAll`，是否全选：
```js
// 全选
const checkedAll = cartData.length !== 0 && filterChecked().length === cartData.length
```
写出全选和反全选的函数：
```js
const onCheckedAllChange = newCheckedAll => {
  // 构造新的勾选map
  let newCheckedMap: CheckedMap = {}
  // 全选
  if (newCheckedAll) {
    cartData.forEach(cartItem => {
      newCheckedMap[cartItem.id] = true
    })
  }
  // 取消全选的话 直接把map赋值为空对象
  setCheckedMap(newCheckedMap)
}
```

如果是
- `全选` 就把`checkedMap`的每一个商品id都赋值为true。
- `反选` 就把`checkedMap`赋值为空对象。  

### 渲染商品子组件
```js
{cartData.map(cartItem => {
  const { id } = cartItem
  const checked = checkedMap[id]
  return (
      <ItemCard
        key={id}
        cartItem={cartItem}
        checked={checked}
        onCheckedChange={onCheckedChange}
      />
  )
})}
```

可以看出，是否勾选的逻辑就这样轻松的传给了子组件。  

## React.memo性能优化
到了这一步，基本的购物车需求已经实现了。

但是现在我们有了新的问题。

这是React的一个缺陷，默认情况下几乎没有任何性能优化。  

我们来看一下动图演示：

![gif2](https://user-gold-cdn.xitu.io/2020/3/3/1709e458494cf448?w=1644&h=1048&f=gif&s=138141)

购物车此时有5个商品，看控制台的打印，每次都是以5为倍数增长每点击一次checkbox，都会触发所有子组件的重新渲染。

如果我们有50个商品在购物车中，我们改了其中某一项的`checked`状态，也会导致50个子组件重新渲染。  

我们想到了一个api： `React.memo`，这个api基本等效于class组件中的`shouldComponentUpdate`，如果我们用这个api让子组件只有在checked发生改变的时候再重新渲染呢？  

好，我们进入子组件的编写：
```js
// memo优化策略
function areEqual(prevProps: Props, nextProps: Props) {
  return (
    prevProps.checked === nextProps.checked
  )
}

const ItemCard: FC<Props> = React.memo(props => {
  const { checked, onCheckedChange } = props
  return (
    <div>
      <checkbox 
        value={checked} 
        onChange={(value) => onCheckedChange(cartItem, value)} 
      />
      <span>商品</span>
    </div>
  )
}, areEqual)
```

在这种优化策略下，我们认为只要前后两次渲染传入的props中的`checked`相等，那么就不去重新渲染子组件。  

## React Hook的陈旧值导致的bug
到这里就完成了吗？其实，这里是有bug的。

我们来看一下bug还原：

![gif3](https://user-gold-cdn.xitu.io/2020/3/3/1709e454fc3b64d9?w=790&h=1034&f=gif&s=49176)

如果我们先点击了第一个商品的勾选，再点击第二个商品的勾选，你会发现第一个商品的勾选状态没了。  

在勾选了第一个商品后，我们此时的最新的`checkedMap`其实是 
```
{ 1: true }
```

而由于我们的优化策略，第二个商品在第一个商品勾选后没有重新渲染，  

注意React的函数式组件，在每次渲染的时候都会重新执行，从而产生一个闭包环境。  

所以第二个商品拿到的`onCheckedChange`还是前一次渲染购物车这个组件的函数闭包中的，那么`checkedMap`自然也是上一次函数闭包中的最初的空对象。
```js
  const onCheckedChange: OnCheckedChange = (cartItem, checked) => {
    const { id } = cartItem
    // 注意，这里的checkedMap还是最初的空对象！！
    const newCheckedMap = Object.assign({}, checkedMap, {
      [id]: checked,
    })
    setCheckedMap(newCheckedMap)
  }
```

因此，第二个商品勾选后，没有按照预期的计算出正确的`checkedMap`
```js
{ 
  1: true, 
  2: true
} 
```

而是计算出了错误的
```js
{ 2: true }
```

这就导致了第一个商品的勾选状态被丢掉了。  

这也是React Hook的闭包带来的臭名昭著陈旧值的问题。

那么此时有一个简单的解决方案，在父组件中用`React.useRef`把函数通过一个引用来传递给子组件。

由于`ref`在React组件的整个生命周期中只存在一个引用，因此通过current永远是可以访问到引用中最新的函数值的，不会存在闭包陈旧值的问题。

```diff
  // 要把ref传给子组件 这样才能保证子组件能在不重新渲染的情况下拿到最新的函数引用
  const onCheckedChangeRef = React.useRef(onCheckedChange)
  // 注意要在每次渲染后把ref中的引用指向当次渲染中最新的函数。
  useEffect(() => {
    onCheckedChangeRef.current = onCheckedChange
  })
  
  return (
    <ItemCard
      key={id}
      cartItem={cartItem}
      checked={checked}
+     onCheckedChangeRef={onCheckedChangeRef}
    />
  )
```

子组件
```js
// memo优化策略
function areEqual(prevProps: Props, nextProps: Props) {
  return (
    prevProps.checked === nextProps.checked
  )
}

const ItemCard: FC<Props> = React.memo(props => {
  const { checked, onCheckedChangeRef } = props
  return (
    <div>
      <checkbox 
        value={checked} 
        onChange={(value) => onCheckedChangeRef.current(cartItem, value)} 
      />
      <span>商品</span>
    </div>
  )
}, areEqual)
```

到此时，我们的简单的性能优化就完成了。

## 自定义hook之useChecked
那么下一个场景，又遇到这种全选反选类似的需求，难道我们再这样重复写一套吗？这是不可接受的，我们用自定义hook来抽象这些数据以及行为。  

并且这次我们通过useReducer来避免闭包旧值的陷阱（dispatch在组件的生命周期中保持唯一引用，并且总是能操作到最新的值）。

```ts
import { useReducer, useEffect, useCallback } from 'react'

interface Option {
  /** 用来在map中记录勾选状态的key 一般取id */
  key?: string;
}

type CheckedMap = {
  [key: string]: boolean;
}

const CHECKED_CHANGE = 'CHECKED_CHANGE'

const CHECKED_ALL_CHANGE = 'CHECKED_ALL_CHANGE'

const SET_CHECKED_MAP = 'SET_CHECKED_MAP'

type CheckedChange<T> = {
  type: typeof CHECKED_CHANGE;
  payload: {
    dataItem: T;
    checked: boolean;
  };
}

type CheckedAllChange = {
  type: typeof CHECKED_ALL_CHANGE;
  payload: boolean;
}

type SetCheckedMap = {
  type: typeof SET_CHECKED_MAP;
  payload: CheckedMap;
}

type Action<T> = CheckedChange<T> | CheckedAllChange | SetCheckedMap
export type OnCheckedChange<T> = (item: T, checked: boolean) => any

/**
 * 提供勾选、全选、反选等功能
 * 提供筛选勾选中的数据的函数
 * 在数据更新的时候自动剔除陈旧项
 */
export const useChecked = <T extends Record<string, any>>(
  dataSource: T[],
  { key = 'id' }: Option = {}
) => {
  const [checkedMap, dispatch] = useReducer(
    (checkedMapParam: CheckedMap, action: Action<T>) => {
      switch (action.type) {
        case CHECKED_CHANGE: {
          const { payload } = action
          const { dataItem, checked } = payload
          const { [key]: id } = dataItem
          return {
            ...checkedMapParam,
            [id]: checked,
          }
        }
        case CHECKED_ALL_CHANGE: {
          const { payload: newCheckedAll } = action
          const newCheckedMap: CheckedMap = {}
          // 全选
          if (newCheckedAll) {
            dataSource.forEach(dataItem => {
              newCheckedMap[dataItem.id] = true
            })
          }
          return newCheckedMap
        }
        case SET_CHECKED_MAP: {
          return action.payload
        }
        default:
          return checkedMapParam
      }
    },
    {}
  )

  /** 勾选状态变更 */
  const onCheckedChange: OnCheckedChange<T> = useCallback(
    (dataItem, checked) => {
      dispatch({
        type: CHECKED_CHANGE,
        payload: {
          dataItem,
          checked,
        },
      })
    },
    []
  )

  type FilterCheckedFunc = (item: T) => boolean
  /** 筛选出勾选项 可以传入filter函数继续筛选 */
  const filterChecked = useCallback(
    (func: FilterCheckedFunc = () => true) => {
      return (
        Object.entries(checkedMap)
          .filter(entries => Boolean(entries[1]))
          .map(([checkedId]) =>
            dataSource.find(({ [key]: id }) => id === Number(checkedId))
          )
          // 有可能勾选了以后直接删除 此时id虽然在checkedMap里 但是dataSource里已经没有这个数据了
          // 先把空项过滤掉 保证外部传入的func拿到的不为undefined
          .filter(Boolean)
          .filter(func)
      )
    },
    [checkedMap, dataSource, key]
  )
  /** 是否全选状态 */
  const checkedAll =
    dataSource.length !== 0 && filterChecked().length === dataSource.length

  /** 全选反选函数 */
  const onCheckedAllChange = (newCheckedAll: boolean) => {
    dispatch({
      type: CHECKED_ALL_CHANGE,
      payload: newCheckedAll,
    })
  }

  // 数据更新的时候 如果勾选中的数据已经不在数据内了 就删除掉
  useEffect(() => {
    filterChecked().forEach(checkedItem => {
      let changed = false
      if (!dataSource.find(dataItem => checkedItem.id === dataItem.id)) {
        delete checkedMap[checkedItem.id]
        changed = true
      }
      if (changed) {
        dispatch({
          type: SET_CHECKED_MAP,
          payload: Object.assign({}, checkedMap),
        })
      }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataSource])

  return {
    checkedMap,
    dispatch,
    onCheckedChange,
    filterChecked,
    onCheckedAllChange,
    checkedAll,
  }
}
```

这时候在组件内使用，就很简单了：
```js
const {
  checkedAll,
  checkedMap,
  onCheckedAllChange,
  onCheckedChange,
  filterChecked,
} = useChecked(cartData)
```

我们在自定义hook里把复杂的业务逻辑全部做掉了，包括数据更新后的无效id剔除等等。快去推广给团队的小伙伴，让他们早点下班吧。  

## 自定义hook之useMap
有一天，突然又来了个需求，我们需要用一个map来根据购物车商品的id来记录另外的一些东西，我们突然发现，上面的自定义hook把map的处理等等逻辑也都打包进去了，我们只能给map的值设为`true / false`，灵活性不够。  

我们进一步把`useMap`也抽出来，然后让`useCheckedMap`基于它之上开发。

### useMap
```ts
import { useReducer, useEffect, useCallback } from 'react'

export interface Option {
  /** 用来在map中作为key 一般取id */
  key?: string;
}

export type MapType = {
  [key: string]: any;
}

export const CHANGE = 'CHANGE'

export const CHANGE_ALL = 'CHANGE_ALL'

export const SET_MAP = 'SET_MAP'

export type Change<T> = {
  type: typeof CHANGE;
  payload: {
    dataItem: T;
    value: any;
  };
}

export type ChangeAll = {
  type: typeof CHANGE_ALL;
  payload: any;
}

export type SetCheckedMap = {
  type: typeof SET_MAP;
  payload: MapType;
}

export type Action<T> = Change<T> | ChangeAll | SetCheckedMap
export type OnValueChange<T> = (item: T, value: any) => any

/**
 * 提供map操作的功能
 * 在数据更新的时候自动剔除陈旧项
 */
export const useMap = <T extends Record<string, any>>(
  dataSource: T[],
  { key = 'id' }: Option = {}
) => {
  const [map, dispatch] = useReducer(
    (checkedMapParam: MapType, action: Action<T>) => {
      switch (action.type) {
        // 单值改变
        case CHANGE: {
          const { payload } = action
          const { dataItem, value } = payload
          const { [key]: id } = dataItem
          return {
            ...checkedMapParam,
            [id]: value,
          }
        }
        // 所有值改变
        case CHANGE_ALL: {
          const { payload } = action
          const newMap: MapType = {}
          dataSource.forEach(dataItem => {
            newMap[dataItem[key]] = payload
          })
          return newMap
        }
        // 完全替换map
        case SET_MAP: {
          return action.payload
        }
        default:
          return checkedMapParam
      }
    },
    {}
  )

  /** map某项的值变更 */
  const onMapValueChange: OnValueChange<T> = useCallback((dataItem, value) => {
    dispatch({
      type: CHANGE,
      payload: {
        dataItem,
        value,
      },
    })
  }, [])

  // 数据更新的时候 如果map中的数据已经不在dataSource内了 就删除掉
  useEffect(() => {
    dataSource.forEach(checkedItem => {
      let changed = false
      if (
        // map中包含此项
        // 并且数据源中找不到此项了
        checkedItem[key] in map &&
        !dataSource.find(dataItem => checkedItem[key] === dataItem[key])
      ) {
        delete map[checkedItem[key]]
        changed = true
      }
      if (changed) {
        dispatch({
          type: SET_MAP,
          payload: Object.assign({}, map),
        })
      }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataSource])

  return {
    map,
    dispatch,
    onMapValueChange,
  }
}
```
这是一个通用的map操作的自定义hook，它考虑了闭包陷阱，考虑了旧值的删除。

在此之上，我们实现上面的`useChecked`

### useChecked
```js
import { useCallback } from 'react'
import { useMap, CHANGE_ALL, Option } from './use-map'

type CheckedMap = {
  [key: string]: boolean;
}

export type OnCheckedChange<T> = (item: T, checked: boolean) => any

/**
 * 提供勾选、全选、反选等功能
 * 提供筛选勾选中的数据的函数
 * 在数据更新的时候自动剔除陈旧项
 */
export const useChecked = <T extends Record<string, any>>(
  dataSource: T[],
  option: Option = {}
) => {
  const { map: checkedMap, onMapValueChange, dispatch } = useMap(
    dataSource,
    option
  )
  const { key = 'id' } = option

  /** 勾选状态变更 */
  const onCheckedChange: OnCheckedChange<T> = useCallback(
    (dataItem, checked) => {
      onMapValueChange(dataItem, checked)
    },
    [onMapValueChange]
  )

  type FilterCheckedFunc = (item: T) => boolean
  /** 筛选出勾选项 可以传入filter函数继续筛选 */
  const filterChecked = useCallback(
    (func?: FilterCheckedFunc) => {
      const checkedDataSource = dataSource.filter(item =>
        Boolean(checkedMap[item[key]])
      )
      return func ? checkedDataSource.filter(func) : checkedDataSource
    },
    [checkedMap, dataSource, key]
  )
  /** 是否全选状态 */
  const checkedAll =
    dataSource.length !== 0 && filterChecked().length === dataSource.length

  /** 全选反选函数 */
  const onCheckedAllChange = (newCheckedAll: boolean) => {
    // 全选
    const payload = !!newCheckedAll
    dispatch({
      type: CHANGE_ALL,
      payload,
    })
  }

  return {
    checkedMap: checkedMap as CheckedMap,
    dispatch,
    onCheckedChange,
    filterChecked,
    onCheckedAllChange,
    checkedAll,
  }
}
```

## 总结
本文通过一个真实的购物车需求，一步一步的完成优化、踩坑，在这个过程中，我们对React Hook的优缺点一定也有了进一步的认识。  

在利用自定义hook把通用逻辑抽取出来后，我们业务组件内的代码量大大的减少了，并且其他相似的场景都可以去复用。  

React Hook带来了一种新的开发模式，但是也带来了一些陷阱，它是一把双刃剑，如果你能合理使用，那么它会给你带来很强大的力量。

感谢你的阅读，希望这篇文章可以给你启发。