---
title: GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并
summary: 通过一项文档修改学习 PR 的来源与目标、Issue 自动关闭条件、Draft 与评审反馈，并验证合并后的文件与任务状态。
tags:
  - github
  - pull-request
  - collaboration
created: 2026-11-18
status: learning
---

# GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。前置：已完成第 02 篇，在 [[GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务]] 中创建了“补充 PR 验收说明”子任务 A。下面仍以父项 #20、A #21、B #22 举例，必须替换实际编号。若跳过了 02A，先按其中表格的 A 行创建一条独立 Issue，也可完成本篇的单 PR 练习。

在自己的 fork 或获准的实验仓库操作，默认分支仍为 master。任务是修改已经存在的《GitHub 工作流实操记录》，不修改 Actions 配置。资料核对日期：2026-11-18。

Issue 说明要什么，PR 展示准备如何改变仓库。现在 A 已有完成条件，但尚无修改；接下来要把修改放进一个可讨论的 PR，让反馈进入同一条记录，最终核对文件和 Issue 状态。

## 1. 从明确的修改范围开始

在 Code 页面选择最新 master，创建 `lab/02b-pr-review`。打开 `笔记/GitHub 工作流实操记录.md`，点击编辑，保留元数据、仓库介绍和原有目标，在末尾追加：

```markdown
## PR 验收

PR 合并后，回到 master 打开文件，确认内容符合关联 Issue 的完成条件。
```

这只是初稿，还没把 A 的所有条件写全，稍后会演示如何把评审反馈落实进去。将修改提交到 `lab/02b-pr-review`，不要直接提交到 master。

在 Pull requests → New pull request 中核对仓库和分支：base repository 是当前实验仓库，base 为 master；head repository 同样是当前仓库，compare 为 lab/02b-pr-review。fork 页面可能预选组织仓库，创建前必须纠正。Files changed 应只出现这份记录的新段落。

PR 标题写“补充学习记录中的 PR 验收说明”，正文填：

```markdown
## 修改内容
在既有学习记录中新增 PR 验收小节，保留原有目标。

## 解决的任务
Closes #21

## 当前验证
已检查差异仅涉及该记录。正文仍需对照 Issue 补齐验收细节。
本次未运行自动测试，也没有配置 CI。
```

关闭关键词放在 PR 描述正文，而不是只写进标题或评论；下面会解释原因。示例没有写 `Closes #20`，因为这个 PR 只完成 A，不能替仍未完成的 B 宣告整个父任务结束。

### 初稿先用 Draft 表达状态

如果创建按钮旁提供 Create draft pull request，就选择它。Draft 表示仍在准备，不能合并；可以先收集讨论，准备好后再标为 Ready for review。Draft 的可用性与仓库和账号条件有关；没有入口时可创建普通 PR，在正文说明仍未完成并暂不合并。标题写 `[WIP]` 只是文字，不等于平台的 Draft 状态。

Draft 不保证 Actions 停止运行，是否触发由 workflow 事件和条件决定。本篇不需要借助 CI 来建立关联。有关状态切换见 [改变 PR 阶段](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request)。

## 2. 让 GitHub 知道这个 PR 解决谁

`Closes #21` 是 GitHub 内置的关联与自动关闭语法，不需要 Actions、Webhook 或机器人。GitHub 解析 PR 描述，将修改与工作项连接；符合条件的 PR 合入默认分支后，关联 Issue 才自动关闭。

本篇实际只用 Closes，一旦理解它，其他写法也容易读懂：

| 关键词组 | 示例 |
| --- | --- |
| close / closes / closed | `Closes #21` |
| fix / fixes / fixed | `Fixes #21` |
| resolve / resolves / resolved | `Resolves #21` |

官方也支持大写和关键词后的冒号，例如 `CLOSES: #21`。同仓库用 `#编号`；跨仓库用 `OWNER/REPOSITORY#编号`。一次确实完成多个 Issue 时，为每个编号都写完整关键词，例如：

```text
Closes #21
Closes #22
```

