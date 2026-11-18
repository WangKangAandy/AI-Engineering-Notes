---
title: 现代 GitHub：把一个有边界的任务交给 Agent
summary: 用 GitHub Copilot Cloud Agent 完成一次小而可验收的资源导航改进，理解会话、环境、分支、PR 与权限的边界。
tags:
  - github
  - copilot
  - agents
created: 2026-11-16
status: learning
---

# 现代 GitHub：把一个有边界的任务交给 Agent

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[GitHub 协作与自动化：01 学习路线](<GitHub 协作与自动化：01 学习路线.md>)。

前面章节已经让资源导航仓库能在本地测试、构建并通过 CI。这里第一次把一个**有边界的一次性任务**交给 AI。主线选 GitHub Copilot 的 **Cloud** 环境：它在 GitHub 托管的隔离环境中工作，完成后把分支和 PR 交回仓库。它不是本地终端，也不是第 22 章的 Actions 自动化。相同仓库不代表相同登录、凭据或执行环境。

## 先确定任务和验收

好的 Agent 任务同时写清输入、允许修改的范围、命令和停止条件。第 12 章的练习仓库根目录已有 `test_catalog.py`。其中 `test_rejects_blank_field` 已验证标题为空；本次只增加一个针对性的断言，验证 **category 为空**也被拒绝。不要借任务重写解析器、改 workflow 或增加新的数据格式。

这一项只有几行，人工通常更快；这里用它学习委派和验收，并不意味着所有小改动都值得调用付费模型。

可直接复制下面的任务描述（把仓库和默认分支换成自己的值）：

```text
在我的资源导航仓库中，完成一项最小测试改进：

- 只修改test_catalog.py；
- 在现有空字段测试旁增加一个 category 为空的测试，保持现有实现和错误判据；
- 在仓库根目录运行 python -m unittest discover -v、python catalog.py resources.csv 和 python build.py；
- 有变更时创建面向 main 的 PR；
- 不修改 catalog.py、resources.csv、workflow 或文档；
- 不合并 Pull Request。完成后列出修改文件、实际执行的命令和结果。
```

这份请求有明确的文件边界和可复现命令。它也故意让 Agent 做一个小 diff：任务越大，越难从会话记录中判断哪个结果来自哪项要求。

## 选择 Cloud 并启动会话

GitHub 文档目前说明，Copilot cloud agent 面向付费 Copilot 计划；仓库还可能受“托管用户账号”或管理员策略限制。启动前先确认自己的账号、仓库写权限和可用量。看得到仓库不能推出你有权让 Agent 推送分支。[官方可用条件与入口](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/start-copilot-sessions)

在目标仓库打开 **Agents**，或进入 `github.com/copilot` 的会话页：

1. 在仓库选择器中选择自己的 `YOUR_LOGIN/resource-nav`，不要选上游示例仓库。
2. 在 Agent/环境选择器中选择 Copilot 和 **Cloud**。Cloud 指 GitHub 托管沙箱，不是 Actions 的 Environment 审批。
3. 选择 `main` 作为基础分支，粘贴任务描述并启动。
4. 在 session 日志中确认它找到已有的 `catalog.py` 和测试文件，再等待它提出修改或 PR。

从 Issue 指派 Copilot 时，官方行为是完成后创建 PR；从 prompt 启动时，可以在会话中要求创建 PR，也可以在完成后手动创建。[启动任务的三种入口](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task)

## 观察环境和结果

Cloud Agent 使用自己的临时开发环境。会话日志可以显示它读取的文件、工具调用、测试命令和提交；这些记录帮助你复核“它说做过什么”。它的环境并不会改变你的本地工作区，也不会继承你本地 `gh` 的登录状态。官方文档把会话日志、提交追踪和测试能力分开说明。[会话管理与日志](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/manage-and-track-agents)

看到以下情况时，先停下来判断，不要用一句“看起来完成了”覆盖证据：

| 观察 | 应得出的结论 |
| --- | --- |
| session 显示完成 | Agent 的会话结束，不等于需求验收或 PR 可合并 |
| 测试命令出现在日志且退出成功 | 这次环境中的测试通过；仍要查看 diff 和 CI |
| 修改了额外文件 | 越界，需要让 Agent 回退或在 PR 中人工修正 |
| 没有测试输出 | 测试未验证；补充请求或在本地/CI 运行 |
| 只有一个提交 | 只说明提交存在，不说明内容正确 |

