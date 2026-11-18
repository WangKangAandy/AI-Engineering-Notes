---
title: GitHub 协作与自动化：02 Issue、分支与 Pull Request
summary: 从 GitHub 仓库、Issue 和 Pull Request 的含义开始，通过网页完成一次提出需求、修改文件和合并的练习，并提供本地 Git 对应路径。
tags:
  - github
  - collaboration
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：02 Issue、分支与 Pull Request

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。本篇面向已有 GitHub 账号、还没有做过 PR 的读者；网页主线不需要安装 Git，也不要求会写代码。完成后再读 [[GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务]] 和 [[GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并]]。

> 本篇实验分支：`lab/02-issue-pr`，PR 目标：当前操作仓库的 `master`。公开读者先按第 2 节准备自己的 fork；组织成员仅在获准的仓库实验。

资料核对日期：2026-11-18。界面可能调整，关键是核对仓库归属、来源分支、目标分支与结果。

## 1. 先理解 GitHub 上正在协作什么

Git 负责记录文件版本；GitHub 在 Git 仓库之上提供托管、讨论和协作页面。仓库（repository，常简称 repo）不只是一个下载目录：Code 页面展示文件和提交历史，Issues 记录问题与任务，Pull requests 展示拟合入的修改。第一次练习可以全程在浏览器里完成，GitHub 网页会代你创建提交。[GitHub 入门练习](https://docs.github.com/en/get-started/start-your-journey/hello-world)

打开仓库时先看左上角的 `OWNER/REPOSITORY`：前者是谁的仓库，后者是仓库名。再看 Code 页面的分支选择器。默认分支是这个仓库的主要整合位置，常叫 main 或 master；本系列仓库使用 master，这不是 GitHub 对所有仓库的固定命名。

假设发现“学习记录没有说明要学哪些内容”。**Issue** 用来把这个问题说清楚：为什么要改、希望得到什么、怎样判断完成。它可以先存在，甚至由不会修改文件的人提出。打开一个 Issue 不会自动创建分支或改动文件，也不要求以后一定有 PR；讨论、调查或决定不做，都可以是处理结果。

当你准备补上记录时，先从 master 建立一个分支，在该分支保存改动。**Pull Request（PR）** 则提出“请把这个来源分支的修改合入目标分支”。PR 中有文件差异、讨论、评审和合并状态；文档修改同样可以用 PR。它不是下载请求，也不是 Git 命令 `git pull`。

Issue 让人看懂要解决什么，PR 让人检查具体怎么解决。一个小 Issue 可以由一个 PR 解决；较大的工作可能需要多个 PR。本篇先走最简单的一对一流程，拆解与关联的细节留到 02A、02B。

### 各个动作改变了什么

| 操作 | 改变什么 | 没有自动完成什么 |
|---|---|---|
| 新建 Issue | 新增一条工作项 | 不会自动修改代码 |
| 创建 branch | 给一条开发线命名 | 不会复制出另一个 GitHub 仓库 |
| commit | 保存一次有说明的 Git 快照 | 本地提交不会自动上传 |
| push | 把本地提交发送到远程仓库 | 不等于合并到主分支 |
| 创建 PR | 请求将来源分支合并到目标分支 | 不等于批准或已合并 |
| merge | 把 PR 的改动整合进目标分支 | 是否部署由自动化配置决定 |

Fork 是你账号下的仓库副本，常用于没有原仓库写权限时贡献代码；branch 是一个仓库内部的开发线。初学在自己的练习仓库建分支即可。

GitHub flow 的核心是分支、提交、PR、评审及合并。[官方流程说明](https://docs.github.com/en/get-started/using-github/github-flow)

## 2. 准备练习仓库

打开 [组织仓库](https://github.com/xallor-ai/AI-Engineering-Notes)。没有组织写权限的读者点击 Fork，将仓库复制到自己的账号；随后确认地址栏已经变成 `你的账号/AI-Engineering-Notes`。接下来创建 Issue、分支和 PR 都在这个 fork 内完成，暂时不向组织仓库发实验 PR。

若自己的 fork 看不到 Issues，进入 Settings → General → Features，启用 Issues。看到 Issues 不代表你有其他仓库的管理权限；本例能配置，是因为你拥有自己的 fork。组织成员已有获准的实验仓库时，可以直接使用，不再建一份。

回到当前操作仓库的 Code，确认分支选择器为 `master`。本篇新增 `笔记/GitHub 工作流实操记录.md`，不依赖其他分支的文件。如果同名记录已经存在，更新其中的学习目标即可。fork 是 GitHub 上另一份仓库；本地 clone 才是把仓库取到电脑上，本篇网页路径不需要 clone。

网页与本地路径二选一，完成后继续 02A、02B；已经熟悉协作流程时可直接进入第 03 篇。不要在同一仓库把两条路径重复做一遍。

## 3. 全程网页练习

### 提出一个能完成的小需求

在当前操作仓库选择 Issues → New issue。如果出现模板选择页，选合适模板；允许空白 Issue 时可选 Open a blank issue。本次标题写“添加 GitHub 工作流学习记录”，正文写：

```markdown
目前缺少一份能跟随本系列填写的学习记录。

希望在笔记目录新增或补齐《GitHub 工作流实操记录》，列出 PR、CI、Pages 三个学习目标。

完成条件：master 中能打开该文件，三个目标清楚可读。本次只写学习目标，不声称 CI 或 Pages 已配置成功。
```

点击 Submit new issue，记下页面标题旁的编号与地址。下面的 `#1` 只是占位示例，必须换成自己的编号。Issue 与 PR 使用仓库内同一套编号，因此你的第一个 Issue 不一定是 1，跨仓库的同一编号也不是同一个对象。[创建 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue)

### 在分支上修改文件

回到 Code，选中 master，再用分支选择器输入 `lab/02-issue-pr` 并创建分支。确认当前显示的是新分支，用 Add file → Create new file 新建 `笔记/GitHub 工作流实操记录.md`，填入下方模板；已有文件则打开它并点击编辑按钮。

点击 Commit changes，填写提交说明 `docs: add workflow learning record`，确认提交到当前实验分支。网页保存会直接形成 GitHub 上的提交，不需要另做本地 push。切回 master 时暂时看不到这次改动，这是分支隔离的结果。

### 提出 PR 并检查合并方向

进入 Pull requests → New pull request。fork 的比较页面可能默认朝向原仓库；先把 **base repository** 选为自己的 fork，再确认以下方向：

| 页面字段 | 本次应选 | 含义 |
| --- | --- | --- |
| base | master | 修改要进入哪里 |
| head / compare | lab/02-issue-pr | 修改来自哪里 |

确认两个仓库栏都是当前实验仓库。查看差异：增加的行通常带 `+`，删除的行带 `-`；文件列表应只有你准备修改的记录。点击 Create pull request，标题写“添加 GitHub 工作流学习记录”，正文写改动与检查方式，并单独写一行 `Closes #1`，替换实际编号后提交。

创建 PR 后 Issue 暂时仍是 Open，这是正常的。`Closes` 在 PR 正文中声明解决对象；当前目标是默认分支且仓库启用自动关闭时，合并才会触发关闭。CI、Approve 和手动关闭 PR 都不能代替这次合并，详细机制见 02B。

### 合并后同时检查文件和工作项

在 Files changed 再读一遍完整改动，在 Conversation 查看讨论和合并条件。此时本例没有配置 CI，没有自动测试结果是正常的。自己创建的 PR 可以自查和评论，但不能给自己提交 Approve 评审；如果仓库要求别人批准，必须请符合规则的人评审，不能把自查当作批准。

满足页面显示的合并条件后，使用允许的合并方式并确认。看到 PR 状态为 Merged，再回 Code → master 打开记录文件，核对三个目标。最后回 Issue 检查关闭状态及指向该 PR 的记录；若仍然 Open，按第 6 节排查，不将“按钮点过了”当作验收。

可选删除已合并分支；这不会删除已进入主分支的内容。Issue 关联语法参见 [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)。

新文件的最小模板如下。日期填写实际创建日；按照仓库要求保留摘要、标签和开头介绍。

```markdown
---
title: GitHub 工作流实操记录
summary: 记录本仓库的 PR、CI 与 Pages 学习目标及验证结果。
tags:
  - github
created: 2026-11-16
status: learning
---

# GitHub 工作流实操记录

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

## 学习目标

- 创建并合并一个 PR。
- 观察 CI 从失败到通过。
- 追踪一次 Pages 部署对应的提交。
```

## 4. 本地 Git 对应做法

以下路径供有组织仓库写权限的成员使用。需要 Git；最后一条 `gh` 命令需要已安装并登录 GitHub CLI，也可以改用网页创建 PR。

```powershell
git clone https://github.com/xallor-ai/AI-Engineering-Notes.git
cd AI-Engineering-Notes
git switch master
git pull --ff-only
git switch -c lab/02-issue-pr
```

先在当前操作仓库的 Issues 按第 3 节新建工作项并记下编号。现在在编辑器中创建上述记录文件并保存，再继续；将下面的 `123` 换成刚创建的 Issue 编号：

```powershell
$issueNumber = 123
git add "笔记/GitHub 工作流实操记录.md"
git commit -m "docs: add workflow learning record"
git push -u origin lab/02-issue-pr
gh pr create --repo xallor-ai/AI-Engineering-Notes --base master --head lab/02-issue-pr --title "docs: add workflow learning record" --body "Closes #$issueNumber

添加 PR、CI 和 Pages 学习目标。"
```

创建成功后打开 gh 返回的 PR URL，按第 3 节“合并后同时检查文件和工作项”检查并合并。确认当前仓库 master 已有实操记录、关联 Issue 已关闭，再更新本地 master 并进入下一篇。

如果已有 checkout，直接进入它并确认 origin 指向当前操作仓库，不重复 clone。每章开始前确认工作区干净，再 `git switch master`、`git pull --ff-only`，最后 `git switch -c` 创建该章分支。PR 合并后回到 master 拉取新内容，再开始下一章。

### 没有组织写权限时：fork 实验和正式贡献分开

先在 GitHub 网页 Fork 组织仓库到自己的账号，保留默认分支 master。若 fork 看不到 Issues，在该 fork 的 Settings → General → Features 启用 Issues，再进行本篇工作项和第 07 篇报告练习。下面的 `YOUR_LOGIN` 替换为自己的用户名；在一个新的本地目录执行：

```powershell
git clone https://github.com/YOUR_LOGIN/AI-Engineering-Notes.git
cd AI-Engineering-Notes
git remote add upstream https://github.com/xallor-ai/AI-Engineering-Notes.git
git switch master
git pull --ff-only
git switch -c lab/02-issue-pr
```

origin 现在指向自己的 fork。先在 fork 的 Issues 新建工作项，记录该 fork 的编号。按上方模板编辑，使用上方的 git add、commit、push 命令提交并推送；不要执行其中指向组织仓库的 gh pr create。改用下面命令，123 替换为 fork 内的实际 Issue 编号：

```powershell
$issueNumber = 123
gh pr create --repo YOUR_LOGIN/AI-Engineering-Notes --base master --head lab/02-issue-pr --title "docs: add workflow learning record" --body "Closes #$issueNumber

个人 fork 中的工作流练习。"
```

打开上述命令返回的 fork PR URL，按第 3 节“合并后同时检查文件和工作项”检查并合并；确认记录进入 fork master 且该 fork 的 Issue 关闭，再拉取本地 master。

后续主线实验的 Issue、PR、Actions、Pages、Secrets 和 App 都选择这个 fork；确认 fork 默认分支仍为 master，按需启用 Actions。第 03～07 篇主线合并和运行的是 fork 的 master，不能记成组织仓库上线；03A 自托管选学另建私有 runner-lab，不能把个人电脑注册到公开 fork。

如果某项改动要正式贡献给组织，从组织最新 master 新建独立贡献分支，仅搬入准备提交的改动，避免将全部实验提交带入正式 PR：

```powershell
git fetch upstream master
git switch -c docs/workflow-contribution upstream/master
```

在此分支完成选定文件修改并提交后：

```powershell
git push -u origin docs/workflow-contribution
gh pr create --repo xallor-ai/AI-Engineering-Notes --base master --head YOUR_LOGIN:docs/workflow-contribution --title "docs: improve workflow learning notes" --body "提交选定的文档改进及验证结果。"
```

正式 PR 由组织维护者审核、合并。个人 fork 的实验合并权限不等于组织权限。

## 5. 三种合并方式只先记用途

| 方式 | 历史表现 | 初学时怎么选 |
|---|---|---|
| Merge commit | 保留分支提交并增加合并提交 | 需要保留完整分支历史时使用 |
| Squash and merge | 把本次 PR 改动压成一个提交 | 小任务有很多修补提交时方便阅读 |
| Rebase and merge | 将提交依次放到目标分支之上 | 团队要求线性历史时使用 |

选项受仓库设置控制。先遵守仓库现有约定，不必为学习修改团队策略。

## 6. 卡住时看哪里

| 现象 | 先检查 |
|---|---|
| PR 没有差异 | 是否选反 base / compare；改动是否已进入目标基线分支 |
| 无法直接编辑原仓库 | 是否有写权限；没有时走 fork + PR |
| 出现 merge conflict | 同一位置是否被其他提交改过；解决冲突后重新检查 |
| PR 不能合并 | 页面是否要求检查、评审、解决讨论或更新分支 |
| Issue 没关闭 | PR 正文的关键词、编号和仓库是否正确；是否合入默认分支；仓库是否关闭了自动关闭功能，详见 02B |

## 7. 合并后发生了什么

PR 合并后，切回 master 可以看到新增的实操记录；本例的 Issue 是否自动关闭，取决于描述中的关闭关键词是否正确关联该 Issue、PR 是否合入默认分支，以及仓库是否启用了自动关闭。PR 尚未合并时，继续向同一来源分支推送提交，会更新现有 PR，通常不需要另建一个。

继续入门：[[GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务]] → [[GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并]]。已经熟悉这些协作动作的读者可直接进入 [[GitHub 协作与自动化：03 Actions 与 Workflow]]。
