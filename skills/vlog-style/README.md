# vlog-style

**有运动感、有人味的研究生日常 Vlog。** 为北理工 AI 男研账号保存内容与审美偏好，适用于小红书、抖音。

本地版本：**2.0.0**。本次将转场技术拆至同仓库并列技能 [video-transitions](https://github.com/zhousicheng23-creator/vlog-style/tree/main/skills/video-transitions)。本地更新待发布。历史版本保留在 Git 历史与已有标签中。

- [SKILL.md](SKILL.md)：创作者风格、叙事节奏、训练与生活、原声音乐、字幕封面及转场选择。
- [references/examples.md](references/examples.md)：可选风格案例，不是每期模板。
- [agents/openai.yaml](agents/openai.yaml)：Codex 展示信息，默认允许自动发现。

本技能回答“为什么这样剪、选择什么表达”。转场制作交给可用的 `$video-transitions`；整片生产由项目已有视频工具承担，`video-use` 保持独立。两技能无需相邻安装，风格规划本身不依赖技术技能。

## 安装与使用

将仓库中的 `skills/vlog-style/` 安装为工具用户技能目录或项目 `.agents/skills/` 下的 `vlog-style`，不要重复安装或覆盖已有内容。重开会话以发现技能。

```text
用 $vlog-style 给本期素材排剪辑方案，说明取舍与转场意图，先不改视频。
按 $vlog-style 评审我指定的成片，用时间码说明建议。
```

实际剪辑仅在授权范围内进行，交付与导出遵守项目约定。每期时长、次数、歌曲、活动顺序和效果均不固定。

## 历史与许可

v1.0.0 为原始风格；v1.1.0 加入蒙版制作；v1.2.0 加入短暗场；2.0.0 将制作内容拆出。用 `git log --oneline --decorate` 或 `git show v1.2.0:SKILL.md` 只读查看旧版。切换版本前保存工作区改动，不重写已有标签。

沿用 [MIT 许可证](LICENSE)。
