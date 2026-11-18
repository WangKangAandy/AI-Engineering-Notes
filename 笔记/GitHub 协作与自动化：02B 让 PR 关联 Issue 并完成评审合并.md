---
title: 现代 GitHub：用 PR 完成评审与验收
summary: 让资源清单的修改经过具体反馈、原分支修订和合并验收，理解 PR 关联、自动关闭、批准与实际完成之间的区别。
tags:
  - github
  - pull-request
  - collaboration
created: 2026-11-18
status: learning
---

# 现代 GitHub：用 PR 完成评审与验收

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

这是第 8 章，接续[用 Issue 把需求变成可执行工作](<GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务.md>)。仍在自己的 `YOUR_LOGIN/resource-nav` 操作，默认分支为 `main`。父项 #20、A #21、B #22 都是教学占位号，写入 PR 前必须替换成实际编号。

Issue A 要求在 `resources.csv` 新增 Pro Git，分类为 Git。PR 则把这个要求变成可以检查的文件差异。我们会先做一份含分类错误的草稿，用一条有依据的反馈纠正它，再分别验收文件、PR 和 Issue。这里的错误是受控练习，不能把故意错误的草稿直接合入 main。

## 在任务分支准备一份可评审的修改

在第 3 章克隆的本地 resource-nav 目录中打开 PowerShell 7，先确认工作区干净。若有未完成修改，按第 6 章保存或处理后继续，不要用丢弃命令清场。

```powershell
git status
git switch main
git pull --ff-only
git switch -c add/pro-git
```

用编辑器打开 `resources.csv`，保留现有内容，在末尾新增以下一行，保存为 UTF-8。注意这个初稿的分类故意写成了 GitHub：

```csv
Pro Git,https://git-scm.com/book/en/v2,GitHub
```

表头仍应为 `title,url,category`。如果上一章核对时发现已有同 URL 条目，应修改该条目的分类来练习，不再追加重复行。先检查再提交：

```powershell
git diff -- resources.csv
git add resources.csv
git commit -m "Add Pro Git resource draft"
git push -u origin add/pro-git
```

在 GitHub 创建 PR，核对 base repository 与 head repository 都是自己的 resource-nav，base 为 `main`，compare 为 `add/pro-git`。Files changed 只能出现预期的清单差异。标题写“新增 Pro Git 学习资源”，描述为：

```markdown
## 修改内容
新增 Pro Git 官方在线书籍链接，保留现有资源与三个字段。

## 对应任务
Closes #21
父需求背景：#20。本次不包含 README 分类说明。

## 当前检查
已查看 diff；只有资源清单变化。
分类还需要对照 Issue 核对。本次未运行自动测试。
```

关闭关键词写在描述正文，不放在标题或普通评论里。创建时选择 Create draft pull request；Draft 表示还在准备，不能合并。准备好后才能 Ready for review。标题中的 `[WIP]` 只是文字，并没有 Draft 的平台效果；Draft 也不保证工作流停止执行，触发仍由 workflow 决定。本书使用公开个人仓库；其他环境若无 Draft 入口，可用普通 PR 说明尚未完成并暂不合并。[改变 PR 阶段](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request)

## 关联的含义决定了谁会被关闭

