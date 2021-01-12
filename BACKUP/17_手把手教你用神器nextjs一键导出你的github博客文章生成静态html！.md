---
title: '手把手教你用神器nextjs一键导出你的github博客文章生成静态html！'
date: '2019-09-18'
spoiler: ''
---

相信有不少小伙伴和我一样用github issues记录自己的blog，但是久而久之也发现了一些小问题，比如
- 国内访问速度比较慢
- 不能自定义主题样式等等
- 不能在博客中加入自己想要的功能

正好最近又在学nextjs，react做ssr的神器，nextjs提供了`next export`这个命令，如果不熟悉next小伙伴可以先去官网阅读一下  
https://nextjs.org/docs#static-html-export

nextjs的教程，推荐一下技术胖的免费视频教程  
http://jspang.com/posts/2019/09/01/react-nextjs.html#p02%EF%BC%9Acreact-next-app%E5%BF%AB%E9%80%9F%E5%88%9B%E5%BB%BAnext-js%E9%A1%B9%E7%9B%AE

这个命令可以把react项目导出成静态html页面，这样在性能和seo方面考虑都是最优解。配合这个命令我就有了个折腾的想法，能不能把github issues导入到项目里，然后配合这个命令生成我的静态html博客呢。

## 目标
配合nextjs实现一个命令把自己的github issues里的文章导出成自己的博客html页面。
这样的好处是
- 可以折腾
- 可以折腾
- 可以折腾

开玩笑的，真正的好处是
- 编写博客时可以利用github完善的编辑器。
- 可以把github issues作为自己的数据存储服务，不用担心数据丢失和维护。
- 可以在自己的博客内加入自己想要的任何功能。
- 可以利用react的完整能力，完善的第三方生态。
- 生成的博客是html格式的页面，回归原始，回归本心，seo和性能最优化。

## 尝鲜使用
### 项目地址
https://github.com/sl1673495/next-blog 先clone到本地。

### 运行
安装依赖：
```
yarn
```
开发环境：
```
yarn dev
```
导出博客(会放在out目录下，导出后请进入out目录后启动anywhere或者http-server类似的静态服务然后访问)：
```
yarn all
```

### 说明
只需要在config.js里改掉repo的owner和name两个字段，  
分别对应你的github用户名和博客仓库名，  
然后执行`yarn all`，  
就可以在out目录下生成静态博客目录。
config中填写client_id和client_secret可以用于取消请求限制。

### （可选）使用[now](https://zeit.co/home)部署
进入out目录，然后执行`now`，页面就会自动部署了。


## 预览地址
对应的github博客: https://github.com/sl1673495/blogs/issues 

自动生成的博客  http://blog.shanshihao.cn  

可以先访问一下生成博客的效果，可以看到静态html页面的速度是非常快的，体验在某些方面可以说比起spa和ssr都要好。  

## 代码解析
想要实现上面所说的功能，需要先把功能拆解一下。

1. 发起请求拉取自己github仓库里的博客，获取文章存成md格式在本地。
2. 根据nextjs的约定，把生成的md文章改写成jsx，写入到pages目录下。（这样nextjs就会识别成为一个个路由）
3. 根据自定的规则生成首页jsx，写入pages文件夹。
4. 使用next export导出博客。

首先先用next脚手架生成一个项目，然后在项目下建立builder文件夹，用来编写逻辑。

### 全局配置
全局的一些配置我放在了config.js中，拉取我项目的小伙伴只需要更改里面的配置，就可以一键生成你自己的静态博客了。
```js
const path = require('path')

const mdDir = path.resolve(__dirname, './md')

module.exports = {
  mdDir,
  // 用于更改标题上的用户信息
  user: {
    name: 'ssh',
  },
  // 用于同步github的博客
  repo: {
    owner: 'sl1673495',
    name: 'blogs',
  },
  // 可选 如果申请了github Oauth app的话
  // 可以填写用于取消github请求限制
  client_id: '',
  client_secret: '',
}
```

`repo`字段中的信息决定了请求会去哪个仓库下拉取issues生成博客，`user`下的字段定义了首页显示的用户名，`client_id`和`client_secret`的作用后面会讲。

### 同步博客
builder/sync.js  
```js
/**
 * 同步github上的blogs
 */
const axios = require('axios')
const fs = require('fs')
const path = require('path')
const { rebuild } = require('./utils')
const {
  repo: { owner, name }, mdDir,
} = require('../config')

const GITHUB_BASE_URL = 'https://api.github.com'
module.exports = async () => {
  // 清空md文件夹
  rebuild(mdDir)

  try {
    // 请求github博客内容
    const { data: blogs } = await axios.get(
      `${GITHUB_BASE_URL}/repos/${owner}/${name}/issues`,
    )

    // 创建md文件
    blogs.forEach((blog) => {
      fs.writeFileSync(path.join(mdDir, `${blog.id}.md`), blog.body, 'utf8')
    })

    return blogs
  } catch (e) {
    console.error('仓库拉取失败，请检查您的用户名和仓库名')
    throw e
  }
}
```
其中rebuild函数就是用node的fs模块把文件夹删除再重新创建，

