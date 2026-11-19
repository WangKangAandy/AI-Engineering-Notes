---
title: 现代 GitHub：从一个仓库开始：看懂项目、Issue、提交和 PR
summary: 从一个空的学习资源导航仓库开始，用网页完成第一次 Issue、分支、提交、Pull Request 和合并。
tags:
  - github
  - beginner
  - pull-request
created: 2026-11-18
status: ready
---

# 现代 GitHub：从一个仓库开始：看懂项目、Issue、提交和 PR

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章只完成一件事：你第一次打开 GitHub 后，能看懂一个仓库，并把一项小修改通过 Pull Request 合入自己的主分支。先获得一次完整成功，后面再解释 Git 如何在本地保存同样的过程。

## 开始前

你需要：

- 一个可以登录的 GitHub 账号；
- 一个浏览器；
- 一个自己可以管理的公开仓库。

本书把练习仓库称为 RESOURCE_REPO。请在自己的账号下创建名为 resource-nav 的公开仓库。不要把练习 Issue、Pull Request、Pages 或 Secrets 写入本书源仓库。

### 创建仓库

在 GitHub 首页选择 New repository：

1. Owner 选择自己的账号；
2. Repository name 填 resource-nav；
3. 选择 Public；
4. 勾选 Add a README file；
5. 点击 Create repository。

创建后，仓库首页的 Code 标签显示文件；Issues 用来记录要完成的工作；Pull requests 用来审查分支之间的修改；Actions 用来查看自动化运行。它们是同一个项目的不同观察面，不是四个互不相干的产品。

## 先读懂一项修改会经过什么

把 README 的第一行改成更明确的标题，完整过程会产生以下对象：

1. Issue：说明为什么要改，以及什么结果算完成；
2. Branch：让修改先离开稳定的 main；
3. Commit：在分支上记录一个可回看的快照；
4. Pull Request：请求把分支的修改合入 main；
5. Review：其他人或你自己检查差异；
6. Merge：把通过的修改写入 main。

GitHub 页面中的 commit 是 Git 保存的快照；Pull Request 不是一次提交，而是围绕一组分支差异进行讨论、检查和合并的工作面。

## 建立第一个 Issue

进入 Issues，选择 New issue，填写：

标题：

~~~text
完善资源导航项目的说明
~~~

正文：

~~~markdown
## 现状
仓库只有一段默认 README，读者不知道项目要解决什么问题。

## 预期结果
README 能说明资源导航项目的用途，并留下后续添加资源的入口。

## 完成条件
- [ ] README 有项目用途说明
- [ ] 修改通过一个 Pull Request 合入 main
- [ ] Pull Request 与本 Issue 关联
~~~

点击 Submit new issue。记下它的编号，后面用它关联 Pull Request。Issue 编号只属于你的仓库；不要照抄别人的编号。

## 在网页上创建分支并修改文件

回到 Code 标签，打开 README.md：

1. 点击铅笔图标；
2. 将标题改为：

~~~markdown
# 学习资源导航

记录经过验证、适合持续维护的学习资源。
~~~

3. 在提交区域选择 Create a new branch for this commit and start a pull request；
4. 分支名填写 resource-nav-readme；
5. 提交信息填写 Update resource navigation README；
6. 点击 Propose changes。

此时修改还不在 main。GitHub 会创建分支和 Pull Request 编辑页。

## 创建 Pull Request

在 Pull Request 页面检查：

- base repository 是你的 resource-nav；
- base branch 是 main；
- compare branch 是 resource-nav-readme；
- Files changed 中只有 README.md；
- 预览内容符合预期。

在描述中加入：

~~~text
Closes #1
~~~

把 1 换成你刚才创建的 Issue 编号。Closes、Fixes 和 Resolves 都是 GitHub 支持的关闭关键词；只有 Pull Request 合入仓库默认分支时，关联 Issue 才会自动关闭。普通的 #1 只能形成引用，不会表示“合并后关闭”。

选择 Create pull request。现在你已经拥有一个可评审的 PR，即使只有一个人维护仓库，也要把检查过程走完。

## 审查并合入

打开 Files changed：

1. 观察绿色新增和红色删除；
2. 确认改动只解决本次 Issue；
3. 在评论中写下你检查了什么；
4. 选择 Merge pull request；
5. 选择 Confirm merge；
6. 合并后回到 Code，切换到 main，打开 README。

成功的观察不是按钮消失，而是三个对象同时发生变化：

- main 中出现新的 README；
- Pull Request 状态是 Merged；
- Issue 在合入默认分支后变为 Closed。

如果 Issue 没有关闭，先检查 Pull Request 的目标分支是否是 main、关闭关键词是否拼写正确、编号是否属于当前仓库。不要立刻重复创建 Issue。

## 本章结束状态

现在你的 RESOURCE_REPO/main 应该包含一个更新后的 README，第一次 Pull Request 已合并，关联 Issue 已关闭。这个状态是下一章的输入：我们会把同一项目克隆到本地，在 Git Bash 中完成一次修改。

本章没有讲 Git 命令，也没有讲 Python。网页操作足以让你先建立仓库、分支、提交、PR 和合并之间的关系。

