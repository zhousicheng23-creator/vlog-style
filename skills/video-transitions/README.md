# video-transitions

实现已确定意图的视频转场：动作引导蒙版、缓动滑屏、短暗场及原声时间映射。独立于个人风格与整片生产运行时。

本地版本：**1.0.0**。同仓库技能目录：[video-transitions](https://github.com/zhousicheng23-creator/vlog-style/tree/main/skills/video-transitions)，本地更新待发布。

## 资源

- [SKILL.md](SKILL.md)：共通规则及按需路由。
- [动作蒙版](references/motion-mask-transitions.md)、[关键帧示例](references/motion-mask-example.json)、[历史翻页案例](references/page-reveal-v6.md)。
- [缓动滑屏](references/slide-transitions.md)、[短暗场](references/dark-scene-transitions.md)。
- [build_motion_mask.py](scripts/build_motion_mask.py)：手工关键帧生成灰度 PNG，不自动追踪。依赖 NumPy、Pillow。
- [check_audio_sync.py](scripts/check_audio_sync.py)：原声偏移估计，不是完整音画验收。依赖 NumPy、SciPy 和显式 FFmpeg。

将仓库中的 `skills/video-transitions/` 安装为用户技能目录或项目 `.agents/skills/` 下的 `video-transitions`，不覆盖已有目录。默认允许自动发现，重开会话后使用：

```text
用 $video-transitions 做已确定的缓动左滑，旧画面左移、新画面从右同步进入，先做局部预览。
```

脚本先运行 `--help`。在具备依赖的 Python 环境，从技能根目录可生成纯蒙版测试缓存（不需要原片）：

```text
python scripts/build_motion_mask.py references/motion-mask-example.json --output edit/mask-example
python scripts/check_audio_sync.py --help
```

`edit/mask-example` 只是示例，实际工作目录遵守项目约定。仓库不含媒体。已有 `video-use` 可承担生产运行时，无须复制或重新安装。个人审美可由 [vlog-style](https://github.com/zhousicheng23-creator/vlog-style/tree/main/skills/vlog-style) 提供，但非依赖。

迁移自 vlog-style 1.2.0，脚本逻辑与 CLI 保持不变。沿用 [MIT 许可证](LICENSE)。
