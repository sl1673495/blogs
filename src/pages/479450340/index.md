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