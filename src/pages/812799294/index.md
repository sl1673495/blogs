---
title: '浅谈 Vite 2.0 原理，依赖预编译，插件机制是如何兼容 Rollup 的？'
date: '2021-02-21'
spoiler: ''
---

![Vite](https://images.gitee.com/uploads/images/2021/0217/222137_7c85515f_1087321.png '屏幕截图.png')

前几天，尤雨溪在各个社交平台宣布 Vite 2.0 发布了。

看得出他对 Vite 倾注了很多感情，甚至都冷落了 Vue3，停更了两个多月。

![Vue3](https://images.gitee.com/uploads/images/2021/0218/200622_06d60673_1087321.png '屏幕截图.png')

相关的中文公告已经有翻译了，可以在[尤雨溪的知乎文章：Vite 2.0 发布了](https://zhuanlan.zhihu.com/p/351147547)中查看。

这篇文章来谈谈 Vite 2.0 的发布中，几个让我比较感兴趣的技术点。

## Vite 原理

为什么会出现 Vite？在过去的 Webpack、Rollup 等构建工具的时代，我们所写的代码一般都是基于 ES Module 规范，在文件之间通过 `import` 和 `export` 形成一个很大的依赖图。

这些构建工具在本地开发调试的时候，也都会**提前把你的模块**先打包成浏览器可读取的 js bundle，虽然有诸如路由懒加载等优化手段，但懒加载并不代表懒构建，Webpack 还是需要把你的异步路由用到的模块提前构建好。

当你的项目越来越大的时候，启动也难免变的越来越慢，甚至可能达到分钟级别。而 `HMR` 热更新也会达到好几秒的耗时。

Vite 则别出心裁的利用了[浏览器的原生 ES Module 支持](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)，直接在 html 文件里写诸如这样的代码：

```html
// index.html
<div id="app"></div>
<script type="module">
  import { createApp } from 'vue'
  import Main from './Main.vue'

  createApp(Main).mount('#app')
</script>
```

Vite 会在本地帮你启动一个服务器，当浏览器读取到这个 html 文件之后，会在执行到 import 的时候才去向服务端发送 `Main.vue` 模块的请求，Vite 此时在利用内部的一系列黑魔法，包括 Vue 的 template 解析，代码的编译等等，解析成浏览器可以执行的 js 文件返回到浏览器端。

这就保证了只有在真正使用到这个模块的时候，浏览器才会请求并且解析这个模块，最大程度的做到了按需加载。

用 Vite 官网上的图来解释，传统的 bundle 模式是这样的：

![传统 bundle](https://images.gitee.com/uploads/images/2021/0221/134955_717f9a0a_1087321.png '屏幕截图.png')

而基于 ESM 的构建模式则是这样的：

![基于 ESM](https://images.gitee.com/uploads/images/2021/0221/135014_e69e1022_1087321.png '屏幕截图.png')

灰色部分是暂时没有用到的路由，甚至完全不会参与构建过程，随着项目里的路由越来越多，构建速度也不会变慢。

## 依赖预编译

依赖预编译，其实是 Vite 2.0 在为用户启动开发服务器之前，先用 `esbuild` 把检测到的依赖预先构建了一遍。

也许你会疑惑，不是一直说好的 no-bundle 吗，怎么还是走启动时编译这条路线了？尤老师这么做当然是有理由的，我们先以导入 `lodash-es` 这个包为例。

当你用 `import { debounce } from 'lodash'` 导入一个命名函数的时候，可能你理想中的场景就是浏览器去下载只包含这个函数的文件。但其实没那么理想，`debounce` 函数的模块内部又依赖了很多其他函数，形成了一个依赖图。

当浏览器请求 `debounce` 的模块时，又会发现内部有 2 个 `import`，再这样延伸下去，这个函数内部竟然带来了 600 次请求，耗时会在 1s 左右。

![lodash 请求依赖链路](https://images.gitee.com/uploads/images/2021/0221/155744_89195130_1087321.png '屏幕截图.png')

这当然是不可接受的，于是尤老师想了个折中的办法，正好利用 [Esbuild](https://github.com/evanw/esbuild) 接近无敌的构建速度，让你在没有感知的情况下在启动的时候预先帮你把 `debounce` 所用到的所有内部模块全部打包成一个传统的 `js bundle`。

`Esbuild` 使用 Go 编写，并且比以 JavaScript 编写的打包器预构建依赖快 10-100 倍。

![Esbuild 的速度](https://images.gitee.com/uploads/images/2021/0221/125137_cee193c2_1087321.png '屏幕截图.png')

在 `httpServer.listen` 启动开发服务器之前，会先把这个函数劫持改写，放入依赖预构建的前置步骤，[Vite 启动服务器相关代码](https://github.com/vitejs/vite/blob/main/packages/vite/src/node/server/index.ts)。

```ts
// server/index.ts
const listen = httpServer.listen.bind(httpServer)
httpServer.listen = (async (port: number, ...args: any[]) => {
  try {
    await container.buildStart({})
    // 这里会进行依赖的预构建
    await runOptimize()
  } catch (e) {
    httpServer.emit('error', e)
    return
  }
  return listen(port, ...args)
}) as any
```

而 `runOptimize` 相关的代码则在 [Github optimizer](https://github.com/vitejs/vite/blob/main/packages/vite/src/node/optimizer/index.ts) 中。

首先会根据本次运行的入口，来扫描其中的依赖：

```ts
let deps: Record<string, string>, missing: Record<string, string>
if (!newDeps) {
  ;({ deps, missing } = await scanImports(config))
}
```

`scanImports` 其实就是利用 `Esbuild` 构建时提供的钩子去扫描文件中的依赖，收集到 `deps` 变量里，在扫描到入口文件（比如 `index.html`）中依赖的模块后，形成类似这样的依赖路径数据结构：

```js
{
  "lodash-es": "node_modules/lodash-es"
}
```

之后再根据分析出来的依赖，使用 `Esbuild` 把它们提前打包成单文件的 bundle。

```ts
const esbuildService = await ensureService()
await esbuildService.build({
  entryPoints: Object.keys(flatIdDeps),
  bundle: true,
  format: 'esm',
  external: config.optimizeDeps?.exclude,
  logLevel: 'error',
  splitting: true,
  sourcemap: true,
  outdir: cacheDir,
  treeShaking: 'ignore-annotations',
  metafile: esbuildMetaPath,
  define,
  plugins: [esbuildDepPlugin(flatIdDeps, flatIdToExports, config)]
})
```

在浏览器请求相关模块时，返回这个预构建好的模块。这样，当浏览器请求 `lodash-es` 中的 `debounce` 模块的时候，就可以保证只发生一次接口请求了。

你可以理解为，这一步和 `Webpack` 所做的构建一样，只不过速度快了几十倍。

在预构建这个步骤中，还会对 `CommonJS` 模块进行分析，方便后面需要统一处理成浏览器可以执行的 `ES Module`。

## 插件机制

很多同学提到 Vite，第一反应就是生态不够成熟，其他构建工具有那么多的第三方插件，提供了各种各样开箱即用的便捷功能，Vite 需要多久才能赶上呢？

Vite 从 preact 的 WMR 中得到了启发，把插件机制做成**兼容 Rollup** 的格式。

于是便有了这个**相亲相爱**的 LOGO：

![Vite Rollup Plugins](https://images.gitee.com/uploads/images/2021/0221/151024_0f3cd350_1087321.png '屏幕截图.png')

目前和 vite 兼容或者内置的插件，可以查看[vite-rollup-plugins](https://vite-rollup-plugins.patak.dev/)。

简单的介绍一下 Rollup 插件，其实插件这个东西，就是 Rollup 对外提供一些时机的钩子，还有一些工具方法，让用户去写一些配置代码，以此介入 Rollup 运行的各个时机之中。

比如在打包之前注入某些东西，或者改变某些产物结构，仅此而已。

而 Vite 需要做的就是基于 Rollup 设计的接口进行扩展，在保证 Rollup 插件兼容的可能性的同时，再加入一些 Vite 特有的钩子和属性来扩展。

举个简单的例子，[@rollup/plugin-image](https://github.com/rollup/plugins/blob/master/packages/image/src/index.js) 可以把图片模块解析成 base64 格式，它的源码其实很简单：

```ts
export default function image(opts = {}) {
  const options = Object.assign({}, defaults, opts)
  const filter = createFilter(options.include, options.exclude)

  return {
    name: 'image',

    load(id) {
      if (!filter(id)) {
        return null
      }

      const mime = mimeTypes[extname(id)]
      if (!mime) {
        // not an image
        return null
      }

      const isSvg = mime === mimeTypes['.svg']
      const format = isSvg ? 'utf-8' : 'base64'
      const source = readFileSync(id, format).replace(/[\r\n]+/gm, '')
      const dataUri = getDataUri({ format, isSvg, mime, source })
      const code = options.dom
        ? domTemplate({ dataUri })
        : constTemplate({ dataUri })

      return code.trim()
    }
  }
}
```

其实就是在 `load` 这个钩子，读取模块时，把图片转换成相应格式的 `data-uri`，所以 Vite 只需要在读取模块的时候，也去兼容执行相关的钩子即可。

虽然 Vite 很多行为和 Rollup 构建不同，但他们内部有很多相似的行为和时机，只要确保 Rollup 插件只使用了这些共有的钩子，就很容易做到插件的通用。

可以参考 [Vite 官网文档 —— 插件部分](https://cn.vitejs.dev/guide/api-plugin.html#rollup-%E6%8F%92%E4%BB%B6%E5%85%BC%E5%AE%B9%E6%80%A7)

> 一般来说，只要一个 Rollup 插件符合以下标准，那么它应该只是作为一个 Vite 插件:
>
> - 没有使用 moduleParsed 钩子。
> - 它在打包钩子和输出钩子之间没有很强的耦合。
> - 如果一个 Rollup 插件只在构建阶段有意义，则在 build.rollupOptions.plugins 下指定即可。

Vite 后面的目标应该也是尽可能和 Rollup 相关的插件生态打通，社区也会一起贡献力量，希望 Vite 的生态越来越好。

## 比较

和 Vite 同时期出现的现代化构建工具还有：

- [Snowpack - The faster frontend build tool](https://www.snowpack.dev/)
- [preactjs/wmr: 👩‍🚀 The tiny all-in-one development tool for modern web apps.](https://github.com/preactjs/wmr)
- [Web Dev Server: Modern Web](https://modern-web.dev/docs/dev-server/overview/)

### Snowpack

Snowpack 和 Vite 比较相似，也是基于 ESM 来实现开发环境模块加载，但是它的构建时却是交给用户自己选择，整体的打包体验显得有点支离破碎。

而 Vite 直接整合了 Rollup，为用户提供了完善、开箱即用的解决方案，并且由于这些集成，也方便扩展更多的高级功能。

### WMR

WMR 则是为 Preact 而生的，如果你在使用 Preact，可以优先考虑使用这个工具。

### @web/dev-server

这个工具并未提供开箱即用的框架支持，也需要手动设置 Rollup 构建配置，不过这个项目里包含的很多工具也可以让 Vite 用户受益。

更具体的比较可以参考[Vite 文档 —— 比较](https://cn.vitejs.dev/guide/comparisons.html)

## 总结

Vite 是一个充满魔力的现代化构建工具，尤老师也在各个平台放下狠话，说要替代 Webpack。其实 Webpack 在上个世代也是一个贡献很大的构建工具，只是由于新特性的出现，有了可以解决它的诟病的解决方案。

目前我个人觉得，一些轻型的项目（不需要一些特别奇怪的依赖构建）完全可以开始尝试 Vite，比如：

- 各种框架、库中的展示 demo 项目。
- 轻量级的一些企业项目。

也衷心祝福 Vite 的生态越来越好，共同迎接这个构建的新世代。

不过到那个时候，我可能还会挺怀念从前 Webpack 怀念构建的时候，那几分钟一本正经的摸鱼时刻 😆。

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![image](https://user-images.githubusercontent.com/23615778/108619258-76929d80-745e-11eb-90bf-023abec85d80.png)

