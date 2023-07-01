---
title: '未来前端构建工具链的故事里，会有这个 97 年的韩国小哥？'
date: '2021-08-20'
spoiler: ''
---

Next.js 在 8 月 12 号发布了 11.1 版本，在前端圈子里引起了不小的动荡，我总结了两点原因：

1.  **SWC 作者和 Parcel Contributor** 的加入。
2. 前端工具链领域  **Rust or Go based**  的发展方向。

先来看看联合作者，豪华的阵容：
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/cbd0e723fc5e42598eb881f061d252c6~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

其中 [DongYong Kang](https://twitter.com/kdy1dev) 是最近很火的基于 Rust 的编译框架 SWC 的作者，97 年出生的韩国小哥。
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f760d4e517744bb8b5fb4caca2c11c5f~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

而 [Maia Teegarden](https://twitter.com/padmaia) 是 Parcel 的贡献者之一。
![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/dd02ba273ed74e79845e316b6d79d3a7~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

在这些巨佬的加持下，Next.js 11.1 带来了很多让人振奋的新改进：

- [**安全补丁**](https://nextjs.org/blog/next-11-1#security-patch)： 防止潜在的打开重定向风险的重要更新。
- [**ES Modules 支持**](https://nextjs.org/blog/next-11-1#es-modules-support)： 今日起可用，通过实验性 flag 开启。
- [**Rust-based 工具链**](https://nextjs.org/blog/next-11-1#adopting-rust-based-swc)： 集成 SWC，取代了 JS 工具链（Babel 和 Terser）。
- [**更快的数据获取**](https://nextjs.org/blog/next-11-1#builds--data-fetching)： **2x 快**的数据获取，在预渲染的时候通过 HTTP `keep-alive` 特性加持来获得。
- [**更快的 Source Maps**](https://nextjs.org/blog/next-11-1#source-maps)：构建速度加快 **70%**，内存使用减少 **67%**。
- [**ESLint 集成优化**](https://nextjs.org/blog/next-11-1#eslint-improvements)： 更好的可访问性和拼写检查。
- [**`next/image`  优化**](https://nextjs.org/blog/next-11-1#nextimage-improvements)： 可选的 Sharp 用法, 对  `next export` 的支持更好。

**接下来，咱一起看看本次更新的新闻稿内容** ：

## 安全补丁

Next.js 团队与安全研究人员和审计人员合作来防止漏洞。我们感谢来自 Robinhood 的 Gabriel Benmergui，他们调查并发现了一个使用 `pages/_error.js`的打开重定向风险，并随后负责任的进行报告。

好在报告的问题没有直接伤害到用户，但它存在被钓鱼攻击从信任域重定向到攻击者的域的风险。我们在 Next.js 11.1 中安装了一个补丁，以防止这种问题的发生，我们也做好了[安全回归测试](https://github.com/vercel/next.js/blob/canary/test/integration/repeated-slashes/test/index.test.js)。

欲了解更多详情，请阅读[公开的 CVE](https://github.com/vercel/next.js/security/advisories/GHSA-vxf5-wxwp-m7g9)。我们建议升级到 Next.js 的最新版本，以提高应用程序的整体安全性。如需跟进日后的报告信息，请发送电子邮件至 security@vercel.com。

**注意**：托管在 Vercel 上的 Next.js 应用程序**不受此漏洞的影响**（因此，在 Vercel 上运行的 Next.js 应用程序**不需要执行任何操作**。）

## ES Modules 支持

我们致力于 Next.js 中广泛的 [ES Modules](https://nodejs.org/docs/latest/api/esm.html) 支持，作为引入模块或者输出目标的支持都在完善。从 Next.js 11.1 起，你可以通过开启实验性标志，用 ES Modules 引入 npm 包（例如 `package.json` 中的 `"type": "module"`）

```js
// next.config.js
module.exports = {
  // Prefer loading of ES Modules over CommonJS
  experimental: { esmExternals: true },
};
```

ES Modules 的支持也向后兼容，以支持传统的 CommonJS 导入行为。在 Next.js 12 中，`esmExternals: true` 会成为默认选项，我们强烈建议尝试这个新选项，并且在 [Github Discussions 留下反馈](https://github.com/vercel/next.js/discussions/27876)一起讨论如何改进。

## 采用基于 Rust 的 SWC

我们正在集成 [SWC](https://swc.rs/)，这是一个基于 Rust 的**超级快**的 JavaScript 和 TypeScript 的编译器，它可以替代 Next.js 里的两条工具链：编译独立文件的 Babel 和压缩产物的 Terser。

作为用 SWC 取代 Babel 的一部分，我们正在将 Next.js 用到的所有自定义代码转换，移植到用 Rust 编写的 SWC 代码转换，最大限度的提升性能。例如，在 `getStaticProps`、`getStaticPaths` 和`getServerSideProps`中 tree shaking 掉未使用的代码。

在早期的测试中，以前使用 Babel 的代码转换从 `500ms` 下降到 `10ms`，代码压缩从`250ms`下降到 `30ms`。总的来说，比以前**快两倍**。

我们很高兴地宣布，[SWC](https://swc.rs/)的创建者 [DongYoon Kang](https://twitter.com/kdy1dev) 和[Parcel](https://parceljs.org/)的贡献者[Maia Teegarden](https://twitter.com/padmaia) 已经加入了 Vercel 的 Next.js 团队，致力于改善`next dev`和`next build`的性能。当 SWC 稳定后，我们将在下一个版本中分享更多关于 SWC 集成的结果。

## 性能提升

### 构建和数据获取

当你使用`next build` 且发送大量 HTTP 请求时，我们的性能平均提高了**2 倍**。例如，如果你使用`getStaticProps`和 g`etStaticPaths`从 Headless CMS 获取内容，那么你会看到明显更快的构建。

Next.js 自动 polyfill 了 `node-fetch`，现在默认启用[HTTP Keep-Alive](https://en.wikipedia.org/wiki/HTTP_persistent_connection)。根据 [external benchmarks](https://github.com/Ethan-Arrowood/undici-fetch/blob/main/benchmarks.md#fetch)，这将使预渲染速度快**2 倍**。

要对某些`fetch()`调用禁用 HTTP Keep-Alive，可以添加 `agent` 选项:

```js
import { Agent } from "https";
const url = "<https://example.com>";
const agent = new Agent({ keepAlive: false });
fetch(url, { agent });
```

要全局覆盖所有`fetch()`调用，可以使用`next.config.js`:

```js
module.exports = {
  httpAgentOptions: {
    keepAlive: false,
  },
};
```

### Source Maps

基于 Webpack 对 Assets 和 SourceMap 处理的优化，在 Next.js 中 SourceMap 现在可以减少约**70%的性能消耗**和约**67%的内存消耗**。

这只会影响在 `next.config.js` 文件中开启 `productionBrowserSourceMaps: true` 的 Next.js 应用程序。在 Next.js 11.1 中，当启用 SourceMap 时，构建时间仅仅增加了 11%。

我们还与 Sentry 合作，通过 [Sentry Next.js plugin](https://docs.sentry.io/platforms/javascript/guides/nextjs/) 来[提高上传 SourceMap 的性能](https://github.com/vercel/next.js/issues/26588#issuecomment-894329188)。

## ESLint 优化

在 Next.js 11 中，我们通过`next lint`引入了内置的 ESLint 支持。自最初发布以来，我们一直在持续添加 rules，帮助开发人员修复应用程序中的常见错误。

### 默认的可访问性 rules

现在默认情况下包含了更好的可访问性规则，防止 ARIA 属性之间不匹配，或者是使用不存在的 ARIA 属性的问题。默认情况下，这些规则将是 warn 级别。

- [aria-props](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/aria-props.md?rgh-link-date=2021-06-04T02%3A10%3A36Z)
- [aria-proptypes](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/aria-proptypes.md?rgh-link-date=2021-06-04T02%3A10%3A36Z)
- [aria-unsupported-elements](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/aria-unsupported-elements.md?rgh-link-date=2021-06-04T02%3A10%3A36Z)
- [role-has-required-aria-props](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/role-has-required-aria-props.md?rgh-link-date=2021-06-04T02%3A10%3A36Z)
- [role-supports-aria-props](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/HEAD/docs/rules/role-supports-aria-props.md?rgh-link-date=2021-06-04T02%3A10%3A36Z)

特别感谢社区贡献者 [JeffersonBledsoe](https://github.com/JeffersonBledsoe) 添加了这些规则。

### 常见的拼写错误

对于`getStaticProps`、`getStaticPaths`和`getServerSideProps`中的常见拼写错误，默认情况下将会检测到并且发出警告。这有助于解决由于一个小的输入错误，导致无法调用数据获取的情况。例如，`getstaticprops`或`getstaticprops` 会被检测并警告。

特别感谢社区贡献者[kaykdm](https://github.com/kaykdm)创建了这个规则。

## `next/image` 优化

我们一直在收集关于`next/image`和内置的[图片优化](https://nextjs.org/docs/basic-features/image-optimization)的社区反馈，很高兴可以分享对性能、开发体验和用户体验的众多改进。

### 图像优化

默认情况下，Next.js 使用 WebAssembly 来执行 Image Optimization，这抵消了 Next.js 包的安装时间，因为它非常小，而且没有 post-install 的步骤。在 Next.js 11.1 中，你可以选择性的安装`sharp`，它优化了非缓存图片生成时间，同时也降低了安装速度。

基于 WebAssembly 的图像优化器已经更新，以支持 ARM 芯片，比如如使用 Node.js 16 的 Apple M1。

内置图像优化器现在根据响应主体的内容自动检测外部图像内容类型。这允许 Next.js 在优化托管在 AWS S3 且响应头为`Content-Type: application/octet-stream`的图像。

### 在开发环境中懒生成模糊占位图

在 `next dev` [静态图片引入](https://nextjs.org/docs/basic-features/image-optimization#image-imports)，且写明了`placeholder="blur"` 属性时，这些图片会自动开启懒生成，当引入很多静态图片时，可以优化开发服务器的启动速度。

```js
import Image from "next/image";
import author from "../public/me.png";

export default function Home() {
  return (
    // The placeholder for this image is lazy-generated during development
    <Image src={author} alt="Picture of the author" placeholder="blur" />
  );
}
```

### 其他的一些图片优化

- **以前加载过的图片不再被延迟加载**：当一个图片之前已经被加载过，无论是通过客户端导航还是在页面的另一个部分加载它，Next.js 都会自动跳过延迟加载，以避免在显示图像之前出现快速的闪烁。
- **通过`next export`支持自定义图像加载器**：`next/image` 现在在 `next export` 时支持 [第三方图像优化服务](https://nextjs.org/docs/basic-features/image-optimization#loader)。当你想提供 [`自定义 loader 属性`](https://nextjs.org/docs/api-reference/next/image#loader) 给 `next/image` 时，你可以在 `next.config.js` 中配置 `images.loader: "custom"`。
- **图像加载完成时的新事件**：根据用户的反馈，我们在`next/image`中添加了一个新的属性`onLoadingComplete`。这允许注册一个在**图像完全加载**后的回调函数。
- **配置默认图像缓存 TTL(Time To Live)**：你现在可以在 next.config.js 中配置[`images.minimumCacheTTL`](https://nextjs.org/docs/basic-features/image-optimization#minimumcachettl)来更改默认的缓存 TTL。如果可能的话，我们建议使用[静态图片导入](https://nextjs.org/docs/basic-features/image-optimization#image-imports),，因为 URL 中包含图像 hash 值，所以静态图片导入会自动使用最大 TTL。

> 新闻稿地址：https://nextjs.org/blog/next-11-1#other-image-improvements
>
> 翻译 / 润色：ssh, 字节跳动 Web Infra APM 团队成员，内推欢迎联系微信 sshsunlight

## 社区

Next.js 是社区 1700 多位独立开发者、谷歌和 Facebook 等行业合作伙伴，以及我们的核心团队共同努力的结果。

我们很自豪地看到这个社区持续发展。仅在过去的 6 个月里，我们就看到 Next.js 在 NPM 上的**下载量增长了 50%**，**从 410 万次增长到 620 万次**，在 Alexa 排名前 1 万的网站中**使用 Next.js 的主页数量也增长了 50%**。