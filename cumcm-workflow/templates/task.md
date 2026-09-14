# Task / 外发 Prompt

字段示例不是实际任务；占位内容必须替换。mode 定义见 [multi-agent.md](../references/multi-agent.md)。
简单任务在 TASKS 内联目标/owner/状态/输入/验收即可，无需填满外发字段。
委派任务正文唯一存于 `handoffs/outgoing/TASK-NNN-vN.md`，TASKS 只留 locator 和控制字段。
任务状态：TODO / DOING / BLOCKED / DONE / CANCELED，不能把验收状态混入执行状态。

## 普通长任务

以下信息内联当前 TASK，已有配置/记录用引用代替重复正文；小修可更短：

```text
目标：一个可验收交付
依据：题面必答项、有效决定、正式入口、输入版本
动作与范围：本次允许分析/修改/计算/导出/同步哪些内容，保护内容与计算限制
验收：真实产物、必要检查、消费者匹配或待同步范围
续接：已完成/未验证、运行中 job/session、下一条操作、有效确认
```

这些由执行者从对话推断，不要求用户填写。每个解释性必答项也要有证据与章节，
不能只列结果文件。跨 Agent 时才补齐下面的写集和返回契约。

## 委派任务元数据

```yaml
---
id: TASK-031
prompt_version: 1
project_id: competition-local
mode: EXECUTION
role: coding
owner: agent-q2
question: Q2
base_revision: 1
depends_on: []
time_budget_minutes: 60
deadline_at: null
stop_condition: "<预算用完、输入缺失或关键接口冲突时停止受影响工作并报告>"
context_refs:
  - {id: DEC-017, path: "memory/decisions/DEC-017.md", version: "<版本或hash>"}
inputs:
  - path: "<输入文件>"
    version: "<不可变版本或SHA-256>"
    schema: "<字段、类型、主键、单位、缺失值约定>"
allow_write:
  - "results/q2/TASK-031/"
  - "memory/evidence/EXP-Q2-T031-01.md"
  - "memory/evidence/RES-Q2-T031-01.md"
  - "handoffs/incoming/TASK-031-v1-r1-return.md"
read_only:
  - "data/raw/"
  - "memory/active/"
  - "memory/decisions/"
reserved_ids: [EXP-Q2-T031-01, RES-Q2-T031-01]
do_not_reopen: [DEC-017]
approval_refs: ["DEC-017#approval_ref"]
---
```

代码修改需要把具体 src 路径加入 allow_write；未列出即未授权。
若共享文件需改，向 Coordinator 提议，不擅自扩大路径。
approval_refs 可指向 context_refs 中正式 DEC 的确认字段，连同其 approval_scope 核对；
本例只是引用骨架，不证明真实确认已存在。依赖关键决策的正式执行任务须能解析到真实确认，
无共享文件系统时内嵌必要确认内容与范围；只有提案或不涉及所需确认的任务才可按实际情况留空。

## Prompt 正文

```markdown
# TASK-031

## Objective
<一个可验收目标；不是“尽量研究”>

## Context
<最小题意、已定模型/假设、已知事实；重要内容标出处>

## Scope
<必须做的工作、明确不做的事、可自行决定与须用户确认的边界；注明正式执行还是候选探索>

## Upstream Interface
<输入来自哪个模型/结果、字段与单位、版本、依赖何时就绪>

## Downstream Contract
<输出路径、文件格式、关键字段/单位、成功标准及消费者>

## Validation
<实际需要执行的检查、预期标准、无法运行时如何标记>

## Return Contract
返回 task_id、prompt_version、return_id、base_revision、status、
最多五条结论、产物/证据、实际验证、风险、decision_request 和 state_suggestion。
结果先为 candidate，不修改 Control；详细报告单独引用。

## Attachments
<已提供附件/可访问路径；不共享文件系统时内嵌必要定义，不只给ID>
```

返回路径、格式和目标环境不可省略。跨环境任务若缺必要数据，标 BLOCKED，
可以交付不依赖数据的部分，但不能把编写代码报成运行成功。

## Coordinator 续接记录

在 TASKS 中维护可变控制项；外发 Prompt 是当时的不可变分配，不持续刷新状态：

```yaml
id: TASK-031
status: TODO
owner: agent-q2
prompt_ref: "handoffs/outgoing/TASK-031-v1.md"
acceptance: null
processed_returns: []
evidence_refs: []
```

processed_returns 记录已处理 return_id/hash 和接纳结果，不得复制整份 Prompt。
prompt_ref 指向项目根内的实际外发文件，其 frontmatter id 与本任务一致；
需要机器核对分配版本时在控制项保留 prompt_version。检查能力见
[project-checks.md](../references/project-checks.md)，控制状态仍以当前 TASK 为准。
Resume 按需记：已完成/未验证、最近命令/日志、下一步、运行中 job/session、
关键版本、确认和仍存在的阻断。任务结束后保留归档 locator。
