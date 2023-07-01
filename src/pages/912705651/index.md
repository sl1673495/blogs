---
title: '我的学习方法是每天看 10 个 NPM 模块？'
date: '2021-06-06'
spoiler: ''
---

最近看到阿里前端技术专家狼叔在 17 年的这篇[《迷茫时学习 Node.js 最好的方法》](https://zhuanlan.zhihu.com/p/29625882)提到：

> 今天小弟过来找我，说迷茫，我告诉他一个密法：一天看 10 个 npm 模块，坚持一年就是 3000+，按正常工作需要，超过 200 个都很厉害了。

第一次看到的时候感觉**有点鸡汤**，但静下心来仔细想想却不无道理，以 Vite 来举例子，我在看它代码的时候，印象很深的一个点就是各种开源模块信手拈来，恰到好处的解决了需求，这种能力是一定需要大量的开源模块阅读量的。

### Vite magic-string

比如 Vite 中大量运用 [magic-string](https://www.npmjs.com/package/magic-string) 这个库做一些字符串的魔术替换，这个库的目的就是在一些轻量级替换源代码的场景中替代 AST 这种过于庞大的解决方案。

```js
var MagicString = require('magic-string')
var s = new MagicString('problems = 99')

// 替换 problems -> answer
s.overwrite(0, 8, 'answer')
s.toString() // 'answer = 99'

// 生成 sourcemap
var map = s.generateMap({
  source: 'source.js',
  file: 'converted.js.map',
  includeContent: true
})
```

### Vite fast-glob

再比如用 [fast-glob](https://www.npmjs.com/package/fast-glob) 去实现 Vite 中好用的 [Glob Import](https://vitejs.dev/guide/features.html#glob-import) 批量导入语法

![](https://images.gitee.com/uploads/images/2021/0606/144742_9aba8489_1087321.png '屏幕截图.png')

好，现在我们知道有 `fast-glob` 这么好用的库了，顺带读一读文档看看它的用法，那么之后我们在自己的工作中，写诸如脚手架的工具时，就可以用这个库对外提供一些好用的批量导入 API，这就成为了我们自己知识体系中的一部分。

### Vite SSG

我最近一直比较关注的小哥 [Anthony Fu](https://antfu.me/)，最近刚参加完 2021 年的 VueConf 大会，带来了对日常开发非常实用的一场演讲。

![](https://images.gitee.com/uploads/images/2021/0606/145925_78b509ed_1087321.png '屏幕截图.png')

他最近在开源方面非常活跃，很大一部分精力投入在 Vite 相关的生态建设中，他开发的 [vite-ssg](https://github.com/antfu/vite-ssg) 插件支持把 Vite 项目构建为静态网站。

> SSG，全称是 Static-Site-Generators，静态站点生成器。在**构建时**就把你的 Web 应用构建为 HTML 格式，对 SEO 和性能都有非常显著的帮助。

他当然不是从零完成这么庞大的工作量，`@vue/server-renderer` 这个包本身是为 Vue 构建 SSR 应用
而生的，他巧妙利用这个库把 Vue 组件渲染为 HTML 字符串的能力，节省了非常多的工作量。

在他的博客中也有提到：

> The idea here is fairly simple: bundle the app entry, then for each route, dump the app using APIs from the `@vue/server-renderer` package. Simplified code here:

```js
import { renderToString } from '@vue/server-renderer'

const createApp = required('dist-ssr/app.js')

await Promise.all(
  routes.map(async (route) => {
    const { app, router, head } = createApp(false)

    router.push(route)
    await router.isReady()

    const appHTML = await renderToString(app)
    const renderedHTML = renderHTML(indexHTML, appHTML)

    await fs.writeFile(`${route}.html`, renderedHTML, 'utf-8')
  })
)
```

简化后的思路就是，在 SSR 的环境下启动应用后，对每个路由用 `@vue/server-renderer` 生成静态的 HTML 字符串，写入为 HTML 文件。

虽然代码看似简短，但这背后体现的是对 Vue3 生态的熟悉，更具体的说就是对 Vue3 发布的每个 npm 包所具有的能力的熟悉。

### 只是 npm 库吗？

当然不是，比如最近我们工作中的项目接入了微软开源的 [Rush](https://rushjs.io/pages/intro/welcome/)，Rush 是为 Monorepo 工程设计的一体化解决方案。

在我阅读文档的过程中，我就学习到了很多包管理方面的知识：

- [NPM vs PNPM vs Yarn](https://rushjs.io/pages/maintainer/package_managers/)
- [幽灵依赖(Phantom Dependencies)](https://rushjs.io/pages/advanced/phantom_deps/)
- [NPM 分身(NPM doppelgangers)](https://rushjs.io/pages/advanced/npm_doppelgangers/)

在阅读 Vue.js 文档的时候，[风格指南](https://v3.cn.vuejs.org/style-guide/) 部分也给我留下了很深的印象，开源作者大佬在多年代码生涯总结而成的实践指南，一定是有非常多的精华。比如：

> 组件名称应该以高阶的 (通常是一般化描述的) 单词开头，以描述性的修饰词结尾。

![](https://images.gitee.com/uploads/images/2021/0606/153906_7b8fcc63_1087321.png '屏幕截图.png')

当你在现实中的维护场景下，假设你在想：“我要给搜索按钮（SearchButton）的清除(Clear)功能换个图标”。

那么你在视线扫过这个文件夹的时候，关注点自然先集中到 `SearchButton` 这个部分，再去寻找后缀的 `Clear`、`Run` 描述性修饰词，点进 `Clear` 组件进行维护。这样组件关系就非常一目了然。

这些开源作者的心血经常在文档中不起眼的部分静静等候你去发现。

### 工作太忙？

其实很多人第一反应可能是：“一天看 10 个，我工作都那么忙了，哪有空啊？”

关于这点，狼叔也在原文中提到了：

> 这里的 10 个其实只是个虚数，看个人能力和决心，量力而行即可。
>
> 但请一定要能做到每日精进。
>
> Node.js 模块在 npm 上的统计数据表明，截止到今天 2017 年 9 月 24 日，共有 55.9 万个模块。单日下载在 1.5 亿次。这么大规模的模块，每天学几个，水平一定会增长的非常快的。
>
> 最难的不是下决心，而是坚持！这是最值得自豪的称赞，没有之一！

比如 VueConf 大会里提到了某些新的技术，比如你的同事在聊天的时候提到了一些让你感兴趣的库，你都可以去搜索看看，或许在将来工作中的某天就会不经意的帮助到你。

## 总结

不积硅步，无以至千里。保持好奇心、热情和耐心，不要对任何东西都不求甚解，当然也不要对某些地方太钻牛角尖。

“每天 10 个 NPM 模块” 更像是一种激励，可能中间我们会断掉两三天，甚至几周都提不起精神，但只要在心里保持这个新年，期待一年、三年、五年以后不一样的我们。
