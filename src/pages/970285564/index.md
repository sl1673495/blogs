---
title: '如何在大型代码仓库中删掉 6w 行废弃的文件和 exports？'
date: '2021-08-13'
spoiler: ''
---

> 作者：ssh，字节跳动 [Web Infra 团队](https://webinfra.org/bytedance/web-infra)成员，内推欢迎联系 sshsunlight
>
> 本文是我最近在公司内部写的**废弃代码删除工具**的一篇思考总结，目前在多个项目中已经删除约 **6w** 行代码。
>
> 首发于公众号[前端从进阶到入院](https://p1-jj.byteimg.com/tos-cn-i-t2oaga2asx/gold-user-assets/2020/4/5/17149cbcaa96ff26~tplv-t2oaga2asx-image.image)，欢迎关注。
## 起因

很多项目历史悠久，其中很多 **文件或是 export 出去的变量** 已经不再使用，非常影响维护迭代。
举个例子来说，后端问你：“某某接口统计一下某接口是否还有使用？”你在项目里一搜，好家伙，还有好几处使用呢，结果那些定义或文件是从未被引入的，这就会误导你们去继续维护这个文件或接口，影响迭代效率。

**先从删除废弃的 exports 讲起，后文会讲删除废弃文件。**

删除 exports，有几个难点：

1. 怎么样稳定的 **找出 export 出去，但是其他文件未 import 的变量** ？

2. 如何确定步骤 1 中变量在 **本文件内部没有用到** （作用域分析）？

3. 如何稳定的 **删除这些变量** ？

## 整体思路

先给出整体的思路，公司内的小伙伴推荐了 [pzavolinsky/ts-unused-exports](https://github.com/pzavolinsky/ts-unused-exports) 这个开源库，并且已经在项目中稳定使用了一段时间，这个库可以搞定上述**第一步**的诉求，也就是**找出 export 出去，但是其他文件未 import 的变量。**
但下面两步依然很棘手，先给出我的结论：

1.  **如何确定步骤 1 中变量在本文件内部没有用到（作用域分析）？**

对分析出的文件调用 ESLint 的 API，`no-unused-vars` 这个 ESLint rule 天生就可以分析出文件内部某个变量是否使用，但默认情况下它是不支持对 export 出去的变量进行分析的，因为既然你 export 了这个变量，那其实 ESLint 就认为你这个变量会被外部使用。对于这个限制，其实只需要 fork 下来稍微改写即可。
    ![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/74f7539d1a594f40b08ddb50f51421de~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

2.  **如何稳定的删除这些变量？**

自己编写 `rule fixer` 删除掉分析出来的无用变量，之后就是**格式化**，由于 ESLint 删除代码后格式会乱掉，所以手动调用 prettier API 让代码恢复美观即可。

接下来我会对上述每一步详细讲解。

### 导出导入分析

使用测试下来， [pzavolinsky/ts-unused-exports](https://github.com/pzavolinsky/ts-unused-exports) 确实可以靠谱的分析出 **未使用的 export 变量** ，但是这种分析 `import、export` 关系的工具，只是局限于此，不会分析 `export` 出去的这个变量 **在代码内部是否有使用到** 。

### 文件内部使用分析

第二步的问题比较复杂，这里最终选用 `ESLint` 配合自己 fork 改写 `no-unused-vars` 这个 `rule` ，并且自己提供规则对应的修复方案 `fixer` 来实现。

#### 为什么是 ESLint？

1. 社区广泛使用，经过无数项目验证。

2. 基于 [作用域分析](https://eslint.org/docs/developer-guide/working-with-rules#contextgetscope) ，准确的找出未使用的变量。

3. 提供的 AST 符合 [estree/estree](https://github.com/estree/estree) 的通用标准，易于维护拓展。

4. ESLint 可以解决 **删除之后引入新的无用变量的问题** ，最典型的就是删除了某个函数，这个函数内部的某个函数也可能会变成无效代码。ESLint 会 **重复执行** `fix` 函数，直到不再有新的可修复错误为止。

![](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/74a693da325e4b6087da09b6abbc5395~tplv-k3u1fbpfcp-zoom-1.image "屏幕截图.png")

#### 为什么要 fork 下来改写它？

1. 官方的 `no-unused-vars` 默认是不考虑 `export` 出去的变量的，而经过我对源码的阅读发现，仅仅 **修改少量的代码** 就可以打破这个限制，让 `export` 出去的变量也可以被分析，在模块内部是否使用。

2. 第一步的改写后，很多 `export` 出去的变量 **被其他模块引用** ，但由于在 **模块内部未使用** ，也会 **被分析为未使用变量** 。所以需要给 `rule` 提供一个 `varsPattern` 的选项，把分析范围限定在 `ts-unused-exports` 给出的 **导出未使用变量** 中，如 `varsPattern: '^foo$|^bar$'` 。

3. 官方的 `no-unused-vars` 只给出提示，没有提供 **自动修复** 的方案，需要自己编写，下面详细讲解。

### 如何删除变量

当我们在 IDE 中编写代码时，有时会发现保存之后一些 ESLint 飘红的部分被自动修复了，但另一部分却没有反应。
这其实是 ESLint 的 `rule fixer` 的作用。
参考官方文档的 [Apply Fixer](https://eslint.org/docs/developer-guide/working-with-rules#applying-fixes) 章节，每个 ESLint Rule 的编写者都可以决定自己的这条规则 **是否可以自动修复，以及如何修复。**
修复不是凭空产生的，需要作者自己对相应的 AST 节点做分析、删除等操作，好在 ESLint 提供了一个 `fixer` 工具包，里面封装了很多好用的节点操作方法，比如 `fixer.remove()` ， `fixer.replaceText()` 。
官方的 `no-unused-vars` 由于稳定性等原因未提供代码的自动修复方案，需要自己对这个 `rule` 写对应的 [fixer](https://eslint.org/docs/developer-guide/working-with-rules#applying-fixes) 。官方给出的解释在 [Add fix/suggestions to `no-unused-vars` rule · Issue #14585 · eslint/eslint](https://github.com/eslint/eslint/issues/14585) 。

## 核心改动

把 ESLint Plugin 单独拆分到一个目录中，结构如下：

```plain%20text
packages/eslint-plugin-deadvars
├── ast-utils.js
├── eslint-plugin.js
├── eslint-rule-typescript-unused-vars.js
├── eslint-rule-unused-vars.js
├── eslint-rule.js
└── package.json
```

- `eslint-plugin.js` : 插件入口，外部引入后才可以使用 `rule`

- `eslint-rule-unused-vars.js` : ESLint 官方的 `eslint/no-unused-vars` 代码，主要的核心代码都在里面。

- `eslint-rule-typescript-unused-vars` : `typescript-eslint/no-unused-vars` 内部的代码，继承了 `eslint/no-unused-vars` ，增加了一些 TypeScript AST 节点的分析。

- `eslint-rule.js` ：规则入口，引入了 `typescript rule` ，并且利用 [eslint-rule-composer](https://github.com/not-an-aardvark/eslint-rule-composer) 给这个规则增加了自动修复的逻辑。

### ESLint Rule 改动

我们的分析涉及到删除，所以必须有一个严格的限定范围，就是 **exports 出去** 且被 ts-unused-exports 认定为 **外部未使用** 的变量。
所以考虑增加一个配置 `varsPattern` ，把 ts-unused-exports 分析出的未使用变量名传入进去，限定在这个名称范围内。
主要改动逻辑是在 `collectUnusedVariables` 这个函数中，这个函数的作用是 **收集作用域中没有使用到的变量** ，这里把 **exports 且不符合变量名范围** 的全部跳过不处理。

```diff
else if (
  config.varsIgnorePattern &&
  config.varsIgnorePattern.test(def.name.name)
) {
  // skip ignored variables
  continue;
+ } else if (
+  isExported(variable) &&
+  config.varsPattern &&
+  !config.varsPattern.test(def.name.name)
+) {
+  // 符合 varsPattern
+  continue;
+ }
```

这样外部就可以这样使用这样的方式来限定分析范围：

```javascript
rules: {
  '@deadvars/no-unused-vars': [
    'error',
    { varsPattern: '^foo$|^bar$' },
  ]
}
```

接着删除掉原版中 **收集未使用变量时** 对 `isExported` 的判断，把 **exports 出去但文件内部未使用** 的变量也收集起来。由于上一步已经限定了变量名，所以这里只会收集到 ts-unused-exports 分析出来的变量。

```diff
if (
  !isUsedVariable(variable) &&
- !isExported(variable) &&
  !hasRestSpreadSibling(variable)
) {
  unusedVars.push(variable);
}
```

### ESLint Rule Fixer

接下来主要就是增加自动修复，这部分的逻辑在 `eslint-rule.js` 中，简单来说就是对上一步分析出来的各种未使用变量的 AST 节点进行判断和删除。
贴一下简化的函数处理代码：

```javascript
module.exports = ruleComposer.mapReports(rule, (problem, context) => {
  problem.fix = fixer => {
    const { node } = problem;
    const { parent } = node;

    // 函数节点
    switch (parent.type) {
      case 'FunctionExpression':
      case 'FunctionDeclaration':
      case 'ArrowFunctionExpression':
        // 调用 fixer 进行删除
        return fixer.remove(parent);
      ...
      ...
      default:
        return null;
    }
  };
  return problem;
});
```

目前会对以下几种节点类型进行删除：

- FunctionExpression

- FunctionDeclaration

- ArrowFunctionExpression

- ImportSpecifier

- ImportDefaultSpecifier

- ImportNamespaceSpecifier

- VariableDeclarator

- TSEnumDeclaration

后续新增节点的删除逻辑，只需要维护这个文件即可。

## 无用文件删除

之前基于 [webpack-deadcode-plugin](https://github.com/MQuy/webpack-deadcode-plugin) 做了一版无用代码删除，但是在实际使用的过程中，发现一些问题。

首先是 **速度太慢** ，这个插件会基于 webpack 编译的结果来分析哪些文件是无用的，每次使用都需要编译一遍项目。

而且前几天加入了 fork-ts-checker-webpack-plugin 进行类型检查之后， **这个删除方案突然失效了** ，检测出来的只有 .less 类型的无用文件，经过和排查后发现是这个插件的锅，它会把 **src** **目录下的所有** **ts** **文件** 都加入到 webpack 的依赖中，也就是 `compilation.fileDependencies` （可以尝试开启这个插件，在开发环境试着手动改一个完全未导入的 ts 文件，一样会触发重新编译）

而 deadcode-plugin 就是依赖 `compilation.fileDependencies` 这个变量来判断哪些文件未被使用，所有 ts 文件都在这个变量中的话，扫描出来的无用文件自然就只有其他类型了。

这个行为应该是插件的官方有意而为之，考虑如下情况：

```javascript
// 直接导入一个 TS 类型
import { IProps } from "./type.ts";

// use IProps
```

在使用旧版的 fork-ts-checker-webpack-plugin 时，如果此时改动了 IProps 造成了类型错误，是不会触发 webpack 的编译报错的。

经过排查，目前官方的行为好像是把 tsconfig 中的 `include` 里的所有 ts 文件加入到依赖中，方便改动触发编译，而我们项目中的 `include` 是 `["src/**/*.ts"]` ，所以……

具体讨论可以查看这个 Issue： [Files that provide only type dependencies for main entry and unused files are not being checked for](https://github.com/TypeStrong/fork-ts-checker-webpack-plugin/issues/502)

### 方案

首先尝试在 deadcode 模式中手动删除 fork-ts-checker-webpack-plugin，这样可以扫描出无用依赖，但是上文中那样从文件中只导入类型的情况，还是会被认为是无用的文件而误删。

考虑到现实场景中单独建一个 type.ts 文件书写接口或类型的情况比较多，只好先放弃这个方案。

转而一想， [pzavolinsky/ts-unused-exports](https://github.com/pzavolinsky/ts-unused-exports) 这个工具既然都能分析出
所有文件的 **导入导出变量的依赖关系** ，那分析出未使用的文件应该也是小意思才对。

经过源码调试，大概梳理出了这个工具的原理：

1. 通过 TypeScript 内置的 `ts.parseJsonConfigFileContent` API 扫描出项目内完整的 ts 文件路径。

```json
[
  {
    "path": "src/component/A",
    "fullPath": "/Users/admin/works/test/src/component/A.tsx",
  },
  {
    "path": "src/component/B",
    "fullPath": "/Users/admin/works/test/apps/app/src/component/B.tsx",
  }
]
...
```

2. 通过 TypeScript 内置的一些 compile API 分析出文件之间的 exports 和 imports 关系。

```json
[{
  "path": "src/component/A",
  "fullPath": "/Users/admin/works/test/src/component/A.tsx",
  "imports": {
    "styled-components": ["default"],
    "react": ["default"],
    "src/components/B": ["TestComponentB"]
  },
  "exports": ["TestComponentA"]
}]
```

3. 根据上述信息来分析出每个文件中每个变量的使用次数，筛选出未使用的变量并且输出。

到此思路也就有了，把所有文件中的 `imports` 信息取一个合集，然后从第一步的文件集合中找出未出现在 `imports` 里的文件即可。

## 一些值得一提的改造

### 循环删除文件

在第一次检测出无用文件并删除后，很可能会暴露出一些新的无用文件。
比如以下这样的例子：

```json
[
  {
    "path": "a",
    "imports": "b"
  },
  {
    "path": "b",
    "imports": "c"
  },
  {
    "path": "c"
  }
]
```

文件 a 引入了文件 b，文件 b 引入了文件 c。

第一轮扫描的时候，没有任何文件引入 a，所以会把 a 视作无用文件。

由于 a 引入了 b，所以不会把 b 视作无用的文件，同理 c 也不会视作无用文件。

所以 **第一轮删除只会删掉 a 文件** 。

只要在每次删除后，把 files 范围缩小，比如第一次删除了 a 以后，files 只留下：

```javascript
[
  {
    path: "b",
    imports: "c",
  },
  {
    path: "c",
  },
];
```

此时会发现没有文件再引入 b 了，b 也会被加入无用文件的列表，再重复此步骤，即可删除 c 文件。

### 支持 Monorepo

原项目只考虑到了单个项目和单个 tsconfig 的处理，而如今 monorepo 已经非常流行了，monorepo 中每个项目都有自己的 tsconfig，形成一个自己的 project，而经常有项目 A 里的文件或变量被项目 B 所依赖使用的情况。

而如果单独扫描单个项目内的文件，就会把很多被子项目使用的文件误删掉。

这里的思路也很简单：

1. 增加 `--deps` 参数，允许传入多个子项目的 tsconfig 路径。

2. 过滤子项目扫描出的 `imports` 部分，找出从别名为 `@main`的主项目中引入的依赖（比如 `import { Button } from '@main/components'`）

3. 把这部分 `imports` 合并到主项目的依赖集合中，共同进行接下来的扫描步骤。

### 支持自定义文件扫描

TypeScript 提供的 API，默认只会扫描 `.ts, .tsx` 后缀的文件，在开启 `allowJS` 选项后也会扫描 `.js, .jsx` 后缀的文件。
而项目中很多的 `.less, .svg` 的文件也都未被使用，但它们都被忽略掉了。

这里我断点跟进 `ts.parseJsonConfigFileContent` 函数内部，发现有一些比较隐蔽的参数和逻辑，用比较 hack 的方式支持了自定义后缀。

当然，这里还涉及到了一些比较麻烦的改造，比如这个库原本是没有考虑 `index.ts, index.less` 同时存在这种情况的，通过源码的一些改造最终绕过了这个限制。

**目前默认支持了** `.less, .sass, .scss` **这些类型文件的扫描** ，只要你确保该后缀的引入都是通过 `import` 语法，那么就可以通过增加的 `extraFileExtensions` 配置来增加自定义后缀。

```javascript
import * as ts from "typescript";

const result = ts.parseJsonConfigFileContent(
  parseJsonResult.config,
  ts.sys,
  basePath,
  undefined,
  undefined,
  undefined,
  extraFileExtensions?.map((extension) => ({
    extension,
    isMixedContent: false,
    // hack ways to scan all files
    scriptKind: ts.ScriptKind.Deferred,
  }))
);
```

## 其他方案：ts-prune

[ts-prune](https://github.com/nadeesha/ts-prune) 是完全基于 TypeScript 服务实现的一个 dead exports 检测方案。

### 背景

TypeScript 服务提供了一个实用的 API： [findAllReferences](https://github.com/microsoft/TypeScript/blob/main/src/services/findAllReferences.ts) ，我们平时在 VSCode 里右键点击一个变量，选择 “Find All References” 时，就会调用这个底层 API 找出所有的引用。

[ts-morph](https://github.com/dsherret/ts-morph) 这个库封装了包括 `findAllReferences` 在内的一些底层 API，提供更加简洁易用的调用方式。

ts-prune 就是基于 ts-morph 封装而成。

一段最简化的基于 ts-morph 的检测 dead exports 的代码如下：

```javascript
// this could be improved... (ex. ignore interfaces/type aliases that describe a parameter type in the same file)
import { Project, TypeGuards, Node } from "ts-morph";

const project = new Project({ tsConfigFilePath: "tsconfig.json" });

for (const file of project.getSourceFiles()) {
  file.forEachChild((child) => {
    if (TypeGuards.isVariableStatement(child)) {
      if (isExported(child)) child.getDeclarations().forEach(checkNode);
    } else if (isExported(child)) checkNode(child);
  });
}

function isExported(node: Node) {
  return TypeGuards.isExportableNode(node) && node.isExported();
}

function checkNode(node: Node) {
  if (!TypeGuards.isReferenceFindableNode(node)) return;

  const file = node.getSourceFile();
  if (
    node.findReferencesAsNodes().filter((n) => n.getSourceFile() !== file)
      .length === 0
  )
    console.log(
      `[${file.getFilePath()}:${node.getStartLineNumber()}: ${
        TypeGuards.hasName(node) ? node.getName() : node.getText()
      }`
    );
}
```

### 优点

1. TS 的服务被各种 IDE 集成，经过无数大型项目检测，可靠性不用多说。

2. 不需要像 ESLint 方案那样，额外检测变量在文件内是否使用， `findAllReferences` 的检测范围包括文件内部，开箱即用。

### 缺点

1. **速度慢** ，TSProgram 的初始化，以及 `findAllReferences` 的调用，在大型项目中速度还是有点慢。

2. **文档和规范比较差** ，ts-morph 的文档还是太简陋了，挺多核心的方法没有文档描述，不利于维护。

3. **模块语法不一致** ，TypeScript 的 `findAllReferences` 并不识别 Dynamic Import 语法，需要额外处理 `import()` 形式导入的模块。

4. **删除方案难做** ，ts-prune 封装了相对完善的 dead exports 检测方案，但作者似乎没有做自动删除方案的意思。这时 **第二点的劣势**就出来了，按照文档来探索删除方案非常艰难。看起来有个德国的小哥 [好不容易说服作者](https://github.com/nadeesha/ts-prune/pull/67) 提了一个自动删除的 MR：[Add a fix mode that automatically fixes unused exports (revival)](https://github.com/nadeesha/ts-prune/pull/104) ，但是最后因为内存溢出没通过 GithubCI，不了了之了。我个人把这套代码 fork 下来在公司内部的大型项目中跑了一下，也确实是**内存溢出** ，看了下自动修复方案的代码，也都是很常规的基于 ts-morph 的 API 调用，猜测是底层 API 的性能问题？

所以综合评估下来，最后还是选择了 ts-unused-exports + ESLint 的方案。

## 最后
我们是字节跳动的 Web Infrastructure Team，作为公司的基础技术团队，我们的目标是提供优秀的技术解决方案，助力公司业务成长，同时打造开放的技术生态，推动公司和业界前端技术的发展。目前团队主要专注的方向包括 [现代 Web 开发解决方案、低代码搭建](https://zhuanlan.zhihu.com/p/88616149)、Serverless、[跨端解决方案](https://tzxhy.github.io/2020/02/19/%E5%85%B3%E4%BA%8E%E8%B7%A8%E7%AB%AF%E6%96%B9%E6%A1%88%E7%9A%84%E8%B0%83%E7%A0%94/)、终端基础体验、ToB 等等，已经在多个地方设立了研发团队，包括 北京、上海、杭州、广州、深圳、新加坡。

团队专栏：<https://zhuanlan.zhihu.com/bytedancer>

投递 wx：sshsunlight

**部分团队成员：**

-   <https://github.com/leeight> (Team Leader)
-   <https://github.com/dexteryy> (JS Hacker, SF/F Nerd)
-   <https://github.com/underfin> (Vue.js Core Contributor)
-   <https://github.com/Amour1688> (Vue.js Contributor)
-   <https://github.com/oyyd> (Node.js Core Contributor)
-   <https://github.com/theanarkh> (Node.js Advocate)
-   <https://github.com/leizongmin> (Node.js Advocate)
-   <https://github.com/losfair> (WebAssembly)
-   <https://github.com/Brooooooklyn> (Rust & https://napi.rs/)
-   <https://github.com/amio>
-   <https://github.com/niudai> & <https://www.zhihu.com/people/niu-dai-68-44>
-   <https://github.com/protoman92>
