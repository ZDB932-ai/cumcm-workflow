# 上下文与持久化记忆

只保存可恢复执行所需的状态、约束、决策和证据，不保存完整对话或隐含推理流水。
本文件负责存放位置、最小加载、恢复、失效传播和旧版兼容。

## 1. 运行时结构与唯一来源

```text
competition/
|-- data/raw/                 原始来源，不静默覆盖
|-- data/processed/           可重建处理结果
|-- src/                     求解和验证代码
|-- results/                  真实输出
|-- figures/                  图表
|-- paper/                    稿件及数字来源映射
|-- reports/                  详细分析/审查，按需
|-- logs/                     运行日志及 AI 使用记录，按需
|-- handoffs/                 仅实际委派/跨环境交接时创建
|   |-- outgoing/             TASK-NNN-vN.md
|   `-- incoming/             TASK-NNN-vN-rK-return.md
`-- memory/
    |-- active/
    |   |-- STATE.md           控制索引，Coordinator 单写
    |   `-- TASKS.md           当前行动队列及任务事实，Coordinator 单写
    |-- decisions/            DEC-NNN.md 和 OVR-NNN.md
    |-- evidence/             每个重要 Evidence 一个文件
    |-- issues/               重要问题与关闭依据
    |-- checkpoints/          checkpoint-Gn-NNN.md，不覆盖
    `-- archive/              历史任务/旧日志，不破坏 ID 定位
```

OVR 是 DECISION 子类，不另外维护 overrides 注册簿。
Return 是 TASK 的交付物，Review 是报告，Checkpoint 是 STATE 的历史快照；
它们不再产生独立业务状态机。

事实内容以 Evidence 和对应版本产物为准，任务以 TASK 为准，选型理由以 DEC 为准。
STATE 汇总这些事实，不能覆盖它们。快照不能覆盖更新的当前状态。

## 2. STATE 最小格式

字段枚举由 [workflow.md](workflow.md) 定义。以 YAML frontmatter 保存简短控制字段：

```yaml
---
schema_version: "5.1"
project_id: competition-local
revision: 1
coordinator: main
updated: "2026-09-09T17:00:00+08:00"
clock:
  starts_at: null
  deadline_at: null
  timezone: Asia/Shanghai
  source_ref: null
gate: null
pressure: NORMAL
workflow_mode: DEFAULT
freeze: {active: false, checkpoint: null}
paper_status: EMPTY
active_tasks: []
active_overrides: []
critical_issues: []
checkpoint_ref: null
---
```

正文仅包括 Problems 表（问题、状态、当前 model/result/claim ID）和 Next Actions。
`gate: null` 表示尚无已验收里程碑；只有选题确认与 G1 验收条件满足后才写 G1。
不复制实验数据、决策理由、日志。时钟 null 表示未知，不推算官方截止。
绝对时间带时区；剩余时间为计算值，可展示但不作为持久化权威值。

建议 STATE 低于 150 行且约 8 KB，二者均为软预算。超预算先压缩已结束指针和重复描述，
不能删重要约束来达标。大量问题可用当前子集 + 独立问题地图指针。
`revision` 只在实际控制状态变化时增加，不为每条回复刷新时间和版本。

每问当前卡片可放在 STATE 的 Problems 表或 `memory/active/<问题>-CURRENT.md`，
只留有效 DEC、正式入口/配置、最近有效运行与结果、论文/表格/支撑包入口及待同步项。
优先链接已有 current-policy 或等价清单，不复制参数真值。题面/有效决定定义预期，
入口/调用链/真实产物证明实际；二者分别核对，不用目录名或时间戳自动选版本。

消费者（论文、图、Excel、支撑包）分别标记 matching / stale / unverified / excluded：
matching 需有与来源版本匹配的依据；excluded 只表示本次明确不改，不表示已经匹配。
这是交付关系，不改变 Evidence 生命周期。更新后在本次授权范围内同步，范围外保留
待办；不把局部结果已完成写成全部交付已更新。机器清单格式见
[project-checks.md](project-checks.md)，普通任务可用已有文字映射。

