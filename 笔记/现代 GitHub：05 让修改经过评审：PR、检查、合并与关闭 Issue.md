---
title: 现代 GitHub：让修改经过评审：PR、检查、合并与关闭 Issue
summary: 用一个文档子任务完成分支、Pull Request、评审、修订、合并策略和 Issue 关闭，理解 squash 不会删除评审过程。
tags:
  - github
  - pull-request
  - code-review
created: 2026-11-18
status: ready
---

# 现代 GitHub：让修改经过评审：PR、检查、合并与关闭 Issue

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上一章已经有两个文档子 Issue。本章只完成第一个：在 README 中写清资源格式和网页贡献路径。它不需要 Python，也不修改 workflow。

## 从子 Issue 开始

在 GitHub 打开 README 子 Issue，确认父项、完成条件和依赖方向正确。在 Git Bash 中回到干净的 main：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
git switch -c docs/resource-contribution
~~~

编辑 README，增加：

~~~markdown
## 资源格式

每项资源都要有名称、绝对 HTTP(S) 链接和 category。提交前请检查链接是否完整，并在 Pull Request 中说明来源和用途。

## 如何贡献

贡献指南将在下一项子任务中加入。现在先说明：贡献者应从一个 Issue 或已有需求开始，不要直接向 main 推送。
~~~

保存后检查：

~~~bash
git diff -- README.md
git diff --check
~~~

## 创建 Draft Pull Request

提交并推送：

~~~bash
git add README.md
git commit -m "docs: explain resource contribution"
git push -u origin docs/resource-contribution
~~~

在 Pull requests → New pull request 中选择 base main 和 compare docs/resource-contribution，创建 Draft PR。描述写清：

~~~markdown
## What changed
- 说明资源字段和贡献入口。

## Related issue
Closes #README_CHILD_ISSUE_NUMBER

## Verification
- [x] git diff --check
- [x] README 链接和 Markdown 预览可读
~~~

Draft 表示还不要求最终合并，但可以先收集反馈。

## 评审和修订

打开 Files changed：

1. 是否只修改 README；
2. 字段名称是否与 Issue 一致；
3. 链接和示例是否能让新读者照做。

提交 Review 时选择 Comment、Approve 或 Request changes：Comment 只留下意见，Approve 表示当前审阅者认为可以继续，Request changes 表示修复前不应合并。一个人维护自己的练习仓库时可以用 Comment 记录自查，但不要伪装成另一名协作者的批准。填写审阅摘要后点击 Submit review；评论存在不等于 Review 已提交。

如果发现字段名称不一致，在具体行评论，再在原分支修订：

~~~bash
git switch docs/resource-contribution
git pull --ff-only origin docs/resource-contribution
# 修改 README 后

git add README.md
git commit -m "fix: align resource field names"
git push
~~~

原 PR 会自动更新。评论中写“已修改”不等于修复，必须在新的差异中看到变化。

所有反馈处理完后点击 Ready for review，再检查关联 Issue 和分支。

## 合并策略：Merge、Squash 和 Rebase

- Create a merge commit：保留分支关系和合并提交；
- Squash and merge：把 PR 提交压成 main 上的一个新提交；
- Rebase and merge：逐个重放提交，通常保持线性历史。

本例选择 Squash and merge。Squash 压缩的是 main 接收的提交历史，不删除 PR 页面的原始提交、评论和评审记录。合并后观察：

- PR 是 Merged；
- README 修改出现在 main；
- 子 Issue 因 Closes 关键词关闭；
- 父 Issue 仍开放，因为第二个文档子 Issue 尚未完成。

如果 required check 尚未配置，合并按钮不会自动出现检查门禁；第 8 章才会把 CI 设置成必需检查。

## 完成第二个文档子任务

合并 README 后，从最新 main 创建第二个分支：

~~~bash
git switch main
git pull --ff-only origin main
git switch -c docs/contributing-guide
~~~

创建 CONTRIBUTING.md，内容至少包括资源字段、提交前检查、PR 描述和不提交凭据；同时把 README 中“贡献指南将在下一项子任务中加入”替换为指向仓库根目录 CONTRIBUTING.md 的相对链接。通过第二个 PR 合并，并在描述中写：

~~~text
Closes #CONTRIBUTING_CHILD_ISSUE_NUMBER
~~~

父 Issue 的两个子项都完成后，再回到父 Issue 核对整体完成条件。不要因为第一个 PR 合并就提前关闭父项。

## 用 gh 核对交付链

~~~bash
gh pr list --repo YOUR_LOGIN/resource-nav --state merged
gh issue view PARENT_ISSUE_NUMBER --repo YOUR_LOGIN/resource-nav
git switch main
git pull --ff-only origin main
git log --oneline --decorate -5
~~~

网页状态、gh 读回和本地 main 应互相吻合。

## 本章结束状态

main 已包含 README 和 CONTRIBUTING.md 两个文档入口，两个文档子 Issue 都已处理，父 Issue 可以完成验收。你已经实践了 PR、修订、Squash、关闭关键词和合并后同步，但还没有写程序。

下一章把这两个入口整理成维护者可持续使用的贡献制度；再下一章才引入 Python 项目。
