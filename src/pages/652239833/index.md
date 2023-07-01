---
title: '前端算法进阶指南'
date: '2020-07-07'
spoiler: ''
---

## 前言

最近国内大厂面试中，出现 `LeetCode` 真题考察的频率越来越高了。我也观察到有越来越多的前端同学开始关注算法这个话题。

但是算法是一个门槛很高的东西，在一个算法新手的眼里，它的智商门槛要求很高。事实上是这个样子的吗？如果你怀疑自己的**智商不够**去学习算法，那么你一定要先看完这篇文章：[《天生不聪明》](https://mp.weixin.qq.com/s/QvXIDpyrpiOmvEhcOUUmxQ)，也正是这篇文章激励了我开始了算法之路。

这篇文章，我会先总结几个**必学的题目分类**，给出**这个分类下必做例题**的详细题解，并且在文章的末尾给出**每个分类下必刷的题目**的获取方式。

一定要耐心看到底，会有重磅干货。

## 心路

我从 5 月份准备离职的时候开始学习算法，在此之前对于算法我是**零基础**，在最开始我对于算法的感受也和大家一样，觉得自己智商可能不够，望而却步。但是看了一些大佬对于算法和智商之间的关系，我发现算法好像也是一个通过练习可以慢慢成长的学科，而不是只有智商达到了某个点才能有入场券，所以我开始了我的算法之路。通过**视频课程** + **分类刷题** + **总结题解** + **回头复习**的方式，我在两个月的时间里把力扣的解题数量刷到了**200**题。对于一个算法新人来说，这应该算是一个还可以的成绩，这篇文章，我把我总结的一些经典题解分享给大家。

## 学习方式

1. **分类刷题**：很多第一次接触力扣的同学对于刷题的方法不太了解，有的人跟着题号刷，有的人跟着每日一题刷，但是这种漫无目的的刷题方式一般都会在中途某一天放弃，或者刷了很久但是却发现没什么沉淀。这里不啰嗦，直接点明一个所有大佬都推荐的刷题方法：把自己的学习阶段分散成几个时间段去刷不同分类的题型，比如第一周专门解**链表**相关题型，第二周专门解**二叉树**相关题型。这样你的知识会形成一个体系，通过一段时间的刻意练习把这个题型相关的知识点强化到你的脑海中，不容易遗忘。

2. **适当放弃**：很多同学遇到一个难题，非得埋头钻研，干他 2 个小时。最后挫败感十足，久而久之可能就放弃了算法之路。要知道算法是个沉淀了几十年的领域，题解里的某个算法可能是某些教授研究很多年的心血，你想靠自己一个新手去想出来同等优秀的解法，岂不是想太多了。所以要学会适当放弃，一般来说，比较有目的性（面试）刷题的同学，他面对一道新的题目毫无头绪的话，会在 10 分钟之内直接放弃去看题解，然后记录下来，**反复复习**，直到这个解法成为自己的知识为止。这是效率最高的学习办法。
3. **接受自己是新手**：没错，说的难听一点，接受自己不是天才这个现实。你在刷题的过程中会遇到很多困扰你的时候，比如相同的题型已经看过例题，**稍微变了条件就解不出来**。或者对于一个 **`easy` 难度的题毫无头绪**。或者甚至**看不懂别人的题解**（没错我经常）相信我，这很正常，不能说明你不适合学习算法，只能说明算法确实是一个博大精深的领域，把自己在其他领域的沉淀抛开来，接受自己是新手这个事实，多看题解，多请教别人。

## 分类大纲

1. 算法的复杂度分析。
2. 排序算法，以及他们的区别和优化。
3. 数组中的双指针、滑动窗口思想。
4. 利用 Map 和 Set 处理查找表问题。
5. 链表的各种问题。
6. 利用递归和迭代法解决二叉树问题。
7. 栈、队列、DFS、BFS。
8. 回溯法、贪心算法、动态规划。

## 题解

接下来我会放出几个分类的经典题型，以及我对应的讲解，当做开胃菜，并且在文章的末尾我会给出获取每个分类**推荐你去刷**的题目的合集，记得看到底哦。

### 查找表问题

两个数组的交集 II-350

给定两个数组，编写一个函数来计算它们的交集。

```
示例 1:

输入: nums1 = [1,2,2,1], nums2 = [2,2]
输出: [2,2]
示例 2:

输入: nums1 = [4,9,5], nums2 = [9,4,9,8,4]
输出: [4,9]
```

来源：力扣（LeetCode）  
链接：https://leetcode-cn.com/problems/intersection-of-two-arrays-ii  
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

为两个数组分别建立 map，用来存储 num -> count 的键值对，统计每个数字出现的数量。

然后对其中一个 map 进行遍历，查看这个数字在两个数组中分别出现的数量，取出现的最小的那个数量（比如数组 1 中出现了 1 次，数组 2 中出现了 2 次，那么交集应该取 1 次），push 到结果数组中即可。

```js
/**
 * @param {number[]} nums1
 * @param {number[]} nums2
 * @return {number[]}
 */
let intersect = function (nums1, nums2) {
  let map1 = makeCountMap(nums1)
  let map2 = makeCountMap(nums2)
  let res = []
  for (let num of map1.keys()) {
    const count1 = map1.get(num)
    const count2 = map2.get(num)

    if (count2) {
      const pushCount = Math.min(count1, count2)
      for (let i = 0; i < pushCount; i++) {
        res.push(num)
      }
    }
  }
  return res
}

function makeCountMap(nums) {
  let map = new Map()
  for (let i = 0; i < nums.length; i++) {
    let num = nums[i]
    let count = map.get(num)
    if (count) {
      map.set(num, count + 1)
    } else {
      map.set(num, 1)
    }
  }
  return map
}
```

### 双指针问题

最接近的三数之和-16

给定一个包括  n 个整数的数组  nums  和 一个目标值  target。找出  nums  中的三个整数，使得它们的和与  target  最接近。返回这三个数的和。假定每组输入只存在唯一答案。

```
示例：

输入：nums = [-1,2,1,-4], target = 1
输出：2
解释：与 target 最接近的和是 2 (-1 + 2 + 1 = 2) 。
```

提示：

`3 <= nums.length <= 10^3`
`-10^3 <= nums[i] <= 10^3`
`-10^4 <= target <= 10^4`

来源：力扣（LeetCode）

链接：https://leetcode-cn.com/problems/3sum-closest

著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

先按照升序排序，然后分别从左往右依次选择一个基础点 `i`（`0 <= i <= nums.length - 3`），在基础点的右侧用双指针去不断的找最小的差值。

假设基础点是 `i`，初始化的时候，双指针分别是：

- **`left`**：`i + 1`，基础点右边一位。
- **`right`**: `nums.length - 1` 数组最后一位。

然后求此时的和，如果和大于 `target`，那么可以把右指针左移一位，去试试更小一点的值，反之则把左指针右移。

在这个过程中，不断更新全局的最小差值 `min`，和此时记录下来的和 `res`。

最后返回 `res` 即可。

```js
/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number}
 */
let threeSumClosest = function (nums, target) {
  let n = nums.length
  if (n === 3) {
    return getSum(nums)
  }
  // 先升序排序 此为解题的前置条件
  nums.sort((a, b) => a - b)

  let min = Infinity // 和 target 的最小差
  let res

  // 从左往右依次尝试定一个基础指针 右边至少再保留两位 否则无法凑成3个
  for (let i = 0; i <= nums.length - 3; i++) {
    let basic = nums[i]
    let left = i + 1 // 左指针先从 i 右侧的第一位开始尝试
    let right = n - 1 // 右指针先从数组最后一项开始尝试

    while (left < right) {
      let sum = basic + nums[left] + nums[right] // 三数求和
      // 更新最小差
      let diff = Math.abs(sum - target)
      if (diff < min) {
        min = diff
        res = sum
      }
      if (sum < target) {
        // 求出的和如果小于目标值的话 可以尝试把左指针右移 扩大值
        left++
      } else if (sum > target) {
        // 反之则右指针左移
        right--
      } else {
        // 相等的话 差就为0 一定是答案
        return sum
      }
    }
  }

  return res
}

function getSum(nums) {
  return nums.reduce((total, cur) => total + cur, 0)
}
```

### 滑动窗口问题

无重复字符的最长子串-3

给定一个字符串，请你找出其中不含有重复字符的   最长子串   的长度。

示例  1:

```
输入: "abcabcbb"
输出: 3
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。
```

示例 2:

```
输入: "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。
```

示例 3:

```
输入: "pwwkew"
输出: 3
解释: 因为无重复字符的最长子串是 "wke"，所以其长度为 3。
     请注意，你的答案必须是 子串 的长度，"pwke" 是一个子序列，不是子串。
```

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/longest-substring-without-repeating-characters
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

这题是比较典型的滑动窗口问题，定义一个左边界 `left` 和一个右边界 `right`，形成一个窗口，并且在这个窗口中保证不出现重复的字符串。

这需要用到一个新的变量 `freqMap`，用来记录窗口中的字母出现的频率数。在此基础上，先尝试取窗口的右边界再右边一个位置的值，也就是 `str[right + 1]`，然后拿这个值去 `freqMap` 中查找：

1. 这个值没有出现过，那就直接把 `right ++`，扩大窗口右边界。
2. 如果这个值出现过，那么把 `left ++`，缩进左边界，并且记得把 `str[left]` 位置的值在 `freqMap` 中减掉。

循环条件是 `left < str.length`，允许左边界一直滑动到字符串的右界。

```js
/**
 * @param {string} s
 * @return {number}
 */
let lengthOfLongestSubstring = function (str) {
  let n = str.length
  // 滑动窗口为s[left...right]
  let left = 0
  let right = -1
  let freqMap = {} // 记录当前子串中下标对应的出现频率
  let max = 0 // 找到的满足条件子串的最长长度

  while (left < n) {
    let nextLetter = str[right + 1]
    if (!freqMap[nextLetter] && nextLetter !== undefined) {
      freqMap[nextLetter] = 1
      right++
    } else {
      freqMap[str[left]] = 0
      left++
    }
    max = Math.max(max, right - left + 1)
  }

  return max
}
```

### 链表问题

两两交换链表中的节点-24

给定一个链表，两两交换其中相邻的节点，并返回交换后的链表。

你不能只是单纯的改变节点内部的值，而是需要实际的进行节点交换。

示例:

```
给定 1->2->3->4, 你应该返回 2->1->4->3.
```

来源：力扣（LeetCode）

链接：https://leetcode-cn.com/problems/swap-nodes-in-pairs

著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

这题本意比较简单，`1 -> 2 -> 3 -> 4` 的情况下可以定义一个递归的辅助函数 `helper`，这个辅助函数对于节点和它的下一个节点进行交换，比如 `helper(1)` 处理 `1 -> 2`，并且把交换变成 `2 -> 1` 的尾节点 `1`的`next`继续指向 `helper(3)`也就是交换后的 `4 -> 3`。

边界情况在于，如果顺利的作了两两交换，那么交换后我们的函数返回出去的是 **交换后的头部节点**，但是如果是奇数剩余项的情况下，没办法做交换，那就需要直接返回 **原本的头部节点**。这个在 `helper`函数和主函数中都有体现。

```js
let swapPairs = function (head) {
  if (!head) return null
  let helper = function (node) {
    let tempNext = node.next
    if (tempNext) {
      let tempNextNext = node.next.next
      node.next.next = node
      if (tempNextNext) {
        node.next = helper(tempNextNext)
      } else {
        node.next = null
      }
    }
    return tempNext || node
  }

  let res = helper(head)

  return res || head
}
```

### 深度优先遍历问题

二叉树的所有路径-257

给定一个二叉树，返回所有从根节点到叶子节点的路径。

说明:  叶子节点是指没有子节点的节点。

示例:

```
输入:

   1
 /   \
2     3
 \
  5

输出: ["1->2->5", "1->3"]

解释: 所有根节点到叶子节点的路径为: 1->2->5, 1->3
```

来源：力扣（LeetCode）

链接：https://leetcode-cn.com/problems/binary-tree-paths

著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

用当前节点的值去拼接左右子树递归调用当前函数获得的所有路径。

也就是根节点拼上以左子树为根节点得到的路径，加上根节点拼上以右子树为根节点得到的所有路径。

直到叶子节点，仅仅返回包含当前节点的值的数组。

```js
let binaryTreePaths = function (root) {
  let res = []
  if (!root) {
    return res
  }

  if (!root.left && !root.right) {
    return [`${root.val}`]
  }

  let leftPaths = binaryTreePaths(root.left)
  let rightPaths = binaryTreePaths(root.right)

  leftPaths.forEach((leftPath) => {
    res.push(`${root.val}->${leftPath}`)
  })
  rightPaths.forEach((rightPath) => {
    res.push(`${root.val}->${rightPath}`)
  })

  return res
}
```

### 广度优先遍历（BFS）问题

在每个树行中找最大值-515

https://leetcode-cn.com/problems/find-largest-value-in-each-tree-row

您需要在二叉树的每一行中找到最大的值。

```
输入:

          1
         / \
        3   2
       / \   \
      5   3   9

输出: [1, 3, 9]

```

----

这是一道典型的 BFS 题目，BFS 的套路其实就是维护一个 queue 队列，在读取子节点的时候同时把发现的孙子节点 push 到队列中，但是**先不处理**，等到这一轮队列中的子节点处理完成以后，下一轮再继续处理的就是**孙子节点**了，这就实现了层序遍历，也就是一层层的去处理。

但是这里有一个问题卡住我了一会，就是如何知道当前处理的节点是**哪个层级**的，在最开始的时候我尝试写了一下二叉树求某个 index 所在层级的公式，但是发现这种公式只能处理「平衡二叉树」。

后面看题解发现他们都没有专门维护层级，再仔细一看才明白层级的思路：

其实就是在每一轮 while 循环里，再开一个 for 循环，这个 for 循环的终点是「提前缓存好的 length 快照」，也就是进入这轮 while 循环时，queue 的长度。其实这个长度就恰好代表了「一个层级的长度」。

缓存后，for 循环里可以安全的把子节点 push 到数组里而不影响缓存的当前层级长度。

另外有一个小 tips，在 for 循环处理完成后，应该要把 queue 的长度截取掉上述的缓存长度。一开始我使用的是 `queue.splice(0, len)`，结果速度只击败了 33%的人。后面换成 for 循环中去一个一个`shift`来截取，速度就击败了 77%的人。

```js
/**
 * @param {TreeNode} root
 * @return {number[]}
 */
let largestValues = function (root) {
  if (!root) return []
  let queue = [root]
  let maximums = []

  while (queue.length) {
    let max = Number.MIN_SAFE_INTEGER
    // 这里需要先缓存length 这个length代表当前层级的所有节点
    // 在循环开始后 会push新的节点 length就不稳定了
    let len = queue.length
    for (let i = 0; i < len; i++) {
      let node = queue[i]
      max = Math.max(node.val, max)

      if (node.left) {
        queue.push(node.left)
      }
      if (node.right) {
        queue.push(node.right)
      }
    }

    // 本「层级」处理完毕，截取掉。
    for (let i = 0; i < len; i++) {
      queue.shift()
    }

    // 这个for循环结束后 代表当前层级的节点全部处理完毕
    // 直接把计算出来的最大值push到数组里即可。
    maximums.push(max)
  }

  return maximums
}
```

### 栈问题

有效的括号-20

给定一个只包括 `'('，')'，'{'，'}'，'['，']'` 的字符串，判断字符串是否有效。

有效字符串需满足：

- 左括号必须用相同类型的右括号闭合。
- 左括号必须以正确的顺序闭合。
- 注意空字符串可被认为是有效字符串。

示例 1:

```
输入: "()"
输出: true
```

示例 2:

```
输入: "()[]{}"
输出: true
```

示例 3:

```
输入: "(]"
输出: false
```

示例 4:

```
输入: "([)]"
输出: false
```

示例 5:

```
输入: "{[]}"
输出: true
```

https://leetcode-cn.com/problems/valid-parentheses

----

提前记录好左括号类型 `(, {, [`和右括号类型`), }, ]`的映射表，当遍历中遇到左括号的时候，就放入栈 `stack` 中（其实就是数组），当遇到右括号时，就把 `stack` 顶的元素 `pop` 出来，看一下是否是这个右括号所匹配的左括号（比如 `(` 和 `)` 是一对匹配的括号）。

当遍历结束后，栈中不应该剩下任何元素，返回成功，否则就是失败。

```js
/**
 * @param {string} s
 * @return {boolean}
 */
let isValid = function (s) {
  let sl = s.length
  if (sl % 2 !== 0) return false
  let leftToRight = {
    "{": "}",
    "[": "]",
    "(": ")",
  }
  // 建立一个反向的 value -> key 映射表
  let rightToLeft = createReversedMap(leftToRight)
  // 用来匹配左右括号的栈
  let stack = []

  for (let i = 0; i < s.length; i++) {
    let bracket = s[i]
    // 左括号 放进栈中
    if (leftToRight[bracket]) {
      stack.push(bracket)
    } else {
      let needLeftBracket = rightToLeft[bracket]
      // 左右括号都不是 直接失败
      if (!needLeftBracket) {
        return false
      }

      // 栈中取出最后一个括号 如果不是需要的那个左括号 就失败
      let lastBracket = stack.pop()
      if (needLeftBracket !== lastBracket) {
        return false
      }
    }
  }

  if (stack.length) {
    return false
  }
  return true
}

function createReversedMap(map) {
  return Object.keys(map).reduce((prev, key) => {
    const value = map[key]
    prev[value] = key
    return prev
  }, {})
}
```

### 递归与回溯

直接看我写的这两篇文章即可，递归与回溯甚至是平常业务开发中最常见的算法场景之一了，所以我重点总结了两篇文章。

[《前端电商 sku 的全排列算法很难吗？学会这个套路，彻底掌握排列组合。》](https://juejin.im/post/5ee6d9026fb9a047e60815f1)

[前端「N 皇后」递归回溯经典问题图解](https://juejin.im/post/5eeafa406fb9a058b51e60c0)

### 动态规划

打家劫舍 - 198

你是一个专业的小偷，计划偷窃沿街的房屋。每间房内都藏有一定的现金，影响你偷窃的唯一制约因素就是相邻的房屋装有相互连通的防盗系统，如果两间相邻的房屋在同一晚上被小偷闯入，系统会自动报警。

给定一个代表每个房屋存放金额的非负整数数组，计算你在不触动警报装置的情况下，能够偷窃到的最高金额。

```
示例 1:

输入: [1,2,3,1]
输出: 4
解释: 偷窃 1 号房屋 (金额 = 1) ，然后偷窃 3 号房屋 (金额 = 3)。
  偷窃到的最高金额 = 1 + 3 = 4 。
示例 2:

输入: [2,7,9,3,1]
输出: 12
解释: 偷窃 1 号房屋 (金额 = 2), 偷窃 3 号房屋 (金额 = 9)，接着偷窃 5 号房屋 (金额 = 1)。
  偷窃到的最高金额 = 2 + 9 + 1 = 12 。
```

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/house-robber
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

动态规划的一个很重要的过程就是找到「状态」和「状态转移方程」，在这个问题里，设 `i` 是当前屋子的下标，状态就是 **以 i 为起点偷窃的最大价值**

在某一个房子面前，盗贼只有两种选择：**偷或者不偷**。

1. 偷的话，价值就是「当前房子的价值」+「下两个房子开始盗窃的最大价值」
2. 不偷的话，价值就是「下一个房子开始盗窃的最大价值」

在这两个值中，选择**最大值**记录在 `dp[i]`中，就得到了**以 `i` 为起点所能偷窃的最大价值。**。

动态规划的起手式，找**基础状态**，在这题中，以**终点**为起点的最大价值一定是最好找的，因为终点不可能再继续往后偷窃了，所以设 `n` 为房子的总数量， `dp[n - 1]` 就是 `nums[n - 1]`，小偷只能选择偷窃这个房子，而不能跳过去选择下一个不存在的房子。

那么就找到了动态规划的状态转移方程：

```js
// 抢劫当前房子
robNow = nums[i] + dp[i + 2] // 「当前房子的价值」 + 「i + 2 下标房子为起点的最大价值」

// 不抢当前房子，抢下一个房子
robNext = dp[i + 1] //「i + 1 下标房子为起点的最大价值」

// 两者选择最大值
dp[i] = Math.max(robNow, robNext)
```

，并且**从后往前**求解。

```js
function (nums) {
  if (!nums.length) {
    return 0;
  }
  let dp = [];

  for (let i = nums.length - 1; i >= 0; i--) {
    let robNow = nums[i] + (dp[i + 2] || 0)
    let robNext = dp[i + 1] || 0

    dp[i] = Math.max(robNow, robNext)
  }

  return dp[0];
};
```

最后返回 **以 0 为起点开始打劫的最大价值** 即可。

### 贪心算法问题

分发饼干-455

假设你是一位很棒的家长，想要给你的孩子们一些小饼干。但是，每个孩子最多只能给一块饼干。对每个孩子 i ，都有一个胃口值  gi ，这是能让孩子们满足胃口的饼干的最小尺寸；并且每块饼干 j ，都有一个尺寸 sj 。如果 sj >= gi ，我们可以将这个饼干 j 分配给孩子 i ，这个孩子会得到满足。你的目标是尽可能满足越多数量的孩子，并输出这个最大数值。

注意：

你可以假设胃口值为正。
一个小朋友最多只能拥有一块饼干。

```
示例 1:

输入: [1,2,3], [1,1]

输出: 1

解释:
你有三个孩子和两块小饼干，3个孩子的胃口值分别是：1,2,3。
虽然你有两块小饼干，由于他们的尺寸都是1，你只能让胃口值是1的孩子满足。
所以你应该输出1。
示例 2:

输入: [1,2], [1,2,3]

输出: 2

解释:
你有两个孩子和三块小饼干，2个孩子的胃口值分别是1,2。
你拥有的饼干数量和尺寸都足以让所有孩子满足。
所以你应该输出2.
```

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/assign-cookies
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。

----

把饼干和孩子的需求都排序好，然后从最小的饼干分配给需求最小的孩子开始，不断的尝试新的饼干和新的孩子，这样能保证每个分给孩子的饼干都恰到好处的不浪费，又满足需求。

利用双指针不断的更新 `i` 孩子的需求下标和 `j`饼干的值，直到两者有其一达到了终点位置：

1. 如果当前的饼干不满足孩子的胃口，那么把 `j++` 寻找下一个饼干，不用担心这个饼干被浪费，因为这个饼干更不可能满足下一个孩子（胃口更大）。
2. 如果满足，那么 `i++; j++; count++` 记录当前的成功数量，继续寻找下一个孩子和下一个饼干。

```js
/**
 * @param {number[]} g
 * @param {number[]} s
 * @return {number}
 */
let findContentChildren = function (g, s) {
  g.sort((a, b) => a - b)
  s.sort((a, b) => a - b)

  let i = 0
  let j = 0

  let count = 0
  while (j < s.length && i < g.length) {
    let need = g[i]
    let cookie = s[j]

    if (cookie >= need) {
      count++
      i++
      j++
    } else {
      j++
    }
  }

  return count
}
```

## 必做题目

其实写了这么多，以上分类所提到的题目，只是当前分类下比较适合作为例题来讲解的题目而已，在整个 `LeetCode` 学习过程中只是冰山一角。这些题可以作为你深入这个分类的一个入门例题，但是不可避免的是，你必须去下苦功夫刷**每个分类下的其他经典题目**。

如果你信任我，你也可以[**点击这里**](https://github.com/sl1673495/leetcode-javascript) 获取我总结的各个分类下**必做题目**的详细题解，还有我推荐给你的一个**视频课程**。

算法这种逻辑复杂的东西，其实看文章也只是能做个引子，如果有老师耐心的讲解，配合动图演示过程，学习效率是**翻倍都不止**的。不瞒你说，我个人就是把上面推荐的那个视频课程完全跟着走了一遍，能感觉到比起看文章来说，效率是翻倍都不止的。因为有大牛老师耐心的带着你从零开始，由浅入深的配合动图去图文并茂的抽丝剥茧的讲清楚一道题，我**拿不到任何回扣**，甚至连那个老师的微信都没有，但我真心实意的推荐你去学这门课程。

## 总结

关于算法在工程方面有用与否的争论，已经是一个经久不衰的话题了。这里不讨论这个，我个人的观念是**绝对有用**的，只要你不是一个甘于只做简单需求的人，你一定会在后续开发架构、遇到难题的过程中或多或少的从你的算法学习中受益。

再说的功利点，就算是为了面试，刷算法能够进入大厂也是你职业生涯的一个起飞点，大厂给你带来的的环境、严格的 `Code Review`、完善的导师机制和协作流程也是你作为**工程师**所梦寐以求的。

希望这篇文章能让你不再继续害怕算法面试，跟着我一起攻下这座城堡吧，大家加油！

## ❤️ 感谢大家

1.如果本文对你有帮助，就点个赞支持下吧，你的「赞」是我创作的动力。

2.关注公众号「前端从进阶到入院」即可加我好友，我拉你进「前端进阶交流群」，大家一起共同交流和进步。

![](https://user-gold-cdn.xitu.io/2020/4/5/17149cbcaa96ff26?w=910&h=436&f=jpeg&s=78195)
