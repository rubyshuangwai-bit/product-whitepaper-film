# 实现与运行依赖

## 包内工具

- `project.py`：工程记录、来源关联、镜头时序和验收状态检查。
- `pwf-motion.js`：基础动画函数和布局、描线、沿路径运动、文字分层配方。
- `fonts.py`：可见文字采集、在线/离线字体准备、字形覆盖校验及OFL记录。
- `film.py` 与 `voice_worker.py`：外部渲染工具和本地语音环境的调用入口。
- `package.py`：文件白名单检查及发布候选包生成。

配方设计参考的公开技术文档见 [配方来源](recipe-sources.md)，字体接口见 [字体说明](fonts.md)。

## 单独配置的依赖

GSAP、HyperFrames、FFmpeg、fontTools、Noto字体、MLX及语音模型分别承担动画、渲染、媒体处理、字体或语音能力。本包不捆绑模型、音色或这些工具的运行文件；安装与使用按各自许可处理。具体版权和来源声明集中在 [第三方说明](../THIRD_PARTY_NOTICES.md) 与 [LICENSE](../LICENSE)。

公开示例采用虚构资料与示意界面。真实客户材料、个人音色和本机配置保留在作品工程中，不进入通用Skill包。
