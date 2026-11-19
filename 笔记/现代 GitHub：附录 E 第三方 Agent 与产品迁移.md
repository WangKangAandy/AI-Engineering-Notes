---
title: 现代 GitHub：附录 E 第三方 Agent 与产品迁移
summary: 将 Issue、分支、PR、CI 和人工验收契约迁移到 Cursor 等第三方 Agent，同时区分代码审查、任务执行和事件自动化。
tags:
  - github
  - ai
  - cursor
  - agent
created: 2026-11-18
status: ready
---

# 现代 GitHub：附录 E 第三方 Agent 与产品迁移

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新。欢迎通过 Issue 交流和纠错。

第三方 Agent 改变的是执行入口，不改变项目的验收契约。无论任务从 Cursor、IDE、GitHub Cloud Agent 还是其他服务开始，都要回到同一个仓库、分支、PR、CI 和人工结果。

## 先比较三个产品职责

| 能力 | 核心职责 | 主要结果 |
| --- | --- | --- |
| 代码审查产品 | 对 PR 差异提出意见 | 评论或建议，不等于批准 |
| Cloud Agent | 研究仓库并完成代码任务 | 分支、提交、PR 或任务记录 |
| Custom Automation | 按事件、时间或条件调用 Agent | 一次可观察、可停止的自动运行 |

它们可能使用相同的 Agent 基础设施，但入口、权限、触发条件和结果不同。不要因为 Bugbot 出现在 Automations 页面，就把它当成普通自定义 Automation。

## 迁移一个小任务到 Cursor

选择第 11 章已经完成过的“小测试改进”任务，不要挑会修改权限、workflow 或发布的任务。开始前准备：

- GitHub 仓库地址；
- Issue 编号和完成条件；
- 允许修改的文件；
- 禁止修改的文件；
- 本地可重复的测试命令；
- 关闭或撤销入口。

在 Cursor 中连接自己的仓库，选择从 Issue 或任务入口开始。产品界面会变化，按照当前官方文档确认授权和仓库范围；不要把截图中的按钮名称当作永恒 API。

提示内容应保留：

~~~text
请完成 Issue #ISSUE_NUMBER。
只允许修改 test_catalog.py 和必要的 catalog.py。
先给出计划，再执行。
必须运行 python -m unittest discover -s . -p 'test_*.py' -v。
完成后说明实际修改文件、测试命令和结果；不要创建或修改 workflow、Secrets、权限或发布设置。
~~~

Agent 完成后，到 GitHub PR 页面查看差异。不要只在 Cursor 的会话里验收。

## 配置规则的边界

项目规则可以说明：

- 默认命令在 Git Bash 执行；
- 修改前先读 README 和 CONTRIBUTING；
- 测试命令是什么；
- 不得提交 Secrets；
- 完成后必须报告验证边界。

规则不能替代任务契约，也不能授予 Agent 它本来没有的仓库权限。若同时存在 AGENTS.md、客户端规则和服务端配置，先确认它们实际作用范围，不要把“文件存在”写成“Agent 一定读取并遵守”。

## Bugbot 与 Custom Automation

Bugbot 是专用的 PR 审查能力，重点是发现差异中的问题。Custom Automation 是用户定义的触发条件、提示和工具权限。两者都可能在产品的自动化页面出现，但不能混为一谈。

为 Bugbot 或自定义审查设置规则时，明确：

- 检查哪些路径；
- 是否只读；
- 是否允许发表评论；
- 每个 PR 最多输出多少评论；
- 评论是否需要人工确认；
- 如何停用和清理凭据。

审查评论不能成为 required check，除非你另外配置了一个有明确退出码和验收规则的检查。

## 版本变化和验证边界

第三方产品的套餐、模型、入口、权限和 YAML 字段都可能变化。每次迁移记录：

- 产品名称和文档日期；
- 使用的账号和仓库范围；
- 入口和授权结果；
- Agent 分支、PR 和 head SHA；
- 本地或云端测试；
- 评论、失败和撤销结果。

如果产品只在本地修改，不能声称 GitHub Cloud Agent 已验证；如果它创建了 PR，不能把 PR 创建当成测试通过。

## 结束和撤销

完成迁移练习后：

1. 关闭或合并 PR；
2. 停止仍在运行的 Agent；
3. 禁用不再需要的 Automation；
4. 删除无用的仓库授权、Secret 和 webhook；
5. 在 Issue 中记录实际结果和未验证部分。

第三方 Agent 的最终评价仍然回到主线：任务是否可追溯、差异是否受限、测试是否通过、权限是否最小、结果是否由人验收。

