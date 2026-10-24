# 字体准备与字形检查

实现：`scripts/fonts.py`。根据 [Google Fonts CSS2 API](https://developers.google.com/fonts/docs/css2) 的公开接口请求正文字符子集。

## 在线与离线

```bash
# 明确联网：上传的是所需去重字符集，不是整份白皮书
python3 scripts/fonts.py --html /path/film/index.html --out /path/film/assets/fonts --download
# 离线：读取已合法取得的完整/足够覆盖的Noto Sans SC WOFF2
python3 scripts/fonts.py --html /path/film/index.html --out /path/film/assets/fonts \
  --regular /path/regular.woff2 --bold /path/bold.woff2 --license-file /path/OFL.txt
```

联网模式通过Google Fonts下载400和700字重的文本子集；从Google Fonts的Noto Sans SC字体目录获取对应OFL许可。离线模式不发网络请求，输入必须是Noto Sans SC的WOFF2及其许可，不能给其他字体冒用Noto名称或许可。

工具跳过HTML的script/style，收集画面文字与基础拉丁字符；若文本由JavaScript动态产生或存在于外部模板，用 `--text-file` 补充必要文字。动态文字漏记仍可能缺字，不能只相信静态扫描。

每个字重都会用fontTools的cmap核对字符覆盖，拒绝缺字、无效字体、错误响应与未预期的多分片响应。超过1200个独立字符时建议使用本地完整字体，避免大URL与隐私泄露。manifest记录字体文件hash、字形检查范围与字体URL，不保存正文字符集。

缺字检查通过不等于浏览器成功加载字体。渲染后仍需核对中文、标点、数字和文字布局。缺字体应明确失败，不用系统字体静默代替。

输出含 `sans-400.woff2`、`sans-700.woff2`、`OFL.txt` 和 `manifest.json`。这些为作品运行资产，不随Skill包分发；分享作品字体文件时保留对应OFL。字体授权来源：[Google Fonts Noto Sans SC](https://github.com/google/fonts/tree/main/ofl/notosanssc)。
