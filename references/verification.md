# 验证与工程记录

## 轻量工程辅助工具

`python3 scripts/project.py init /absolute/path/new-project` 创建 brief.md、sources.json、claims.json、shots.json、review.json 及素材/输出目录，目标存在即停止，不覆盖文件。

`python3 scripts/project.py check /absolute/path/project` 检查记录结构、引用、文件存在性、时序、内容事件与验收证据。未完成记录会报告 pending，不替用户判定画面好坏。`--release` 要求各审查项通过或有合理的“不适用”说明，视频文件存在，且 `ffprobe` 能读取视频流。它仍不能证明事实真实、动画美观或声音自然。

镜头引用规划事实时设置 `planning_disclosed: true`，并实际核对口播/画面确实说明规划；工具检查标记，人工检查措辞。纯引导语等无产品事实镜头可用 `nonfactual_reason` 说明为何不引用事实，不能以此绕过产品主张核验。

轻量工具是可选辅助；已有项目可保留自身结构，只需保存等价记录。状态、证据、来源字段的含义应保持一致。

示例事实：
```json
{"id":"C1","text":"支持关键词查找","source_ids":["S1"],"locator":"虚构白皮书 使用过程章节","status":"supported"}
```

示例镜头（具体时间按实际口播调整）：
```json
{
  "id":"lookup","start":0,"end":8,
  "narration":"输入关键词，查找相关资料。",
  "claim_ids":["C1"],"asset_ids":["A1"],
  "read_hold":{"start":1,"end":4},
  "events":[
    {"at":1,"kind":"reveal","cue":"关键词","meaning":"标明查找入口"},
    {"at":4.2,"kind":"connect","cue":"相关资料","meaning":"突出对应条目"}
  ]
}
```

sources.json 的 `sources` 数组记录 `id/path或url/title`；`assets` 数组记录 `id/path/source_id/status`，status 为 usable、placeholder 或 missing。项目内路径相对工程根目录；绝对来源路径也可使用，但共享前需检查隐私。

review.json 的 `checks` 数组每项包含 `id/status/evidence/note`。检查项为 facts、motion、readability、sync、audio、playback；状态 pass、fail、pending、not_applicable。evidence 是非空文件路径列表，不是“通过”文字。not_applicable 必须说明原因；无配音可将 audio 和 sync 标不适用，但应符合用户需求。evidence 指向实际审查记录、帧图、ASR/波形或探测输出，助手不能自动伪造人工验收。`video` 指向待交付文件。

## 人和工具分别验证什么

| 检查项 | 需要做什么 | 不能据此声称什么 |
|---|---|---|
|事实|核对口播、图中文字与来源，区分支持/规划/待核实|有引文不等于实机已验证|
|内容动画|逐镜写明语义事件，实际抽帧检查变化与落点|事件数组非空不等于动画好看|
|可读性|检查最密画面、最短字幕、截图阅读区间、转场边界|布局程序无碰撞不等于小字可读|
|同步|对照真实音频时间，专有名词与画面对象核对|字幕存在不等于同步正确|
|音频|检查句首句尾、疑似吞音、峰值；保留需试听项|ASR通过不等于自然度通过|
|播放|完整解码，探测时长、尺寸、帧率、实际音轨|文件存在不等于导出成功|

新视频需渲染后看图；新旁白须标明是否实际试听。不要以“检测通过”合并所有状态。草稿可交付评审，但明确残留缺陷与占位；发布版修复事实错误、缺词、遮挡、截断和播放错误。

## 局部修订

保存旧版及修改清单；记录受影响的镜头/音频时间段。认可的画面、截图、文案、音色默认保持；修改一段配音长度后重新核对后续时间轴。工程应能从源文件重建，不只交一个 MP4。

跨项目可复用风格方法；用户音色、个人资料、未公开文档、产品截图及本地绝对路径不进入通用 Skill 包。不得把用户历史案例、验证过程或验收结果写入公开包，即使已经隐去姓名。
