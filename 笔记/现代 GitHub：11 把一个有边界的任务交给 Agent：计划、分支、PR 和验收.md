---
title: 现代 GitHub：把一个有边界的任务交给 Agent：计划、分支、PR 和验收
summary: 从一个小 Issue 委派 Agent 任务，检查它的上下文、分支、差异、测试和权限，并在不合格时纠偏或停止。
tags:
  - github
  - ai
  - copilot
  - code-review
created: 2026-11-18
status: ready
---

# 现代 GitHub：把一个有边界的任务交给 Agent：计划、分支、PR 和验收

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

Agent 的价值不是替你按下 Merge。它可以研究仓库、制定计划、在自己的分支中修改和运行检查，但结果仍需要回到人已经熟悉的 Pull Request、CI 和验收证据。

本章以 GitHub Copilot cloud agent 为例。没有相应计划或权限时，你仍然可以完成任务契约、差异审查和人工验收；不要为了展示产品入口而跳过这些能力。

## 先写任务契约

在自己的 resource-nav 仓库创建 Issue：

~~~markdown
## 任务
为页面渲染增加一个“每项资源都生成一个列表项”的测试。

## 允许修改
- test_catalog.py
- 不修改 catalog.py 或 build.py

## 禁止修改
- resources.csv 的现有资源
- catalog.py、build.py 和 .github/workflows/
- Secrets、权限和发布设置

## 验收条件
- 新测试覆盖两个资源时生成两个列表项的结果
- 现有测试全部通过；本任务是补充覆盖率，不要求修改生产实现
- Pull Request 只包含允许修改的文件
~~~

这份契约先定义范围，再定义结果。把“请改进项目”直接交给 Agent，通常无法在评审时判断它是否越界。

## 启动 Cloud Agent

本章选择一种可观察的入口：在 Issue 的评论框中输入 @copilot，明确要求它先研究并在分支中补充测试；发送后等待 GitHub 返回任务状态或 PR 链接。如果账号没有 @copilot 入口，改用 Agents 面板，并记录这只是产品资格差异，不把本地 IDE 修改写成 Cloud Agent 结果。

评论内容：

~~~text
@copilot 请处理本 Issue：只修改 test_catalog.py，增加两个资源会生成两个 li 元素的测试。先给出计划，完成后创建 Pull Request。运行 python -m unittest discover -s . -p 'test_*.py' -v。不要修改 catalog.py、build.py、workflow、Secrets 或权限。
~~~

GitHub Copilot cloud agent 会在自己的环境中工作，并在分支上提交修改。它与 IDE 中直接修改本地文件的 agent mode 不是同一个执行面。提交 PR 前先观察它的计划和修改范围。由于本任务补充的是已有行为的测试覆盖，测试首次通过也可以接受；不要为了制造红灯而修改断言或生产代码。

如果你的账号没有 cloud agent 入口，不能把本地 IDE 生成的代码写成“Cloud Agent 已验证”。本章仍可用手工方式模拟：在 feature/agent-test-coverage 分支中按同一契约完成修改，再用 PR 验收。

## 观察四类证据

任务运行时依次核对：

1. **上下文**：Agent 是否读到了 README、CONTRIBUTING 和 Issue；
2. **范围**：它是否只修改允许文件；
3. **结果**：测试是否真的运行，失败是否与输入有关；
4. **身份和权限**：提交、分支和 PR 属于正确仓库，未读取或写入不必要的秘密。

“Session completed”只表示 Agent 停止了工作；“Pull Request created”只表示创建了 PR。二者都不等于代码正确。

## 在 PR 上验收

打开 Agent 创建的 PR：

- 看 Files changed，确认没有修改 workflow、Secrets 或资源数据；
- 看 Checks，确认测试命令与第 7 章相同；
- 看提交 SHA，确认 PR 显示的 head 与当前分支一致；
- 阅读 Agent 的说明，区分它声称做了什么和日志实际证明了什么。

如果 PR 的 Checks 区域显示 Waiting for approval 或 workflow requires approval：先检查 Files changed，确认没有越界文件和不可信脚本；在确认来源可信后，点击 Approve and run workflows。授权后再区分三种状态：尚待授权、正在运行、已失败。不要把“没有自动运行”写成测试通过，也不要在未审查差异时批准任意 PR 的工作流。

在本地取回同一 PR 的分支：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
gh pr checkout PR_NUMBER --repo YOUR_LOGIN/resource-nav
git status --short --branch
git diff main...HEAD -- test_catalog.py
python -m unittest discover -s . -p 'test_*.py' -v
~~~

用完后回到 main：

~~~bash
git switch main
git status --short --branch
~~~

PR_NUMBER 要换成自己的编号。不要在 Agent 分支上直接继续做另一个任务，以免把两个验收范围混在一起。

## 做一次纠偏

假设 Agent 还修改了 .github/workflows/ci.yml。不要只在评论里说“不要改这个”。在 Agent 创建的 PR 评论中输入 @copilot，明确触发继续处理：

~~~text
@copilot 请撤回对 .github/workflows/ci.yml、catalog.py 和 build.py 的修改，只保留 test_catalog.py 中的测试覆盖改动。重新运行完整 unittest，并在 PR 描述中列出实际修改文件。
~~~

它更新后再次检查差异。纠偏后的 PR 仍由人决定是否合并；如果反复越界，关闭任务或关闭 PR，保留原因。

## 什么时候停止

遇到以下情况时停止，而不是让 Agent 无限重试：

- 它无法说明修改依据；
- 反复修改同一处仍无法通过测试；
- 它要求访问与任务无关的 Secrets 或写权限；
- PR 的 head、仓库或目标分支不对；
- 任务需求本身需要重新讨论。

停止当前会话、关闭或标记 PR，并在 Issue 中记录未完成状态。停止是一种验收结果，不是失败的遮掩。

## 本章结束状态

合格的 Agent 任务有一条可追溯链：

Issue 契约 → Agent 计划或会话 → 分支提交 → PR 差异 → CI 日志 → 人的验收 → 合并或关闭。

下一章会把“只分析资源变更并发表评论”的场景做成受控事件自动化。自动化仍然要遵守本章的任务范围、权限和停止原则。

