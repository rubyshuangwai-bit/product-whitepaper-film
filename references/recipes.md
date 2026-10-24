# 可运行的动画配方

包内提供 [动画函数库](../assets/motion/pwf-motion.js)、[基础四镜示例](../examples/gallery.html) 和 [新配方展示片源码](../examples/recipe-gallery.html)。参考网站、独立实现方式和验证边界见 [配方来源](recipe-sources.md)。

## 选择配方

| 要讲什么 | 选择 | 注意 |
|---|---|---|
| 从整体挑出重点，再回到整体 | `PWFRecipes.layout` | 坐标和缩放由分镜给定；截图阅读时保持稳定 |
| 接入、支撑、层间职责关系 | `PWFRecipes.stroke` | 只画有资料依据的关系，线路不穿过可见文字 |
| 方向、传递、汇聚与到达 | `PWFRecipes.follow` | 与stroke配合；光点是解释层，不冒充实机运行证据 |
| 口播带出若干完整观点 | `PWFRecipes.lines` | HTML中预写完整行，时间对应真实口播，不强制逐字打散 |

```js
// 透明度初始状态放在 CSS。文字行使用 overflow:hidden 的父容器。
PWFRecipes.layout(tl, [{target:'#screen',
  from:{x:0,y:0,scale:1}, to:{x:400,y:-100,scale:.5}}], 6.2,
  {duration:.85,stagger:0,ease:'expo.inOut'});
PWFRecipes.stroke(tl, '#connector', 7.1, {from:0,to:1,duration:.8});
PWFRecipes.follow(tl, '#dot', '#connector', 8.0, {duration:1.2});
PWFRecipes.lines(tl, ['#line1','#line2'], [1.2,3.4], {duration:.65});
```

这四个配方只需要现有GSAP，不另行引入Flip、SplitText或Anime.js插件。SVG path与circle须在相同坐标空间，路径先写入HTML；不要在播放中动态生成随机几何或更改DOM布局。

## 创建与验证展示片

```bash
python3 scripts/film.py example /absolute/path/new-recipes --template recipes --fetch-fonts
python3 scripts/film.py preview /absolute/path/new-recipes/film --port 3040
python3 scripts/film.py render /absolute/path/new-recipes/film --out /absolute/path/new-recipes/output/demo.mp4
node scripts/verify_recipes.cjs
```

不指定 `--template recipes` 则保留原有16秒基础示例。示例均为通用示意；替换内容时重新核对产品事实、口播时间和读图停留。修改文案后运行 `film.py fonts` 更新字体子集。

## 原基础函数仍可用

`PWF.reveal` 信息入场、`mask` 蒙版揭示、`draw` 完整线条绘制、`signal` 显式折线路径、`steps` 依次建立步骤、`focus` 真实控件强调、`reflow` 简单归位、`camera` 镜头层调整、`count` 有证据的数据变化。曲线路径与参数化布局可用于更复杂的内容推进。

不要只替换标题便沿用不适用的模型或硬件结构。布局、配方参数和画面素材都应服从当前产品内容。动作库的数量不是审美结论；新内容需渲染后看图，包含语音时还需口画同步与试听。
