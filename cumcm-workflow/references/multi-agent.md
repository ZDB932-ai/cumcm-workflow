# 多 Agent 任务接口

采用一名 Coordinator + 按任务存在的执行者。role 是专业视角，mode 是动作边界，
二者分开；不要求常驻多个 Agent，也不按模型品牌猜测能力。

## 1. 何时派发

用户明确让另一个 Agent 执行，或当前环境/适用指令授权委派时，才实际调用调度工具。
用户只要外发提示词时交付提示词，不继续替该 Agent 完成整项工作。
工具、账号或文件不可达时说明限制，生成可交接包，不假装完成派发。

局部简单任务直接做。独立数据检查、代码实现、论文章节可并行；
强依赖上游结果的任务先准备接口，输入未就绪时不要拿猜测冒充真实输入。
用户要求独立评审/方案比较时可有意冗余，明确预算和不读取其他评审结论的范围。

## 2. Mode 与角色

| mode | 任务目标 | 默认边界 |
|---|---|---|
| PROPOSAL | 分析选项、证据与推荐 | 不改正式选型或控制状态 |
| EXECUTION | 实现、求解、写作或修复既定任务 | 不无故重开方案；实质错误上报 |
| VALIDATION | 验证假设、代码、结果 | 默认只查不修；修复需明确任务授权 |
| REVIEW | 独立审查交付物 | 给定位明确的 Finding，不擅自重写 |
| RESEARCH | 查找适用资料和来源 | 资料先作为候选，不冒称已验证 |

role 可为 modeling/coding/data/paper/reviewer 等，无需新增 MODE。
论文手可读取候选资料理解背景，但其事实输出遵守 [paper.md](paper.md)。

## 3. 写入范围与版本

- Control：STATE、TASKS、DEC/OVR、Gate/Freeze、正式 ISSUE 结案及 Evidence 发布，
  仅 Coordinator 写。人直接编辑时也需停止其他控制写者，交接后继续。
- 写权不等于决策权。关键决策适用 [user-intent.md](user-intent.md) 的用户确认要求；
  Coordinator 和子 Agent 均不能把任务分配、返回验收或实验验证当作该确认。
- Candidate：Agent 只能创建/修改任务 allow_write 列明的候选证据和产物。
- 已发布 Evidence 和源数据不可原地覆盖；共享 `src/common` 等文件由一名 Owner 集成。
- 为任务分配 ID/路径，例如 `results/q2/TASK-031/`；不是全局 `results/**` 写权。
- 不同问题也可能写同一工具模块，因此按实际文件集合查重，而不是按 Q 编号判断安全。
- 同一 Q 可并行不同文件、独立比较或只读审查；重叠写必须串行或在独立工作区产出补丁。

Task Packet 包含 base_revision、输入 hash/不可变版本、depends_on、allow_write、
read_only、reserved_ids、deadline/stop_condition 和验收方法。
依赖关键决策的执行任务须带可核对的确认引用与范围；确认未就绪时只分派已授权的
提案/候选工作或独立任务，不把“采用提案后执行”包装成普通编码委派。
共享引用不能指向会被另一任务覆盖的临时文件。
这些是协作约定，不是文件系统锁；不能声称 Markdown 能强制隔离写入。

## 4. Prompt 生成与交接

使用 [task 模板](../templates/task.md)。内部简单任务在 TASKS 内联；
跨 Agent 的完整 Prompt 存 `handoffs/outgoing/TASK-NNN-vN.md`，
TASKS 只留摘要、owner、状态和 locator，不维护两份任务正文。

共享文件系统：给 ID、准确路径、版本及必要读取片段。
不共享文件系统：提供题意、模型定义、字段/单位、必要数值、决策和确认范围，
并列出已提供附件与缺失附件。只给一个本地 ID 的 Prompt 不算自包含。
大型/敏感数据不要整包复制；确认传输目标和必要范围，遵守当届资料/AI 使用限制。
没有执行环境的 Agent 只能分析或产代码，不能伪称已本地运行。

输出约定只需结论、证据、文件、验证、风险和决策请求；长分析另存报告。
需要返回的格式与关键字段直接包含在 Prompt 内，外部执行者不能依赖未提供的模板路径。
修改已派发 Prompt 要增加版本，说明旧任务是否取消；不默默覆盖 v1。

## 5. Return 验收

标准返回见 [return 模板](../templates/return.md)。Coordinator：

1. 检查 task_id、prompt_version、return_id、base_revision 与来源。
2. 检查实际改动范围和交付物存在；外部文本/代码先在隔离位置检查，不直接运行未知脚本。
3. 比对输入版本。全局 revision 变化不必一律拒收：无关变化可接受；
   输入、接口、决策或写入文件冲突时暂停受影响的接纳，要求复核/重跑。
4. 核对实际输出、测试、依赖与失败项；按 [validation.md](validation.md) 决定证据发布。
5. 涉及关键决策的正式采用/替换时先核对用户确认。无确认的建议可作为提案或候选接纳，
   但不生成正式 DEC、不改变当前选型；确认与证据验收是两个条件。
6. 在 TASK 记录 ACCEPTED / PARTIALLY_ACCEPTED / NEEDS_VALIDATION / REJECTED 和原因；
   只合并已验收且具备所需确认的部分，最后更新必要的 STATE。

同一 return_id + 内容 hash 已处理，则不再重复建 Evidence/DEC 或晋级。
同 ID 不同内容属于冲突，不能当作正常重试；修订返回使用新 return_id。
返回保存为 `handoffs/incoming/<return_id>-return.md`，将具体路径或该任务的修订范围
纳入 allow_write。第一次 PARTIAL 和随后 DONE 分别保留，不覆盖原返回。
保留输入 Prompt、原始 Return 和已接纳 Evidence 的关联。

DONE 表示 Agent 自报工作完成，不代表验收成功。
代码可以已交付但结果仍未验证；TASK 的 acceptance 与 Evidence.status 分开记录。
范围外建议、新模型建议和新权限请求都是提议，不自动授予执行权。

## 6. 错误、控制权和续接

发现旧决定有问题，在 Return 中写 decision_request：目标 DEC、新证据、影响、建议。
不另开 DRR 注册簿。只有实质选型改变才新建 DEC，普通修 bug 不必造新决策。

任务失败/中断保留现有 candidate 和运行日志，在 TASK Resume 留下一条可执行下一步。
如需换 Coordinator，先确认旧写者停下，记录新 owner/revision，检查在途返回；
若无法确认旧写者是否仍在写，暂停控制层变更，保留只读诊断和隔离产物。
