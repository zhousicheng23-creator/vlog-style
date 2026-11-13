# Vlog skills

同一仓库中的六个独立 Codex 技能，包括四个岗位入口与两个共享能力：

| 技能 | 职责 | 入口 |
| --- | --- | --- |
| vlog-coordinator 1.0.0 | 总指挥：最新意图与授权、派工、版本、状态日志和交付 | [SKILL.md](skills/vlog-coordinator/SKILL.md) |
| vlog-material-planner 1.0.0 | 素材策划：增量观察、源证据和可执行剪辑简报 | [SKILL.md](skills/vlog-material-planner/SKILL.md) |
| vlog-editor 1.0.0 | Terra：唯一主时间线、真实原声、局部修订和最终画声合成 | [SKILL.md](skills/vlog-editor/SKILL.md) |
| vlog-bgm 1.0.0 | BGM：统一配乐、干净音乐 stem 和版本绑定 cues | [SKILL.md](skills/vlog-bgm/SKILL.md) |
| vlog-style 2.0.0 | 创作者风格、叙事节奏、镜头取舍、声音审美、字幕封面和转场选择 | [SKILL.md](skills/vlog-style/SKILL.md) · [说明](skills/vlog-style/README.md) |
| video-transitions 1.1.0 | 动作蒙版、缓动滑屏、短暗场、画面填字片尾及对应声音同步 | [SKILL.md](skills/video-transitions/SKILL.md) · [说明](skills/video-transitions/README.md) |

岗位先读自己的技能，再按当前任务调用共享能力：`vlog-style` 决定表达与选择，`video-transitions` 实现已定转场。整片生产继续使用项目已有工具；`video-use` 保持独立，不在本仓库复制或重新安装。Astra按需整理风格和技能；独立检查员与清理模块仍按用户要求调用，四个岗位技能不自动启动全部流程。

## 安装

克隆本仓库后，将所需的 `skills/<技能名>/` 分别复制或链接到工具的用户技能目录或项目 `.agents/skills/` 下，目录名保持对应技能名。也可通过 Codex 的 `skill-installer` 指定本仓库、技能路径及固定提交安装。不要把仓库根目录作为技能目录，也不要重复安装或覆盖已有内容。技能默认允许自动发现；安装后下一轮会话可发现。

```text
总指挥用 $vlog-coordinator 统一任务与派工。
策划用 $vlog-material-planner 复用观察并交清源证据。
Terra用 $vlog-editor 维护主时间线，按需读风格、转场和运行时技能。
BGM用 $vlog-bgm 交统一音乐stem及cues，由Terra混入一次。
```

## 版本

每个技能以自身 `SKILL.md` 的 `metadata.version` 为准，版本清单见 [versions.json](versions.json)。四个岗位技能首个正式版为1.0.0，由已确认的第二轮草稿发布；草稿轮次与正式版本分开。

后续迭代先提供草稿供用户过目；用户明确授权当次直接更新时按其范围执行，否则确认后再安装、发布。每次完成向用户报告受影响技能的新版本及GitHub提交。修复使用补丁版本，兼容新增使用次版本，改变职责或不兼容规则使用主版本；未改技能不随同升级。Git提交保存每次发布的内容与历史。

## 文件与历史

`skills/` 内每个技能有独立入口；共享技能按需提供UI元数据、参考及本地辅助脚本。岗位入口引用的共享技能需在目标环境可用。仓库不含原片、个人录音或剪辑工程。实际剪辑、预览和导出遵守所在项目的授权与目录约定。

旧版 v1.0.0、v1.1.0、v1.2.0 的根目录布局保留在已有 Git 历史和标签中，不重写。这些历史仓库标签不代表新岗位技能的版本。

沿用 [MIT 许可证](LICENSE)。
