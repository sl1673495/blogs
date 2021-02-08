---
title: 'Vuex 4.0 正式发布！新年官方生态齐聚一堂'
date: '2021-02-05'
spoiler: ''
---

Vuex 4 官方版本正式发布。

Vuex 4 的重点是**兼容性**。Vuex 4 支持 Vue 3，但是仍然提供了与 Vuex 3 完全相同的 API，因此用户可以在 Vue 3 中直接**复用他们现有的 Vuex 代码**。

下文会把破坏性的改动列出来，请注意查看。

在[源码的 example 文件夹](https://github.com/vuejs/vuex/tree/v4.0.0/examples "源码的 example 文件夹")可以看到 Optional 和 Composition API 下的基本用法。

它仍然和 Vue 3 一样在 NPM 包的 next 标签下发布，我们计划在 Vue3 准备好的时候移除 next 标签。

为了 Vuex 4 的稳定发布，大家齐心协力做出了很多贡献。非常感谢你们的帮助。若不是有如此出色的 Vue 社区，根本不可能实现这一切！

## 文档

请访问 [next.vuex.vuejs.org](https://next.vuex.vuejs.org/ "next.vuex.vuejs.org") 查看文档。

## 破坏性变动

### 安装流程更改

为了和 Vue3 的初始化流程一致，Vuex 的安装流程有所改动。

我们建议用户用新的 `createStore` 函数来建立一个 `store` 实例。

```js
import { createStore } from "vuex";

export const store = createStore({
  state() {
    return {
      count: 1,
    };
  },
});
```

> 同时这在技术上并不是一个破坏性的改动，你依然可以用 `new Store(...)` 语法，不过我们推荐你用新语法，这样可以和 Vue3 以及 Vue Router 4 保持一致。

在 Vue 实例上安装 Vuex，传递 store 即可。

```js
import { createApp } from "vue";
import { store } from "./store";
import App from "./App.vue";

const app = createApp(App);

app.use(store);

app.mount("#app");
```

### 构建产物和 Vue3 一致

以下的构建产物可以和 Vue3 的产物保持一致：

- `vuex.global(.prod).js`
  - 直接在浏览器中使用 `<script src="...">`，暴露全局 Vuex 变量。
  - 全局构建会被打包成 IIFE，并不是 UMD，仅用于直接使用 `<script src="...">` 引入。
  - 包含了硬编码的 `prod/dev` 分支判断，`prod.js` 是压缩后的，在生产环境记得使用这个文件。
- `vuex.esm-broswer(.prod).js`
  - 为了使用 native ES module imports（需要浏览器支持 es module 用法，`<script type="module">`）
- `vuex.esm-bundler.js`
  - 为了通过 `webpack`, `rollup`, `percel` 等构建工具使用模块。
  - 保留 `prod/dev` 分支判断和 `process.env.NODE_ENV` 判断（这个变量需要被构建工具替换）
  - 并不会提供 minified 版本（构建工具可以引入后一起处理）
- `vuex.cjs.js`
  - 为了使用 Node.js 服务端渲染时通过 `require()` 导入。

### 类型 `ComponentCustomProperties`

Vuex 4 移除了为了推导 `this.$store` 而编写的全局类型，解决了 [issue #994](https://github.com/vuejs/vuex/issues/994 "issue #994")，在使用 TypeScript 时，你必须自己手动添加模块类型声明。

在项目中使用如下的代码，`this.$store` 就可以正确推导：

```ts
// vuex-shim.d.ts
import { ComponentCustomProperties } from "vue";
import { Store } from "vuex";

declare module "@vue/runtime-core" {
  // Declare your own store states.
  interface State {
    count: number;
  }

  interface ComponentCustomProperties {
    $store: Store<State>;
  }
}
```

### 核心模块中导出 `createLogger` 函数

在 Vuex 3 中, `createLogger` 函数从 `vuex/dist/logger` 中导出，现在它被包含在核心包中了，你可以直接这样导入：

```js
import { createLogger } from "vuex";
```

### 自 4.0.0-rc.2 以来的 Bug 修复

- 未导出 `storeKey`([4ab2947](https://github.com/vuejs/vuex/commit/4ab294793a2c20ea6040f01f316618682df61fff "4ab2947"))
- 修复 webpack 中 tree shaking 未生效 ([#1906](https://github.com/vuejs/vuex/issues/1906 "#1906")) ([#1907](https://github.com/vuejs/vuex/issues/1907 "#1907")) ([aeddf7a](https://github.com/vuejs/vuex/commit/aeddf7a7c618eda7f316f8a6ace8d21eb96c29ff "aeddf7a"))

## 原文发布地址

https://github.com/vuejs/vuex/releases/tag/v4.0.0
