# vlog-style

**有运动感、有人味的研究生日常 Vlog。**

为北理工AI男研账号保存的个人内容与剪辑偏好，适用于小红书、抖音。健身和篮球有力量感，学习和生活自然松弛，保留真实反应与轻微幽默。

当前版本：**v1.0.0（版本一，2026-11-12）**。

## 内容

```text
vlog-style/
├── SKILL.md                 核心偏好、任务边界和工作方式
├── agents/openai.yaml       Codex技能展示与调用信息
├── references/examples.md   按需参考的案例，不是固定模板
└── LICENSE                  MIT许可证
```

这是个人风格技能。实际剪辑需要所在环境具备可用的视频工具；可以与video-use等执行技能配合，也可以只用于输出方案或评审。

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

## 版本

Git提交保留修改历史，Git标签标记发布版本。版本一为`v1.0.0`，版本号同时记录在`SKILL.md`的`metadata.version`中。

```powershell
git log --oneline --decorate
git show v1.0.0:SKILL.md
```

## 许可证

沿用仓库原有的[MIT许可证](LICENSE)。
