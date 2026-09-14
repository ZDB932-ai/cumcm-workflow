# Checkpoint

保存为 `memory/checkpoints/checkpoint-Gn-NNN.md`，修订另用新编号。
快照允许保存当时的小型 STATE；禁止覆盖更新的当前状态。
恢复规范见 [memory.md](../references/memory.md)，冻结见 [submission.md](../references/submission.md)。

```yaml
---
id: checkpoint-G4-001
gate: G4
created: "<带时区时间>"
created_by: main
state_revision: 12
snapshot_kind: gate
evidence_refs: []
decision_refs: []
issue_refs: []
artifacts: []
restoration: state_only
---
```

snapshot_kind：gate / freeze / submission。
restoration：state_only / artifacts_available，只有真实副本/版本可用时才填后者。

```markdown
## State at Capture
<当时状态、问题表、关键任务/例外/问题指针>

## Artifact Manifest
<代码/数据/论文/结果的实际副本路径或commit、hash、必要环境>

## Gate Evidence
<各验收条件及支持ID；未满足部分如实列出>

## Restore Procedure
<先核对当前文件和快照，不覆盖用户新改动；逐步恢复办法及限制>

## Submission Receipt
<仅提交快照填写：各必需步骤的目标、时间、材料版本和回执位置>
```

Gate 快照和 Context Resume 不重复：快照是历史验收，Resume 是当前行动。
没有真实产物备份时只能恢复状态线索，不承诺完整回滚。