## 3. 上下文加载预算

```text
L0: SKILL 路由 + STATE
L1: 当前 TASK、其约束、scope 内仍有效的确认/决策
L2: context_refs 的指定 Evidence，按需要沿依赖展开
L3: 历史实验、旧快照、完整日志，仅在具体疑点需要时读取
```

初次恢复建议先读 STATE、TASK 和 1-3 个相关引用，再按缺口增读。
这是加载起点，不是截断必要上下文的硬限额。
先 `rg --files` 定位文件，再 `rg -n` 定位 ID/字段，读相关记录或片段。
审查全部证据可以扫描元数据；不等于把所有正文装入上下文。

每次决定扩展加载先指出缺口：缺单位、缺约束、缺当前结果，还是需要核对输入版本。
ID 找不到时报告具体缺项，不能从文件名猜内容或从旧聊天补造数值。

## 4. 恢复与中断

新会话接手、`RECOVER PROJECT`、长任务中断或压缩后：

1. 确认项目根目录，读取最新 STATE，核对 project_id、Coordinator、revision。
2. 在 TASKS 中定位待续 TASK；核对其执行状态、产物、决策与有效确认。
   gate 为 null 时从 Next Actions 恢复待办，不推断 G1 已通过；旧 G1 记录按其验收依据核对，
   不批量重置，也不因字段存在就视为通过。
   当前任务涉及关键决策时核对 approval_ref 与 approval_scope，
   不能把已有 active 标签当作用户确认。
3. 只加载任务引用，检查产物存在、输入版本、未决问题和正在运行的进程/任务。
4. STATE 丢失或冲突时才读 checkpoint_ref 指向的快照，找不到再定位最近候选。
5. 区分“已确认、待核实、阻断”，先报告恢复范围，再执行安全的下一步。

不默认读取全部 active DEC 或最新 checkpoint。
HIGH/MEDIUM/LOW 只是摘要标签，必须同时说明缺失项；不得替代文件/证据验证。
中断后不知道外部操作是否完成，先查询状态或检查产物，不能直接重试有副作用操作。

压缩/交接前，在现有 TASK 的 Resume 段保存：
已完成步骤与输出、未验证项、最近失败命令及日志位置、下一条具体操作、
运行中的 job/session 标识及状态、输入版本、适用确认和禁止重开事项。
先落 Evidence/产物，再更新 TASK，最后更新必要的 STATE 指针。

长 debug 可有 `reports/TASK-NNN-working.md`，仅记观察与待做项；
结束时先把独有信息纳入 TASK/Evidence，再归档，不一律清空。
若来不及预写摘要，恢复必须以现有文件和真实运行状态为准，不虚构丢失的步骤。

## 5. ID 与查找

新记录以 `文件名 = id + .md` 精确定位；已有合法 ID 保持不变。
Coordinator 分配编号或任务命名空间，例如 `EXP-Q2-T031-01`、`RES-Q2-T031-01`。
任务不能自行扫描“最大序号 + 1”抢号。

通常定位：Evidence -> `memory/evidence/<ID>.md`；
DEC/OVR -> `memory/decisions/<ID>.md`；ISSUE -> `memory/issues/<ID>.md`；
TASK -> TASKS 的对应标题，已归档的任务通过保留的精确 locator 定位。
重名 ID 视为冲突，不选更新时间较新的猜测为真。
外部不共享文件系统时，ID 必须连同路径/附件或必要正文交付，不能只发 ID。

## 6. Evidence 与变更传播

格式见 [evidence 模板](../templates/evidence.md)，验证标准见 [validation.md](validation.md)。
`depends_on` 保存证据依赖；`artifacts` 记录路径和 SHA-256 或不可变版本。
代码/数据可作为 artifact，不强迫每个源文件再建一张 Evidence。

