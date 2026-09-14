---
name: cumcm-workflow
description: 管理全国大学生数学建模竞赛项目的选题、建模、实验验证、论文、提交准备及跨 Agent 交接，维护可恢复上下文和结果证据链。用于当前赛题或明确的比赛项目工作；纯数学知识问答、普通编程和本技能自身的维护不启动比赛流程。
metadata:
  version: "5.2.2"
  agent_created: "true"
---

# CUMCM Workflow

辅助用户完成比赛，不接管比赛策略。保留五类对象：

| 对象 | 职责 |
|---|---|
| STATE | 当前控制状态和少量索引，不是历史日志 |
| TASK | 一个可验收的行动及其输入输出接口 |
| DECISION | 重要选择；OVR 是有期限的决策子类 |
| EVIDENCE | 模型、实验、结果、论断、事实、图表的可追溯记录 |
| ISSUE | 影响正确性、交付或协作的实质问题 |

本技能中的 HARD/SOFT/DEFAULT 是领域规则分类，不改变系统、开发者及工具权限的指令层级。

## 1. 选择执行范围

- 普通知识问题：直接回答，不创建比赛状态、不显示 Gate。
- 当前项目的局部工作：只加载该任务需要的上下文；小修正无需创建新 TASK/DEC。
- 比赛组织、模型推进、论文或交接：使用下述执行循环。
- 用户只要计划、分析、提示词或审查：只交付所请求内容，不自动执行后续实验。
- 维护本技能或赛后复盘：处理用户指定的维护/复盘范围；不启动比赛执行或按旧截止推进状态。

已有 memory 目录不是自动启动依据；先确认它属于本次项目。项目尚未初始化时，
只创建必要的 STATE/TASKS；其余目录在首次产生内容时创建。

## 2. 最小执行循环

```text
确认用户目标与项目
  -> 读取 STATE + 当前 TASK，恢复动作范围、正式入口和必要引用
  -> 检查权限/领域硬约束、关键决策的用户确认、风险及截止压力
  -> 在授权范围内执行，或按需生成 Task Packet
  -> 保存真实产物及 candidate Evidence
  -> 按题面必答项与本次交付验收，核对受影响消费者的版本
  -> Coordinator 接纳结果，更新当前索引并收束过期描述
  -> 报告完成项、未验证项及下一步
```

普通任务通常只需修改产物、当前 TASK 和少量证据。文件数量是预算建议，
不能成为省略必要证据、错误记录或用户交付物的理由。

长任务按 [task 模板](templates/task.md) 留下简短目标、依据、动作范围、验收与续接信息。
从用户已有要求推断并维护，不让用户填表。授权求解并导出时完成整个闭环；
“仅分析”“只改说明”“先试后定”则沿用相应边界，具体见 user-intent。

## 3. 不可丢失的约束

1. 不伪造数据、运行结果、引用、审核或提交回执；猜测、假设和候选结果明确标注。
2. 不把未验证或已失效的结论当作确认事实。验证是针对版本和范围的检查，不是绝对真理。
3. 不静默修改原始数据、既有决策或他人产物；保留来源与可恢复版本。
4. 不绕过环境权限、用户明确保留的决定权或已核实适用的赛事规则。
5. 发现证据或控制状态冲突，暂停依赖该冲突的操作，继续无关的安全工作。
6. 关键建模决策的正式采用与落盘遵守 [user-intent.md](references/user-intent.md)；
   复用其规定的有效确认，确认前按提案/候选处理。

Baseline、止损时间、Gate 建议时间、Freeze 策略、目录命名不是诚信硬约束。
规则分类与确认逻辑只在 [user-intent.md](references/user-intent.md) 定义。
同一范围的有效确认不重复询问；目标、风险或后果发生实质变化才重新评估。

## 4. 上下文与协作

- 常规加载：`STATE -> 当前 TASK -> context_refs -> 必要的证据依赖`。
- 当前版本以有效决定、正式入口和真实运行产物交叉核对；“最终版”目录名、
  文件时间及孤立函数不能单独证明当前采用或实际运行。规则与实现冲突时分别报告。
- 不默认读整个 memory、全部决策、所有实验或完整聊天；先定位 ID，再读正文。
- 失去上下文时使用 [memory.md](references/memory.md) 的恢复协议。`RECOVER PROJECT`
  只是显式入口；新会话继续任务也应主动恢复，不依赖用户记住命令。
- Control 层由一名 Coordinator 写；Evidence 多写者仅能写各自分配的候选文件。
- Coordinator 的接纳与发布按 [validation.md](references/validation.md) 执行。
- 使用 [multi-agent.md](references/multi-agent.md) 定义写入范围、输入版本和返回验收。
  “生成另一 Agent 的提示词”不等于授权启动 Agent、上传数据或执行该任务。
- 不具备调度工具或授权时，交付自包含提示词；不声称已派发或已完成。

## 5. 按需路由

每个主题只有一份规范来源；模板只提供字段，不重新定义策略。

| 当前需要 | 读取 |
|---|---|
| 初始化、选题、状态晋级、Gate、截止压力、止损 | [workflow.md](references/workflow.md) |
| 关键决策确认、正式落盘、确认复用、Override、工作模式 | [user-intent.md](references/user-intent.md) |
| 上下文预算、恢复、ID 定位、证据失效、旧版迁移 | [memory.md](references/memory.md) |
| 任务分工、跨环境 Prompt、写入权、Return 验收 | [multi-agent.md](references/multi-agent.md) |
| 建模、数据检查、实验、代码及结果产物 | [modeling.md](references/modeling.md) |
| Micro Review、验证发布、Final Review | [validation.md](references/validation.md) |
| 论断、论文同步、数字来源、图表与摘要 | [paper.md](references/paper.md) |
| 规则核实、Freeze、AI 记录、提交包与回执 | [submission.md](references/submission.md) |
| 实际项目的引用、产物依赖或交付清单检查 | [project-checks.md](references/project-checks.md) |

按需使用 [task](templates/task.md)、[return](templates/return.md)、
[decision](templates/decision.md)、[override](templates/override.md)、
[evidence](templates/evidence.md)、[issue](templates/issue.md)、
[checkpoint](templates/checkpoint.md)、[review](templates/review.md) 模板。

## 6. 对用户的呈现

日常用自然、简短的工作说明；不强制每轮打印 Gate/Risk/Pressure 面板。
只有风险确认、交接、阶段验收和正式审查使用结构化输出。
重要工作结束说明实际改变、验证依据、生成文件、残余风险；
“已写代码”“已运行”“已验证”“已提交”分别报告，不互相替代。
