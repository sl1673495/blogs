# [react-component源码学习（2） rc-steps](https://github.com/sl1673495/blogs/issues/6)

rc-steps是antd的步骤组件所依赖的底层组件，先看官方给的用法示例。
```js
<Steps current={1}>
  <Steps.Step title="first" />
  <Steps.Step title="second" />
  <Steps.Step title="third" />
</Steps>
```
简洁明了的父子嵌套组件。
先从父组件的源码看起。
## Steps.jsx
```js
/* eslint react/no-did-mount-set-state: 0 */
import React, { cloneElement, Children, Component } from 'react';
import PropTypes from 'prop-types';
import { findDOMNode } from 'react-dom';
import classNames from 'classnames';
import debounce from 'lodash/debounce';
import { isFlexSupported } from './utils';

export default class Steps extends Component {
  static propTypes = {
    prefixCls: PropTypes.string,
    className: PropTypes.string,
    iconPrefix: PropTypes.string,
    direction: PropTypes.string,
    labelPlacement: PropTypes.string,
    children: PropTypes.any,
    status: PropTypes.string,
    size: PropTypes.string,
    progressDot: PropTypes.oneOfType([
      PropTypes.bool,
      PropTypes.func,
    ]),
    style: PropTypes.object,
    initial: PropTypes.number,
    current: PropTypes.number,
    icons: PropTypes.shape({
      finish: PropTypes.node,
      error: PropTypes.node,
    }),
  };
  static defaultProps = {
    prefixCls: 'rc-steps',
    iconPrefix: 'rc',
    direction: 'horizontal',
    labelPlacement: 'horizontal',
    initial: 0,
    current: 0,
    status: 'process',
    size: '',
    progressDot: false,
  };
  constructor(props) {
    super(props);
    this.state = {
      flexSupported: true,
      lastStepOffsetWidth: 0,
    };
    this.calcStepOffsetWidth = debounce(this.calcStepOffsetWidth, 150);
  }
  componentDidMount() {
    this.calcStepOffsetWidth();
    if (!isFlexSupported()) {
      this.setState({
        flexSupported: false,
      });
    }
  }
  componentDidUpdate() {
    this.calcStepOffsetWidth();
  }
  componentWillUnmount() {
    if (this.calcTimeout) {
      clearTimeout(this.calcTimeout);
    }
    if (this.calcStepOffsetWidth && this.calcStepOffsetWidth.cancel) {
      this.calcStepOffsetWidth.cancel();
    }
  }
  calcStepOffsetWidth = () => {
    if (isFlexSupported()) {
      return;
    }
    // Just for IE9
    const domNode = findDOMNode(this);
    if (domNode.children.length > 0) {
      if (this.calcTimeout) {
        clearTimeout(this.calcTimeout);
      }
      this.calcTimeout = setTimeout(() => {
        // +1 for fit edge bug of digit width, like 35.4px
        const lastStepOffsetWidth = (domNode.lastChild.offsetWidth || 0) + 1;
        // Reduce shake bug
        if (this.state.lastStepOffsetWidth === lastStepOffsetWidth ||
          Math.abs(this.state.lastStepOffsetWidth - lastStepOffsetWidth) <= 3) {
          return;
        }
        this.setState({ lastStepOffsetWidth });
      });
    }
  }
  render() {
    const {
      prefixCls, style = {}, className, children, direction,
      labelPlacement, iconPrefix, status, size, current, progressDot, initial,
      icons,
      ...restProps,
    } = this.props;
    const { lastStepOffsetWidth, flexSupported } = this.state;
    const filteredChildren = React.Children.toArray(children).filter(c => !!c);
    const lastIndex = filteredChildren.length - 1;
    const adjustedlabelPlacement = !!progressDot ? 'vertical' : labelPlacement;
    const classString = classNames(prefixCls, `${prefixCls}-${direction}`, className, {
      [`${prefixCls}-${size}`]: size,
      [`${prefixCls}-label-${adjustedlabelPlacement}`]: direction === 'horizontal',
      [`${prefixCls}-dot`]: !!progressDot,
    });

    return (
      <div className={classString} style={style} {...restProps}>
        {
          Children.map(filteredChildren, (child, index) => {
            if (!child) {
              return null;
            }
            const stepNumber = initial + index;
            const childProps = {
              stepNumber: `${stepNumber + 1}`,
              prefixCls,
              iconPrefix,
              wrapperStyle: style,
              progressDot,
              icons,
              ...child.props,
            };
            if (!flexSupported && direction !== 'vertical' && index !== lastIndex) {
              childProps.itemWidth = `${100 / lastIndex}%`;
              childProps.adjustMarginRight = -Math.round(lastStepOffsetWidth / lastIndex + 1);
            }
            // fix tail color
            if (status === 'error' && index === current - 1) {
              childProps.className = `${prefixCls}-next-error`;
            }
            if (!child.props.status) {
              if (stepNumber === current) {
                childProps.status = status;
              } else if (stepNumber < current) {
                childProps.status = 'finish';
              } else {
                childProps.status = 'wait';
              }
            }
            return cloneElement(child, childProps);
          })
        }
      </div>
    );
  }
}

```

