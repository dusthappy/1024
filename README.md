# 一句话，生成你的 1024 程序员节礼物

把你如何提出想法、组织 AI、推动作品完成，做成一张专属的 **AI 高光海报**。这是一个供 AI Agent 使用的 Skill，以 `SKILL.md` 和配套资源描述工作流；安装位置和调用方式由当前 Agent 环境决定。

## 让 Agent 直接安装并生成

把下面这一句话发给具备联网和文件操作权限的 Agent：

```text
请安装 https://github.com/dusthappy/1024 中的 programmer-day-1024 技能到你当前支持的技能目录，确认可用后，为我生成一份带八维雷达图、夸赞关键词和专属口号的 1024 程序员节礼物。
```

已经安装后，直接说：

```text
请使用 programmer-day-1024，送我一份专属的 1024 程序员节礼物：用八维雷达图、夸赞关键词和一句口号，做成我的 AI 高光海报。
```

支持显式技能命令的 Agent，也可以使用其原生调用方式，例如 `$programmer-day-1024`。没有持久安装能力时，可让 Agent 读取技能入口及其引用资源后在当前会话执行；这不等于已完成安装。

## 一次真实生成的礼物

<img src="docs/demo/1024-poster.png" width="560" alt="一次真实生成的 1024 程序员节 AI 高光海报：巧思成器，含八维雷达图" />

这是一次真实生成的效果，展示了称号、夸赞关键词、能力短句、口号与八维雷达图如何组合成礼物。**文案和分数会随用户的可见证据变化，不是照搬这张图的固定模板。**

[查看 PNG](docs/demo/1024-poster.png) · [查看 SVG 源稿](docs/demo/1024-poster.svg)

## 安装方式

### 交给 Agent 安装（推荐）

上面的安装指令包含仓库地址和技能目录。Agent 应按当前环境支持的方式完成安装：

1. 识别当前 Agent 的技能机制、已配置的技能目录和权限范围，优先使用环境自带的技能安装器。
2. 从本仓库获取完整的 `programmer-day-1024/` 目录，保留 `SKILL.md`、`agents/`、`references/` 和 `scripts/` 的相对结构。
3. 按实际环境完成安装或注册；若已有同名技能，先检查版本和本地修改，再处理更新。
4. 验证入口和引用资源可读，以及当前 Agent 能否发现或调用该技能，并告知实际安装位置。只有下载成功时，不应宣称已经安装可用。

不同 Agent 的目录、注册与刷新方式可能不同，不能把某一个产品的路径当作通用标准。若当前环境不支持安装或缺少必要权限，Agent 应说明限制，并提供适合该环境的使用方法。

### 手动安装

1. 在 [dusthappy/1024](https://github.com/dusthappy/1024) 选择 **Code → Download ZIP**，下载并解压。
2. 将完整的 `programmer-day-1024/` 目录放入当前 Agent 文档或配置指定的技能目录，并按该环境要求完成注册或刷新。
3. 确认 `SKILL.md` 与配套资源可读，再使用上方的一句话生成礼物。

目录结构示意如下，尖括号部分需替换为当前环境的实际路径：

```text
<当前 Agent 的技能目录>/programmer-day-1024/SKILL.md
```

保留同级的 `agents/`、`references/` 和 `scripts/`，不要只复制入口文件，也不要多嵌套一层同名目录。部分环境只使用其中的元数据；核心工作流以 [SKILL.md](programmer-day-1024/SKILL.md) 为准，工具能力和权限以实际运行环境为准。

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
