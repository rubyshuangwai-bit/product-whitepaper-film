# 本地制作入口

`python3 scripts/film.py` 提供实际工具调用；`project.py` 只负责工程记录。渲染器、GSAP、字体和语音模型仍分别安装，Skill 不捆绑权重或个人音色。

## 本机配置与检查

默认配置 `~/.config/product-whitepaper-film/runtime.json` 在 Skill 外，不进入可分享包。可用全局 `--config /path/runtime.json` 指定其他配置。

```bash
python3 scripts/film.py configure \
  --gsap /absolute/path/gsap.min.js \
  --hyperframes-command '["hyperframes"]' \
  --tts-python /absolute/path/venv/bin/python \
  --model /absolute/path/local-model \
  --voice-profile /absolute/path/voice-profile.json
python3 scripts/film.py doctor --verify
```

示例调用已安装的 HyperFrames 命令；请按自己的安装方式配置 argv，不在命令中隐式下载软件。配置目标已存在会拒绝覆盖；更新时只修改希望变化的字段。Python 路径保留虚拟环境入口的符号链接，不 resolve 到系统解释器。

doctor 分别报告工具与音色是否就绪：检查 CLI、模块可导入、模型目录、参考音频 SHA256。不能据此宣称已生成或声音自然。

## 从示例到视频

```bash
python3 scripts/film.py example /absolute/path/new-demo --fetch-fonts
python3 scripts/film.py preview /absolute/path/new-demo/film --port 3040
python3 scripts/film.py check /absolute/path/new-demo/film
python3 scripts/film.py render /absolute/path/new-demo/film --out /absolute/path/new-demo/output/picture.mp4
```

--fetch-fonts 调用本包新写的 fonts.py，从 Google Fonts 下载 Noto 子集并实际检查字形，需网络；字体保持 SIL OFL。未提供该参数时不联网抓字体；渲染前自行准备或用 `film.py fonts <工程目录>`。此命令根据当前 index.html 重新采集可见字符；私有文案用 `scripts/fonts.py` 离线模式，详见 [字体说明](fonts.md)。示例无任何真实产品图；替换资产需要自行记录来源和使用权限。

render 先运行 HyperFrames 检查，阻止实际错误，保留警告供审查；渲染后 ffprobe 探测并完整解码。不会把动效数量或 craft 提示自动当成审美结论。输出存在会停止，不覆盖已认可视频。

## 新配方展示

用 `film.py example <新目录> --template recipes --fetch-fonts` 创建28秒新配方展示工程。默认基础示例仍为16秒。用 `node scripts/verify_recipes.cjs` 对真实配置的GSAP验证时间轴前进与回退；该脚本不操作浏览器，实际布局和截图效果仍需渲染检查。

## 本地语音

```bash
python3 scripts/film.py voice --text-file /path/narration.txt --out /path/voice.wav
```

调用本机已配置的 MLX / Qwen3-TTS Base 环境，始终传入已确认的 ref_audio/ref_text，并核验参考文件 hash。离线运行，不下载权重、不换预设声、不调用外部付费服务。适配器使用 MLX Audio 的 `_generate_icl`，属于内部接口，可能随版本变化；使用前检查兼容性，失败就明确报错。

一次生成一个知识完整段。保留原始 WAV、采样参数、当前音频hash和尾段能量筛查。生成的 `.voice.json` 一律是 `pending-listening`；安静尾段不足0.35秒会标 `ending_review_needed`，不证明缺字，也不自动补零或删字。通过 ASR 和实际试听核对句首、专有名词、最后一句；确认缺词则有依据地重生成受影响段，不能无限重试。

```bash
# 仅制作供试听的样片，明确保留未试听状态
python3 scripts/film.py mux --video /path/picture.mp4 --audio /path/voice.wav \
  --out /path/listening-preview.mp4 --preview-unreviewed
# 配音实际试听确认后，以绑定当前音频hash的记录合成
python3 scripts/film.py mux --video /path/picture.mp4 --audio /path/voice.wav \
  --out /path/reviewed.mp4 --listening-review /path/listening-review.json
```

试听记录包含 `status: listened_complete`、当前 WAV 的 `audio_sha256`、`notes`（核对的句尾与真实试听结论）。程序和助手不能伪造试听。mux 拒绝音频长于画面，须延长画面与字幕，不能截断口播；不足画面时只延续尾部静音，原 WAV 不变。最终 MP4 保存探测与语音审查状态。此接口不自动添加配乐；需要配乐时按实际需求设计混音并验证可听性。

## 迁移与共享

Skill 文件可复制到另一台机器；运行配置单独重配。模型和音色仍属于本机资产，GSAP与字体使用各自许可。缺依赖应清楚报告缺什么；不要宣称“内置模型”或“安装 Skill 即已装好全部依赖”。

## 音色档案格式

`--voice-profile` 指向本机JSON，至少包含以下字段；参考音频路径相对该JSON所在文件夹。该档案与音频不要放进开源包。

```json
{
  "ref_audio": "reference.wav",
  "ref_text": "与参考音频逐字一致的参考稿",
  "reference_sha256": "参考WAV文件的实际SHA256"
}
```

可用 `python3 -c "import hashlib; print(hashlib.sha256(open('reference.wav','rb').read()).hexdigest())"` 计算校验值。换参考音频后需重新确认音色；哈希校验只确认文件一致，不证明你拥有音色权利或新语句听感合格。
