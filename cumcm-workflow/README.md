# cumcm-workflow

数学建模竞赛的工作流技能。当前维护版本为 5.2.2，保留五对象与关键决策确认，
增加任务范围恢复、参数来源、论文论证、交付映射及只读项目检查。入口是 [SKILL.md](SKILL.md)。

## 工程结构

```text
cumcm-workflow/
|-- SKILL.md
|-- README.md
|-- references/
|   |-- workflow.md       状态、Gate、压力与止损
|   |-- user-intent.md    规则归属、风险、用户确认
|   |-- memory.md         上下文、恢复、证据依赖、迁移
|   |-- legacy-memory.md  旧目录恢复与迁移，按需
|   |-- multi-agent.md    任务模式、并发写入和验收
|   |-- modeling.md       数据、模型、实验及实现
|   |-- validation.md     验证发布与审查
|   |-- paper.md          论断与论文来源映射
|   |-- submission.md     规则核实、冻结、提交
|   `-- project-checks.md 检查命令、交付清单及边界
|-- scripts/
|   `-- check_project.py  只读引用/依赖/交付检查
`-- templates/
    |-- task.md
    |-- return.md
    |-- decision.md
    |-- override.md
    |-- evidence.md
    |-- issue.md
    |-- checkpoint.md
    `-- review.md
```

## 使用

纯知识问答不启动比赛流程。比赛项目先确定实际根目录、题面和时间来源，
再按 [memory.md](references/memory.md) 建最小状态；模板按需填，不一次性复制全套空文件。
新会话直接要求继续任务，或输入 `RECOVER PROJECT`，均触发恢复。
关键决策的确认范围、提案保存和正式 DEC/STATE 写入条件只在
[user-intent.md](references/user-intent.md) 定义；用户确认与实验验证分别核对。

五核心对象保持不变；Gate、状态、压力、写权等分别由对应 reference 唯一定义。
此 README 只导航，不复制验收表。运行时目录不要建在技能包里。
本设计目录的 Skill 实体位于 `.workbuddy/skills/cumcm-workflow`。同步来源为
`E:/26国赛建模/.agents/skills/cumcm-workflow`；比赛工作区内的 WorkBuddy 路径是联接，
本设计目录内的是独立副本。维护后重新同步，不另装全局副本。

## 兼容与边界

旧版 CURRENT_STATE/registry 通过 [迁移说明](references/memory.md) 按需读取和升级。
先备份、保留 ID、核对验证依据，再切换指针；不强删旧项目。

技能是执行约定，不是调度服务器、文件锁或数据库。并发隔离、持续后台运行、
自动失效传播和平台上传需要执行者及实际工具落实，不因文档存在就视为已实现。
只读检查器能报告声明的引用、hash 与影响关系；不会自动改状态、运行模型、
核实数学结论或证明交付合规。具体覆盖范围见 [project-checks.md](references/project-checks.md)。
官方时间/规则须按届核实；74 小时时间表仅为示例。

## 维护

规则只在其 reference 修改，字段只在对应模板修改，然后核对入口路由和跨文档消费者。
审查报告、备份及测试属于维护工程，不应作为竞赛启动上下文自动加载。
原维护工程的审查记录位于其 `docs/cumcm-workflow-review/`，未随本技能分发，
不是当前比赛项目的运行依赖。
