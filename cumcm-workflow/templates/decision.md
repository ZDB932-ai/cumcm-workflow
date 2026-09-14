# Decision

只为重要策略、模型/假设或接口选择建 `memory/decisions/DEC-NNN.md`。
普通修 bug、例行验收或小图改色不要求新 DEC。
规则见 [user-intent.md](../references/user-intent.md)。
以下为需要用户确认的正式决策骨架，不是已获批准的实际记录；
只有取得真实确认并替换占位内容后才能创建，待确认提案保存在 TASK/Return/报告。

```yaml
---
id: DEC-017
type: decision
status: active
question: Q2
created: "<带时区时间>"
updated: "<带时区时间>"
user_confirmation_required: true
decided_by: user
approval_ref: "<真实用户确认的消息/时间定位及必要原话，或可解析到该确认的引用>"
approval_scope: "<用户确认覆盖的具体方案/版本、问题与边界>"
related: []
supersedes: null
superseded_by: null
---
```

status：active / superseded / rejected。提案先在 TASK/Return 中，不冒充 active。
历史 `obsolete` 需结合替代记录读取，不自动判 rejected 或重新激活；新记录使用上表枚举。
`decided_by` 是作出决定者，不是写文件者；Coordinator 代为记录时仍填写 user。
仅不属于关键决策、也不触发其他用户确认要求的授权内决定，才可填写
`user_confirmation_required: false`、`decided_by: "<Coordinator>"`，
并将 `approval_ref/approval_scope` 留空；不能靠改字段免除实际适用的确认。

```markdown
## Decision
<已获确认的明确选择；与 approval_scope 和备选表保持一致>

## Rationale
<关键证据、假设适合性、成本与限制>

## Alternatives
<有意义的备选及未采纳理由，无需凑三种>

## Reopen
<新证据、关键前提失效或用户新要求>

## Recovery
<可逆性、原版本和回退办法；未知明确写出>
```

Subagent 重开请求在 Return 内写目标 DEC、新证据、影响和建议，不新建 DRR 文件。
涉及关键决策时，取得用户确认后新 DEC 才指向旧 DEC；拒绝时在 TASK/Return 验收处保存理由。
单次执行批准留在 TASK；长期方案决策留在 DEC；有期限策略例外用 OVR。
