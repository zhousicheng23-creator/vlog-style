# Vlog skills

同一仓库中的两个独立 Codex 技能：

| 技能 | 职责 | 入口 |
| --- | --- | --- |
| vlog-style 2.0.0 | 创作者风格、叙事节奏、镜头取舍、声音审美、字幕封面和转场选择 | [SKILL.md](skills/vlog-style/SKILL.md) · [说明](skills/vlog-style/README.md) |
| video-transitions 1.0.0 | 已确定意图的动作蒙版、缓动滑屏、短暗场、时间映射与原声同步 | [SKILL.md](skills/video-transitions/SKILL.md) · [说明](skills/video-transitions/README.md) |

风格技能决定表达与选择，技术技能实现转场。整片生产继续使用项目已有工具；`video-use` 保持独立，不在本仓库复制或重新安装。

## 安装

克隆本仓库后，将需要的 `skills/vlog-style/` 或 `skills/video-transitions/` 分别复制或链接到工具的用户技能目录或项目 `.agents/skills/` 下，目录名保持对应技能名。不要把仓库根目录作为技能目录，也不要重复安装或覆盖已有内容。重新打开会话以发现技能；两者默认允许自动发现，也能单独安装。

```text
用 $vlog-style 根据真实素材提出本期叙事、节奏与转场意图。
用 $video-transitions 实现已确定的转场，先提供项目约定的局部预览。
```

## 文件与历史

`skills/` 内每个技能均自包含入口、UI元数据及所需参考；技术技能还包括两个本地辅助脚本。仓库不含原片、个人录音或剪辑工程。实际剪辑、预览和导出遵守所在项目的授权与目录约定。

旧版 v1.0.0、v1.1.0、v1.2.0 的根目录布局保留在已有 Git 历史和标签中，不重写。当前为本地待发布布局；不据此声称已完成远程更新。

沿用 [MIT 许可证](LICENSE)。
