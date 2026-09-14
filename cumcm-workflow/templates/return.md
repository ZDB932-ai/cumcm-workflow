# Agent Return

每份返回对应一个 Prompt 版本。保存 `handoffs/incoming/<return_id>-return.md`，
例如 `TASK-031-v1-r1-return.md`；修订 r2 使用新路径，不能覆盖 r1。
重试同一内容复用 return_id；修订内容另用新 return_id，避免歧义。
同 ID 同内容的重试只返回既有文件；同 ID 异内容先报告冲突。旧无修订号路径仍可
按任务 locator 读取，新返回不能覆盖它；新路径须在 Coordinator 分配的写集内。
验收流程只在 [multi-agent.md](../references/multi-agent.md) 定义。

```yaml
---
task_id: TASK-031
prompt_version: 1
return_id: TASK-031-v1-r1
base_revision: 1
status: PARTIAL
created: "<带时区时间>"
input_versions:
  - {path: "<实际输入>", version: "<实际版本或SHA-256>"}
evidence_created: []
deliverables:
  - {path: "<实际产物>", version: "<hash或不可变版本>", description: "<说明>"}
decision_request: null
state_suggestion: null
---
```

status 使用 DONE / PARTIAL / BLOCKED / FAILED，仅描述执行者的工作结果。
不要自行填写 Coordinator 的 acceptance，也不要宣称 candidate 已被发布。

```markdown
## Findings
<最多五条关键发现，区分事实、推测与建议，不再加一份重复摘要>

## Validation Performed
<实际命令/检查、退出状态、输出/日志、未运行检查及原因>

## Risks and Limitations
<输入变化、未知项、缺失产物、范围外建议>

## Decision Request
<没有则 NONE；有则目标DEC、新证据、影响、建议>

## State Suggestion
<只提议受影响字段及Evidence ID，不复制整个STATE>

## Next
<最必要的1-3项；长报告给路径>
```

Coordinator 在 TASK 中记录返回内容 hash、接纳状态和理由：
ACCEPTED / PARTIALLY_ACCEPTED / NEEDS_VALIDATION / REJECTED。
正文与元数据同字段只填写一次；复杂请求可在元数据用短摘要并引用正文。
缺少约定格式时先提取事实再验收，不能因有整齐模板就降低验证标准。
