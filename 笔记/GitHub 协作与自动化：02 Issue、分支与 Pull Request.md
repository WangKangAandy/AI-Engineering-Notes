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

> 本篇实验分支：`lab/02-issue-pr`，PR 目标：`docs/github-agent-channel-architecture`。本篇具体命令固定使用这个测试基线；如果该分支尚未同步到组织仓库，先在已有测试 checkout 中完成，或先同步分支后再操作。先阅读第 01 篇的“实操对象与分支约定”。

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

不要新建练习仓库。打开 [xallor-ai/AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，确认目标仓库已经有 `docs/github-agent-channel-architecture`；从该分支创建 `lab/02-issue-pr`。如果组织仓库尚未同步该分支，先在已有测试 checkout 中完成本篇，或先同步分支后再从网页操作。

如果要完成 Pages 免费练习，可使用只包含示例代码的公开仓库；私有仓库的 Pages 可用性依账户套餐而定。教程后续发布的是练习页面。[Pages 可用范围](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

## 3. 全程网页练习

1. 在 Issues 新建“给现有的 `笔记/GitHub Agent Channel 架构与阶段计划.md` 增加一段学习目标”，正文写：在该笔记末尾增加一段说明，列出 PR、CI、Pages 三个学习目标。
2. 记下 Issue 编号。下面用 `#1` 举例，实际使用自己的编号。
3. 回到 Code，通过分支选择器从 `docs/github-agent-channel-architecture` 创建 `lab/02-issue-pr`。
4. 在该分支编辑 `笔记/GitHub Agent Channel 架构与阶段计划.md`，增加目标说明并提交。网页保存操作会直接形成远程提交，不需要另做本地 push。
5. 进入 Pull requests → New pull request。检查 `base: docs/github-agent-channel-architecture`，`compare: lab/02-issue-pr`。
6. 查看差异，确认只包含预期改动，创建 PR。
7. PR 正文说明改了什么、怎样检查，并写 `Closes #1`。关联关闭通常在 PR 合并到默认分支后发生。
8. 在 Files changed 阅读改动，在 Conversation 查看讨论和状态。此时还没配置 CI，没有自动测试结果是正常的。
9. 使用页面允许的合并方式完成合并，再回到 `docs/github-agent-channel-architecture` 验证文件内容。

可选删除已合并分支；这不会删除已进入主分支的内容。Issue 关联语法参见 [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)。

## 4. 本地 Git 对应做法

以下命令从组织仓库 clone；如果你是在测试 fork 上操作，把远程地址和 push 目标替换为自己的 fork。工作区没有待处理改动。`git add "笔记/GitHub Agent Channel 架构与阶段计划.md"` 前先在编辑器完成修改。

```powershell
git clone https://github.com/xallor-ai/AI-Engineering-Notes.git AI-Engineering-Notes
cd AI-Engineering-Notes
git switch master
git switch -c lab/02-issue-pr
git status
git add "笔记/GitHub Agent Channel 架构与阶段计划.md"
git commit -m "docs: add learning goals"
git push -u origin lab/02-issue-pr
```

随后在网页创建 PR。合并后切回本地 `docs/github-agent-channel-architecture` 并执行 `git pull --ff-only`，让本地跟上远程。

GitHub CLI 的命令以 `gh` 开头，用于操作 PR、Issue、Actions 等 GitHub 对象；`git` 管理版本历史。初期不安装 CLI 也能完成网页练习。

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
| Issue 没关闭 | 编号和关联仓库是否正确；是否合入目标基线分支 |

## 7. 验收

找出 Issue、PR、合并后的提交，说明三者关系。能回答：“我的分支上又提交了一次修改，是否需要重新创建 PR？”答案是：同一个未关闭 PR 通常会随来源分支的新提交更新。

下一篇：[[GitHub 协作与自动化：03 Actions 与 Workflow]]。
