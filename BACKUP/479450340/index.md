---
title: '英文技术文章阅读。'
date: '2019-08-12'
spoiler: ''
---

https://medium.com/@martin_hotell/10-typescript-pro-tips-patterns-with-or-without-react-5799488d6680
React +  TypeScript 10个需要避免的错误模式。

https://medium.com/scrum-ai/4-testing-koa-server-with-jest-week-5-8e980cd30527
单元测试TypeScript + Koa的实践

https://kentcdodds.com/blog/profile-a-react-app-for-performance
React使用DevTools分析性能的一些注意事项

https://kentcdodds.com/blog/optimize-react-re-renders
React中优化组件重渲染，这里有几个隐含的知识点。
1. React组件每次createElement，会生成一份新的props引用。
2. 如果React在re-render中发现一个组件的type和props都保持了相同的引用，就会跳过这个组件的重渲染。
这篇文章中提到的具体的优化策略是把
```js
function Counter() {
  const [count, setCount] = React.useState(0)
  const increment = () => setCount(c => c + 1)
  return (
    <div>
      <button onClick={increment}>The count is {count}</button>
      <Logger label="counter" />
    </div>
  )
}
```
改成
```js
function Counter(props) {
  const [count, setCount] = React.useState(0)
  const increment = () => setCount(c => c + 1)
  return (
    <div>
      <button onClick={increment}>The count is {count}</button>
      {props.logger}
    </div>
  )
}
```
然后把Logger组件的创建提到外层，而不要放在setCount会影响到的作用域下，这样logger组件就不会重新渲染了。

https://kentcdodds.com/blog/the-state-reducer-pattern-with-react-hooks
React Hooks的自定义hook中，如何利用reducer的模式提供更加灵活的数据管理，让用户拥有数据的控制权。

https://mariusschulz.com/blog/const-assertions-in-literal-expressions-in-typescript
TypeScript中的const常量声明和let变量声明的类型区别，以及as const的应用。

https://github.com/piotrwitek/react-redux-typescript-guide#react---type-definitions-cheatsheet
React-Redux + TypeScript 的备忘录。

https://github.com/typescript-cheatsheets/react-typescript-cheatsheet
React + TypeScript 进阶用法备忘录。

https://blog.echobind.com/integrating-prettier-eslint-airbnb-style-guide-in-vscode-47f07b5d7d6a
在项目中集成Prettier + ESLint + Airbnb Style Guide

https://levelup.gitconnected.com/setting-up-eslint-with-prettier-typescript-and-visual-studio-code-d113bbec9857
在项目中集成ESLint with Prettier, TypeScript

---

https://kentcdodds.com/blog/when-to-break-up-a-component-into-multiple-components
何时应该把代码拆分为组件。

https://blog.logrocket.com/rxjs-with-react-hooks-for-state-management/
rxjs + hooks实现一个简单的聊天系统。

https://kentcdodds.com/blog/understanding-reacts-key-prop
在React中巧用key来控制组件的重新创建。

---


https://vue-composition-api-rfc.netlify.com/#logic-extraction-and-reuse
vue composition api 这部分主要讲述了Code Organization的改变，based on option type -> based on logical concern


---

https://vue-composition-api-rfc.netlify.com
 vue composition api 阅读完成。

---

https://medium.com/javascript-scene/master-the-javascript-interview-what-s-the-difference-between-class-prototypal-inheritance-e4cd0a7562e9
描述了组合比继承更好的地方。

> “…the problem with object-oriented languages is they’ve got all this implicit environment that they carry around with them. You wanted a banana but what you got was a gorilla holding the banana and the entire jungle.” ~ Joe Armstrong — “Coders at Work”

> 面向对象语言的问题在于它们带来了所有这些隐含的环境。
你想要一个香蕉，但你得到的是拿着香蕉和整个丛林的大猩猩。

---

https://nextjs.org/learn/basics/getting-started
nextjs官方文档的学习任务全部做完，包括基础和进阶。

---

https://medium.com/swlh/clean-up-redux-code-with-react-redux-hooks-71587cfcf87a
react-redux提供的hook让我们摆脱了connect高阶组件和很多样板代码，nice~

---

https://kentcdodds.com/blog/fix-the-slow-render-before-you-fix-the-re-render
在解决重渲染之前，先解决过慢的渲染。

---

https://kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster/
仔细思考你的React应用中，状态应该放在什么位置，是组件自身，提升到父组件，亦或是局部context和redux，这会有益于提升应用的性能和可维护性。

---

https://kentcdodds.com/blog/dont-sync-state-derive-it
仔细思考React组件中的状态应该如何管理，优先使用派生状态，并且在适当的时候利用useMemo、reselect等库去优化他们。

---

https://www.bluematador.com/blog/how-to-share-variables-between-js-and-sass
在webpack构建的项目中实现css和js共享sass变量。

---

https://github.com/vuejs/rfcs/issues/89
132提出了vue3中为何取消time slice的疑问，
尤雨溪从react和vue在原理层面的差异出发解释了这个问题。

---

https://stackoverflow.com/questions/28818849/how-do-the-different-enum-variants-work-in-typescript
ts官方团队的[Ryan Cavanaugh](https://stackoverflow.com/users/1704166/ryan-cavanaugh)回答关于ts中enum 和 declare enum的一些区别。

> Remember the golden rule: Never declare things that don't actually exist
不要用declare去声明运行时不存在的东西。

---

https://artsy.github.io/blog/2018/11/21/conditional-types-in-typescript/
ts 泛型继承的分配 还需要进一步理解