首先看到在componentDidMount, componentDidUpdate阶段都调用了calcStepOffsetWidth这个方法，这个方法其实就是计算lastStepOffsetWidth最后一个步骤条的偏移距离 用来调整子组件的间距到正好撑满容器的效果。

### calcStepOffsetWidth
在这个方法的开头，我们看到
```js
if (isFlexSupported()) {
   return;
}
```
如果浏览器支持flex，就直接return，因为flex本身就是弹性自适应布局，
```js
export function isFlexSupported() {
  if (typeof window !== 'undefined' && window.document && window.document.documentElement) {
    const { documentElement } = window.document;
    return 'flex' in documentElement.style ||
      'webkitFlex' in documentElement.style ||
      'Flex' in documentElement.style ||
      'msFlex' in documentElement.style;
  }
  return false;
}
```
如果不支持flex，
则先用React.findDomNode(this)拿到当前组件的dom节点，然后用了一个类似debouce的处理，利用setTimout在下一个事件循环里处理，并且保证一个事件循环里触发的多次此方法被归并成一次，
拿到children中lastChild的offsetWidth并且赋给state的lastStepOffsetWidth。

### render
filteredChildren是利用React.Children.toArray把子节点转成数组且过滤掉空节点，然后拿到lastIndex最后一项的序号，在最后的return中调用React.Children.map循环子节点数组，在这个循环中，stepNumber是props.initial + index，childProps在child原有的props基础上扩展了
stepNumber步骤序号和一系列样式，
```js
if (!flexSupported && direction !== 'vertical' && index !== lastIndex) {
      childProps.itemWidth = `${100 / lastIndex}%`;
      childProps.adjustMarginRight = -Math.round(lastStepOffsetWidth / lastIndex + 1);
}
```
在不支持flex的情况下继续扩展 
itemWidth为 100除以最后一项的下标
adjustMarginRight 是上面计算的lastStepOffsetWidth除以子元素数量并取负。

```js
// fix tail color
   if (status === 'error' && index === current - 1) {
  childProps.className = `${prefixCls}-next-error`;
}
```
status代表props中传入的当前步骤的状态，如果是错误并且这时候的step是当前步骤的前一个的话，加一个next-error的class

```js
          if (!child.props.status) {
              if (stepNumber === current) {
                childProps.status = status;
              } else if (stepNumber < current) {
                childProps.status = 'finish';
              } else {
                childProps.status = 'wait';
              }
            }
```
这段是假设用户不传入status的情况下自动计算当前应该的状态，
current之前是finished 之后是wait
```js
 return cloneElement(child, childProps);
```
最后调用React.cloneElement把child和childProps合并成一个新节点返回。



