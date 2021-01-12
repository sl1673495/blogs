---
title: 'react-dev-inspector 原理解析，点击页面组件自动打开 VSCode 对应文件？'
date: '2020-11-26'
spoiler: ''
---

## 前言

在大型项目开发中，经常会遇到这样一个场景，QA 丢给你一个出问题的链接，但是你完全不知道这个页面 & 组件对应的文件位置。

这时候如果可以**点击页面上的组件，在 VSCode 中自动跳转到对应文件，并定位到对应行号**岂不美哉？

[react-dev-inspector](https://github.com/zthxxx/react-dev-inspector) 就是应此需求而生。

使用非常简单方便，看完这张动图你就秒懂：

![preview](https://user-images.githubusercontent.com/23615778/101280479-42ff8a00-3804-11eb-8b7d-15986e2b44fb.gif)

可以在 [预览网站](https://react-dev-inspector.zthxxx.me/) 体验一下。

## 使用方式

简单来说就是三步：

1. **构建时**：
   - 需要加一个 `webpack loader` 去遍历编译前的的 `AST` 节点，在 DOM 节点上加上文件路径、名称等相关的信息 。
   - 需要用 `DefinePlugin` 注入一下项目运行时的根路径，后续要用来拼接文件路径，打开 VSCode 相应的文件。
2. **运行时**：需要在 React 组件的最外层包裹 `Inspector` 组件，用于在浏览器端监听快捷键，弹出 debug 的遮罩层，在点击遮罩层的时候，利用 `fetch` 向本机服务发送一个打开 VSCode 的请求。
3. **本地服务**：需要启动 `react-dev-utils` 里的一个中间件，监听一个特定的路径，在本机服务端执行打开 VSCode 的指令。

下面简单分析一下这几步到底做了什么。

## 原理简化

### 构建时

首先如果在浏览器端想知道这个组件属于哪个文件，那么不可避免的要在构建时就去遍历代码文件，根据代码的结构解析生成 AST，然后在每个组件的 DOM 元素上挂上当前组件的对应文件位置和行号，所以在开发环境最终生成的 DOM 元素是这样的：

```html
<div
  data-inspector-line="11"
  data-inspector-column="4"
  data-inspector-relative-path="src/components/Slogan/Slogan.tsx"
  class="css-1f15bld-Description e1vquvfb0"
>
  <p
    data-inspector-line="44"
    data-inspector-column="10"
    data-inspector-relative-path="src/layouts/index.tsx"
  >
    Inspect react components and click will jump to local IDE to view component
    code.
  </p>
</div>
;
```

这样就可以在输入快捷键的时候，开启 debug 模式，让 DOM 在 hover 的时候增加一个遮罩层并展示组件对应的信息：
![image](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/eb5825a6e5f14077b99ba5124d89e532~tplv-k3u1fbpfcp-zoom-1.image)

这一步通过 `webpack loader` 拿到**未编译**的 `JSX` 源码，再配合 `AST` 的处理就可以完成。

### 运行时

既然需要在浏览器端增加 hover 事件，添加遮罩框元素，那么肯定不可避免的要侵入运行时的代码，这里通过在整个应用的最外层包裹一个 `Inspector` 来尽可能的减少入侵。

```jsx
import React from 'react'
import { Inspector } from 'react-dev-inspector'

const InspectorWrapper = process.env.NODE_ENV === 'development'
  ? Inspector
  : React.Fragment

export const Layout = () => {
  // ...

  return (
    <InspectorWrapper
      keys={['control', 'shift', 'command', 'c']} // default keys
      ...  // Props see below
    >
     <Page />
    </InspectorWrapper>
  )
}
```

这里也可以自定义你喜欢的快捷键，用来开启 debug 模式。

开启了 debug 模式之后，鼠标 hover 到你想要调试的组件，就会展现出遮罩框，再点击一下，就会自动在 VSCode 中打开对应的组件文件，并且跳转到对应的行和列。

那么关键在于，这个跳转其实是借助 fetch **发送了一个请求到本机的服务端**，利用**服务端执行脚本命令**如 `code src/Inspector/index.ts` 这样的命令来打开 VSCode，这就要借助我说的第三步，启动本地服务并引入中间件了。

### 本地服务

还记得 `create-react-app` 或者 `vue-cli` 启动的前端项目，在错误时会弹出一个全局的遮罩和对应的堆栈信息，点击以后就会跳转到 VSCode 对应的文件么？没错，`react-dev-inspector` 也正是直接借助了 `create-react-app` 底层的工具包 `react-dev-utils` 去实现。（没错 `create-react-app` 创建的项目自带这个服务，不需要手动加载这一步了）

`react-dev-utils` 为这个功能封装了一个中间件： [errorOverlayMiddleware](https://github.com/facebook/create-react-app/blob/master/packages/react-dev-utils/errorOverlayMiddleware.js)

其实代码也很简单，就是监听了一个特殊的 URL：

```js
// launchEditorEndpoint.js
module.exports = "/__open-stack-frame-in-editor";
```

```js
// errorOverlayMiddleware.js
const launchEditor = require("./launchEditor");
const launchEditorEndpoint = require("./launchEditorEndpoint");

module.exports = function createLaunchEditorMiddleware() {
  return function launchEditorMiddleware(req, res, next) {
    if (req.url.startsWith(launchEditorEndpoint)) {
      const lineNumber = parseInt(req.query.lineNumber, 10) || 1;
      const colNumber = parseInt(req.query.colNumber, 10) || 1;
      launchEditor(req.query.fileName, lineNumber, colNumber);
      res.end();
    } else {
      next();
    }
  };
};
```

`launchEditor` 这个核心的打开编辑器的方法我们一会再详细分析，现在可以先略过，只要知道我们需要开启这个服务即可。

这是一个为 `express` 设计的中间件，webpack 的 `devServer` 选项中提供的 `before` 也可以轻松接入这个中间件，如果你的项目不用 `express`，那么你只要参考这个中间件去重写一个即可，只需要监听接口拿到文件相关的信息，调用核心方法 `launchEditor` 即可。

只要保证这几个步骤的完成，那么这个插件就接入成功了，可以通过在浏览器的控制台执行 `fetch('/__open-stack-frame-in-editor?fileName=/Users/admin/app/src/Title.tsx')` 来测试 `react-dev-utils`的服务是否开启成功。

### 注入绝对路径
注意上一步的请求中 `fileName=` 后面的前缀是绝对路径，而 DOM 节点上只会保存形如 `src/Title.tsx` 这样的相对路径，源码中会在点击遮罩层的时候去取 `process.env.PWD` 这个变量，和组件上的相对路径拼接后得到完整路径，这样 VSCode 才能顺利打开。

这需要借助 `DefinePlugin` 把启动所在路径写入到浏览器环境中：

```js
new DefinePlugin({
  "process.env.PWD": JSON.stringfy(process.env.PWD),
});
```

至此，整套插件集成完毕，简化版的原理解析就结束了。

## 源码重点

看完上面的简化原理解析后，其实大家也差不多能写出一个类似的插件了，只是实现的细节可能不太相同。这里就不一一解析完整的源码了，来看一下源码中比较值得关注的一些细节。

### 如何在元素上埋点

在浏览器端能找到节点在 VSCode 里的对应的路径，关键就在于编译时的埋点，`webpack loader` 接受代码字符串，返回你处理过后的字符串，用作在元素上增加新属性再合适不过，我们只需要利用 `babel` 中的整套 AST 能力即可做到：

```js
export default function inspectorLoader(
  this: webpack.loader.LoaderContext,
  source: string
) {
  const { rootContext: rootPath, resourcePath: filePath } = this;

  const ast: Node = parse(source);

  traverse(ast, {
    enter(path: NodePath<Node>) {
      if (path.type === "JSXOpeningElement") {
        doJSXOpeningElement(path.node as JSXOpeningElement, { relativePath });
      }
    },
  });

  const { code } = generate(ast);

  return code
}
```

这是简化后的代码，标准的 `parse -> traverse -> generate` 流程，在遍历的过程中对 `JSXOpeningElement`这种节点类型做处理，把文件相关的信息放到节点上即可：

```js
const doJSXOpeningElement: NodeHandler<
  JSXOpeningElement,
  { relativePath: string }
> = (node, option) => {
  const { stop } = doJSXPathName(node.name)
  if (stop) return { stop }

  const { relativePath } = option

  // 写入行号
  const lineAttr = jsxAttribute(
    jsxIdentifier('data-inspector-line'),
    stringLiteral(node.loc.start.line.toString()),
  )

  // 写入列号
  const columnAttr = jsxAttribute(
    jsxIdentifier('data-inspector-column'),
    stringLiteral(node.loc.start.column.toString()),
  )

  // 写入组件所在的相对路径
  const relativePathAttr = jsxAttribute(
    jsxIdentifier('data-inspector-relative-path'),
    stringLiteral(relativePath),
  )

  // 在元素上增加这几个属性
  node.attributes.push(lineAttr, columnAttr, relativePathAttr)

  return { result: node }
}
```
### 获取组件名称

在运行时鼠标 hover 在 DOM 节点上，这个时候拿到的只是 DOM 元素，如何获取组件的名称？其实 React 内部会在 DOM 上反向的挂上它所对应的 `fiber node` 的引用，这个引用在 DOM 元素上以 `__reactInternalInstance` 开头命名，可以这样拿到：

```js
/**
 * https://stackoverflow.com/questions/29321742/react-getting-a-component-from-a-dom-element-for-debugging
 */
export const getElementFiber = (element: HTMLElement): Fiber | null => {
  const fiberKey = Object.keys(element).find(
    key => key.startsWith('__reactInternalInstance$'),
  )

  if (fiberKey) {
    return element[fiberKey] as Fiber
  }

  return null
}
```

由于拿到的 `fiber`可能对应一个普通的 DOM 元素比如 `div` ，而不是对应一个组件 `fiber`，我们肯定期望的是向上查找最近的**组件节点**后展示它的名字（这里使用的是 `displayName` 或者 `name` 属性），由于 `fiber` 是链表结构，可以通过**向上**递归查找 `return` 这个属性，直到找到第一个符合期望的节点。

这里递归查找 `fiber` 的 `return`，就类似于在 DOM 节点中递归向上查找 `parentNode` 属性，不停的向父节点递归查找。

```js
// 这里用正则屏蔽了一些组件名 如果匹配成功则会忽略掉这一层 fiber 继续向上查找
export const debugToolNameRegex = /^(.*?\.Provider|.*?\.Consumer|Anonymous|Trigger|Tooltip|_.*|[a-z].*)$/;

export const getSuitableFiber = (baseFiber?: Fiber): Fiber | null => {
  let fiber = baseFiber
  
  while (fiber) {
    // while 循环向上递归查找 displayName 符合的组件
    const name = fiber.type?.displayName ?? fiber.type?.name
    if (name && !debugToolNameRegex.test(name)) {
      return fiber
    }
	// 找不到的话 就继续找 return 节点
    fiber = fiber.return
  }

  return null
}
```

`fiber` 上的属性 `type` 在函数式组件的情况下对应你书写的函数，在 `class` 组件的情况下就对应那个类，取上面的的 `displayName` 或 `name` 属性即可：

```js
export const getFiberName = (fiber?: Fiber): string | undefined => {
  const fiberType = getSuitableFiber(fiber)?.type
  let displayName: string | undefined

  // The displayName property is not guaranteed to be a string.
  // It's only safe to use for our purposes if it's a string.
  // github.com/facebook/react-devtools/issues/803
  //
  // https://github.com/facebook/react/blob/v17.0.0/packages/react-devtools-shared/src/utils.js#L90-L112
  if (typeof fiberType?.displayName === 'string') {
    displayName = fiberType.displayName
  } else if (typeof fiberType?.name === 'string') {
    displayName = fiberType.name
  }

  return displayName
}
```

![image](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/eb5825a6e5f14077b99ba5124d89e532~tplv-k3u1fbpfcp-zoom-1.image)

### 服务端跳转 VSCode 原理

虽然简单来说，`react-dev-utils` 其实就是开了个接口，当你 fetch 的时候帮你执行 `code filepath` 指令，但是它底层其实是很巧妙的实现了多种编辑器的兼容的。

如何“猜”出用户在用哪个编辑器？它其实实现定义好了一组进程名对应开启指令的映射表：

```js
const COMMON_EDITORS_OSX = {
  '/Applications/Atom.app/Contents/MacOS/Atom': 'atom',
  '/Applications/Visual Studio Code.app/Contents/MacOS/Electron': 'code',
  ...
}
```

然后在 `macOS` 和 `Linux` 下，通过执行 `ps x` 命令去列出进程名，通过进程名再去映射对应的打开编辑器的指令。比如你的进程里有 `/Applications/Visual Studio Code.app/Contents/MacOS/Electron`，那说明你用的是 `VSCode`，就获取了 `code` 这个指令。

之后调用 `child_process` 模块去执行命令即可：

```js
child_process.spawn("code", pathInfo, { stdio: "inherit" });
```

[launchEditor 源码地址](https://github.com/facebook/create-react-app/blob/master/packages/react-dev-utils/launchEditor.js)

## 详细接入教程

构建时只需要对 webpack 配置做点改动，加入一个全局变量，引入一个 loader 即可。
```js
const { DefinePlugin } = require('webpack');

{
  module: {
    rules: [
      {
        test: /\.(jsx|js)$/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              presets: ['es2015', 'react'],
            },
          },
          // 注意这个 loader babel 编译之前执行
          {
            loader: 'react-dev-inspector/plugins/webpack/inspector-loader',
            options: { exclude: [resolve(__dirname, '想要排除的目录')] },
          },
        ],
      }
    ],
  },
  plugins: [
    new DefinePlugin({
      'process.env.PWD': JSON.stringify(process.env.PWD),
    }),
  ]
}
```

如果你的项目是自己搭建而非 `cra` 搭建的，那么有可能你的项目中没有开启 `errorOverlayMiddleware` 中间件提供的服务，你可以在 webpack 的 `devServer` 中开启：

```js
import createErrorOverlayMiddleware from 'react-dev-utils/errorOverlayMiddleware'

{
  devServer: {
    before(app) {
      app.use(createErrorOverlayMiddleware())
    }
  }
}
```

此外需要保证你的命令行本身就可以通过 `code` 命令打开 VSCode 编辑器，如果没有配置这个，可以参考以下步骤：

1、首先打开 VSCode。

2、使用 `command + shift + p` (注意 window 下使用 `ctrl + shift + p`) 然后搜索 `code`，选择 `install 'code' command in path`。  

最后，在 React 项目的最外层接入：

```jsx
import React from 'react'
import { Inspector } from 'react-dev-inspector'

const InspectorWrapper = process.env.NODE_ENV === 'development'
  ? Inspector
  : React.Fragment

export const Layout = () => {
  // ...

  return (
    <InspectorWrapper
      keys={['control', 'shift', 'command', 'c']} // default keys
      ...  // Props see below
    >
     <Page />
    </InspectorWrapper>
  )
}
```

## 总结

在大项目的开发和维护过程中，拥有这样一个调试神器真的特别重要，再好的记忆力也没法应对日益膨胀的组件数量…… 接入了这个插件后，指哪个组件跳哪个组件，大大节省了我们的时间。

在解读这个插件的源码过程中也能看出来，想要做一些对项目整体提效的事情，经常需要我们全面的了解运行时、构建时、Node 端的很多知识，学无止境。
