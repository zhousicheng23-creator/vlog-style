# Vlog skills

本仓库提供 Vlog 岗位技能和共享制作技能。

| 技能 | 职责 | 入口 |
| --- | --- | --- |
| vlog-coordinator 1.0.4 | 总指挥：最新意图与授权、派工、版本、状态日志和交付 | [SKILL.md](skills/vlog-coordinator/SKILL.md) |
| vlog-material-planner 1.0.3 | 素材策划：增量观察、源证据和可执行剪辑简报 | [SKILL.md](skills/vlog-material-planner/SKILL.md) |
| vlog-editor 1.0.3 | Terra：唯一主时间线、真实原声、局部修订和最终画声合成 | [SKILL.md](skills/vlog-editor/SKILL.md) |
| vlog-bgm 1.0.4 | BGM：分场音乐强弱、旁白和同期声让位、独立音乐轨和版本绑定 cues | [SKILL.md](skills/vlog-bgm/SKILL.md) |
| vlog-retrospective 1.0.0 | Astra：依据用户反馈、版本差异和制作回执复盘，整理待审技能改动 | [SKILL.md](skills/vlog-retrospective/SKILL.md) |
| vlog-style 2.0.2 | 创作者风格、叙事节奏、镜头取舍、声音审美、字幕封面和转场选择 | [SKILL.md](skills/vlog-style/SKILL.md) · [说明](skills/vlog-style/README.md) |
| video-transitions 1.1.2 | 动作蒙版、缓动滑屏、短暗场、画面填字片尾及对应声音同步 | [SKILL.md](skills/video-transitions/SKILL.md) · [说明](skills/video-transitions/README.md) |

岗位先读自己的技能，再按当前任务调用共享能力：`vlog-style` 决定表达与选择，`video-transitions` 实现已定转场。整片生产继续使用项目已有工具；`video-use` 保持独立，不在本仓库复制或重新安装。制作复盘由 Astra 按用户要求用 `vlog-retrospective`，需要时参考共享风格或调用技能编写工具。独立检查和清理按用户需求调用。

## 安装

克隆本仓库后，将所需的 `skills/<技能名>/` 分别复制或链接到工具的用户技能目录或项目 `.agents/skills/` 下，目录名保持对应技能名。也可通过 Codex 的 `skill-installer` 指定本仓库、技能路径及固定提交安装。不要把仓库根目录作为技能目录，也不要重复安装或覆盖已有内容。技能默认允许自动发现；安装后下一轮会话可发现。

```text
总指挥用 $vlog-coordinator 统一任务与派工。
策划用 $vlog-material-planner 复用观察并交清源证据。
Terra用 $vlog-editor 维护主时间线，按需读风格、转场和运行时技能。
BGM用 $vlog-bgm 交独立配乐与 cues，由 Terra 混入一次。
Astra用 $vlog-retrospective 核对制作反馈，交待审的技能草稿。
```

## 版本

每个技能以自身 `SKILL.md` 的 `metadata.version` 为准，版本清单见 [versions.json](versions.json)。

后续迭代先提供草稿供用户过目；用户明确授权当次直接更新时按其范围执行，否则确认后再安装、发布。每次完成向用户报告受影响技能的新版本及GitHub提交。修复使用补丁版本，兼容新增使用次版本，改变职责或不兼容规则使用主版本；未改技能不随同升级。Git提交保存每次发布的内容与历史。

## 文件与历史

`skills/` 内每个技能有独立入口；共享技能按需提供UI元数据、参考及本地辅助脚本。岗位入口引用的共享技能需在目标环境可用。仓库不含原片、个人录音或剪辑工程。实际剪辑、预览和导出遵守所在项目的授权与目录约定。

旧版 v1.0.0、v1.1.0、v1.2.0 的根目录布局保留在已有 Git 历史和标签中，不重写。这些历史仓库标签不代表新岗位技能的版本。

沿用 [MIT 许可证](LICENSE)。
