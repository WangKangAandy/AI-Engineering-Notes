---
title: 现代 GitHub：安全地协作：分支、同步、冲突与恢复
summary: 用一个受控协作实验理解分支、fetch、pull、push、冲突和中止，并在不破坏共享历史的前提下恢复本地工作。
tags:
  - github
  - git
  - collaboration
created: 2026-11-18
status: draft
---

# 现代 GitHub：安全地协作：分支、同步、冲突与恢复

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章把四个经常被混在一起的问题放入一个故事：你如何在分支上工作，如何知道远程发生了什么，冲突为什么会出现，以及出错后怎样回到可继续的状态。

## 先建立安全边界

开始前在自己的 resource-nav 目录执行：

~~~bash
git switch main
git pull --ff-only origin main
git status --short --branch
~~~

只有最后一条显示工作区干净且在 main，才继续。pull --ff-only 不会悄悄创建合并提交；如果本地和远程已经分叉，它会停下来让你先判断。

本章的冲突实验使用一个临时目录和两个克隆，不直接污染主线。实验结束后删除临时目录，不把实验分支推到书的源仓库。

## 创建工作分支

在 resource-nav 中创建一个只负责 README 小改动的分支：

~~~bash
git switch -c docs/collaboration-note
printf '\n## 协作\n\n每次修改先在分支中完成，再通过 Pull Request 合入 main。\n' >> README.md
git add README.md
git commit -m "docs: add collaboration note"
git push -u origin docs/collaboration-note
~~~

-u 让本地分支记录远程跟踪分支，之后可以直接执行 git push 和 git pull。此时 main 仍然没有这次修改；远程的工作分支已经存在，可以在 GitHub 上创建 PR。

## fetch、pull 和 push 分别做什么

- git fetch origin 只把远程的新对象和远程跟踪分支带回本地，不改变当前文件；
- git pull --ff-only origin main 通常等于 fetch 加 fast-forward，要求本地没有分叉；
- git push origin branch-name 把本地提交发送到远程分支。

先查看远程跟踪关系：

~~~bash
git fetch origin
git branch -vv
git log --oneline --decorate --graph --all -8
~~~

origin/main 是本地记录的远程 main，不是另一个工作目录。看到远程分支移动，不代表当前分支的文件已经改变。

## 用两个克隆制造一次冲突

为了让冲突可观察，创建两个临时克隆。将 URL 换成自己的仓库：

~~~bash
cd /tmp
rm -rf resource-nav-conflict-a resource-nav-conflict-b
git clone https://github.com/YOUR_LOGIN/resource-nav.git resource-nav-conflict-a
git clone https://github.com/YOUR_LOGIN/resource-nav.git resource-nav-conflict-b
~~~

在第一个克隆中：

~~~bash
cd /tmp/resource-nav-conflict-a
git switch -c lab/conflict-a
printf '\n冲突实验：A 的版本\n' >> README.md
git add README.md
git commit -m "test: create conflict from A"
git push -u origin lab/conflict-a
~~~

在第二个克隆中，先把 A 合入 main，再创建 B 的工作：

~~~bash
cd /tmp/resource-nav-conflict-b
git switch main
git pull --ff-only origin main
printf '\n冲突实验：B 的版本\n' >> README.md
git add README.md
git commit -m "test: create conflict from B"
git push -u origin lab/conflict-b
~~~

两个分支末尾都修改了同一片区域。GitHub 可以在 PR 页面提示冲突；也可以在本地把一个分支合到另一个分支来观察标记。

## 先中止，再完成

在 B 克隆中模拟把 A 合并进 B：

~~~bash
cd /tmp/resource-nav-conflict-b
git fetch origin
git merge origin/lab/conflict-a
~~~

如果 Git 报冲突，README 中会出现：

~~~text
<<<<<<< HEAD
冲突实验：B 的版本
=======
冲突实验：A 的版本
>>>>>>> origin/lab/conflict-a
~~~

先练习安全退出：

~~~bash
git status
git merge --abort
git status --short
~~~

merge --abort 只取消这次尚未完成的合并，恢复到合并前的工作状态。它不是通用的“撤销所有错误”按钮。

再次合并后，打开 README，删除三行标记，保留你真正想要的一段内容。然后：

~~~bash
git add README.md
git commit -m "test: resolve collaboration conflict"
git log --oneline --decorate --graph -5
~~~

你应看到一个合并提交，两个父提交都在历史图中。若项目团队规定线性历史，也可以通过 rebase 解决，但 rebase 会重写本地提交关系；共享分支不要未经协作就强制推送。

## 常见拒绝如何处理

- push 被拒绝：先 fetch，确认当前分支和远程分支，再决定 pull、rebase 或创建 PR；
- pull 报无法 fast-forward：说明本地与远程分叉，不要直接强制推送；
- merge 发生冲突：先看 git status，决定继续解决还是 merge --abort；
- 不确定当前目录：执行 pwd、git rev-parse --show-toplevel 和 git remote -v；
- 不确定是否已经提交：执行 git status 和 git log -1。

这些命令的价值在于把“感觉出错了”变成可观察状态。

## 本章结束状态

删除两个临时克隆：

~~~bash
rm -rf /tmp/resource-nav-conflict-a /tmp/resource-nav-conflict-b
~~~

回到真实项目：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
~~~

最终应在干净的 main 上。你已经见过分支为何隔离工作、远程跟踪分支是什么、冲突标记如何产生，以及如何中止和完成合并。

下一章会把恢复方法系统化：面对未提交修改、错误提交和已经共享的错误时，分别选择保留、撤销还是回退。