已发布 Evidence 的实质内容和其产物版本不原地覆盖；修改生成新 ID 或新不可变版本。
Coordinator 可更新生命周期、验证记录、替代链接，保留原因与时间。
`supersedes` 永远由新指旧，`superseded_by` 由旧指新。

上游数据、代码、参数、结果或已证实假设变更时：

1. 判断旧证据是否仍描述可访问的原版本；仅新增模型不使旧 Baseline 自动失效。
2. 如旧证据依赖被覆盖、验证依据无效或本身发现错误，标 stale/rejected，建必要 ISSUE。
3. 按 depends_on 反向查找受影响 Result/Claim/Figure，传播 stale 并定位论文引用。
4. Coordinator 将受影响选定问/章节回退至可证明状态，重新验证后发布；无关工作继续。

缺失引用、循环依赖或 hash 不符时不能发布 verified。
Paper 的来源映射和依赖字段共同用于查找受影响章节。
采用新方案不等于所有旧证据作废；obsolete 可保留为明确标注的历史比较资料。

## 7. 一致性、快照和归档

Coordinator 更新顺序：产物 -> Evidence/Issue -> TASK/DEC -> STATE（revision 最后增加）。
写后重读并检查引用。这个顺序不是跨文件数据库事务；中断时按事实逐项核对。
多人编辑或控制权交接时先确认前任停止写，记录新 Coordinator 与 revision。
冲突只阻塞相关操作，不进行强制覆盖、清空或“自动选择最近版本”。

Checkpoint 保存当时状态、证据指针和恢复产物位置，可包含当时小型 STATE 内容。
必须说明代码/数据/论文快照或 Git commit、校验值和恢复限制。
只有 Markdown 指针没有实际版本副本时，只能回溯状态，不能声称可回滚全部工程。

Gate 时可整理 TASKS 和旧日志；Evidence/DEC/ISSUE 原位保留可发现性，避免断链。
已完成 TASK 从活跃列表移除，详情归档时保留 locator；不因数量阈值删除失败证据。
本技能不要求 TIMELINE；需要赛事 AI 使用记录时按 [submission.md](submission.md) 保留。

重要工作结束时更新当前条目，替换已经过期的“当前/下一步”描述，不能把新结论
追加在互相矛盾的旧描述旁就视为同步。先核对 Issue 的实际关闭依据，再收束 STATE；
旧判断作为有版本和时间的历史保留。小修不需要重新总结全部项目。
TASKS 保留活跃任务和必要交付索引；长详情可迁入 `memory/archive/TASK-NNN.md`，
原位置留下 ID 与精确路径/标题。先保存独有的约束、批准、失败依据和续接信息，再归档。
摘要压缩是语义整理，不能机械截断行数。没有清理授权的审查只报告，不自动归档。

状态、依赖或交付诊断可按 [project-checks.md](project-checks.md) 运行只读工具；
自然语言矛盾、完整调用链和数学正确性仍需核读。检查脚本不替代 Coordinator 验收。

## 8. v3/v4/v5 兼容

V5.2 skill 保持 STATE/Evidence 的 `schema_version: "5.1"`；新增内容为可选记录
及独立交付清单格式，不要求批量改写旧记录。旧 ISSUE 的 `closed` 作为已关闭别名
读取并核对 Resolution，新写使用 `resolved`。旧 DEC 的 `obsolete` 表示历史取代提示，
结合替代链接判断，不自动转 active/rejected；新写仍用决策模板枚举。
缺 frontmatter 的记录可按文件名定位，状态按正文核实，不猜成 verified。
格式诊断不等于研究结论失效；保留原件并在涉及该记录时做有依据的迁移。

详细旧目录定位、迁移步骤及旧 Gate 映射见 [legacy-memory.md](legacy-memory.md)，仅遇到旧格式时读取。
