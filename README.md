# Product Whitepaper Film

**把产品白皮书，变成客户看得懂的产品宣传视频。**

一个面向软件、AI 平台和操作系统的产品宣传视频 Skill，可由支持读取 Skill 指令、编辑文件和运行本地命令的 AI 工具使用。读取白皮书、用户手册、PPT 与截图，提炼产品主线，编写口播和分镜，再通过代码动画展示功能、流程与关系。

重点不只是标题入场和镜头转场：**每个分镜内部，都应随着内容推进发生有意义的变化。** 截图保持清晰，重点、步骤和关系动态展开。

当前版本：**0.4.7** · [MIT 许可](LICENSE)

## 它能帮你完成什么

| 环节 | 工作内容 |
| --- | --- |
| 读资料 | 整理产品定位、核心能力与证据，区分已支持、规划和待确认 |
| 写内容 | 围绕目标受众形成宣传主线、口播和逐句画面构想 |
| 做分镜 | 先完成一个有完整叙述的代表分镜，确认效果后扩展 |
| 做动画 | 用布局重组、描线、沿路径运动和文字分层呈现内容发展 |
| 处理截图 | 保留阅读时间，用讲解图层强调重点，避免伪造实机操作 |
| 导出交付 | 准备字体、调用渲染器、可选本地配音，输出视频与可编辑工程 |
| 局部修订 | 保留已认可的镜头，只调整受影响的内容与时间段 |

适合产品介绍、平台能力讲解和客户交流视频。它需要由 AI 助手读取资料、判断内容并编写工程，**不是上传文件后自动生成成片的独立应用**。

## 安装 Skill

将本仓库文件夹命名为 `product-whitepaper-film`，放入所用 AI 工具支持的技能目录，或让工具读取本仓库的 `SKILL.md`，按其中的指引工作：

```text
<技能目录>/product-whitepaper-film/SKILL.md
```

技能目录、自动发现与调用语法由所用工具决定。工具需要具备读取资料、编辑工程和执行本地命令的能力；未对所有工具逐一做兼容验证。`agents/openai.yaml` 是可选的工具界面配置，其他工具可忽略。安装 Skill 不等于装好渲染器和语音模型，实际工具需按下文独立准备。

## 一句话开始

在所用 AI 工具中提供资料并输入（`$名称` 为支持该语法时的调用方式）：

> 用 $product-whitepaper-film，把这些白皮书、手册和截图做成面向客户的产品宣传视频。先对齐口播，再给我一个完整分镜验证动画效果，确认后扩展整片。

如果工具不支持 `$名称`，可以改为“读取本仓库的 SKILL.md，并按其流程完成任务”。

也可以明确强调：

> 每个分镜内部都要有跟随内容推进的动画，不只是标题入场和镜头转场。截图需要保持清晰，但流程、重点和关系要动态呈现。

已有视频需要修改时，可以指定镜头、截图或口播范围。已确认的内容会作为后续工作的约束。

## 推荐准备的资料

- 产品白皮书、用户手册或功能介绍 PPT。
- 可用于视频的截图、Logo 或演示素材。
- 目标受众、最想突出的两三个信息及发布渠道。
- 可选：期望时长、视觉风格、自己的录音或合法取得的音色。

资料不齐时，可先整理内容或制作明确标记的示意画面。没有证据的性能、兼容范围和运行结果，不应写成产品事实。

## 包内资源

- **9 个基础动画函数**：信息入场、蒙版、描线、信号、步骤、强调、归位、镜头和计数。
- **4 个参数化配方**：布局重组、局部描线、沿 SVG 路径运动、文字逐行揭示。
- **16 秒基础示例**与 **28 秒配方示例**源码。
- **完整虚构白皮书示例**：资料、口播、人工编排的时间轴与动画构建脚本。
- 工程记录检查、字体字形校验、渲染与媒体处理入口。

| 示例 | 源码与资料 |
| --- | --- |
| 基础动画 | [gallery.html](examples/gallery.html) |
| 动画配方 | [recipe-gallery.html](examples/recipe-gallery.html) |
| 虚构产品介绍 | [白皮书](examples/whitepaper-demo/whitepaper.md) · [口播](examples/whitepaper-demo/narration.txt) · [动画模板](examples/whitepaper-demo/index.tpl.html) · [构建脚本](examples/whitepaper-demo/build.py) |

