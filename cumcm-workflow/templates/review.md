# Review

同一格式用于 micro/final/scoped，检查深度服从范围和风险。
实际验收条件见 [validation.md](../references/validation.md)，不在模板重复维护。

```yaml
---
task_id: TASK-040
reviewer: "<人/Agent>"
scope: micro
created: "<带时区时间>"
reviewed_versions: []
input_refs: []
unreviewed: []
---
```

输入只读任务必要的题面、稿件和引用，必要时查反例/失败实验，不只看支持性证据。

```markdown
## Summary
<Critical/Major/Minor/Optional数量及实际检查范围>

## Findings

### FINDING-01
Severity: Major
Location: <文件/章节/公式/表格/代码行>
Problem: <具体问题及发生条件>
Evidence: <可核对的ID、数值、来源或复现步骤>
Blocks: <影响哪个结论/任务/Gate，或NONE>
Suggested Fix: <可执行修复>
Recheck: <修复后的复核方法>

## Outcome
<可通过/需修复/未完成验证；列出未覆盖范围>
```

独立评审先读题目和交付物，再查证据，不预先接受作者解释。
适用时逐项记录题面必答覆盖、执行/选参信息、消费者版本与人工核验依据。
字段只在有实际检查时使用；程序复现、Agent 审查、人工核验和提交回执分开报告。
普通 stylistic 偏好仅在用户要求或影响可读性时提出。
没有发现问题只能表述为“本次检查范围内未发现”，不能承诺无错误。
