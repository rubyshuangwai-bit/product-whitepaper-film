# 新配方来源、实现与验证

公开技术概念及实现对应关系如下。下面区分“参考的公开技术概念”和“包内实现”；没有从网页整段搬运插件或示例代码，也未打包外部示例图片。

| 配方 / 包内函数 | 概念来源 | 本版实现与适用场景 |
|---|---|---|
| 布局重组 `PWFRecipes.layout` | [GSAP Flip](https://gsap.com/docs/v3/Plugins/Flip/)、[Codrops GridLayoutAnimation](https://github.com/codrops/GridLayoutAnimation) | 借鉴布局前后状态过渡思路，调用者显式传入 from/to 坐标、缩放与透明度，不依赖点击事件或运行时重新测量DOM。用于截图展开与归位，不声称实现完整Flip插件 |
| 关系线 `PWFRecipes.stroke` | [Anime.js createDrawable](https://animejs.com/documentation/svg/createdrawable/) | 使用浏览器 SVG 长度和 GSAP dashoffset 改变可见线段，支持0–1进度，不引入Anime.js运行库。用于按叙述建立关系 |
| 沿线运动 `PWFRecipes.follow` | [Anime.js createMotionPath](https://animejs.com/documentation/svg/createmotionpath/) | 使用 SVG getPointAtLength 从时间轴代理进度计算圆点位置；支持曲线和折线，不使用浏览器实时循环。用于概念流向示意，不表示实测时延 |
| 文字分层 `PWFRecipes.lines` | [GSAP SplitText](https://gsap.com/docs/v3/Plugins/SplitText/) 的分层文字动画思路 | 文字行在HTML中预先写好，外层蒙版、内层按口播时间揭示；不使用或复制SplitText插件。不自动拆中文词语，不破坏已编辑的文本元素 |

以上四函数为本项目新写代码，保留技术来源说明；GSAP引擎仍是独立第三方运行依赖。Codrops该仓库的代码标注 [MIT](https://github.com/codrops/GridLayoutAnimation/blob/main/LICENSE)，[Anime.js引擎](https://github.com/juliangarnier/anime)标注MIT；这不等于所有网页文字、图片和GSAP插件都改为MIT。当前仅参考概念，未捆绑这些库的源码。

## 可运行示例

- `examples/recipe-gallery.html`：28秒，四类配方各7秒，通用说明内容。
- `assets/motion/pwf-motion.js`：9个基础函数与4个参数化配方。
- `scripts/verify_recipes.cjs`：以实际配置的GSAP测试任意时间定位、前进/后退重算、曲线路径、部分描线、布局落点、文字行及无效参数。使用模拟SVG几何，不能代替浏览器画面检查。

实际使用时渲染、解码并逐镜检查布局与可读性。自动检查不等于视觉观感验收。
