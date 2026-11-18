---
title: 现代 GitHub：错误之后：保留工作与恢复历史
summary: 先判断修改是否已提交、是否已共享，再选择 restore、revert、reset、stash 或 reflog，避免用强制推送掩盖错误。
tags:
  - github
  - git
  - recovery
created: 2026-11-18
status: draft
---

# 现代 GitHub：错误之后：保留工作与恢复历史

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

恢复命令没有一个“最强”的答案。先问两个问题：

1. 你要保留的是文件内容、暂存状态，还是提交记录？
2. 出错的提交是否已经推送给别人？

共享历史和本地草稿的恢复方式不同。本章在一个临时克隆中演示危险操作，真实 resource-nav 只在最后确认没有未保存工作时返回 main。

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
git revert HEAD
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

现在修改回到暂存区。若希望修改回到工作区：

~~~bash
git reset HEAD~1
git status
~~~

这类 reset 会重写本地历史。若提交已经 push，其他人可能已经基于它工作；此时优先用 revert，或先和协作者约定再进行历史重写。

不要把 git reset --hard 当作清理命令。它可能同时删除工作区和暂存区中的内容；除非已经有可恢复副本，否则不要在不理解状态时执行。

## 暂时移开未完成工作：stash

当你需要切换分支，但当前修改还没到可以提交的程度：

~~~bash
git stash push -m "wip: before switching branch"
git status --short
git switch main
~~~

回来后查看 stash：

~~~bash
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

找到丢失提交的短哈希后，先创建恢复分支：

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

删除临时克隆并回到真实项目：

~~~bash
cd /tmp
rm -rf resource-nav-recovery
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
~~~

main 应该是干净的。下一章不再演示 Git 命令，而是把一项具体需求写成 Issue、子 Issue 和项目视图，让修改有明确的验收条件。

