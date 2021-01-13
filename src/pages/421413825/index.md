---
title: 'babel7的配置与优化。'
date: '2019-03-15'
spoiler: ''
---

网上关于babel7的文章很多，但是大多都没有实践，很多讲的模棱两可。
本文将手把手的带你看各种配置下的输入输出转换，彻底让你了解babel7到底该怎么去配置和优化。

首先我们知道进入了babel7的时代，stage-0这种已经作为不推荐使用的present了，最流行的应该是@babel/present-env 顾名思义让babel拥有根据你的环境来编译不同代码的需求。

## targets
我们先配置最基础的.babelrc配置
```js
{
  "presets": [
    [
      "@babel/preset-env",
      {
        "targets": {
          "chrome": "58",
          "ie": "10"
        }
      },
    ]
  ],
}
```

targets配置的意思就是让babel根据你写入的兼容平台来做代码转换，这里我们指定ie10为我们要兼容的最低版本，来看下面es6代码的输出。

#### 输入： src/main.js
```js
const a = () => {}
```

#### 输出： dist/main.js
```js
var a = function a() {};
```
这里因为ie10是不支持es6语法的，所以代码被全部转换，如果我们把ie10这条去掉，因为高版本的chrome是支持es6大部分语法的，所以代码就不会被做任何转换了。

[browserlist](https://github.com/browserslist/browserslist) 这里是具体的可配置列表，可以根据你自己项目的兼容性要求来配置。

## useBuiltIns
首先我们来看一行简单的代码
```js
a.includes(1);
```
includes作为数组的实例方法，在某些浏览器其实是不支持的，babel默认的转换对于这种场景并不会做处理，同样不会处理的包括WeakMap, WeakSet, Promise等es6新引入的类，所以我们需要[babel-polyfill](https://babeljs.io/docs/en/6.26.3/babel-polyfill)为我们这些实例方法等等打上补丁。

在很多项目中我们会看到项目的main.js入口顶部require了babel-polyfill包， 或者指定webpack的entry为数组，第一项引入babel-polyfill包，这样的确没问题而且很保险，但是很多场景下我们可能只是使用了少量需要polyfill的api，这个时候全量引入这个包就显得很不划算，babel给我们提供了很好的解决方案，那就是useBuiltIns 这个配置，下面来看实例。

```js
{
  "presets": [
    [
      "@babel/preset-env",
      {
        "useBuiltIns": "usage",
        "targets": {
          "chrome": "58",
          "ie": "10"
        }
      },
    ]
  ],
}
```

#### 输入： src/main.js
```js
a.includes(1)
Promise.reject()
```

#### 输出： dist/main.js
```js
require("core-js/modules/es6.promise");

require("core-js/modules/es7.array.includes");

require("core-js/modules/es6.string.includes");

a.includes(1);
Promise.reject();
```

babel帮我们做好了代码分析，在需要用到polyfill的地方再帮你引入这个单独的补丁，这样就实现了按需引入~

## @babel/plugin-transform-runtime
这个插件是帮我们把一些babel的辅助方法由直接写入代码专为按需引入模块的方式引用，
我们先来看不使用这个插件时候，我们对于es6 class的转换。

#### 输入： src/main.js
```js
class A {}
```

#### 输出： dist/main.js
```js
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var A = function A() {
  _classCallCheck(this, A);
};
```

看似没问题，转换的很好，但是如果在很多模块都用了class语法的情况下呢？辅助函数_classCallCheck就会被重复写入多次，占用无意义的空间。
解决方法就是引入@babel/plugin-transform-runtime
.babelrc
```js
{
  "presets": [
    [
      "@babel/preset-env",
      {
        "useBuiltIns": "usage",
        "targets": {
          "chrome": "58",
          "ie": "10"
        }
      },
    ]
  ],
  "plugins": [
    "@babel/plugin-transform-runtime",
  ]
}
```

#### 输入： src/main.js
```js
class A {}
```

#### 输出： dist/main.js
```js
var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault");
var _classCallCheck2 = _interopRequireDefault(require("@babel/runtime/helpers/classCallCheck"));

var A = function A() {
  (0, _classCallCheck2.default)(this, A);
};
```
这样就解决了辅助函数重复写入的问题了。



## 总结
babel7的版本下，利用present-env做按需转换，利用useBuiltIn做babel-polyfill的按需引入，利用transform-runtime做babel辅助函数的按需引入。