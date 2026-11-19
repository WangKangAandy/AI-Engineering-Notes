---
title: 现代 GitHub：让已上线项目继续可靠：维护、费用、权限与故障
summary: 通过一次失败运行、一次依赖维护和一次 Actions 用量耗尽场景，建立可执行的维护、暂停、恢复和退出流程。
tags:
  - github
  - maintenance
  - security
  - actions
created: 2026-11-18
status: ready
---

# 现代 GitHub：让已上线项目继续可靠：维护、费用、权限与故障

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上线不是终点。一个小项目会遇到失败运行、依赖更新、权限过宽、Actions 额度耗尽和需要暂停自动化的情况。本章不罗列设置项，而是用维护循环回答：发生什么、先查哪一层、如何处理、怎样知道恢复了。

## 维护循环

每次维护都留下四条记录：

1. 触发了什么；
2. 影响了哪个结果；
3. 采取了什么处理；
4. 如何确认恢复或决定退出。

维护对象分三层：

- 仓库内容：代码、依赖、模板和文档；
- 自动化：workflow、权限、Secrets、Environment 和运行；
- 交付结果：artifact、Pages、Release 和线上页面。

不要把“workflow 文件存在”当作“自动化仍然可靠”。

## 处理一次失败运行

在 Actions 页面打开失败的 run，先记录提交 SHA、workflow 名称、job 和失败 step。按顺序检查：

1. 失败是否发生在 checkout 或 setup 环境；
2. 是 catalog.py、测试还是 build.py 失败；
3. 输入文件、Python 版本和依赖是否发生变化；
4. 是否只是网络或服务暂时不可用；
5. 重试是否会造成重复发布。

如果失败来自重复 URL，修复资源数据并创建 PR；如果失败来自 workflow 语法，先在分支上修改并让新的 PR run 验证。不要只点 Re-run 直到变绿，重试不会修复确定性输入错误。

如果一个运行卡住或不再需要，在 Actions → 运行详情中选择 Cancel workflow。取消后检查是否已经产生 artifact 或部署；未完成的 run 不能被当成没有副作用。

## 维护依赖和 action 版本

本项目依赖标准库，风险主要在 action 版本和 Python 版本。每次更新前：

~~~bash
git switch main
git pull --ff-only origin main
git switch -c maintenance/update-actions
git grep -n -E "actions/|python-version" -- .github/workflows
~~~

修改后先运行本机测试，再让 CI 运行。一次 PR 只更新一类依赖，便于定位回归。

如果一个 action 从 v4 更新到 v5，先阅读官方变更说明，确认输入参数、权限和 Node 运行时是否变化。不能因为版本数字更大就直接替换。

## 收紧权限和清理凭据

在已存在的 .github/workflows 文件中查看 workflow 顶层和 job 级 permissions。只读任务优先使用：

~~~yaml
permissions:
  contents: read
~~~

需要发布时才在 deploy job 中授予 pages: write 和 id-token: write。不要给整个 workflow 写 write-all。

清理 Secret 前先搜索使用者：

~~~bash
git grep -n -E "secrets\.|vars\.|GITHUB_TOKEN|COPILOT" -- .github
~~~

然后在 Settings → Secrets and variables 中核对名称。删除 Secret 不会自动修复引用；下一次运行可能直接失败。更换凭据时先添加新值、更新引用、验证运行，再删除旧值。

## Actions 用量耗尽时怎么办

GitHub 的用量提示是账号或组织计划的实际状态，不是所有仓库相同的固定结论。下面的截图是一个“账户用量通知截图”示例，表示该账号在当前计费周期已经用完 Actions minutes：

![账户用量通知截图](<_assets/modern-github/self-hosted-runner/actions-minutes-exhausted.png>)

打开 Settings → Billing and licensing → Actions，确认：

- 当前账号或组织；
- 计费周期；
- 已用分钟数和包含额度；
- 超额后的预算策略；
- 哪些仓库或 workflow 消耗最多。

如果只是普通小型检查，先减少重复运行、取消不必要的 push 触发、缩短缓存和 artifact 保留时间。如果工作需要特殊 SDK、内网、GPU、重型构建，或者确实遇到托管额度限制，转到 [附录 A：Self-hosted Runner](<现代 GitHub：附录 A Self-hosted Runner.md>)。自托管 Runner 会把任务放到自己的机器，不能把它当作“免费且无风险”的托管 runner 替代品。

尤其不要让不可信 Fork PR 在个人电脑 Runner 上执行。Runner 上的代码可能读取本地文件、网络和凭据；可信仓库、可信分支和最小权限是前置条件。

## 什么时候暂停或退出

如果项目暂时不维护：

1. 在 Issues 中记录暂停原因；
2. 禁用不必要的定时 workflow；
3. 保留构建产物和 Release 记录；
4. 撤销不再使用的凭据、App 私钥和 webhook secret；
5. 在 README 中说明项目状态和恢复入口。

如果要关闭 Pages 或删除 Runner，先保存需要的 artifact、配置和证据。删除资源是不可逆或难以恢复的操作，不能作为排错的第一步。

## 本章结束状态

你完成了一次维护审计，知道如何从失败 step、提交 SHA、权限和输入数据定位问题；也知道 Actions 用量耗尽时该减少消耗、调整预算还是使用自托管 Runner。

下一章进入 AI：Agent 只能接收边界清楚的任务，所有结果都要回到本书已经建立的分支、PR、CI 和验收流程。

