# 1024 · 你的 AI 高光海报

`programmer-day-1024` 是一个面向 AI Agent 的技能：结合当前可见且有权限访问的技能、用户记忆与对话，为用户制作 1024 程序员节活动海报，突出用户如何提出想法、组织 AI 并推动成果完成。

默认输出高光称号、夸赞关键词、能力短句、专属口号，以及包含八维雷达图的海报。有可用生图工具时优先生图；没有生图能力、生成失败或图表修正后仍不准确时，交付完整 SVG 海报。没有文件工具时可直接交付 SVG 源码。用户也可以指定只要文字。

## 固定八维与评分

八个维度的名称与顺序固定：**创意构思、目标表达、AI统筹、判断取舍、迭代打磨、知识复用、多元表达、应变交付**。

每维满分 **10.0**，统一保留一位小数。当前规则版本为 `1024-8d-v2`：维度指标 A、B 各占 25%，复杂要求处理 C 占 20%，实际成效 E 占 30%；四项均按有依据的 0–4 级锚点判定，再使用十进制四舍五入计算。

这是基于当前可见证据的**活动趣味评分，不是专业能力测评或排名**。缺少直接用户证据的维度显示“待探索”，不会凭空补分，也不会把 Agent 的工具数量或自主操作算作用户能力。图表与数值来自同一份数据，并融入最终海报。

技能只读取当前可见且有权限的信息。公开绘图数据不包含用户记忆原文或完整证据记录。

## 安装与调用

将本仓库中的整个 `programmer-day-1024/` 目录复制到：

```text
~/.codex/skills/programmer-day-1024/
```

保留 `SKILL.md`、`agents/`、`references/` 和 `scripts/` 的相对结构。更新已有安装时替换对应目录内容，避免多嵌套一层同名目录。

在能发现该技能的 Codex 会话中调用：

```text
$programmer-day-1024 请根据当前可访问的技能、记忆和对话，
为我制作一张 1024 程序员节高光海报，包含八维雷达图和专属口号。
```

其他 Agent 也可以读取 [SKILL.md](programmer-day-1024/SKILL.md)，按其工作流执行；可用工具和权限以实际运行环境为准。

## 评分与雷达图脚本

两个脚本需要 Python 3.9 或更新版本，仅依赖标准库。在技能目录下运行：

```sh
cd programmer-day-1024
python3 scripts/score_profile.py --input rating-input.json --output chart-data.json
python3 scripts/render_radar.py --input chart-data.json --output radar.svg --theme light
```

- `score_profile.py`：校验完整八维的 A、B、C、E 整数评级，计算一位小数分数；没有直接依据的整维输出 `null`。
- `render_radar.py`：依据冻结分数生成精确 SVG 雷达图，支持 `light`、`dark` 配色。输出是图表组件，仍需与称号、能力短句和口号组成完整海报。

脚本默认拒绝覆盖已有输出，明确需要重建时可加 `--force`。输入格式、等级定义、计算公式和图表要求见 [评分与图表规则](programmer-day-1024/references/scoring-and-chart.md)；文案与视觉方法见 [用户高光表达](programmer-day-1024/references/portrait-framework.md)。

## 仓库结构

```text
README.md
programmer-day-1024/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── portrait-framework.md
│   └── scoring-and-chart.md
└── scripts/
    ├── score_profile.py
    └── render_radar.py
```
