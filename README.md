# 一句话，生成你的 1024 程序员节礼物

把你如何提出想法、组织 AI、推动作品完成，做成一张专属的 **AI 高光海报**。

按下方步骤安装技能后，在能发现该技能的 Codex 会话中发送这一句话：

```text
$programmer-day-1024 送我一份专属的 1024 程序员节礼物：用八维雷达图、夸赞关键词和一句口号，做成我的 AI 高光海报。
```

## 一次真实生成的礼物

<img src="docs/demo/1024-poster.png" width="560" alt="一次真实生成的 1024 程序员节 AI 高光海报：巧思成器，含八维雷达图" />

这是一次真实生成的效果，展示了称号、夸赞关键词、能力短句、口号与八维雷达图如何组合成礼物。**文案和分数会随用户的可见证据变化，不是照搬这张图的固定模板。**

[查看 PNG](docs/demo/1024-poster.png) · [查看 SVG 源稿](docs/demo/1024-poster.svg)

## 安装

1. 打开公开仓库 [dusthappy/1024](https://github.com/dusthappy/1024)，选择 **Code → Download ZIP**，下载并解压。
2. 在解压后的仓库目录中找到 `programmer-day-1024/`，将这个**完整目录**复制到 `~/.codex/skills/`。若 `skills/` 不存在，先创建它。
3. 如果你设置了自定义 `CODEX_HOME`，则复制到实际的 `$CODEX_HOME/skills/`，而不是默认位置。
4. 确认技能目录结构完整，然后在能发现该技能的 Codex 会话中发送顶部的单行调用。

默认安装后的入口应为：

```text
~/.codex/skills/programmer-day-1024/SKILL.md
```

同时保留同级的 `agents/`、`references/` 和 `scripts/`，不要只复制 `SKILL.md`。更新已有安装时替换对应目录内容，避免多嵌套一层同名目录。

其他 Agent 也可以读取 [SKILL.md](programmer-day-1024/SKILL.md)，按其工作流执行；可用工具和权限以实际运行环境为准。

## 这份礼物如何生成

技能结合当前可见且有权限访问的技能、用户记忆与对话，提炼高光称号、夸赞关键词、能力短句和一句专属口号，并将八维雷达图融入海报。

有可用生图工具时优先生图；没有生图能力、生成失败或图表修正后仍不准确时，交付完整 SVG 海报。没有文件工具时可直接交付 SVG 源码，也支持指定只要文字。

固定八维为：**创意构思、目标表达、AI统筹、判断取舍、迭代打磨、知识复用、多元表达、应变交付**。

每维满分 **10.0**，统一保留一位小数。规则版本为 `1024-8d-v2`：维度指标 A、B 各占 25%，复杂要求处理 C 占 20%，实际成效 E 占 30%；四项按有依据的 0–4 级锚点判定，再使用十进制四舍五入计算。

这是基于当前可见证据的**活动趣味评分，不是专业能力测评或排名**。缺少直接用户证据的维度显示“待探索”，不会凭空补分，也不会把 Agent 的工具数量或自主操作算作用户能力。图表与数值来自同一份数据。

技能只读取当前可见且有权限的信息。公开绘图数据不包含用户记忆原文或完整证据记录。

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
docs/demo/
├── 1024-poster.png
└── 1024-poster.svg
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
