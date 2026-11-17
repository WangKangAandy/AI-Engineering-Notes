---
title: GitHub 协作与自动化：02 Issue、分支与 Pull Request
summary: 通过一个小改动学习 Issue、分支、提交和 Pull Request，完成创建、评审及合并的协作流程。
tags:
  - github
  - collaboration
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：02 Issue、分支与 Pull Request

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。本篇目标：在目标仓库走完 Issue → 分支 → PR → 合并。

> 本篇实验分支：`lab/02-issue-pr`，PR 目标：当前操作仓库的 `master`。默认操作组织仓库；没有权限时使用下文的 fork 路径。

## 1. 六个操作各自改变什么

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

打开 [组织仓库](https://github.com/xallor-ai/AI-Engineering-Notes)，确认分支选择器为 `master`。本篇新增 `笔记/GitHub 工作流实操记录.md`，不依赖仓库已有 README 或其他分支的文件。如果同名记录已经存在，更新其中的学习目标即可。

网页与本地路径二选一，完成后继续第 03 篇；不要在同一仓库把两条路径重复做一遍。

## 3. 全程网页练习

1. 在当前操作仓库的 Issues 新建“添加 GitHub 工作流学习记录”，正文写：新增一篇记录，列出 PR、CI、Pages 三个学习目标。
2. 记下 Issue 编号。下面用 `#1` 举例，实际使用自己的编号。
3. 回到 Code，通过分支选择器从 `master` 创建 `lab/02-issue-pr`。
4. 在该分支用 Add file → Create new file 新建 `笔记/GitHub 工作流实操记录.md`，填入下方模板后提交。网页保存操作会直接形成远程提交，不需要另做本地 push。
5. 进入 Pull requests → New pull request。检查 `base: master`，`compare: lab/02-issue-pr`。
6. 查看差异，确认只包含预期改动，创建 PR。
7. PR 正文说明改了什么、怎样检查，并写 `Closes #1`。关联关闭通常在 PR 合并到默认分支后发生。
8. 在 Files changed 阅读改动，在 Conversation 查看讨论和状态。此时还没配置 CI，没有自动测试结果是正常的。
9. 使用页面允许的合并方式完成合并，再回到 `master` 验证文件内容。

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

创建成功后打开 gh 返回的 PR URL，按第 3 节第 8～9 步检查并合并。确认当前仓库 master 已有实操记录、关联 Issue 已关闭，再更新本地 master 并进入下一篇。

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

打开上述命令返回的 fork PR URL，按第 3 节第 8～9 步检查并合并；确认记录进入 fork master 且该 fork 的 Issue 关闭，再拉取本地 master。

后续实验的 Issue、PR、Actions、Pages、Secrets 和 App 都选择这个 fork；确认 fork 默认分支仍为 master，按需启用 Actions。第 03～07 篇合并和运行的是 fork 的 master，不能记成组织仓库上线。

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
| Issue 没关闭 | 编号和关联仓库是否正确；是否合入默认分支 |

## 7. 合并后发生了什么

PR 合并后，切回 master 可以看到新增的实操记录；Issue 是否自动关闭，取决于关闭关键词是否正确关联该 Issue，以及 PR 是否合入默认分支。PR 尚未合并时，继续向同一来源分支推送提交，会更新现有 PR，通常不需要另建一个。

下一篇：[[GitHub 协作与自动化：03 Actions 与 Workflow]]。
