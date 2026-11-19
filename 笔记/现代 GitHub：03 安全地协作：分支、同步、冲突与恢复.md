---
title: 现代 GitHub：安全地协作：分支、同步、冲突与恢复
summary: 在一个完整协作故事中理解分支、同步、冲突和恢复，并在不破坏共享历史的前提下回到可继续状态。
tags:
  - github
  - git
  - collaboration
created: 2026-11-18
status: ready
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

在第二个克隆中保持 main 的原始内容，创建独立的 B 工作分支：

~~~bash
cd /tmp/resource-nav-conflict-b
git switch main
git pull --ff-only origin main
git switch -c lab/conflict-b
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

## 错误之后：保留工作与恢复历史

## 先做状态快照

任何恢复前执行：

~~~bash
git status --short --branch
git log --oneline --decorate -5
git diff
git diff --cached
~~~

把输出保存到一个临时文本文件，或至少确认自己看懂了：

- 工作区有哪些修改；
- 暂存区有哪些修改；
- HEAD 指向哪个提交；
- 当前分支是否已经推送。

如果你不知道自己在哪个目录，执行：

~~~bash
pwd
git rev-parse --show-toplevel
git remote -v
~~~

## 只想丢掉未提交的文件修改：restore

在临时克隆中修改 README：

~~~bash
cd /tmp
rm -rf resource-nav-recovery
git clone https://github.com/YOUR_LOGIN/resource-nav.git resource-nav-recovery
cd resource-nav-recovery
git switch -c lab/recovery
printf '\n临时错误内容\n' >> README.md
git diff -- README.md
~~~

确认不需要这段内容后，恢复工作区版本：

~~~bash
git restore README.md
git status --short
~~~

这会丢掉 README 中未提交的修改。它不会影响已经提交的历史，也不会恢复被提交后再删除的内容。对不能确定的文件，先复制一份，再使用 restore。

如果修改已经放入暂存区：

~~~bash
git add README.md
git restore --staged README.md
git restore README.md
~~~

第一条 restore 只把文件移出暂存区，第二条才丢掉工作区内容。把两个动作分开，能避免误删仍想保留的修改。

## 已经共享的错误：用 revert

创建一个错误提交：

~~~bash
printf '\n这是一条故意的错误内容\n' >> README.md
git add README.md
git commit -m "docs: add content to revert"
git push -u origin lab/recovery
~~~

如果这条提交已经出现在共享分支或 Pull Request 中，不要移动别人已经看到的历史。用 revert 创建一个新的反向提交：

~~~bash
git revert --no-edit HEAD
git log --oneline -3
~~~

编辑提交信息并完成后，新的提交会抵消旧提交的文件差异，但历史中仍保留“发生过错误”和“如何纠正”的证据。对于已经合入 main 的错误，通常通过一个新的 Revert Pull Request 完成，而不是直接 reset main。

## 只在本地草稿上移动 HEAD：reset

如果错误提交只存在于你自己的本地分支，尚未推送，可以用 reset 改变分支指针。先创建备份分支：

~~~bash
git branch backup/before-reset
~~~

保留修改但撤回最近一次提交：

~~~bash
git reset --soft HEAD~1
git status
~~~

现在修改回到暂存区。下面是另一种选择：请先从备份分支重新开始，不要在 soft reset 后紧接着再执行一次 HEAD~1。

~~~bash
git switch backup/before-reset
git switch -c lab/reset-mixed
git reset --mixed HEAD~1
git status
~~~

这类 reset 会重写本地历史。若提交已经 push，其他人可能已经基于它工作；此时优先用 revert，或先和协作者约定再进行历史重写。

不要把 git reset --hard 当作清理命令。它可能同时删除工作区和暂存区中的内容；除非已经有可恢复副本，否则不要在不理解状态时执行。

## 暂时移开未完成工作：stash

当你需要切换分支，但当前修改还没到可以提交的程度。先在独立的 stash 实验分支准备修改：

~~~bash
git switch main
git switch -c lab/stash
printf '\n暂存中的实验修改\n' >> README.md
git stash push -m "wip: before switching branch"
git status --short
git switch main
~~~

回来后切回这次实验的原分支，再查看并恢复 stash：

~~~bash
git switch lab/stash
git stash list
git stash show --stat stash@{0}
git stash pop stash@{0}
~~~

如果 pop 产生冲突，按普通冲突流程处理；不要反复执行 pop。stash 是本地临时保存，不是团队交付，也不会自动上传到 GitHub。

## 找回“看不见”的本地提交：reflog

如果你在本地 reset 或切换分支后找不到刚才的提交：

~~~bash
git reflog --date=local -10
~~~

找到丢失提交的短哈希后，把下面的 <commit-id> 连同尖括号一起替换为实际短哈希，再创建恢复分支：

~~~bash
git switch -c recovery/from-reflog <commit-id>
git log --oneline --decorate -3
~~~

reflog 是本地仓库的记录，不会替代远程备份；它也可能因清理而过期。真正重要的工作应尽早形成可审查的分支或 PR。

## 选择表

| 你的状态 | 常用选择 | 结果 |
| --- | --- | --- |
| 未提交，想丢掉文件修改 | restore | 工作区回到当前提交 |
| 未提交，想暂时放一边 | stash | 本地保存一份未完成工作 |
| 已推送或已合入的错误 | revert | 用新提交抵消旧提交 |
| 只在本地的错误提交 | reset 或 rebase | 重写本地历史，先备份 |
| 找不到刚才的本地提交 | reflog + 新分支 | 从本地引用恢复 |

命令本身不是决策。先确认共享边界，再选择能保留协作证据的方式。

## 本章结束状态

删除本章使用的临时克隆，回到真实项目的干净 main：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
~~~

现在你已经把分支、远程同步、冲突、未提交修改、共享错误提交和本地恢复放进同一套判断：先看状态，再决定继续、终止、保留、抵消或恢复。下一章开始把真实需求写成 Issue 和子任务。