所有公开示例均为虚构资料和示意界面，不是客户案例、实机录屏或产品能力证明。示例不附带录音、个人音色或真实项目验收记录。HTML 需准备运行资产后预览，不是直接双击即可完整播放的成片。

## 本地工具准备

需要 Python 3.10+、Node.js、FFmpeg / ffprobe、可运行的 HyperFrames，以及合法取得的本地 GSAP 文件。请使用与工程兼容的版本；不保证全部版本或平台兼容。

在仓库目录安装字体处理依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

后续示例使用虚拟环境 Python。HyperFrames、GSAP 和 FFmpeg 需另行准备，不包含在依赖文件中。

配置已安装的工具：

```bash
.venv/bin/python scripts/film.py configure \
  --gsap /absolute/path/gsap.min.js \
  --hyperframes-command '["hyperframes"]'

.venv/bin/python scripts/film.py doctor --verify
```

配置保存在 `~/.config/product-whitepaper-film/runtime.json`，与可公开源码分离。工具拒绝覆盖已有配置、工程和成片；调整配置前先查看已有文件。完整参数见 [运行说明](references/runtime.md)。

## 创建一个动画示例

以下命令中的绝对路径为占位符，请换成自己的目录。新工程目录应尚不存在。

```bash
.venv/bin/python scripts/film.py example /absolute/path/new-demo \
  --template recipes --fetch-fonts

.venv/bin/python scripts/film.py render /absolute/path/new-demo/film \
  --out /absolute/path/new-demo/output/demo.mp4
```

`--fetch-fonts` 会把去重后的画面字符集提交给 Google Fonts。**涉及私有文案时，请使用 [离线字体方式](references/fonts.md)**。检查字形覆盖后，仍需查看实际渲染效果。

## 构建虚构白皮书示例

```bash
.venv/bin/python scripts/film.py example /absolute/path/whitepaper-demo

.venv/bin/python examples/whitepaper-demo/build.py \
  /absolute/path/whitepaper-demo \
  --timing examples/whitepaper-demo/timing.json

.venv/bin/python scripts/film.py fonts /absolute/path/whitepaper-demo

.venv/bin/python scripts/film.py render /absolute/path/whitepaper-demo/film \
  --out /absolute/path/whitepaper-demo/output/demo.mp4
```

这里的字体命令需要联网，私有内容请改用离线方式。`timing.json` 是人工编排的演示时间轴，不对应任何录音或用户测试。没有语音环境时可以先渲染无声示例；加入配音后，应按真实音频重新对齐。

## 配音与检查

可以使用自己的录音或合法取得的声音。可选适配器面向 Apple Silicon 上的 MLX / Qwen3-TTS Base，需要自行准备模型、参考音频和音色档案；模型及声音不会随 Skill 分发，也不自动切换付费服务。适配器涉及内部模型接口，使用前需检查版本兼容性。

技术检查不能替代内容判断或试听：

- 资料有出处，不等于产品已实机验证。
- 时间轴能定位，不等于画面清晰、动画自然。
- ASR 识别正确，不等于配音没有吞音或听感问题。
- 一个分镜通过，不等于整片已经验收。

检查方法见 [检查范围](VALIDATION.md) 与 [工程记录说明](references/verification.md)。

## 隐私与分享

真实项目应放在 Skill 仓库外。个人资料、客户文档、产品截图、参考录音、运行配置及生成日志不应提交到公开仓库，也不要在公开 Issue 中上传这些内容。

`scripts/package.py` 使用显式公开文件清单并检查常见敏感内容；新增公开文件需要人工核查后更新清单。自动检查不能保证发现所有隐私信息。

## 文档导航

- [资料提炼与口播](references/content.md)
- [动画与口画对齐](references/motion.md)
- [动画配方](references/recipes.md) · [公开技术来源](references/recipe-sources.md)
- [本地制作入口](references/runtime.md) · [字体说明](references/fonts.md)
- [虚构产品示例说明](references/product-case.md)
- [发布准备](references/release.md)

## 许可

本项目代码与文档采用 [MIT License](LICENSE)。GSAP、HyperFrames、FFmpeg、字体、语音模型和使用者提供的素材分别遵循自己的许可，详见 [第三方说明](THIRD_PARTY_NOTICES.md)。本项目许可不替代这些依赖或素材的授权。
