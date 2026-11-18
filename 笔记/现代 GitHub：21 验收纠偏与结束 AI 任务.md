---
title: 现代 GitHub：21 验收纠偏与结束 AI 任务
summary: 用需求、diff、测试和日志验收 Copilot 结果，处理越界或失败，并在不需要时停止会话。
tags:
  - github
  - copilot
  - agents
created: 2026-11-18
status: learning
---

# 现代 GitHub：21 验收纠偏与结束 AI 任务

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[现代 GitHub：00 导读](<现代 GitHub：00 导读.md>)。

第 19 章的会话完成，只是“Agent 停止工作”的事实；第 20 章的规则被读取，只是“输入包含了上下文”的事实。验收要把需求、改动、测试和运行记录拼起来。不要因为 AI 说“已完成”就跳过第 8 章已经学过的 PR 评审。

## 四层证据

以“为 `category` 为空增加测试”为例，逐层核对：

1. **需求**：任务是否只允许修改 `test_catalog.py`，并明确空分类的行为？
2. **diff**：新增断言是否真正构造空 `category`，是否出现无关文件或实现重写？
3. **测试**：会话日志和 PR Checks 是否显示 `python -m unittest discover -v` 的退出结果？
4. **仓库事实**：目标分支、提交、检查和 PR 评论是否对应当前 SHA？

四层有一层缺失，就把结论写成“尚未验证”，而不是“通过”。Agent 自测和 CI 都是证据，但不能代替人对需求的判断。

## 一次真实的纠偏

假设 diff 还修改了 `catalog.py`。先在本地取得第 19 章会话实际创建的 PR 分支，按第 19 章的 `git fetch` 示例核对 head SHA；不要在仍停在 main 的工作区寻找云端尚未合并的测试。确认分支后，在 session 的 steering 输入框写出可执行的修正：

```text
当前 diff 超出范围。请撤销 catalog.py 和其他无关文件的修改，只保留
 test_catalog.py 中针对空 category 的测试；重新运行
 python -m unittest discover -v，并在回复中列出最终文件。
```

等待工具调用完成后，重新看 diff 和测试。若 Agent 无法回退、测试失败或继续扩大范围，停止会话，在本地或 PR 分支人工修正。不要连续发送含义相同的“再试一次”：每次 steering 都消耗额度，且会让责任边界更模糊。

当结果是业务判断错误（例如把“空分类应拒绝”改成“空分类默许”），纠偏消息应指出预期行为和现有测试依据，而不是只说“请修好”。这能让下一次修改有可检查的判据。

## 在同一任务上演练一次错误断言

如果真实 Agent 一次就做对，不要编造它失败过。可以在自己的 PR 工作分支手工构造一个教学故障：将新增 category 测试中的 `assertRaises(ValueError)` 临时改成 `assertRaises(TypeError)`，只改这一处，然后运行：

```powershell
py -3.12 -m unittest test_catalog.CatalogTests.test_rejects_blank_category -v
```

测试应以非零退出：实现实际抛出的是 ValueError，断言却要求 TypeError。先阅读 traceback 和 `load_resources` 的空值检查，再恢复断言；不要为了让测试变绿把实现改成 TypeError。这里的测试方法名以实际 diff 为准；如果 Agent 使用了不同名称，先从 `test_catalog.py` 的新增方法确认，再运行对应方法或直接运行完整测试。随后运行完整 `py -3.12 -m unittest discover -v` 和 `py -3.12 build.py`，检查 diff 只剩最初的新增测试。未提交的教学故障不需要推送。

这次演练的纠偏依据来自已有契约、源码与失败输出。假如真实 Agent 做出同类错误，把这些证据发送到原 session；如果只是环境没有 Python，修复环境后再运行，不能用改断言解决环境失败。恢复后仍需确认最新 PR SHA 的检查，避免把旧绿灯算给新提交。

## 失败、越界和停止

| 现象 | 处理 | 不应作的推断 |
| --- | --- | --- |
| 测试命令失败 | 记录完整错误，先判断环境缺依赖还是代码错误 | 不把计划中的命令当成通过 |
| 修改范围越界 | 要求回退；仍越界就停止并人工处理 | 不认为规则文件自动阻止写入 |
| session 完成但没有 PR | 检查任务是否要求创建 PR，再按入口创建 | 不认为完成等于合并 |
| PR 有绿灯但需求不对 | 退回需求层，补测试或改实现 | 不认为 CI 能判断产品意图 |
| 不再需要任务 | 在会话中 Stop，随后检查已推送提交和 PR | 不认为停止会撤销已有写入 |

GitHub 官方说明可以监控、steer、停止或归档会话；提交可追溯到 session 日志。[会话管理](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/manage-and-track-agents)

## 结束时写清状态

在 PR 描述或工作记录中写四行：

```text
需求：增加 category 为空的拒绝测试。
已验证：diff 只有 test_catalog.py；unittest 退出成功；PR 检查通过。
未验证：未在真实网页上检查所有外部资源链接。
决定：保留 PR 等人工评审，不由 Agent 批准或合并。
```

“会话完成”“Agent 自测通过”“PR 检查通过”“人工批准”“已合并”是五个不同状态。把它们分开，后续自动化才有可靠的输入。

下一篇将同样的验收思想放进 Actions 里的 gh-aw：先手动编译和试跑，再让一个真实 PR 事件产生受控评论。[现代 GitHub：22 从手动试跑到事件驱动自动化](<现代 GitHub：22 从手动试跑到事件驱动自动化.md>)

**来源与限制（2026-11-18 核对）**：依据 GitHub [Kick off a task](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task) 与 [Managing agent sessions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/manage-and-track-agents)。本文未运行云端模型，也未对真实 PR 发表评论；示例是可审计的验收模板，不是运行结果声明。
