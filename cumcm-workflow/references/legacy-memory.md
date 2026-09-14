# 旧版记忆定位与迁移

仅恢复旧项目或迁移旧注册簿时读取；当前记录的生命周期见 [memory.md](memory.md)。

读取优先顺序：当前已声明的 STATE -> `memory/active/STATE.md`
-> `memory/active/CURRENT_STATE.md` -> `memory/CURRENT_STATE.md`。
多个当前状态冲突时先核对，不擅自认定某个更权威。

| 旧记录实际位置 | 兼容方式 |
|---|---|
| `memory/registry/{MODEL,EXPERIMENT,RESULT}_REGISTRY.md` 或 memory 根目录同名文件 | 按旧 ID/标题定位；按需迁出单条 Evidence |
| `memory/registry/DECISIONS.md`、`FACTS.md`、`ISSUES.md` | DEC/FACT/ISSUE 保留 ID，必要时拆出 |
| `memory/active/WORKING_MEMORY.md` | 只提取当前任务独有的 Resume 信息 |
| `memory/handoff/HANDOFF.md`、`memory/log/TIMELINE.md` | 原位保留历史，不作为当前状态权威 |
| v5 的 `memory/overrides/OVR-NNN.md` | 读取兼容；按需迁往 decisions/，避免双份活跃例外 |

迁移前备份；建立 `memory/archive/MIGRATION.md` 中的 ID -> 旧路径#标题 -> 新路径映射。
只迁当前任务和活跃指针，核对数量、引用、验证来源，再切换 STATE。旧文件不删。
只改文件名不足以完成迁移，旧 `verified` 也不能无检查继承。
旧 DEC 缺少确认字段时，按实际内容判断是否属于关键决策，只检查当前任务所需记录。
已有真实确认可引用并补齐字段，无需再问；找不到则暂停依赖其正式采用的工作并核实，
不虚构批准、不自动把历史 active 当作已获确认，也不因确认缺项判定原实验数据失效。
确认规则是当前执行边界，不因继续读取旧格式而停用；STATE/Evidence 的 5.1 schema 不变。

旧 BASELINE 根据实际产物映射为 ANALYZED 或 IMPLEMENTED；
旧 ENHANCED 仅在验证仍有效时映射 VALIDATED，maturity=improved；
旧 FREEZE 压力值需核对冻结清单，不能自动映射为已冻结。
运行时契约不匹配而无时间迁移时，在旧模式继续相关工作并明确限制。