## Step.jsx
```js
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

function isString(str) {
  return typeof str === 'string';
}

export default class Step extends React.Component {
  static propTypes = {
    className: PropTypes.string,
    prefixCls: PropTypes.string,
    style: PropTypes.object,
    wrapperStyle: PropTypes.object,
    itemWidth: PropTypes.oneOfType([
      PropTypes.number,
      PropTypes.string,
    ]),
    status: PropTypes.string,
    iconPrefix: PropTypes.string,
    icon: PropTypes.node,
    adjustMarginRight: PropTypes.oneOfType([
      PropTypes.number,
      PropTypes.string,
    ]),
    stepNumber: PropTypes.string,
    description: PropTypes.any,
    title: PropTypes.any,
    progressDot: PropTypes.oneOfType([
      PropTypes.bool,
      PropTypes.func,
    ]),
    tailContent: PropTypes.any,
    icons: PropTypes.shape({
      finish: PropTypes.node,
      error: PropTypes.node,
    }),
  };
  renderIconNode() {
    const {
      prefixCls, progressDot, stepNumber, status, title, description, icon,
      iconPrefix, icons,
    } = this.props;
    let iconNode;
    const iconClassName = classNames(`${prefixCls}-icon`, `${iconPrefix}icon`, {
      [`${iconPrefix}icon-${icon}`]: icon && isString(icon),
      [`${iconPrefix}icon-check`]: !icon && status === 'finish' && (icons && !icons.finish),
      [`${iconPrefix}icon-close`]: !icon && status === 'error' && (icons && !icons.error),
    });
    const iconDot = <span className={`${prefixCls}-icon-dot`}></span>;
    // `progressDot` enjoy the highest priority
    if (progressDot) {
      if (typeof progressDot === 'function') {
        iconNode = (
          <span className={`${prefixCls}-icon`}>
            {progressDot(iconDot, { index: stepNumber - 1, status, title, description })}
          </span>
        );
      } else {
        iconNode = <span className={`${prefixCls}-icon`}>{iconDot}</span>;
      }
    } else if (icon && !isString(icon)) {
      iconNode = <span className={`${prefixCls}-icon`}>{icon}</span>;
    } else if (icons && icons.finish && status === 'finish') {
      iconNode = <span className={`${prefixCls}-icon`}>{icons.finish}</span>;
    } else if (icons && icons.error && status === 'error') {
      iconNode = <span className={`${prefixCls}-icon`}>{icons.error}</span>;
    } else if (icon || status === 'finish' || status === 'error') {
      iconNode = <span className={iconClassName} />;
    } else {
      iconNode = <span className={`${prefixCls}-icon`}>{stepNumber}</span>;
    }

    return iconNode;
  }
  render() {
    const {
      className, prefixCls, style, itemWidth,
      status = 'wait', iconPrefix, icon, wrapperStyle,
      adjustMarginRight, stepNumber,
      description, title, progressDot, tailContent,
      icons,
      ...restProps,
    } = this.props;

    const classString = classNames(
      `${prefixCls}-item`,
      `${prefixCls}-item-${status}`,
      className,
      { [`${prefixCls}-item-custom`]: icon },
    );
    const stepItemStyle = { ...style };
    if (itemWidth) {
      stepItemStyle.width = itemWidth;
    }
    if (adjustMarginRight) {
      stepItemStyle.marginRight = adjustMarginRight;
    }
    return (
      <div
        {...restProps}
        className={classString}
        style={stepItemStyle}
      >
        <div className={`${prefixCls}-item-tail`}>
          {tailContent}
        </div>
        <div className={`${prefixCls}-item-icon`}>
          {this.renderIconNode()}
        </div>
        <div className={`${prefixCls}-item-content`}>
          <div className={`${prefixCls}-item-title`}>
            {title}
          </div>
          {description && <div className={`${prefixCls}-item-description`}>{description}</div>}
        </div>
      </div>
    );
  }
}

```
子组件里就是根据父组件计算的一些props和本身的props计算出图标和状态进行渲染。