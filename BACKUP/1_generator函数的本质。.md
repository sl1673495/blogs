# [generator函数的本质。](https://github.com/sl1673495/blogs/issues/1)

异步流程控制器。

1. [ generator函数介绍](http://www.ruanyifeng.com/blog/2015/04/generator.html)

2. [Thunk 函数的含义和用法](http://www.ruanyifeng.com/blog/2015/05/thunk.html)
```js
// 正常版本的readFile（多参数版本）
fs.readFile(fileName, callback);

// Thunk版本的readFile（单参数版本）
var readFileThunk = Thunk(fileName);
readFileThunk(callback);

var Thunk = function (fileName){
  return function (callback){
    return fs.readFile(fileName, callback); 
  };
};
```

Thunkify 后的函数只接受callback作为单参数，为自动执行规范化了参数，做了铺垫。

3. [co 函数库的含义和用法](http://www.ruanyifeng.com/blog/2015/05/co.html)

4. [async 函数的含义和用法](http://www.ruanyifeng.com/blog/2015/05/async.html)