`Closes #21` 声明本次修改解决 A。当目标是仓库默认分支时，GitHub 可以根据 PR 描述建立关联；关联 PR 合入默认分支后，才按自动关闭规则处理 Issue。目标若是非默认分支，描述中的关闭关键词会被忽略，不建立这条关联。创建 PR、追加提交、批准和检查通过本身都不会完成这次自动关闭。[关联 PR 与 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

| 表达方式 | 应如何理解 |
| --- | --- |
| 正文或评论中的 `#20` | 普通引用，适合提供背景；不能仅据此期待自动关闭 |
| PR 描述中的 `Closes #21` | 声明解决 A，受目标默认分支及自动关闭设置等条件约束 |
| Development 中手动链接 Issue | 平台关联，也可能在合并时关闭 Issue，不是无副作用的书签 |
| commit message 中的关闭关键词 | 提交进入默认分支时可触发关闭，但该提交所在 PR 不因此列为关联 PR |

支持的关键词包括 close、fix、resolve 及它们的相应变化形式；同仓库用 `Closes #21`，跨仓库写 `Closes OWNER/REPOSITORY#21`。本例只处理自己的仓库。确实解决多项时，每项写完整关键词；仅完成一部分时，不声明关闭全部需求。

有写权限的人可以从 PR 的 Development 手动选择同仓库 Issue，或从 Issue 侧栏建立关联。关键词建立的关联要编辑 PR 描述删除关键词来解除，不能假定取消一个侧栏勾选就消除了所有来源。父项 #20 目前只作普通引用，避免它被第一个子任务 PR 提前关闭。[手动关联规则](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

还有仓库设置：在 Settings → General → Issues 查看 **Auto-close issues with merged linked pull requests**。默认开启；管理员或维护者可以关闭它。练习前确认实际值，遇到关闭状态时保留该策略，验收后手动关闭即可，不必为了教程更改共享仓库配置。[管理自动关闭](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-auto-closing-issues)

现在打开 A，应能找到关联 PR，但它仍然 Open。若没有关联，依次检查描述中的关键词、实际编号、仓库和目标分支。PR 显示 Closed 而非 Merged，表示提案终止，不能用它证明修改已进入 main。

## 评审必须指出哪里不满足要求

先读 A 的完成条件，再看 Files changed。Pro Git 介绍 Git 本身，Issue 要求的分类是 Git，但新增行写了 GitHub。有效的反馈可以是：

> 这条资源是 Git 教材，当前 GitHub 分类与 A 的完成条件不一致，也会混淆工具与托管平台。请把这一行的 category 改为 Git，保留标题和 URL。

这条反馈连接了差异、原因和预期改动，比“感觉不对”更容易执行。有协作者时，可以先在草稿中讨论；准备收正式评审后 Ready for review，在 Reviewers 请求对方。评审者进入 Files changed，在目标行旁点击评论按钮，写下反馈，选择 Start a review。Pending 评论尚未发送，最后必须 Review changes → Submit review，作者才能收到整批意见。

Comment 表示反馈，Approve 表示认可当前修改，Request changes 表示要求修订；是否阻止合并还取决于评审者权限和仓库规则。作者不能批准自己的 PR。单人练习就在 PR 中留自查评论并修订，不能把它写成独立评审已经通过。第 14 章再配置必需评审和检查规则，不在这一章把自己的练习锁死。[评审 PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request)

## 修订原分支，让原 PR 更新

本地确认仍位于 `add/pro-git`，把新增行替换为最终内容：

```csv
Pro Git,https://git-scm.com/book/en/v2,Git
```

然后检查并推送：

```powershell
git branch --show-current
git diff -- resources.csv
git add resources.csv
git commit -m "Classify Pro Git under Git"
git push
```

回到原 PR，Commits 应新增提交，Files changed 应呈现最终 Git 分类，不需要另开 PR。回复“已将 Pro Git 的分类改为 Git，标题与链接未变”，再由评审者复查。Resolve conversation 只是标记一条讨论已处理，不会自动改文件、批准或合并。需要复审时使用 Reviewers 的重新请求入口；新提交是否让旧批准失效，以仓库规则和当前页面为准。

行内 suggestion 也可以提供替换文本；接受并 Commit suggestion 会在来源分支创建提交。若用了这个网页路径，本地继续改之前先同步来源分支，避免把远端的新提交遗落。本例已经通过本地提交完成修订，无需再接受相同建议。[处理评审反馈](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/incorporating-feedback-in-your-pull-request)

## 合并策略改变历史形状，验收仍要做

确认已 Ready for review，base 是 main，差异仅为预期资源变化，页面要求的检查与评审已满足。合并按钮旁可能提供三种方式；仓库可以限制可用方式，因此先读团队约定，再选择适合本次修改的历史形式。

| 方式 | 合并后的历史 | 适合的情况与代价 |
| --- | --- | --- |
| Create a merge commit | 保留来源分支原提交，另建一个连接两条历史的合并提交 | 需要保留分支来龙去脉；目标历史也保留草稿、修补等中间提交 |
| Squash and merge | 将 PR 的最终净改动写成目标分支上的一个新提交 | 一个 PR 对应一个完整小任务，来源分支有多次修补；目标历史不再逐项保留这些中间提交 |
| Rebase and merge | 逐个重放来源提交，形成没有额外合并提交的线性历史 | 每个提交本身都清楚、有独立价值；GitHub 为重放后的提交生成新的 SHA |

这三种方式都要验收最终文件，区别在于以后怎样阅读、定位和撤销这段历史，不是某个按钮天然更正确。[GitHub 合并方式](https://docs.github.com/en/pull-requests/reference/pull-request-merges)

### 用同一份修改看三种结果

本例已有两个来源提交：`c1` 新增 Pro Git 但分类写成 GitHub，`c2` 将分类纠正为 Git。下面的字母只是教学代号，不是可以复制执行的真实 hash。为看清差异，假设期间 main 没有其他新提交，且没有冲突：

```text
合并前：
       c1---c2       add/pro-git
      /
b                    main

Create a merge commit：
b-----------M        main
 \         /
  c1---c2

Squash and merge：
b---S                main

Rebase and merge：
b---c1'---c2'         main
```

`M` 有两个父提交，保留了原来的 `c1`、`c2` 以及这次合并关系。`S` 则是把本 PR 相对目标分支的最终净改动写入一个新提交：对于本例，它直接新增 `Pro Git,...,Git`。它不是删除新增资源，也不是仅保留最后一次“修改分类”的补丁。草稿中的错误分类被后续修改抵消，最终有效内容仍然进入 main。

Rebase 的 `c1'`、`c2'` 保留了两步变化：先新增，再修正。撇号表示它们是新提交，hash 与原来的不同；GitHub 的 Rebase and merge 会更新提交者信息并生成新的 SHA。这与“文件最终看起来一样”并不矛盾，提交身份还包含父关系等信息。[Rebase and merge 的具体行为](https://docs.github.com/en/pull-requests/reference/pull-request-merges#rebase-and-merge-your-commits)

### 区分 PR 的过程记录与 main 的提交历史

Squash 后，main 的历史里只有 `S` 这一个代表本次任务的提交；这不等于 PR 被抹去。PR 页面仍承载讨论、评审和合并事件，来源提交可以在该 PR 的上下文中追溯。想了解“为什么分类从 GitHub 改为 Git”，回看评审讨论；想知道“main 是哪次修改加入这条资源”，查目标分支上的 `S`。两种记录回答不同问题。[PR 保存的协作信息](https://docs.github.com/en/pull-requests/get-started/about-pull-requests)

因此，记录交付版本时使用 main 中实际产生的提交，不要把合并前的 `c2` 当成 squash 后的版本号。合并确认页面中的提交说明也要读：GitHub 可以根据仓库设置用 PR 标题、正文或来源提交信息生成默认消息，但你应把它整理成能说明最终成果的描述，例如“Add Pro Git learning resource”，而不是保留“draft”的临时措辞。[Squash 提交说明设置](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests)

本次任务小，两个提交共同完成同一项资源收录，来源分支也会在任务结束后退出，所以可以选择 Squash and merge。如果团队需要保留每个原始提交及分支关系，选 merge commit；若每个提交已独立整理且团队要求线性历史，才考虑 rebase。不要把本例的 squash 选择推广成所有仓库的默认答案。这里操作的是 GitHub 合并按钮，本地如何整理尚未分享的提交仍按第 6 章处理，不在合并前临时重写共享分支。

### 新提交身份影响后续分支和撤销

Squash 没有把原 `c1`、`c2` 变成 main 的祖先提交。若继续在旧的 `add/pro-git` 上开发，下次 PR 可能再次列出这些旧提交，并增加重复处理冲突的机会。短期任务最清楚的收尾是：合并验收后同步 main，下一项从最新 main 新建分支。下面的 B 正是这样开始。长期持续使用的分支需要另行约定同步策略，不能反复 squash 后一直追加提交。[Squash 与长期分支](https://docs.github.com/en/pull-requests/reference/pull-request-merges#squashing-and-merging-a-long-running-branch)

撤销时也要找实际进入目标历史的对象：本例 squash 后撤销 `S`，表示反向应用整个资源收录的净改动；rebase 后存在两个新提交，需要决定撤销哪几步；merge commit 则涉及以哪个父分支为基准撤销合并。共享 main 应通过新的反向提交或修复 PR 纠正，不通过重置历史让别人已经拉取的版本消失。后续又改过相同行时，任何方式都可能产生冲突，仍需检查最终内容。[Git revert](https://git-scm.com/docs/git-revert)

GitHub 的 Revert 入口会提出一个撤销修改的新 PR，仍需检查并合并；入口不可用或自动撤销产生冲突时，按第 6 章选择适当的本地恢复方法。撤销文件改动不意味着原任务已经重新验收，必要时还要重新打开 Issue 并说明原因。[撤销 PR](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/reverting-a-pull-request)

### 回到本次任务，核对实际结果

选择仓库允许且符合约定的方式，核对提交说明后确认合并。然后核对三份记录：PR 为 Merged；Code → main 的清单恰有一条 Pro Git 且分类为 Git，原有有效资源仍在；A 已按配置关闭并能追溯到此 PR。自动关闭未启用时，先在 A 留下文件核对结果，再手动关闭。若自动关闭预期没有发生，检查实际编号、默认分支、合并状态与设置，不要仅反复编辑 PR 描述期待重放合并事件。

此时 A 完成，B 和父项仍应未完成。平台能执行关联规则，却不能判断“GitHub 分类其实填错了”；真正的验收来自你对照 Issue 检查 main 的结果。

## 第二个 PR 完成说明，最后再验收父项

从合并后的最新 main 创建新分支，避免把 A 的旧来源分支继续当成新任务起点：

```powershell
git switch main
git pull --ff-only
git switch -c docs/resource-categories
```

保留 README 的原有用途说明，在末尾补充以下内容；若已有相同小节则编辑原段落，不重复追加：

```markdown
## 资源分类与维护

Git 分类收录版本控制工具本身的学习资料，例如 Pro Git。
GitHub 分类收录托管平台的使用资料；Python 分类收录 Python 语言资料。

新增资源前，先在 resources.csv 搜索 URL，避免重复收录。
保持 title,url,category 三列表头，每条资源填写标题、完整链接与分类。
提交前检查差异，确认没有删除其他有效条目，分类与资源内容一致。
```

检查 README 与 main 已有清单相符后，确认当前分支为 `docs/resource-categories`，再提交 B 的实际文件：

```powershell
git branch --show-current
git diff -- README.md
git add README.md
git diff --cached
git commit -m "Document resource categories and maintenance"
git push -u origin docs/resource-categories
```

`git diff --cached` 应只显示本次 README 改动；如果出现其他文件，先处理暂存内容，不带着无关修改提交。创建第二个 PR 时，base repository 和 head repository 都是自己的 resource-nav，base 为 `main`，compare 明确选择 `docs/resource-categories`，不能沿用 A 的 `add/pro-git`。描述使用实际 B 编号 `Closes #22`，只普通引用父项，并说明已核对分类与重复规则、本次没有自动测试。

按前文完成评审、合并后，验证 main 说明与 B 的关闭状态。B 的依赖前提 A 此时已经满足。然后在本地确认没有未完成修改，切回 main 并同步合并结果：

```powershell
git status --short
git switch main
git pull --ff-only
git status --short
```

若切换或同步报错，先停下按第 5、6 章排查；不要继续把旧本地内容当作合并结果。同步成功后，本地 README 应包含刚合并的分类与维护说明。

最后回父项 #20，逐条对照整体完成条件，确认清单和说明一致，留下两个 PR 的引用及核对结果，再手动关闭父项。对于一个需要多个 PR 的 Issue，也应只让真正完成全部范围的最终 PR 承担关闭动作，其余 PR 用普通引用说明进展。

本章结束时，main 增加了 Pro Git 并补齐维护说明，两项子任务和父项均有完成依据。若你只有自己参与，成果是完成一次自查和修订，不是获得了另一位评审者的批准。下一章把这些已经理解的对象映射到终端：[用 gh 串起日常协作](<现代 GitHub：用 gh 串起日常协作.md>)。
