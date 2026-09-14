# Issue

重要问题存 `memory/issues/ISSUE-NNN.md`；轻微 debug 留在 TASK/Review。
Subagent 在分配范围内报告 Finding/候选问题，正式分级与关闭由 Coordinator 负责。

```yaml
---
id: ISSUE-007
severity: critical
status: open
created: "<带时区时间>"
updated: "<带时区时间>"
owner: main
affects: [Q2]
blocks: [TASK-031]
related: []
due_at: null
---
```

severity：critical / major。status：open / investigating / resolved / wontfix。
兼容读取历史 `closed`，核对 Resolution 后按已关闭理解；新记录统一写 `resolved`。
Minor/Optional 可留在审查报告；影响正确性或交付的事项不能通过降级绕过。

```markdown
## Problem
<具体错误、定位和复现/来源>

## Impact
<受影响的结果、依赖、论文与任务>

## Next
<当前判断、已尝试的证据指针、下一步或待决定事项>

## Resolution
<实际修复、复核依据、残余限制；关闭时填写>
```

普通修复不必新 DEC。只有证据真实失效时才标 stale/rejected，
不能因关闭一个 ISSUE 就把所有相关 Evidence 标 obsolete。
wontfix 记录原因及允许的不使用/披露范围，不代表已修复；
若仍阻断必要结论或提交，相关 Gate 不能通过。
