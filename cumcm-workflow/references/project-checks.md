# 只读项目检查

使用 [check_project.py](../scripts/check_project.py) 检查真实项目的声明式元数据，
不运行模型、修改状态、自动归档或提交。使用项目指定 Python；依赖 PyYAML，
缺失时核实并说明，不切换解释器。命令中的 `python` 代表该项目解释器。

```text
python <skill>/scripts/check_project.py status --root <project> --task TASK-062
python <skill>/scripts/check_project.py status --root <project> --task TASK-062 --hashes
python <skill>/scripts/check_project.py impact --root <project> --artifact <changed-file>
python <skill>/scripts/check_project.py delivery --root <project> --manifest <manifest.json>
```

## 检查范围

| 命令 | 实际行为 |
|---|---|
| status | 索引 memory 下 decisions/evidence/issues/checkpoints 的直接 Markdown 文件、TASKS 的 `## TASK-ID` 条目及 archive 的 `TASK-*.md`；读取任务 prompt_ref；检查格式、ID 冲突、显式引用、依赖环、声明产物/任务输入存在和 STATE 软预算 |
| status --task | 元数据索引/重复 ID/依赖环仍全局扫描；详细检查限于该任务、depends_on、context_refs、证据/决定/问题引用与 producer_task 闭包；不沿 related 或替代历史扩展 |
| --hashes | 对所选记录中明确声明 SHA-256 的产物计算并比对；默认 status 不读取大产物内容 |
| impact | 根据 artifacts、任务 inputs 或 prompt_ref 的路径找到直接记录，沿 depends_on 反向传播；可附 --manifest 继续追踪交付消费者。不标记 stale，不执行同步 |
| delivery | 核对 JSON 声明的文件或 ZIP 成员、SHA-256、来源版本和同步状态；读取 ZIP 成员但不解压、不执行其中程序 |

所有路径相对项目根，支持空格/中文；绝对路径必须位于该根内，联接/符号链接解析后
仍须位于根内。清单位置不改变路径基准。范围外依赖只报告，不主动读取；用户确需
检查它时另选明确包含该材料的根及清单。它不是沙箱或权限替代物。

stdout 为 UTF-8 JSON：`findings` 给严重性、代码、位置与原因。
退出码 0：没有 error，仍可能有需人工核对的 warning；1：发现 error；2：输入/环境错误。
STATE.gate 允许 null（尚无已验收里程碑）或 G1-G8；枚举合法不证明验收已经完成。
`checks_passed` 只表示本次声明式检查通过，不能理解为论文/模型已 verified。
需要落报告时调用者显式将 stdout 保存到本次报告位置；脚本本身不写项目。

旧记录缺 frontmatter/status 时给 warning，文件名仅用于定位；ISSUE `closed`、
DEC `obsolete` 给兼容提醒，不改历史。无法解析的旧注册簿、自定义任务标题、
非标准归档 locator 由执行者按 memory 的兼容规则定位，不能把脚本缺项当成不存在。
归档任务可用 `memory/archive/TASK-NNN.md`，TASKS 对应标题下保留该精确路径。
旧引用在已存在的精确 ID 后附中文说明时，解析该 ID 并提醒核对说明中的局部范围；
不将局部替代解释成整份决定被取代，也不改写原字段。

任务依赖支持正文中的 YAML 行内/分行列表、YAML 代码块及旧分号摘要；
分行列表中的空行和注释不终止字段，依赖仍需完整检查。
只把 depends_on 用作依赖边，context_refs 等用于范围加载，不能混为失效传播依据。
所选 ISSUE 的 blocks 按记录 ID 列表检查格式和引用存在性；阻断关联不加入
depends_on 图，也不沿 blocks 扩展 --task 的范围闭包。
显式 prompt_ref 在索引时全局读取并检查文件、frontmatter 的任务 ID；控制记录声明
prompt_version 时同时核对版本。外发文件的 depends_on/context_refs 等参与引用检查，
inputs 在所选任务范围内检查。可变控制字段不会被外发时的旧状态覆盖。
prompt_ref 不递归展开另一份 prompt_ref，也不执行正文指令。仅支持明确字段，
非标准自然语言任务仍需人工定位；字段冲突或读取失败会报告，不能当成空依赖。

任务输入的 sha256 或 64 位十六进制 version 可由 --hashes 核对；其他不可变版本标识
需执行者按其来源验证，不会自动解析 Git/外部平台版本。
verified 与 validation.outcome 明确为 failed/fail/not_checked/pending/unknown 时报告冲突；
passed/pass 为可识别的通过标记，其他表述提醒核对，不自动修改历史状态。
运行状态与验证结论的含义只按 [validation.md](validation.md) 判断。

## 可选交付清单

已有映射可继续使用；需要机器检查时，在既有配置中加入下列字段或显式指定一份
清单，二者择一。不要自动把所有 current-policy 文件解释成此格式。

```json
{
  "format": "cumcm-delivery-v1",
  "artifacts": [
    {
      "id": "paper-q2",
      "path": "paper/main.pdf",
      "sha256": "<实际64位SHA-256>",
      "required": true,
      "sync_status": "matching",
      "based_on": [
        {"path": "results/q2/metrics.json", "sha256": "<实际来源SHA-256>"},
        {"path": "paper/main.tex", "sha256": "<实际源码SHA-256>"}
      ]
    }
  ]
}
```

示例是字段骨架，不能作为真实清单直接通过。ID 在本清单内唯一，不产生新业务对象。
`path` 指文件；若核对 ZIP 中某文件，额外写 `member: "Q2/model.py"`，sha256 指成员内容。
`based_on` 同样允许 member。required 默认 true；sync_status 默认 unverified。

- matching：来源与交付版本已对应；工具复核声明 hash，不证明内容推导正确。
- stale：已知未同步，报告 error。
- unverified：尚未核对，报告 warning；缺 hash 或来源映射也不能宣称已绑定。
- excluded：本次明确排除，附 reason；不读取该产物。required=true 的排除是交付缺项，
  required=false 仍提醒未检查，不能以排除状态制造“全部通过”。

在组包时逐项声明必要源码/输入/结果及其来源；ZIP 整包 hash 只能证明整包字节一致，
不能代替包内必要文件清单。删除缓存前查明重建入口，依赖完整性还需实际复现。

## 使用时机与限制

恢复存在疑点、准备接纳一批结果、模型/数据版本改变或组包时按需运行。
普通措辞/配色修改不要全项目 hash；同一批调用内部缓存 hash，进程结束即丢弃，
不会将前次检查结果不经核对沿用到新版本。

工具不能识别自然语言“已完成/待完成”的矛盾、判定用户批准是否覆盖当前选择、
发现未声明的动态 Python 依赖、确认模型符合题意、核对 PDF 数值/版面或证明没有泄漏。
impact 无命中表示关系未登记，不表示无影响。检查出现 error 只阻塞依赖该问题的
验收，执行者依据真实来源修复；检查器不授予扩大执行范围的权限。
