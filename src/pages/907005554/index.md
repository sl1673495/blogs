---
title: 'Vite 太快了，烦死了，是时候该小睡一会了。'
date: '2021-05-31'
spoiler: ''
---

在知乎看[参与 Vue Conf 2021 是怎样的体验？](https://www.zhihu.com/question/460852226 "参与 Vue Conf 2021 是怎样的体验？")这个问题的时候，偶然发现 Anthony Fu 的回答里提到了一个好玩的凡尔赛插件：[vite-plugin-sleep](https://github.com/IndexXuan/vite-plugin-sleep "vite-plugin-sleep")。

先看看回答中 Anthony Fu 是怎么引出这个插件的：

> 关于 QA 环节中对于 Vite 快的意义的提问似乎引发了大家的一些讨论，借此机会说说自己的浅见。
> 我们有两个词，UX 和 DX，分别对应用户体验（User Experience）和开发者体验（Developer Experience）。
>
> 的确某种程度上，作为开发者我们应该优先满足于终端用户的体验，但是随着开发者数量的增加，以及软件需求的越发复杂，开发者同样作为人的体验也十分重要。
>
> 如果开发者不能获得很好的 DX，便很难有足够好的效率去进行 UX 的改善。而性能的提升可以更好的让机器接受人的命令而不是浪费时间在等待机器完成工作。
>
> **当然，如果你是觉得工具太快影响休息的话，这里安利一下 @小炫 的插件，让你的 Vite 也休息一下 vite-plugin-sleep（被你发现了，其实抖这个机灵才是我的目的）**

这充满凡尔赛气息的话语属实逗笑我了，Webpack 的构建之慢确实带给了我们一些美好的摸鱼时间，Vite 是夺走它们的罪魁祸首，这才是**属于打工人的插件**！

## 介绍

先看看 vite-plugin-sleep 的「动机」章节：

> In the old days with webpack, we had many times when we could compile with pay, and with vite it was so
> fast that we couldn't rest.
> Time to take a nap in the vite.

在 Webpack 陪伴的那些日子里，我们在编译的时候有很多的时间可以用来休息，但 Vite 太快了，**夺走了这一切**。

是时候**小睡一会**了……

## 用法

```shell
yarn add vite-plugin-sleep
```

```js
// vite.config.ts
import sleep from "vite-plugin-sleep";

/** @see {@link https://vitejs.dev/config/} */
export default defineConfig({
  plugins: [
    // ...other plugins
    sleep(/* options */),
  ],
});
```

就这么简单，安装然后引入，属于你的摸鱼时间又回来了。

## 原理

看看这个插件的源码是什么样的，顺便学习一下 Vite 插件的编写方式。

Vite 插件的通用形式一般是个函数，接受用户传入的一个 options 配置选项，返回 Vite 标准的插件格式，一个形如这样的对象：

```js
{
  name: 'vite-plugin-sleep',
  config() { // 自定义 config 逻辑 }
  load() { // 自定义 load 逻辑 },
}
```

Vite 暴露了很多钩子函数给用户，让用户在适当的时机对源码内部的行为进行一些介入和更改。

在官网的 [插件 API —— 钩子](https://cn.vitejs.dev/guide/api-plugin.html#universal-hooks "插件 API —— 钩子") 章节阅读文档，注意有一部分钩子是继承自 Rollup 的，所以需要去 Rollup 的官网来查看使用说明。

以官网中提到的例子来解释：

```js
export default function myPlugin() {
  const virtualFileId = "@my-virtual-file";

  return {
    name: "my-plugin", // 必须的，将会显示在 warning 和 error 中
    resolveId(id) {
      if (id === virtualFileId) {
        return virtualFileId;
      }
    },
    load(id) {
      if (id === virtualFileId) {
        return `export const msg = "from virtual file"`;
      }
    },
  };
}
```

这个插件允许用户引入一个虚拟文件（在实际文件中不存在），通过 `load` 钩子来自定义读取文件的内容，用户就可以这样引入 `"from virtual file"` 这个字符串了。

```js
import { msg } from "@my-virtual-file";

console.log(msg);
```

有了这些前置知识，我们来看下这个插件是怎么写的：

```js
import type { Plugin } from "vite";
import type { UserOptions } from "./lib/options";
import { sleep } from "./lib/utils";
import { name } from "../package.json";

export default function sleepPlugin(userOptions: UserOptions = {}): Plugin {
  const options = {
    ...userOptions,
  };
  let firstStart = true;
  return {
    name,
    enforce: "pre",
    configureServer(server) {
      server.middlewares.use(async (req, __, next) => {
        // if not html, next it.
        // @ts-expect-error
        if (!req.url.endsWith(".html") && req.url !== "/") {
          return next();
        }
        if (firstStart) {
          await sleep(options.devServerStartDelay || 20000);
          firstStart = false;
        }
        next();
      });
    },
    async load() {
      await sleep(options.hmrDelay || 2000);
      return null;
    },
  };
}
```

其实很简单，[`configureServer`](https://cn.vitejs.dev/guide/api-plugin.html#configresolved "`configureServer`") 钩子是 Vite 官方提供的**独有钩子**（也就是 Rollup 中不存在的钩子），是用于配置开发服务器的钩子，最常见的用例是添加一些自定义服务中间件。

而 `load` 钩子则是 `Rollup` 内置的，根据官网的说法，`return null` 代表这个文件交给其他插件或者由默认解析行为处理，也就是延迟两秒后啥都不干。

再回到插件的内容，先定义一个睡觉的函数：

```js
export function sleep(delay: number) {
  return new Promise((resolve) => setTimeout(resolve, delay));
}
```

配合 await 语法，可以实现非常优雅的睡眠。

通过 `enforce: 'pre'` 来强制这个插件的钩子在最前面执行（其他插件别想阻止我摸鱼）。

`configureServer` 这个钩子里的代码也很简单，初次启动 Vite 开发服务器的时候，访问入口 HTML 文件时，`sleep` 沉睡用户传入的时间，默认 20 秒。（20 秒够干嘛？XD，请设置成 120 秒。）

![](https://images.gitee.com/uploads/images/2021/0530/012343_3814afa6_1087321.png "屏幕截图.png")

官方给出的例子就是添加中间件，但尤老板万万没想到中间这段注释代码被摸鱼小能手填充之后，竟是用来做这种事！

之后是 `load` 钩子，读取每个文件的时候，默认沉睡 2 秒。

就这么简单，一个 Vite 摸鱼插件完成了。

## 总结

周末了，通过这个凡尔赛的插件图个乐子，顺便学习一下 Vite 插件的基础知识，美滋滋！

## 感谢大家

欢迎关注 ssh，前端潮流趋势、原创面试热点文章应有尽有。

记得关注后加我好友，我会不定期分享前端知识，行业信息。2021 陪你一起度过。

![](https://oscimg.oschina.net/oscnet/up-fa75de6c6ac2dbce9cb2e85b58753d4568b.png)
