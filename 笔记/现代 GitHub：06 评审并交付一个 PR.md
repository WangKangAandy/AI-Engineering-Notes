---
title: 现代 GitHub：06 评审并交付一个 PR
summary: 从一个明确的子任务开始，完成 PR 关联、反馈、修订、合并历史选择和最终验收，并用 gh 操作相同的 GitHub 对象。
tags:
  - github
  - collaboration
created: 2026-11-18
status: draft
---

# 现代 GitHub：06 评审并交付一个 PR

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章选择第 5 章的 A：在 resources.csv 新增 Pro Git。若你没有建立父子 Issue，就创建一条同样范围的独立 Issue；不要复制不存在的编号。开始前确保当前本地仓库在 main，工作区干净。

## 把一个任务交给 PR

从最新 main 创建 `add/pro-git`，新增下面这一行资源，并故意把分类写成 GitHub，作为一次可观察的评评练习：

```csv
Pro Git,https://git-scm.com/book/en/v2,GitHub
```

提交并推送：

```powershell
git add -- resources.csv
git commit -m 'Add Pro Git resource draft'
git push -u origin add/pro-git
```

创建 Draft PR，base 是自己的 resource-nav/main，compare 是 add/pro-git。描述中写 `Closes #实际编号`，只关联这个子任务，不关闭父项。

Draft 说明仍在准备，不能合并；它不等于停用 Actions。进入 Files changed，评审者应把反馈写成“分类与 Issue 完成条件不一致”，而不是只写“请修改”。提交 review 后，作者在同一来源分支把分类改为 Git，再检查、提交并推送：

```powershell
git add -- resources.csv
git commit -m 'Classify Pro Git under Git'
git push
```

原 PR 的 Commits 和 Files changed 会更新。修改完成后，将 Draft 标为 **Ready for review**。没有第二位评审者时，单人练习可以自查并留下 Comment；有协作者时，请符合仓库规则的评审者提交正式 review。

## 关联、评审和自动关闭

普通 `#编号` 是引用；PR 描述中的 `Closes #编号` 声明解决对象；Development 侧栏也可以手动关联。关闭关键词只有在目标是默认分支、PR 真正合并且仓库设置允许时才自动关闭 Issue。自动关闭功能关闭时，PR 可以是 Merged 而 Issue 仍 Open；先验收文件，再手动关闭。[PR 与 Issue 关联](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

评审结果 Comment、Approve、Request changes 的含义不同；作者不能批准自己的 PR。一个 PR 被合并不代表所有需求都完成，仍要检查资源条目、分类、README 和父项的完成条件。

## 合并历史的选择

仓库允许的方式可能不同：

| 方式 | 目标分支留下什么 | 适合什么情况 |
| --- | --- | --- |
| Merge commit | 保留来源提交，并新增连接两条历史的提交 | 需要保留分支关系 |
| Squash and merge | 把 PR 的最终净改动写成目标分支的一个新提交 | 一个 PR 对应一个完整小任务 |
| Rebase and merge | 逐个重放来源提交，形成线性历史 | 每个来源提交都已整理并有独立价值 |

Squash 不是删除代码；PR 的讨论和来源提交仍可追溯，但目标分支会产生新的提交 SHA。后续分支应从合并后的最新 main 创建，回滚也要针对实际进入目标分支的提交。不要把一种策略写成所有团队的默认答案。

## 用 gh 查看同一对象

登录后，终端可以查看网页上相同的 Issue 和 PR：

```powershell
$repo = 'YOUR_LOGIN/resource-nav'
$issueNumber = 123
$prNumber = 456
gh issue view $issueNumber --repo $repo
gh pr view $prNumber --repo $repo --json state,isDraft,baseRefName,headRefName,url
gh pr diff $prNumber --repo $repo
```

这些命令只查询对象。需要创建或合并时，先用 `--repo`、`--base`、`--head` 明确目标，写长正文使用 `--body-file`，命令失败或网络中断后先查询状态再重试。`gh` 不绕过仓库规则，也不会把自查变成另一位评审者的批准。

确认 Ready for review、差异和允许的检查满足要求后，选择仓库允许的合并方式；本例可以选择 Squash and merge。确认 PR 显示 Merged 后，在本地同步最新 main，并核对资源条目、README 和 Issue 状态。Projects 中的任务状态和 GitHub 对象状态应分别核对。

合并后回到 main 拉取最新提交，核对资源清单包含 Pro Git、分类为 Git，README 的维护说明与清单一致。自动关闭开启时子 Issue 通常 Closed；关闭时在 Issue 留下验收说明后手动关闭。父 Issue 等所有子任务完成后再关闭。

本章结束时，一项真实资源修改经过了 Issue、PR、评审、修订、合并历史和文件验收。A 已完成，B 和父项仍 Open；README 分类说明由 B 后续完成。下一章进入贡献指南、模板、权限和维护责任。
