# [cube-ui源码学习 swipe组件](https://github.com/sl1673495/blogs/issues/10)

[swipe组件预览地址（手机模式可体验）](https://didi.github.io/cube-ui/#/zh-CN/docs/swipe)
[作者：黄轶老师](https://github.com/ustbhuangyi)

先吹一波黄老，昨天体验swipe组件的时候感受到了什么叫丝滑，这可以说是东半球移动端最好用的swipe组件了吧。

先来一段文档中的用法的简化版：
```js
<cube-swipe>
    <li class="swipe-item-wrapper" v-for="(data,index) in swipeData" :key="data.item.id">
      <cube-swipe-item
          ref="swipeItem"
          :btns="data.btns"
          :index="index"
          @btn-click="onBtnClick">
           <div></div>
      </cube-swipe-item>
   </li>      
 </cube-swipe>
```
在cube-ui的项目的src/components/swipe目录下，我们可以看到swipe组件被分为swipe.vue和swipe-item.vue。
其实swipe就是列表的外层容器组件，负责处理一些全列表的事件。
swipe-item就是列表中循环出来的某一项元素的组件，负责处理手势等细节。
我们先从swipe.vue入手：

### swipe.vue
```js
<template>
  <div class="cube-swipe">
    <slot>
      <transition-group name="cube-swipe" tag="ul">
        <li v-for="(item, index) in data" :key="item.item.value">
          <cube-swipe-item
            :btns="item.btns"
            :item="item.item"
            :index="index"
            :auto-shrink="autoShrink" />
        </li>
      </transition-group>
    </slot>
  </div>
</template>
```
我们先从template部分入手， 可以看到结构非常简单，就是一个div中给了一个slot子元素，并且slot有个默认值，
如果用户不传slot的话就默认的带transition-group动效循环出一段cube-swipe-item列表，不使用slot的情况下用户可以传入
```js
swipeData: [{
        item: {
          text: '测试1',
          value: 1
        },
        btns: [
          {
            action: 'clear',
            text: '不再关注',
            color: '#c8c7cd'
          },
          {
            action: 'delete',
            text: '删除',
            color: '#ff3a32'
          }
        ]
      }, {
        item: {
          text: '测试2',
          value: 2
        },
        btns: [
          {
            action: 'clear',
            text: '不再关注',
            color: '#c8c7cd'
          },
          {
            action: 'delete',
            text: '删除',
            color: '#ff3a32'
          }
        ]
      }, {
        item: {
          text: '测试3',
          value: 3
        },
        btns: [
          {
            action: 'clear',
            text: '不再关注',
            color: '#c8c7cd'
          },
          {
            action: 'delete',
            text: '删除',
            color: '#ff3a32'
          }
        ]
      }]
```
这样一段大而全的json数组，渲染出一个列表，不过这种方式比较不灵活。

```js
<script type="text/ecmascript-6">
  import CubeSwipeItem from './swipe-item.vue'
  const COMPONENT_NAME = 'cube-swipe'
  const EVENT_ITEM_CLICK = 'item-click'
  const EVENT_BTN_CLICK = 'btn-click'
  export default {
    name: COMPONENT_NAME,
    provide() {
      return {
        swipe: this
      }
    },
    props: {
      data: {
        type: Array,
        default() {
          return []
        }
      },
      autoShrink: {
        type: Boolean,
        default: false
      }
    },
    created() {
      this.activeIndex = -1
      this.items = []
    },
    methods: {
      addItem(item) {
        this.items.push(item)
      },
      removeItem(item) {
        const index = this.items.indexOf(item)
        this.items.splice(index, 1)
        if (index <= this.activeIndex) {
          this.activeIndex -= 1
        }
      },
      onItemClick(item, index) {
        this.$emit(EVENT_ITEM_CLICK, item, index)
      },
      onBtnClick(btn, index) {
        const item = this.data[index]
        this.$emit(EVENT_BTN_CLICK, btn, index, item)
      },
      onItemActive(index) {
        if (index === this.activeIndex) {
          return
        }
        if (this.activeIndex !== -1) {
          const activeItem = this.items[this.activeIndex]
          activeItem.shrink()
        }
        this.activeIndex = index
      }
    },
    components: {
      CubeSwipeItem
    }
  }
</script>
```

script的data和methods里提供了很多东西，但是在template里却没有使用到，那么我们猜测这些都是提供给子组件使用的，
provider里把自身实例提供给了子组件
```js
 provide() {
      return {
        swipe: this
      }
    },
```
那么我们接下来就去探究swipe-item组件。

### swipe-item
```js
<template>
  <div ref="swipeItem"
       @transitionend="onTransitionEnd"
       @touchstart="onTouchStart"
       @touchmove="onTouchMove"
       @touchend="onTouchEnd"
       class="cube-swipe-item">
    <slot>
      <div @click="clickItem" class="cube-swipe-item-inner border-bottom-1px">
        <span>{{item.text}}</span>
      </div>
    </slot>
    <ul class="cube-swipe-btns">
      <li ref="btns"
          v-for="btn in btns"
          class="cube-swipe-btn"
          :style="genBtnStyl(btn)"
          @click.prevent="clickBtn(btn)">
        <span class="text">{{btn.text}}</span>
      </li>
    </ul>
  </div>
</template>

<style lang="stylus" rel="stylesheet/stylus">
  @require "../../common/stylus/variable.styl"
  .cube-swipe-item
    position: relative
  .cube-swipe-item-inner
    height: 60px
    line-height: 60px
    font-size: $fontsize-large
    padding-left: 20px
  .cube-swipe-btn
    display: flex
    align-items: center
    position: absolute
    top: 0
    left: 100%
    height: 100%
    text-align: left
    font-size: $fontsize-large
    .text
      flex: 1
      padding: 0 20px
      white-space: nowrap
      color: $swipe-btn-color
</style>
```
可以看到swipe-item的结构也非常简单， 也提供了slot插槽定制子组件的元素
并且在子组件的旁边有个初始隐藏的ul结构 用来循环btns来生成侧滑出来的按钮
.cube-swipe-btn这个类是绝对定位并且left 100% 也就是相对于父relative容器
  .cube-swipe-item的宽度偏移 正好隐藏到边缘外。

接下来我们看一下script部分
```js
<script type="text/ecmascript-6">
  import {
    getRect,
    prefixStyle
  } from '../../common/helpers/dom'
  import { easeOutQuart, easeOutCubic } from '../../common/helpers/ease'
  import { getNow } from '../../common/lang/date'
  const COMPONENT_NAME = 'cube-swipe-item'
  const EVENT_ITEM_CLICK = 'item-click'
  const EVENT_BTN_CLICK = 'btn-click'
  const EVENT_SCROLL = 'scroll'
  const EVENT_ACTIVE = 'active'
  const DIRECTION_LEFT = 1
  const DIRECTION_RIGHT = -1
  const STATE_SHRINK = 0
  const STATE_GROW = 1
  const easingTime = 600
  const momentumLimitTime = 300
  const momentumLimitDistance = 15
  const directionLockThreshold = 5
  const transform = prefixStyle('transform')
  const transitionProperty = prefixStyle('transitionProperty')
  const transitionDuration = prefixStyle('transitionDuration')
  const transitionTimingFunction = prefixStyle('transitionTimingFunction')
  export default {
    name: COMPONENT_NAME,
    inject: ['swipe'],
    props: {
      item: {
        type: Object,
        default() {
          return {}
        }
      },
      btns: {
        type: Array,
        default() {
          return []
        }
      },
      index: {
        type: Number,
        index: -1
      },
      autoShrink: {
        type: Boolean,
        default: false
      }
    },
    watch: {
      btns() {
        this.$nextTick(() => {
          this.refresh()
        })
      }
    },
    created() {
      this.x = 0
      this.state = STATE_SHRINK
      this.swipe.addItem(this)
    },
    mounted() {
      this.scrollerStyle = this.$refs.swipeItem.style
      this.$nextTick(() => {
        this.refresh()
      })
      this.$on(EVENT_SCROLL, this._handleBtns)
    },
    methods: {
      _initCachedBtns() {
        this.cachedBtns = []
        const len = this.$refs.btns.length
        for (let i = 0; i < len; i++) {
          this.cachedBtns.push({
            width: getRect(this.$refs.btns[i]).width
          })
        }
      },
      _handleBtns(x) {
        /* istanbul ignore if */
        if (this.btns.length === 0) {
          return
        }
        const len = this.$refs.btns.length
        let delta = 0
        let totalWidth = -this.maxScrollX
        for (let i = 0; i < len; i++) {
          const btn = this.$refs.btns[i]
          let rate = (totalWidth - delta) / totalWidth
          let width
          let translate = rate * x - x
          if (x < this.maxScrollX) {
            width = this.cachedBtns[i].width + rate * (this.maxScrollX - x)
          } else {
            width = this.cachedBtns[i].width
          }
          delta += this.cachedBtns[i].width
          btn.style.width = `${width}px`
          btn.style[transform] = `translate(${translate}px)`
          btn.style[transitionDuration] = '0ms'
        }
      },
      _isInBtns(target) {
        let parent = target
        let flag = false
        while (parent && parent.className.indexOf('cube-swipe-item') < 0) {
          if (parent.className.indexOf('cube-swipe-btns') >= 0) {
            flag = true
            break
          }
          parent = parent.parentNode
        }
        return flag
      },
      _calculateBtnsWidth() {
        let width = 0
        const len = this.cachedBtns.length
        for (let i = 0; i < len; i++) {
          width += this.cachedBtns[i].width
        }
        this.maxScrollX = -width
      },
      _translate(x, useZ) {
        let translateZ = useZ ? ' translateZ(0)' : ''
        this.scrollerStyle[transform] = `translate(${x}px,0)${translateZ}`
        this.x = x
      },
      _transitionProperty(property = 'transform') {
        this.scrollerStyle[transitionProperty] = property
      },
      _transitionTimingFunction(easing) {
        this.scrollerStyle[transitionTimingFunction] = easing
      },
      _transitionTime(time = 0) {
        this.scrollerStyle[transitionDuration] = `${time}ms`
      },
      _getComputedPositionX() {
        let matrix = window.getComputedStyle(this.$refs.swipeItem, null)
        matrix = matrix[transform].split(')')[0].split(', ')
        let x = +(matrix[12] || matrix[4])
        return x
      },
      _translateBtns(time, easing, extend) {
        /* istanbul ignore if */
        if (this.btns.length === 0) {
          return
        }
        const len = this.$refs.btns.length
        let delta = 0
        let translate = 0
        for (let i = 0; i < len; i++) {
          const btn = this.$refs.btns[i]
          if (this.state === STATE_GROW) {
            translate = delta
          } else {
            translate = 0
          }
          delta += this.cachedBtns[i].width
          btn.style[transform] = `translate(${translate}px,0) translateZ(0)`
          btn.style[transitionProperty] = 'all'
          btn.style[transitionTimingFunction] = easing
          btn.style[transitionDuration] = `${time}ms`
          if (extend) {
            btn.style.width = `${this.cachedBtns[i].width}px`
          }
        }
      },
      refresh() {
        if (this.btns.length > 0) {
          this._initCachedBtns()
          this._calculateBtnsWidth()
        }
        this.endTime = 0
      },
      shrink() {
        this.stop()
        this.state = STATE_SHRINK
        this.$nextTick(() => {
          this.scrollTo(0, easingTime, easeOutQuart)
          this._translateBtns(easingTime, easeOutQuart)
        })
      },
      grow() {
        this.state = STATE_GROW
        const extend = this.x < this.maxScrollX
        let easing = easeOutCubic
        this.scrollTo(this.maxScrollX, easingTime, easing)
        this._translateBtns(easingTime, easing, extend)
      },
      scrollTo(x, time, easing) {
        this._transitionProperty()
        this._transitionTimingFunction(easing)
        this._transitionTime(time)
        this._translate(x, true)
        if (time) {
          this.isInTransition = true
        }
      },
      genBtnStyl(btn) {
        return `background: ${btn.color}`
      },
      clickItem() {
        this.swipe.onItemClick(this.item, this.index)
        this.$emit(EVENT_ITEM_CLICK, this.item, this.index)
      },
      clickBtn(btn) {
        this.swipe.onBtnClick(btn, this.index)
        this.$emit(EVENT_BTN_CLICK, btn, this.index)
        if (this.autoShrink) {
          this.shrink()
        }
      },
      stop() {
        if (this.isInTransition) {
          this.isInTransition = false
          let x = this.state === STATE_SHRINK ? 0 : this._getComputedPositionX()
          this._translate(x)
          this.$emit(EVENT_SCROLL, this.x)
        }
      },
      onTouchStart(e) {
        this.swipe.onItemActive(this.index)
        this.$emit(EVENT_ACTIVE, this.index)
        this.stop()
        this.moved = false
        this.movingDirectionX = 0
        const point = e.touches[0]
        this.pointX = point.pageX
        this.pointY = point.pageY
        this.distX = 0
        this.distY = 0
        this.startX = this.x
        this._transitionTime()
        this.startTime = getNow()
        if (this.state === STATE_GROW && !this._isInBtns(e.target)) {
          this.shrinkTimer = setTimeout(() => {
            this.shrink()
          }, 300)
        }
      },
      onTouchMove(e) {
        if (this.moved) {
          clearTimeout(this.shrinkTimer)
          e.stopPropagation()
        }
        /* istanbul ignore if */
        if (this.isInTransition) {
          return
        }
        e.preventDefault()
        const point = e.touches[0]
        let deltaX = point.pageX - this.pointX
        let deltaY = point.pageY - this.pointY
        this.pointX = point.pageX
        this.pointY = point.pageY
        this.distX += deltaX
        this.distY += deltaY
        let absDistX = Math.abs(this.distX)
        let absDistY = Math.abs(this.distY)
        if (absDistX + directionLockThreshold <= absDistY) {
          return
        }
        let timestamp = getNow()
        if (timestamp - this.endTime > momentumLimitTime && absDistX < momentumLimitDistance) {
          return
        }
        this.movingDirectionX = deltaX > 0 ? DIRECTION_RIGHT : deltaX < 0 ? DIRECTION_LEFT : 0
        let newX = this.x + deltaX
        if (newX > 0) {
          newX = 0
        }
        if (newX < this.maxScrollX) {
          newX = this.x + deltaX / 3
        }
        if (!this.moved) {
          this.moved = true
        }
        this._translate(newX, true)
        if (timestamp - this.startTime > momentumLimitTime) {
          this.startTime = timestamp
          this.startX = this.x
        }
        this.$emit(EVENT_SCROLL, this.x)
      },
      onTouchEnd() {
        if (!this.moved) {
          return
        }
        if (this.movingDirectionX === DIRECTION_RIGHT) {
          this.shrink()
          return
        }
        this.endTime = getNow()
        let duration = this.endTime - this.startTime
        let absDistX = Math.abs(this.x - this.startX)
        if ((duration < momentumLimitTime && absDistX > momentumLimitDistance) || this.x < this.maxScrollX / 2) {
          this.grow()
        } else {
          this.shrink()
        }
      },
      onTransitionEnd() {
        this.isInTransition = false
        this._transitionTime()
        this._translate(this.x)
      }
    },
    beforeDestroy() {
      this.swipe.removeItem(this)
    }
  }
</script>
```
首先看到inject: ['swipe']， 使得父swipe组件实例自身可以通过this.swipe访问到，
接下来看
```js

  props: {
      item: {
        type: Object,
        default() {
          return {}
        }
      },
      btns: {
        type: Array,
        default() {
          return []
        }
      },
      index: {
        type: Number,
        index: -1
      },
      autoShrink: {
        type: Boolean,
        default: false
      }
    },
```
组件接受四个props，item是在不使用slot自定义子组件元素的情况下使用的，我们可以先不看。
btns就是描述按钮的数组，形如
```js
btns: [
            {
              action: 'clear',
              text: '不再关注',
              color: '#c8c7cd'
            },
            {
              action: 'delete',
              text: '删除',
              color: '#ff3a32'
            }
          ]
```
index 接受在外层v-for拿到的index传递给swipe-item组件 便于标识这个swipe-item在swipe容器中的序号。
autoShrink用于当点击滑块的按钮后，是否需要自动收缩滑块，如果使用自定义插槽，则直接给 cube-swipe-item 传递此值即可。

看完了props 我们可以按生命周期流程开始看了，先看created周期
```js
    created() {
      this.x = 0
      this.state = STATE_SHRINK
      this.swipe.addItem(this)
    },
```

this.x用来记录滑动偏移的量，
this.state用来记录状态，默认是缩起，
this.swipe.addItem(this) 调用父组件的addItem方法把自身实例push到父组件的
this.items数组里收集起来。

初始化完了我们来看
```js
mounted() {
      this.scrollerStyle = this.$refs.swipeItem.style
      this.$nextTick(() => {
        this.refresh()
      })
      this.$on(EVENT_SCROLL, this._handleBtns)
    },
```
首先通过把这个组件的dom节点的style用this.scrollerStyle记录起来 便于后续操作
接着调用了this.refresh

```js
refresh() {
        if (this.btns.length > 0) {
          this._initCachedBtns()
          this._calculateBtnsWidth()
        }
        this.endTime = 0
      },

```
可以看到 我们做了两个初始化工作_initCachedBtns和_calculateBtnsWidth，并且把endTime标识为0
我们先看_initCachedBtns
```js
_initCachedBtns() {
        this.cachedBtns = []
        const len = this.$refs.btns.length
        for (let i = 0; i < len; i++) {
          this.cachedBtns.push({
            width: getRect(this.$refs.btns[i]).width
          })
        }
      },

```
this.cachedBtns记录按钮宽度大小，
最后生成形如[ {width: 50}, {width: 50 } ] 这样的记录，
再来看_calculateBtnsWidth
```js
_calculateBtnsWidth() {
        let width = 0
        const len = this.cachedBtns.length
        for (let i = 0; i < len; i++) {
          width += this.cachedBtns[i].width
        }
        this.maxScrollX = -width
      },
```
其实就是计算出按钮的总长度 
然后记录在this.maxScrollX变量上，用于标识向左滑动的最大距离。

mounted的最后this.$on(EVENT_SCROLL, this._handleBtns)
注册了EVENT_SCROLL事件的回调函数为 this._handleBtns， 我们先记下来 等到触发的时候再详细去讲。

初始化的流程到这就结束了， 那么接下来我们就可以看这个组件的核心 touch事件了，touch事件全部注册在最外层的dom节点上
```js
 <div ref="swipeItem"
       @transitionend="onTransitionEnd"
       @touchstart="onTouchStart"
       @touchmove="onTouchMove"
       @touchend="onTouchEnd"
       class="cube-swipe-item">
```

我们顺着流程onTouchStart - onTouchMove - onTouchEnd - onTransitionEnd一步一步来走。

```js
onTouchStart(e) {
        this.swipe.onItemActive(this.index)
        this.$emit(EVENT_ACTIVE, this.index)
        this.stop()
        this.moved = false
        this.movingDirectionX = 0
        const point = e.touches[0]
        this.pointX = point.pageX
        this.pointY = point.pageY
        this.distX = 0
        this.distY = 0
        this.startX = this.x
        this._transitionTime()
        this.startTime = getNow()
        if (this.state === STATE_GROW && !this._isInBtns(e.target)) {
          this.shrinkTimer = setTimeout(() => {
            this.shrink()
          }, 300)
        }
      },
```
 this.swipe.onItemActive(this.index)
首先通知父组件“我被触摸了”， 这里调用父swipe组件的onItemActive方法
```js
 onItemActive(index) {
        if (index === this.activeIndex) {
          return
        }
        if (this.activeIndex !== -1) {
          const activeItem = this.items[this.activeIndex]
          activeItem.shrink()
        }
        this.activeIndex = index
      }
```
如果父元素中有已经被触摸左滑展开的swipe-item记录 并且和这个新的swipe-item不是同一个 就通知上一个子组件shrink() 收起， 并且在swipe组件中记录this.activeIndex = index新的子组件序号
        this.pointX = point.pageX
        this.pointY = point.pageY
        this.distX = 0
        this.distY = 0
        this.startX = this.x
记录了这个点的xy值 把dist当前手指的触碰距离值置为0，把this.x的值赋值给this.startX
调用this._transitionTime()
```js
      _transitionTime(time = 0) {
        this.scrollerStyle[transitionDuration] = `${time}ms`
      },
```
把style的transitionDuration置为0 手指触摸的时候不需要transitionDuration来帮我们完成动画过渡效果的，所以先把这个过渡关闭
```js
this.startTime = getNow() // 记录触摸开始的时间
if (this.state === STATE_GROW && !this._isInBtns(e.target)) {
          this.shrinkTimer = setTimeout(() => {
            this.shrink()
          }, 300)
        }
```
这段代码做了一个判断 如果当前的状态是展开 并且点击的位置不在btn内部
就设置了一个定时器 如果touchstart过了300ms 就会把这个swipe-item收起
总结起来就是一系列初始化值的设置，接下来看onTouchMove
onTouchMove的方法比较长 也是滑动动画的核心，我们跟着注释一行一行来解读
```js
onTouchMove(e) {
        if (this.moved) {
          // 如果moved变量为true 也就是正在移动中， 就把300ms后自动缩进的定时器清空掉
          clearTimeout(this.shrinkTimer)
         // 并且阻止事件冒泡
          e.stopPropagation()
        }
        /* istanbul ignore if */

       // 如果已经在进行动画 就直接return 
       // 展开动画和缩起动画的过程中这个值都是true
        if (this.isInTransition) {
          return
        }

        // 阻止浏览器默认touch行为，比如页面滚动
        e.preventDefault()
        const point = e.touches[0]

        // 相对于上次触发touchmove时候横向的偏移量deltaX
        let deltaX = point.pageX - this.pointX
        // 相对于上次触发touchmove时候竖直方向的偏移量deltaY
        let deltaY = point.pageY - this.pointY

        // 记录最新的pointX和Y
        this.pointX = point.pageX
        this.pointY = point.pageY

        // 本次从touchstart事件开始移动的横向总距离
        this.distX += deltaX

         // 本次从touchstart事件开始移动的纵向总距离
        this.distY += deltaY

       // distX和distY的绝对值
        let absDistX = Math.abs(this.distX)
        let absDistY = Math.abs(this.distY)

        // 如果横向距离 加directionLockThreshold(被设置成了5) 
        // 小与纵向移动的距离 就判定成上下滑动 不做任何行为
        //这其实就是稍微大于45度角的角度以内的滑动会被识别为侧滑
        if (absDistX + directionLockThreshold <= absDistY) {
          return
        }

        let timestamp = getNow()
        // momentumLimitTime和momentumLimitDistance
        // 定义两次动画的最小间隔事件和最小间隔移动距离
        // 距离上次touchend 300ms内并且 横向移动小于15的move事件会被无视
        if (timestamp - this.endTime > momentumLimitTime && absDistX < momentumLimitDistance) {
          return
        }

        // movingDirectionX 滑动的方向， 如果deltaX大于0 则是向右滑动-1 
        // 如果deltaX小于0则是左滑-1 如果等于0 则记录为0
        this.movingDirectionX = deltaX > 0 ? DIRECTION_RIGHT : deltaX < 0 ? DIRECTION_LEFT : 0
        // this.x在执行_translate动画的之后会被更新成当前的translateX值， 

       // newX拿到了到上次move为止偏移的x值 
       // 加上本次move偏移的deltaX值
       // 计算出newX也就是下一次应该_translate到x位置值，
       // 这个值一定是负数，因为我们的按钮组一定是向左做偏移translateX(-x)
       //  当然这个值不能直接交给_translate方法 我们要做一些边界值处理
        let newX = this.x + deltaX
        // 不能大于0的边界限制， 保证向右滑动不能超出边缘
        if (newX > 0) {
          newX = 0
        }
        // 如果X的值比最大的maxScrollX值还小
        // maxScrollX的值在refresh中
        // 被设置成了按钮组的总width的负值
        // 用比较好理解的方法 就是向左拉到了极限值
        // 那么你下次再拉30px 只会向左做10px的动画
        // 给你一种有阻力的感觉
        if (newX < this.maxScrollX) {
          newX = this.x + deltaX / 3
        }

       // 如果moved是false 记录为true
        if (!this.moved) {
          this.moved = true
        }
       // 调用_translate 真正去操作dom左偏移的行为
        this._translate(newX, true)

       // 如果这次move的事件减去开始事件小于momentumLimitTime边界值300ms
       // 就把这次move手指所在的值定义为下次计算的开始值，好做到手指短暂离开屏幕 动画也可以衔接上
        if (timestamp - this.startTime > momentumLimitTime) {
          // 重置startTime为当前时间
          this.startTime = timestamp
          // 重置startX为当前的偏移值x
          this.startX = this.x
        }
        // 触发EVENT_SCROLL事件 带出当前的x值。
        this.$emit(EVENT_SCROLL, this.x)
      },
```
总结touchmove事件 核心就是根据当前手指的x值和start时的x值 调用_translate让dom去做一些偏移
```js
      _translate(x, useZ) {
        let translateZ = useZ ? ' translateZ(0)' : ''
        this.scrollerStyle[transform] = `translate(${x}px,0)${translateZ}`
        this.x = x
      },
```
_translate很简单 把x值写入dom样式里 并且translateZ(0)开启硬件加速
然后更新实例上的this.x 最后还要触发一个EVENT_SCROLL
我们在created里看到了这个EVENT_SCROLL事件注册的回调是_handleBtns
其实就是在touchmove的时候也驱动按钮组做一些动画
_handleBtns
```js
      // 根据当前的x值驱动每个按钮去做向左滑动动画
      // 并且如果超出了最大x距离 还要让按钮变长
      // 让用户有种按钮有弹性拉动的感觉
     _handleBtns(x) {
        /* istanbul ignore if */
        if (this.btns.length === 0) {
          return
        }
        const len = this.$refs.btns.length
        let delta = 0
        let totalWidth = -this.maxScrollX
        for (let i = 0; i < len; i++) {
          const btn = this.$refs.btns[i]
          let rate = (totalWidth - delta) / totalWidth
          let width
          let translate = rate * x - x
          if (x < this.maxScrollX) {
            width = this.cachedBtns[i].width + rate * (this.maxScrollX - x)
          } else {
            width = this.cachedBtns[i].width
          }
          delta += this.cachedBtns[i].width
          btn.style.width = `${width}px`
          btn.style[transform] = `translate(${translate}px)`
          btn.style[transitionDuration] = '0ms'
        }
      },
```

```js
onTouchEnd() {
       // 如果moved变量为false 什么也不做
        if (!this.moved) {
          return
        }
       
        // 如果是向右滑动 调用shrink缩起滑块
        if (this.movingDirectionX === DIRECTION_RIGHT) {
          this.shrink()
          return
        }
        // this.endTime设置为当前时间
        this.endTime = getNow()

        // 从开始滑动到结束的时间间隔
        let duration = this.endTime - this.startTime
        // 本次滑动的总距离
        let absDistX = Math.abs(this.x - this.startX)

        
        if ((duration < momentumLimitTime && absDistX > momentumLimitDistance) || this.x < this.maxScrollX / 2) {
          // 时间间隔<300ms 滑动距离>15 或者滑动距离x比最大滑动距离的一半要小 就展开
          this.grow()
        } else {
          //  否则收起
          this.shrink()
        }

```
touchend的核心逻辑就是根据记录的一些变量判断是要调用展开还是收起
展开grow
```js
      grow() {
        // 状态记录为展开状态
        this.state = STATE_GROW
        // extend记录为x是否比最大滑动距离要小
        const extend = this.x < this.maxScrollX
        // 展开的贝塞尔曲线描述
        let easing = easeOutCubic
        // 调用scrollTo，值定义为完全展开的x值
        this.scrollTo(this.maxScrollX, easingTime, easing)
        // 调用_translateBtns让按钮组做动画
        this._translateBtns(easingTime, easing, extend)
      },
```
我们来看看scrollTo方法如何让容器偏移到最大滑动距离
```js
     scrollTo(x, time, easing) {
        // 设定transform-property为'transform'
        this._transitionProperty()
        // 设定transform过渡动画为easing贝塞尔曲线
        this._transitionTimingFunction(easing)
        // 设定过渡时间
        this._transitionTime(time)
        // 设定transformX值 开始执行动画
        this._translate(x, true)
        // 有过渡时间的情况下 把isInTransition变量置为true
        if (time) {
          this.isInTransition = true
        }
      },
```
其实scrollTo就是给容器设定了一系列的transform的css值，让css帮我们做动画
再看_translateBtns
```js
_translateBtns(time, easing, extend) {
        /* istanbul ignore if */
        // 如果没有btns 就啥也不做
        if (this.btns.length === 0) {
          return
        }

        // 遍历btn组的dom节点，
        // 给按钮也设置一系列css transform 让按钮一个个做对应的动画
        // 并且如果extend为true 证明此时按钮被拉到超出最大距离 width被变长了
        // 要重置为之前的width
        const len = this.$refs.btns.length
        let delta = 0
        let translate = 0
        for (let i = 0; i < len; i++) {
          const btn = this.$refs.btns[i]
          if (this.state === STATE_GROW) {
            translate = delta
          } else {
            translate = 0
          }
          delta += this.cachedBtns[i].width
          btn.style[transform] = `translate(${translate}px,0) translateZ(0)`
          btn.style[transitionProperty] = 'all'
          btn.style[transitionTimingFunction] = easing
          btn.style[transitionDuration] = `${time}ms`
          if (extend) {
            btn.style.width = `${this.cachedBtns[i].width}px`
          }
        }
      },
``` 
再来看缩起shrink
```js
      shrink() {
        this.stop()
        this.state = STATE_SHRINK
        this.$nextTick(() => {
          this.scrollTo(0, easingTime, easeOutQuart)
          this._translateBtns(easingTime, easeOutQuart)
        })
      },
```
先调用了stop
stop中先把this.isInTransition置为false
在touchstart时候也会调用stop 所以要根据state判断目标值
如果状态已经是缩起状态STATE_SHRINK， 则目标值是0
然后_translate过渡到x位置
并且通过EVENT_SCROLL事件通知按钮组也过渡到x位置
```js
      stop() {
        if (this.isInTransition) {
          this.isInTransition = false
          let x = this.state === STATE_SHRINK ? 0 : this._getComputedPositionX()
          this._translate(x)
          this.$emit(EVENT_SCROLL, this.x)
        }
      },
```
最后在nextTick里调用scrollTo和_translateBtns分别把容器dom和按钮组动画移动到缩起状态原位
因为此时state已经是STATE_SHRINK了 所以_translateBtns内部会判定x的目标值为0

至此touch事件三剑客都分析完毕了，内部有些细节实现的很精巧
在动画结束的时候会调用onTransitionEnd，做一些状态的重置。
```js
      onTransitionEnd() {
        this.isInTransition = false
        this._transitionTime()
        this._translate(this.x)
      }
```

另外在按钮上点击会触发clickBtn方法，驱动‘btn-click’事件的触发
并且判断autoShrink的情况下自动收缩起按钮组
```js
      clickBtn(btn) {
        this.swipe.onBtnClick(btn, this.index)
        this.$emit(EVENT_BTN_CLICK, btn, this.index)
        if (this.autoShrink) {
          this.shrink()
        }
      },
```
