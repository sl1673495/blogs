---
title: 'Dan Abramov 接受油管 UP 主的面试挑战，结果差点没写出来居中……？'
date: '2023-06-30'
spoiler: ''
---

> 首发于公众号[前端从进阶到入院](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2020/4/5/17149cbcaa96ff26~tplv-t2oaga2asx-image.image)，欢迎关注。  

大家好，我是 ssh，前两天大名鼎鼎的 React 核心开发者 Dan Abramov 接受了油管 up 主 Ben Awad 的一场面试，而且是正儿八经做题的那种，不是之前国内那场戏称的面试。我们赶快一起来看看。

刚开场，Dan 首先来了段自我介绍：

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/41d9511e639b410ca33cab9245c78447~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

这绕口令呢？I work on React i did not create react but i work on it on React team...

大意就是，他是 React 和 Redux 的联合开发者，他不是 React 创始人（估计是他对外发声太多，有误解的小白不少），今天他想通过 Ben 的面试，祝他好运！

接下来寒暄几句，Ben 就正式开启了面试环节：

## let vs const

上来就是国内也很经典的一道面试题，让 Dan 回答 let 和 const 的区别。
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/066b0b8163964a9b8c4545c1da122d53~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

Dan 回答说他认为这不重要，于是面试官让他滚回家等通知了（误

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/02d56c6da1e942d6ad54d5c07369f16a~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

开个玩笑，Dan 还是稳稳的回答出了区别，const 可以防止变量重新分配，并且指出 const 创建的对象 object 依然可以用 object.xxx 来修改对象属性的值。

之后主持人问他平时的使用习惯，Dan 说他是个很混乱的人，看心情使用，然后询问主持人是不是要解雇他（哈哈哈）

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d49fbfb19ac042f9be2b6564aca6784b~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

## Redux

主持人非常俏皮的问：“有一个可爱的库，经常和 React 一起使用，你可能知道叫 Redux”

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b0e767bdddf346fab80a8e9ef4b8166b~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

Dan 也很俏皮的回了句：“听说过”。

接下来主持人发出了灵魂拷问： **“什么时候我该考虑在项目中使用 Redux？”** 

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8ea5f3c2158c4c808ccffb0cc2ec834f~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

Dan 略加思索，从以下几点来回答了这个问题：

- 项目中已经使用了它。
- 团队对它比较熟悉。
- 服务端数据 -> 可能需要被缓存。
- 跨组件共享某些数据。

最后 Dan 说，如果现在新建一个项目，他可能不会选择 Redux 了，主持人蛤蛤大笑，问他会选择什么，Dan 说这取决于实际情况，如果是一些需要缓存的服务端数据，他可能会选择 **react-query, relay, apollo** 等一些现代的 react 请求状态库。

主持人接着追问，如果是需要提升到顶部的状态，你喜欢用 **Context** 吗？Dan 给出了肯定的答复。

## dangerouslySetInnerHTML

接下来，主持人对 `dangerouslySetInnerHTML` 这个 API 的使用时机提出了疑问。
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/553cd9e4f5564dad98deeee3132a446f~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

Dan 回答说，这个 API 是在你可能从数据库或者什么地方拿到一串 HTML 想要展示到页面上时，在确保它是**安全**的 HTML 文本的前提下，可以使用。你可以提前对这串 HTML 消毒（santize)，确保没有未经过消毒的用户输入。

## 居中

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bbde9a3b16d84f308075ee4cbf189378~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

一个很常规的 CSS 问题，让这段文本在页面上**水平垂直居中**。

Dan 慌慌张张的开始用 `display: flex` 起手，然后来了个 `width: 100%` 想让容器撑满，他显然已经忘了这是默认的块布局的行为了 XD。

![翻译大误](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/cf8b27a63b0b4608a87e8c3fa59c038b~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

Dan 写到这一步，开始迷茫了，为什么没生效！

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d286046ed87d4b109a46087cbec8ad18~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

经过了大约整整 5 分钟的苦思冥想的调试，Dan 终于试出来了问题，因为 HTML 元素默认不是 100% 的高度，大师原来也会遗忘这些基础，哈哈。

![我得意的笑](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d538a44ce148429dadabce90ef4adf7e~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

国际友人埃文尤也对此事发表了亲切的慰问。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/97fb70ee092d47a5b155f20aa87be7b8~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

## 算法：反转二叉树

主持人：Dan 我要给你出个经典的算法题，你在 Facebook 工作，现在我要看看你能不能在 Google 工作。

没错，接下来他祭出了 homebrew 作者闻风丧胆的**反转二叉树** ！

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b608cd4d7e544ff5899a86761c658991~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

如图所示，把二叉树的节点左右反转。

Dan 很快给出了答案，看来常年维护 React，对树方面的操作必须是手到擒来了，主持人打趣说 Dan 破了他保持的最快反转二叉树的记录。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/83a9b780c22d43228b3448932d4f9961~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

## 奖金问题：找兔子

主持人神秘的拿出了他的额外奖金问题，找兔子。

这个问题大意是，一条直线上有 100 个洞，兔子藏在其中的一个洞里。

你一次只能查看一个洞，并且每次你查看洞的时候，兔子都会跳到它当前所在位置的**相邻**的洞里去。

举例来说，现在有 _ X _ _ 这四个洞，X 代表兔子的位置在第二个洞，如果你查看了第三个洞，那么兔子就可能会跳到它左边的第一个或右边第三个洞中去。

要求写出找到兔子的算法，并且给出复杂度。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/62b92f2e420e4b9992908ae135087f00~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

这是一个比较开放性的问题，具体 Dan 调试和解答的过程可以直接去油管看原视频，占据了整整二十多分钟时间。这题是真的有难度了，不过 Dan 会把他思考的过程转化成代码或者文字写在 IDE 里，帮助自己找到更多线索，并且不断的和面试官进行沟通来确认细节，我觉得这是非常值得学习的。

最后，主持人说他决定雇佣 Dan 了，当他在回答 let vs const、redux、dangerouslySetInnerHTML 的问题时，展现出的思考过程就已经足够打动他了。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/edcfc7fbd2374fbaa4e17d81c549f976~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

主持人说，谷歌也会雇佣 Dan，因为他解决了反转二叉树问题（笑），而且在遇到困难的兔子问题时，他能够一步步的写下自己的思考，和面试官不断进行互动获得更多提示，这是非常关键的。

这也可以给我们自己一些启发。当你在面试中遇到难题的时候，不要闷着头一声不吭的写，最好把你的思考过程转化成文字写下来，多和面试官进行一些提问和细节的确认。不然面试官也不知道你在想什么，该如何提示你。从我个人的感觉来说，没有面试官会喜欢沉默寡言的面试者，毕竟面试招进来的人是要在日后的工作中紧密合作的，确定你的思考过程很清晰，确定你在沟通交流方面友好和耐心也是面试官考察的重要因素，大家共勉。

![彩蛋：油管高赞评论](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/06bf175adc1440ac89a04c6ec70a3d16~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

> 油管地址：https://www.youtube.com/watch?v=XEt09iK8IXs
>
> 首发于公众号[前端从进阶到入院](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2020/4/5/17149cbcaa96ff26~tplv-t2oaga2asx-image.image)，更多有趣的前端文章，欢迎关注。