不要原样用于当前只完成 A 的 PR。跨仓库操作还涉及目标访问与权限；本例不去关闭组织仓库或其他人的工作项。[PR 与 Issue 关联规则](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

### 引用、关联和关闭是不同结果

| 写法或操作 | 能表达什么 | 能否据此期待自动关闭 |
| --- | --- | --- |
| 正文或评论中的普通 `#21` | 引用相关工作，便于跳转和追溯 | 不能仅凭引用期待关闭 |
| PR 描述中的 `Closes #21` | 声明本 PR 解决该 Issue | 需满足默认分支等条件 |
| Development 侧栏手动链接 Issue | 建立平台关联 | 符合条件的关联 PR 合并后也可自动关闭，不是只有关键词这一条路径 |
| commit message 中的关闭关键词 | 让该提交在进入默认分支时触发关闭 | 有独立的提交路径，但该 PR 不会因此作为关联 PR 列出 |

因此，“没有关闭关键词就绝不自动关闭”并不准确；手动建立的关联同样需要留意。不要把只供背景参考的父 Issue 随手加入 Development，当作无副作用的书签。

若采用手动方式：有仓库写权限的人可在 PR 右侧 Development 选择同仓库 Issue；也可从 Issue 的 Development 选择相应仓库及 PR/分支。关键词建立的关联要通过编辑 PR 描述、删除关键词来解除；不是在侧栏取消选择就一定能清除。[手动关联与解除方式](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

### 什么时候关闭，什么时候不会

当前 master 必须真的是该仓库的默认分支。PR 如果以 develop 等非默认分支为目标，描述中的关闭关键词会被忽略，不建立这条自动关闭关联；不要假设“先合进 develop，以后总会按原 PR 描述关闭”。要以最终进入默认分支的 PR 或提交重新核对。[默认分支限制](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

创建 PR、更新提交、CI 通过、有人 Approve，都不会单独触发这次 Issue 自动关闭。关闭但不合并 PR 也不等于解决 Issue。PR 显示 Merged，才表示合并已发生；Closed 而未合并表示这份提案终止，需另行说明后续处理。

还有一项仓库设置：管理员或维护者可进入 Settings → General → Issues，查看 **Auto-close issues with merged linked pull requests**。默认开启，关闭后关联 PR 合并不会按该设置自动关闭 Issue。练习时先确认状态；共享仓库不应为了复现教程而随意改策略，关闭时可以在验收后手动关闭 Issue。[自动关闭设置](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-auto-closing-issues)

现在打开 A，看是否能找到关联 PR；再回 PR 看 Development 与当前目标分支。此时 A 仍为 Open 是预期行为。若没有关联，先检查关键词是否在描述正文、编号是否属于当前仓库、base 是否为默认分支。

## 3. 把“看过”变成具体的评审反馈

先打开 A 的完成条件，再读 PR 的 Files changed。当前初稿只写了查看 master 文件，却没明确检查 Merged、Issue 关闭记录，也没提醒自动关闭不等于内容正确。这就是一条有依据的评审意见：指出缺少什么、会影响哪个判断，以及需要怎样补齐。

有人一起练习时，作者准备收正式评审后可将 Draft 标为 Ready for review，在 Reviewers 中请求有权限的协作者。评审者进入 Files changed，将鼠标移到目标行旁，点击评论按钮，写下例如：“请补上 PR 的 Merged 状态和 Issue 关闭记录检查，并说明自动关闭不能代替内容验收。”选择 Start a review 后，评论仍是 Pending，只有自己能看见；最后要提交 review，作者才会收到整批反馈。

完成检查后点击 Review changes，写总体意见，选择结果并 Submit review：

| 结果 | 表示什么 |
| --- | --- |
| Comment | 给出反馈，没有批准或正式要求修改的决定 |
| Approve | 评审者认为当前修改可以合并；不等于已经合并 |
| Request changes | 要求作者处理反馈；是否阻止合并还取决于规则及评审者权限 |

不能把任何一次 Request changes 都当成强制门禁；必需评审和 CI 检查在第 04 篇配置。作者不能 Approve 自己的 PR。单人练习可以自查并发表评论，按同样步骤修订；没有第二位合格评审者时，不应伪装已完成独立批准。若仓库要求他人批准，就等待符合条件的人评审。[评审与合并约束](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request)

## 4. 在同一个 PR 中修订，再请对方复查

回 Code，切到 **lab/02b-pr-review**，编辑同一文件，将初稿替换为：

```markdown
## PR 验收

先确认 PR 状态为 Merged，再到 master 打开文件，对照关联 Issue 的完成条件检查内容。
回到 Issue 查看关闭状态及关联 PR；自动关闭只表示平台执行了关联规则，不代表内容已经正确。
如果仓库关闭了自动关闭功能，在人工确认完成后再手动关闭 Issue，并留下验收说明。
```

提交到原来源分支。打开原 PR，确认 Commits 增加了提交、Files changed 更新为修订内容；不需要为每条反馈另开一个 PR。如果走本地 Git，同样是切到这个来源分支、修改、commit 后 push，不能把修订误提交到 master。

在评论中回复具体改了哪里，由相应人员复查后 Resolve conversation。解决讨论只是把该线程标为处理完，不会替你修改文件、提交批准或合并 PR。需要重新评审时，在 Reviewers 旁使用重新请求评审入口；有些仓库的新提交会使旧批准失效，要看当前要求。

协作者也可以用行内 suggestion 提出可直接应用的文字改动。作者确认后点击 Commit suggestion，会在 PR 来源分支创建提交，仍需检查最终差异。超出当前范围的建议，例如“再写一个完整部署系统”，可以另开 Issue 讨论，不必把本次 PR 无限扩大。[处理反馈与 suggestions](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/incorporating-feedback-in-your-pull-request)

## 5. 合并后验证三份记录

如果还处于 Draft，先 Ready for review。核对目标仓库/master、最终差异、必要评审和页面显示的检查条件，再使用允许的合并方式并确认。仓库未满足条件时，读清页面指出的原因；不要为练习绕过规则。

合并后逐项对照：

1. PR 显示 **Merged**，来源和目标是本次实验分支与 master。
2. Code → master 中的记录包含修订后的 PR 验收小节，原目标没有丢失。
3. A 在自动关闭开启时显示 Closed，并有与这次 PR 相关的记录；关闭设置未启用时，先验证内容，再在 A 留下验收说明并手动关闭。

若 A 没关闭，按“描述正文的关键词 → 实际编号和仓库 → 目标是否默认分支 → 是否真正合并 → 自动关闭设置”排查。若错误关闭了别的 Issue，及时说明原因，在有权限时重新打开错误对象，验收正确对象后更新其状态；不要认为合并后修改一行 PR 描述就等于重新执行了一次合并。

删除已合并分支可清理工作区，但不会删除 PR 讨论与主分支文件。关闭 Issue 也不会删除正文。正是这些保留的记录，让后来的读者能从问题追到修改、评审与合并。

## 6. 多个子任务不要提前一起关掉

本节适用于已在 02A 建立父项及 A、B 两个子任务的读者。若开头选择了只创建独立 A 的路径，完成上一节的文件与 Issue 验收后，即可进入第 03 篇，不需要补建父项或 B。

回到 02A 的父 Issue，应能看到 A 已完成，而 B 还未完成。本次 PR 没有解决 B，也没有实现整个父项，不能因为一条 PR 通过就将它们一并关闭。

继续完成 B 时，从**合并后的最新 master** 新建 `lab/02b-ci-prep`，在原记录增加以下小节，提交并为同仓库 master 创建另一个 PR：

```markdown
## 开始 CI 前

确认地址栏是当前实验仓库，master 已有这份学习记录。
找到 Actions 标签页；若 fork 显示工作流未启用，按页面提示启用后再进行第 03 篇练习。
能够打开 Actions 页面只说明找到了入口，还没有证明任何测试通过。
```

第二个 PR 描述改写本次实际变更和检查结果，使用 `Closes #22`，不复制第一个 PR 的 `Closes #21`。按同样方式评审、合并并核对 master 与 B 的状态。如果 B 曾标为 blocked by A，确认前提已经满足；如果依赖本身已不再适用，按 02A 的方式调整关系。

最后回父项 #20，对照两个小节和整体条件，确认没有遗漏后留下汇总，手动关闭父项。`Closes #父项` 适合确实完成父项的修改，不适合每个只完成一部分的子任务 PR。对于需要多个 PR 的一个 Issue，也应只让完成全部范围的最终 PR 承担关闭动作，前面的 PR 用普通引用说明关系。

此时文件变更、PR 合并记录和 Issue 完成状态已经对应起来。下一篇 [[GitHub 协作与自动化：03 Actions 与 Workflow]] 再引入自动执行；本篇的关联与关闭机制已经可以独立工作。
