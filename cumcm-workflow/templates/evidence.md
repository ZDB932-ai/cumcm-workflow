# Evidence

每个重要记录存于 `memory/evidence/<id>.md`。
下例为候选结果字段骨架，不是已完成实验。未检查项保留 null/unknown。
生命周期与发布条件由 [validation.md](../references/validation.md) 唯一定义。

```yaml
---
schema_version: "5.1"
id: RES-Q2-T031-01
type: result
source_kind: computational
status: candidate
question: Q2
producer_task: TASK-031
created: "<带时区时间>"
updated: "<带时区时间>"
depends_on: [Q2-M004, EXP-Q2-T031-01]
artifacts:
  - role: output
    path: "results/q2/TASK-031/metrics.json"
    sha256: null
    version: null
validation:
  checked_by: null
  checked_at: null
  method: null
  scope: null
  input_versions: []
  checks_run: []
  outcome: not_checked
  limitations: []
supersedes: null
superseded_by: null
---
```

type：model / experiment / result / claim / fact / figure。
artifact 的 role 为 input/code/output/report 等，发布时提供真实 hash 或可访问不可变版本。
只写 hash 而没有可访问的文件版本不算可恢复。引用不能自指或构成循环。

## 正文

```markdown
## Purpose
<用途>

## Content
<模型/数值/论断/来源的实质内容，单位和口径明确>

## Provenance
<输入、代码、输出、页码/字段、推导或引用的定位>

## Limitations
<假设、未覆盖范围、不确定性>
```

无需给不适用类型添加空 Metrics、Files 等固定章节。

## 按类型补充

| type | 必需内容/依赖 |
|---|---|
| model | 数学定义、假设、参数、约束、验证计划；可有 decision、maturity=baseline/improved |
| experiment | depends_on 含模型；实际命令或推导过程、输入版本、参数、环境、run_status、日志与输出 |
| result | depends_on 含模型与实验；解析结果可用模型及可核对推导；数值/指标/单位/样本范围 |
| claim | depends_on 含支持的 Result/Fact/Model/Claim；原句、推论或计算、适用范围、论文位置 |
| fact | 原始文件/官方页面/文献、页码或字段、访问日期、事实与来源的对应 |
| figure | depends_on 含数据对应证据；代码/产物、单位和图表用途 |

Claim 不必都有数值，也不必都来自实验；Result 的 source_kind 为 computational 或 analytical。
同一批参数实验可有一个 EXP 和 runs 清单；必要的重要结果再独立建 RES。
比对新旧结果时，保留原记录；新 `supersedes` 指旧，旧 `superseded_by` 指新。

## 条件性来源记录

模型涉及顺序决策时，引用执行契约：决策时点、可用信息、可改变量、实际执行、
目标/评价、边界和输出。关键参数记录含义/范围、来源类别、确定方法、选择数据
及确定时点、更新规则与版本；可引用既有配置或参数说明，不另维护第二份数值表。

实验有程序运行时引用正式入口、配置/输入版本、run_id、退出状态、指标字段；
区分实际调用与目录中未调用的候选实现。结果的验证分别说明执行信息、选择信息、
研发过程限制，以及实际做过的可行性/复现/统计检查。不适用字段不添加空壳。

交付消费者关系可引用已有来源映射，或 [交付清单](../references/project-checks.md)。
映射匹配只说明声明来源版本相符，不自动证明正文论断正确。
