# Override

OVR 是有期限的 DECISION 子类，存 `memory/decisions/OVR-NNN.md`。
何时需要 OVR、确认复用及到期处理见 [user-intent.md](../references/user-intent.md)。

```yaml
---
id: OVR-005
type: override
status: active
created: "<带时区时间>"
updated: "<带时区时间>"
rule: "<被覆盖的SOFT策略>"
scope: [Q2]
risk_level: R2
reason: "<用户目的和适用背景>"
risk_accepted: "<本次已经说明并被接受的风险>"
approved_by: user
approval_ref: "<确认消息定位/时间及必要原话>"
expires:
  at: null
  condition: "<例如Q2当前选定结果达到VALIDATED>"
related: [TASK-031]
---
```

status：active / expired / revoked。
`expires.at` 或 `expires.condition` 至少一个非空；两者均填时任一满足即到期。
scope 必须明确；临时 Q2 例外不得扩展到全项目。
at 用带时区绝对时间；不写“剩余 < H+12”等混合相对表达。
条件无法判断时核实，不自动续期，不自动回滚已完成工作。
R0/R1 默认不建 OVR；R4 不可用 OVR 放行。
只有真实确认后才填 active，不能预生成一份“用户已经批准”的记录。