如果方向开始偏离，可在会话输入框发送一次具体纠偏，例如“保留现有实现，只修改测试文件；请撤销其他文件的变更”。每次 steering 都消耗额度，且不能替代最终评审。

## PR 是验收面

从会话链接打开 PR，检查四件事：

- base 是 `main`，来源分支属于本任务；
- `Files changed` 只有 `test_catalog.py`；
- 新测试确实传入空 `category`，而不是仍在测空标题；
- PR Checks 包含 `python -m unittest discover -v`，并且是当前提交的结果。

基线 `test_catalog.py` 有 9 个测试，`test_rejects_blank_field` 只把 title 设为空；实现已经对所有列执行 strip 和空值判断。因此合理改动是新增一个测试，而不是重写实现。下面是可对照的最小用例，放在 `CatalogTests` 类中：

```python
    def test_rejects_blank_category(self):
        with self.assertRaises(ValueError):
            self.load("title,url,category\nDocs,https://example.com/, \n")
```

空格会在实现中被去掉，因而该输入应该抛出 `ValueError`。新增后应发现 10 个测试；如果项目后来增加过其他测试，就按原数量加一，不把固定数字当成功标准。这个用例没有修改正常资源，也没有证明外部 URL 可访问。

Cloud Agent 的分支和提交在远端，不会自动出现在你的本地工作区。如果要在本机复核对应 PR，先在本地 resource-nav 确认工作区干净，再用实际 PR 编号取得它的 head：

```powershell
$prNumber = 123  # 换成会话创建的实际 PR 编号
git status --short
if (git status --porcelain) { throw '先处理本地未提交修改' }
git fetch origin "pull/$prNumber/head:agent/$prNumber"
git switch "agent/$prNumber"
git rev-parse HEAD
git diff main...HEAD -- test_catalog.py
```

核对这里的 SHA 与 PR 页面 head SHA 一致，再运行本地命令。若 Agent 创建的是其他仓库分支或 PR 尚未创建，先从会话结果取得真实来源，不能猜分支名。完成验收后切回 main；是否删除本地临时分支由你决定，不用强制删除：

```powershell
py -3.12 -m unittest discover -v
py -3.12 catalog.py resources.csv
py -3.12 build.py
git switch main
```

命令应在读者自己 resource-nav 仓库根目录执行；它们分别证明测试、清单校验和页面生成。静态看到命令不等于命令成功。CI 还会有自己的运行记录。只有 diff、测试输出和仓库检查互相对应，才足以决定是否合并。

## 这次练习的边界

Cloud Agent 可以修改分支、提交并按请求创建 PR，但不会替你批准、合并或判断产品需求。你仍负责检查资源数据、测试含义和 CI 范围。不要把 Copilot 的账号资格、Cloud 沙箱网络或会话额度写进项目代码；这些是执行条件。

如果会话卡住或任务不再需要，使用 session 的 **Stop**，然后检查已经产生的提交和 PR。停止不会自动撤销已推送的修改；需要放弃时再关闭或删除自己的 PR。完成后保留可追溯记录：任务文字、session 链接、PR、diff、测试结果和未验证项。

下一篇把这次任务里的临时说明整理成项目长期上下文：[现代 GitHub：把项目知识与工作约定交给 Agent](<现代 GitHub：把项目知识与工作约定交给 Agent.md>)。

本书将相同新增用例放入临时副本实际运行：10 项 unittest、清单校验和页面构建均退出 0。该副本使用附件的两项初始数据；读者主线还包含第 8 章的 Pro Git，因此条目数应随自己的 CSV 增长。这是本地测试证据，不能替代自己的 Cloud 和 PR CI 结果。

**来源与限制（2026-11-18 核对）**：GitHub 的 [启动任务文档](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task)、[云端会话入口](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/start-copilot-sessions) 和 [会话管理文档](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/manage-and-track-agents) 支持本文关于 Cloud、入口、日志和停止的说明。本文未启动云端 Agent，也未创建真实 PR；本地命令是否通过应以读者自己的仓库和运行结果为准。
