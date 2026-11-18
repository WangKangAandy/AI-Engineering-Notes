---
title: 现代 GitHub：让修改经过评审：PR、检查、合并与关闭 Issue
summary: 从一个子 Issue 开始完成分支、Pull Request、评审、修订、合并策略和 Issue 关闭，理解 squash 不会删除评审过程。
tags:
  - github
  - pull-request
  - code-review
created: 2026-11-18
status: draft
---

# 现代 GitHub：让修改经过评审：PR、检查、合并与关闭 Issue

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上一章已经有父 Issue 和两个子 Issue。本章只完成第一个子任务：让资源清单中的每项资源都有 category。第二个子任务会在本章末尾说明如何接上，但不会把两个目标塞进一个无法评审的大 PR。

## 从子 Issue 开始

在 GitHub 打开第一个子 Issue，确认：

- 父 Issue 链接正确；
- 完成条件只描述数据和校验，不包含页面布局；
- 没有其他未完成依赖阻塞它。

在 Git Bash 中回到干净的 main：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
git switch -c data/add-resource-categories
~~~

分支名说明范围，不能代替 Issue。分支上只做本子任务对应的修改。

## 修改、检查、提交

打开 resources.csv，为每行增加 category。下面是一行示例：

~~~text
name,url,description,category
Pro Git,https://git-scm.com/book/en/v2,Git 的系统学习资料,git
~~~

保存后先检查差异：

~~~bash
git diff -- resources.csv
git diff --check
~~~

如果项目还没有程序测试，本次先做结构检查；不要把“文件能保存”写成“数据已经被程序验证”。

提交并推送：

~~~bash
git add resources.csv
git commit -m "data: add categories to resources"
git push -u origin data/add-resource-categories
~~~

## 创建 Draft Pull Request

用网页或 gh 创建 PR。网页路径是 Pull requests → New pull request，选择：

- base repository：自己的 resource-nav；
- base branch：main；
- compare branch：data/add-resource-categories。

也可以使用：

~~~bash
gh pr create --repo YOUR_LOGIN/resource-nav --base main --head data/add-resource-categories --draft --title "data: add resource categories" --body-file pr-body.md
~~~

pr-body.md 的内容：

~~~markdown
## What changed
- 为资源清单补充 category。

## Related issue
Closes #CHILD_ISSUE_NUMBER

## Verification
- [x] git diff --check
- [ ] 页面生成测试（由后续子任务完成）
~~~

把 CHILD_ISSUE_NUMBER 换成自己的子 Issue 编号。不要照抄书中的编号。Draft 状态表示还不应要求最终评审；它仍然可以运行检查和收集早期反馈。

## 评审时看什么

打开 Files changed，按三个层次检查：

1. 改动是否只解决当前子 Issue；
2. 数据是否满足每一行都有非空 category；
3. 描述中的完成条件是否有对应证据。

在 Review changes 中选择 Comment、Approve 或 Request changes。一个人维护自己的练习仓库时，可以用 Comment 记录自查，但不要伪装成另一名协作者的批准。真正的团队规则应由仓库权限和分支保护决定。

如果发现某一行分类错误，在具体行上评论：

~~~text
这一行的 category 与描述不一致。请按资源用途修改，并在更新后重新运行检查。
~~~

## 用新提交回应反馈

修改原分支，不关闭并重建 PR：

~~~bash
git switch data/add-resource-categories
git pull --ff-only origin data/add-resource-categories
~~~

修正 CSV 后：

~~~bash
git diff -- resources.csv
git add resources.csv
git commit -m "fix: correct resource categories"
git push
~~~

原 PR 会自动更新。回到 PR 页面再次查看 Files changed 和检查结果。评审意见不能只在评论中回复“已修改”，必须能在新的差异中找到对应变化。

所有反馈处理完后，点击 Ready for review。再次检查标题、描述、关联 Issue 和检查结果。

## 合并策略：Merge、Squash 和 Rebase

GitHub 常见的三个合并方式：

- Create a merge commit：把分支关系和合并提交都保留下来；
- Squash and merge：把 PR 中多个提交压成 main 上的一个新提交；
- Rebase and merge：逐个重放提交，通常保持线性历史。

Squash 只压缩目标分支接收的提交历史，不删除 PR 页面里的原始提交、评论和评审记录。它适合“一个 PR 对应主分支上的一个可回滚单位”的团队。

本例先选择 Squash and merge。填写最终提交信息：

~~~text
data: add categories to resources (#CHILD_ISSUE_NUMBER)
~~~

合并后观察：

- PR 状态是 Merged；
- main 中有一个新的 squash commit；
- 子 Issue 因为 Closes 关键词而关闭；
- 父 Issue 仍然开放，因为第二个子 Issue 尚未完成。

如果仓库设置了 required checks，检查未通过时 Merge 按钮会被阻止。不要用管理员绕过来制造“已通过”的学习结果；先查看检查日志，修正分支，再重新运行。

## 完成第二个子任务

现在打开第二个子 Issue，创建页面改造分支：

~~~bash
git switch main
git pull --ff-only origin main
git switch -c page/group-resources
~~~

这一 PR 只修改页面生成程序和测试。完成后在 PR 描述中写：

~~~text
Closes #SECOND_CHILD_ISSUE_NUMBER
~~~

合并第二个 PR 后，回到父 Issue，核对：

- 两个子 Issue 都已关闭；
- 父 Issue 的子项进度显示完成；
- 页面改造确实满足父 Issue 的全部完成条件。

如果父 Issue 没有自动关闭，不要把 Closes 写到错误的 PR 或错误的目标分支。可以在父 Issue 的 Development 区域手动关联 PR；自动关闭关键词只对指向默认分支的 PR 生效。

## 用 gh 核对同一条交付链

~~~bash
gh pr list --repo YOUR_LOGIN/resource-nav --state merged
gh pr view PR_NUMBER --repo YOUR_LOGIN/resource-nav
gh issue view PARENT_ISSUE_NUMBER --repo YOUR_LOGIN/resource-nav
git switch main
git pull --ff-only origin main
git log --oneline --decorate -5
~~~

网页状态、gh 读回和本地 main 应互相吻合。一个对象显示已合并，不等于本地 main 已经同步。

## 本章结束状态

本章结束时，父 Issue 和两个子任务已经完成，至少有两个经过评审的 PR 合入 main，main 的历史中保留了你选择的合并形状。你也知道：

- PR 是评审和协作面，不只是“上传代码”的按钮；
- Squash 压缩的是主分支历史，不会删除 PR 过程；
- Issue 关闭发生在合入默认分支后；
- 自查可以留下证据，但不能冒充他人批准。

下一章会把这些协作入口写入项目本身，让陌生贡献者知道怎样提出 Issue、创建 PR 和完成检查。

