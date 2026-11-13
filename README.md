# vlog-style

**有运动感、有人味的研究生日常 Vlog。**

为北理工AI男研账号保存的个人内容与剪辑偏好，适用于小红书、抖音。健身和篮球有力量感，学习和生活自然松弛，保留真实反应与轻微幽默。

当前版本：**v1.1.0（2026-11-13）**。新增动作引导蒙版转场、制作辅助工具与原声偏移检查；保留 v1.0.0，支持按标签查阅和回退。

## 内容

```text
vlog-style/
├── SKILL.md                            核心偏好、任务边界和工作方式
├── agents/openai.yaml                  Codex技能展示与调用信息
├── references/
│   ├── examples.md                     按需参考的风格案例
│   ├── motion-mask-transitions.md      蒙版制作、声音同步、检查与交付
│   ├── motion-mask-example.json        手工关键帧示例
│   └── page-reveal-v6.md                已认可翻页案例及同步修正经验
├── scripts/
│   ├── build_motion_mask.py            从关键帧制作灰度蒙版序列
│   └── check_audio_sync.py             辅助测量原声音频偏移
└── LICENSE                             MIT许可证
```

这是个人风格技能。实际剪辑需要所在环境具备可用的视频工具；可以与video-use等执行技能配合，也可以只用于输出方案或评审。

v1.1 新增的蒙版方法只是“音乐、原声与转场”中的可选子项；原有故事、训练、字幕、封面等风格继续保留。

蒙版工具不会自动识别或跟踪物体，声音工具不能单独证明音画同步。依赖、制作边界和调用入口见[动作引导蒙版转场](references/motion-mask-transitions.md)。仓库不包含原始照片、视频、音乐或私有素材路径。

## 安装与调用

将本仓库作为一个名为`vlog-style`的技能目录，放入支持`SKILL.md`的工具所使用的技能目录。Codex可使用用户技能目录`~/.codex/skills/vlog-style`，或项目技能目录`.agents/skills/vlog-style`。不要在两个位置重复安装同一份技能。

例如在Windows PowerShell中安装到用户技能目录：

```powershell
git clone git@github.com:zhousicheng23-creator/vlog-style.git "$env:USERPROFILE\.codex\skills\vlog-style"
```

若目标目录已有内容，先检查，不覆盖。新安装后重新打开会话，使工具重新发现技能。

调用示例：

```text
用 $vlog-style 给这期“看书、练胸、篮球、吃饭”排一个剪辑方案，先不改文件。
```

```text
按 $vlog-style 评审我指定的最新成片，用时间码指出优先修改的地方。
```

```text
按 $vlog-style 和本期已确认的方案开始剪辑，保留原片与可继续修改的工程。
```

技能允许按任务自动选择；只有明确要求实际剪辑时才进入修改工作。标题、时长、歌曲、活动顺序和案例效果均不固定。

动作转场调用示例：

```text
用 $vlog-style 把看书接到健身，蒙版随翻页方向移动，保留对应原声，先做局部预览。
```

```text
按 $vlog-style 看看这段合电脑或推门能否接下一幕，不适合蒙版就用自然的动作衔接。
```

## 版本

Git提交保留修改历史，发布标签不重写；版本号同时记录在`SKILL.md`的`metadata.version`中。

| 版本 | 内容 | 固定版本 |
| --- | --- | --- |
| v1.0.0 | 原有叙事、健身篮球、音乐字幕及封面偏好 | [查看版本一](https://github.com/zhousicheng23-creator/vlog-style/tree/v1.0.0) |
| v1.1.0 | 增加动作引导蒙版制作、关键帧、同步工具和 V6 参考 | [查看版本 1.1](https://github.com/zhousicheng23-creator/vlog-style/tree/v1.1.0) |

查看历史，不改本地内容：

```powershell
git log --oneline --decorate
git show v1.0.0:SKILL.md
```

若要让已安装的技能退回旧版，在其仓库目录先检查 `git status --short`。有未提交修改时先单独备份或提交，不使用强制覆盖。确认工作区干净后：

```powershell
git fetch origin --tags
git switch --detach v1.0.0
```

这会将整个技能切换到固定版本，包括当时的参考文件，不修改 GitHub 历史。需要修改旧版时先创建新分支。切回当前发布版本：

```powershell
git switch --detach v1.1.0
```

或者恢复跟随主分支，在工作区干净时执行：

```powershell
git switch main
git pull --ff-only origin main
```

切换后重新打开 Codex 会话，使技能内容重新加载。没有使用 Git 的环境，也可以从对应标签下载整份仓库 ZIP，备份现有目录后替换整个技能目录；不要只替换 `SKILL.md`。

## 许可证

沿用仓库原有的[MIT许可证](LICENSE)。