这个函数的作用就是把github仓库里的issues拉取下来，并且写入到我们自己定义的存放md的文件夹中。  

### 把博客转为jsx写入pages目录
builder/page-builder.js
```js
/**
 * 生成nextjs识别的pages
 */
const fs = require('fs')
const path = require('path')
const MarkdownIt = require('markdown-it')
const axios = require('axios')
const {
  mdDir,
} = require('../config')
const { rebuild, copyFolder } = require('./utils')

const md = new MarkdownIt({
  html: true,
  linkify: true,
})

const handleMarkdownBody = (body) => {
  return encodeURIComponent(md.render(body))
}

const pageTemplateDir = path.resolve(__dirname, '../pages-template')
const pageDir = path.join(__dirname, './pages')

module.exports = async (blogs) => {
  // 清空pages文件夹
  rebuild(pageDir)
  // 把pages-template目录的模板拷贝到pages下
  await copyFolder(pageTemplateDir, pageDir)

  // 读取md文件夹下的所有md文件的名字（其实就是issue的id）
  const mdPaths = fs.readdirSync(mdDir)
  const convertMdToJSX = async (mdPath) => {
    const mdContent = fs.readFileSync(path.join(mdDir, mdPath)).toString()
    // pages下的页面根据id命名
    const mdId = Number(mdPath.replace('.md', ''))
    const blog = blogs.find(({ id }) => id === mdId)

    if (blog) {
      // body已经在md文件夹内了 不需要了
      const { body, ...restBlog } = blog
      const { comments_url } = restBlog

      // 获取评论信息
      const { data: comments } = await axios.get(comments_url)
        .catch((err) => {
          console.error('评论生成失败，', err)
        })

      // 处理评论的markdown文本 并且写入到html字段中
      comments.forEach(({ body: commentBody }, index) => {
        const commentHtml = handleMarkdownBody(commentBody)
        comments[index].html = commentHtml
      })

      // 页面的jsx
      const pageContent = `
      import Page from '../components/Page'

      const pageProps = {
        blog: ${JSON.stringify(restBlog)},
        comments: ${JSON.stringify(comments)},
        html: \`${handleMarkdownBody(mdContent)}\`,
      }

      export default () => <Page {...pageProps}/>
    `
      // 写入文件
      fs.writeFileSync(path.join(pageDir, `${mdId}.jsx`), pageContent, 'utf8')
    }
  }

  const tasks = mdPaths.map(convertMdToJSX)
  await Promise.all(tasks)
}
```
这个函数需要接受我们刚刚请求到的issues数据，用来生成标题，因为在上一步中使用了issue的id去命名博客，所以可以在这一步中读取md文件夹下的所有issue id，就可以在这个blogs数组中找到对应的issue信息，这个issue对象中有github api给我们提供的comments_url，可以用来请求这个issue下的所有评论，这里也把它一起请求到。

```js
  // 把pages-template目录的模板拷贝到pages下
  await copyFolder(pageTemplateDir, pageDir)
```
函数刚开始这一步的作用是因为每次执行这个函数都需要用rebuild函数清空pages文件夹，防止同步不同账号的数据以后产生数据混乱，但是nextjs中我们可能会自定义`_document.js`或者`_app.js`，这玩意也不需要动态生成，所以我们就先在pages-template文件夹下提前存放好这些组件，然后执行的时候直接拷贝过去就好了。
![pages-template](https://user-gold-cdn.xitu.io/2019/9/18/16d422d1dd410c6c?w=432&h=48&f=png&s=15023)

`convertMdToJSX`这个方法就是把md文件转为nextjs可以识别的jsx格式，
```js
`
      import Page from '../components/Page'

      const pageProps = {
        blog: ${JSON.stringify(restBlog)},
        comments: ${JSON.stringify(comments)},
        html: \`${handleMarkdownBody(mdContent)}\`,
      }

      export default () => <Page {...pageProps}/>
    `
```
其实就是这么个格式，注意写入的时候要用JSON格式化一下，否则写入的会是[Object object]这样的文字。  

另外我们在这一步就要配合`markdown-it`插件把md内容转成html格式，并且通过encodeURIComponent转义后再写入我们的jsx内，否则会出现很多格式错误。  

最后利用Promise.all把convertMdToJSX这个异步方法批量执行一下。  

这一步结束后，我们的pages目录大概是这个样子  
![pages](https://user-gold-cdn.xitu.io/2019/9/18/16d42290ebe72f4c?w=404&h=400&f=png&s=84926)

点开其中的一个jsx  

![jsx](https://user-gold-cdn.xitu.io/2019/9/18/16d422e601ac57ad?w=709&h=659&f=png&s=382507)

这已经是react可以渲染的jsx文件了，快要成功了~

### 生成首页
builder/page-builder.js
```js
/**
 * 生成博客首页
 */
const fs = require('fs')
const path = require('path')

const indexPath = path.resolve(__dirname, '../pages/index.jsx')

module.exports = (blogs) => {
  const injectBlogs = JSON.stringify(
    blogs.map(({ body, ...restBlog }) => restBlog),
  )

  // 把blog数据注入到首页中
  const indexJsx = `
    import React from 'react'
    import Link from 'next/link'
    import Layout from '../components/Layout'
    import Main from '../components/Main'
    
    const blogs = ${injectBlogs}
    const Home = () => (
      <Layout>
        <Main blogs={blogs} />
      </Layout>
    )
    
    export default Home
  `
  fs.writeFileSync(indexPath, indexJsx, 'utf8')
}

```

这一步没啥好说的，一样的套路，写入jsx生成首页。  

### 执行入口

最后我们在入口把这些方法串起来。  
```js
const { withOra, initAxios } = require('./utils')
const syncBlogs = require('./sync')
const pageBuilder = require('./page-builder')
const indexBuilder = require('./index-builder')

const start = async () => {
  initAxios()

  // 同步github上的blogs到md文件夹
  const blogs = await withOra(
    syncBlogs,
    '正在同步博客中...',
  )

  // 抓取评论，生成pages下的博客页面。
  await withOra(
    () => pageBuilder(blogs),
    '正在生成博客页面中...',
  )

  // 生成首页
  indexBuilder(blogs)
}
start()

```

`initAxios`这个函数目的是在请求的时候可以带上github的`client_id`和`client_secret`信息，如果你在github申请了OAuth app就会拿到俩个东西，带上的话就可以更频繁的请求api，否则github会限制同一个ip下请求调用的次数。
```js
function initAxios() {
  axios.default.interceptors.request.use((axiosConfig) => {
    if (client_id) {
      if (!axiosConfig.params) {
        axiosConfig.params = {}
      }
      axiosConfig.params.client_id = client_id
      axiosConfig.params.client_secret = client_secret
    }
    return axiosConfig
  })
}
```
在本项目中，`client_id`和`client_secret`定义在了配置文件config.js中。

`ora`是一个命令行提示加载中的插件，可以让我们在异步生成这些内容的时候得到更友好的提示，withOra就是封装了一层，在传入函数的调用前后去启动、暂停ora的提示。
```js

async function withOra(fn, tip = 'loading...') {
  const spinner = ora(tip).start();

  try {
    const result = await fn()
    spinner.stop()
    return result
  } catch (error) {
    spinner.stop()
    throw error
  }
}
```

然后在package.json中写入自定义script
```
"scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "export": "next export",
    "sync": "node builder/index.js",
    "all": "npm run sync && npm run build && npm run export"
},
```
这样，`npm run sync`命令可以执行上面编写的builder逻辑，拉取github blogs生成pages，可以方便调试。

`npm run all`命令则是在sync命令调用后再去执行`npm run build` 和 `npm run export`，让nextjs去生成out文件夹下的静态html页面，这样就大功告成了。

## 本地调试

![最终pages](https://user-gold-cdn.xitu.io/2019/9/18/16d423281216e445?w=426&h=417&f=png&s=86880)

到了这一步，`npm run dev`后就可以开始调试你的博客了，注意生成的jsx都是尽量把内容最小化，把动态变化的内容都放到组件中去渲染，比如生成的page jsx里的`Page`组件，定义在components/Page.jsx中，在里面可以根据你的喜好去利用react任意发挥，并且调试支持热更新，可以说是非常友好了。

components目录组件：

![components目录](https://user-gold-cdn.xitu.io/2019/9/18/16d423b267fe20ae?w=413&h=134&f=png&s=19120)
`Header.jsx`： 对应首页中头部的部分。
`Layout.jsx`：首页、博文详情页的布局组件，包含了Header.jsx
`Main.jsx`：首页。
`Markdown.jsx`：渲染markdown html文本的组件，本项目中利用了`react-highlight`库去高亮显示代码。
`Page.jsx`：博客详情页，评论区也是在里面实现的。  

## 生成html
本地开发完成后，执行`npm run all`，（或者不需要再同步博客的情况执行`npm run build` + `npm run export`)，就会在out目录下看到静态html页面了。

![out](https://user-gold-cdn.xitu.io/2019/9/18/16d4240937731590?w=409&h=274&f=png&s=68769)
里面的内容是这样的：
![html](https://user-gold-cdn.xitu.io/2019/9/18/16d424159df66f1a?w=852&h=616&f=png&s=306823)
把out目录部署到服务器上，就可以通过 
http://blog.shanshihao.cn/474922327  这样的路径去访问博客内容了。

到此我们就完成了手动生成自己的静态博客，nodejs真的是很强大，nextjs也是ssr的神器，在这里也推荐一下jocky老师的nextjs课程 https://coding.imooc.com/class/334.html ，我在这个课程中也学习到了非常多的东西。

---

废弃