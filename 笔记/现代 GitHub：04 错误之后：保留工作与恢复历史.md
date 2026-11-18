---
title: 现代 GitHub：04 错误之后：保留工作与恢复历史
summary: 区分工作区、暂存区、未分享提交和共享历史，选择安全的恢复方式。
tags:
  - github
  - git
created: 2026-11-18
status: draft
---

# 现代 GitHub：04 错误之后：保留工作与恢复历史

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章以隔离实验说明 restore、revert、stash 和提交整理；不在共享 main 上改写历史。

## 恢复之前先判断要保留什么

“撤销刚才的操作”不是足够明确的请求。同样是改错一句话，它可能只存在于工作区，也可能已经暂存、已经提交，甚至被别人拉取。工具必须根据这些位置选择。

| 发现错误的位置 | 先看的证据 | 本章采取的动作 |
| --- | --- | --- |
| 文件保存后，还未暂存 | git diff | restore 指定文件 |
| 已暂存，文件内容仍要保留 | git diff --cached | restore --staged |
| 提交已分享 | log、show、远端/协作事实 | revert 创建反向提交 |
| 仅在自己本机的草稿提交 | log，确认没有分享 | 隔离实验中 reset --soft 后重新提交 |

先备份有价值的未提交内容，再使用会覆盖文件的命令。Git 不保证找回从未提交或暂存的所有文字，reflog 也不是编辑器的无限撤销记录。以下例子中的 note.txt 是我们新建的实验文件，覆盖它不会损失真实项目内容。

~~~powershell
Set-Location -LiteralPath (Join-Path $HOME 'github-learning/resource-nav') -ErrorAction Stop
git status
$projectRoot = (Get-Location).Path
$recoveryRoot = Join-Path ([IO.Path]::GetTempPath()) ('github-ch06-' + [guid]::NewGuid())
git init --initial-branch=main $recoveryRoot
Set-Location -LiteralPath $recoveryRoot -ErrorAction Stop
git config --local user.name 'Recovery Lab'
git config --local user.email 'recovery@example.invalid'
git config --local commit.gpgsign false
Set-Content note.txt 'Keep useful work.' -Encoding utf8
git add note.txt
git commit -m "Create recovery baseline"
git switch -c ch06/recovery
~~~

## restore：更改文件位置的内容

先产生一处尚未暂存的误改：

~~~powershell
Set-Content note.txt 'A mistaken replacement.' -Encoding utf8
git diff -- note.txt
git restore -- note.txt
Get-Content note.txt
git status --short
~~~

此时应恢复为 Keep useful work.。普通 restore 从暂存区恢复工作区文件；本例暂存区没有新修改，因此它恰好等于当前提交。这条命令会丢弃该文件尚未暂存的变化，不应在没看 diff 时执行。

再做一处应该保留的编辑，但假设它暂时不该进入下一次提交：

~~~powershell
Add-Content note.txt 'This useful paragraph is not ready.' -Encoding utf8
git add note.txt
git diff --cached
git restore --staged -- note.txt
git diff --cached
git diff -- note.txt
~~~

第二次 cached diff 应为空，普通 diff 仍显示新段落。--staged 默认从 HEAD 恢复暂存区，不改工作区，因此它取消的是“选择进入下一次提交”，而非删除文字。若同时指定 --staged --worktree，则两处都会变化，不能当成普通取消暂存来用。[restore 的来源与目标](https://git-scm.com/docs/git-restore)。

确认这段文字有用，把它作为后续的稳定起点：

~~~powershell
git add note.txt
git commit -m "Keep useful paragraph"
~~~

## revert：让历史保留“出错及纠正”的经过

创建一条明显不应该发布的实验修改：

~~~powershell
Add-Content note.txt 'This instruction is wrong.' -Encoding utf8
git add note.txt
git commit -m "Add mistaken instruction"
$badCommit = git rev-parse HEAD
git show $badCommit
git revert --no-edit $badCommit
git log -3 --oneline
Get-Content note.txt
~~~

新历史同时含有错误提交和一个反向提交，文件里的错误句子消失，有用段落仍在。revert 把指定提交造成的变化反向应用，再记录为新提交；它不把过去的提交偷偷移走，因此适合已经分享的普通提交。[revert 官方语义](https://git-scm.com/docs/git-revert)。

本例没有连接远端，只演示内容与历史的变化。真实项目中应在新的修复分支做 revert，经 PR 合入；不要因为“是修错”就绕过评审。涉及合并提交时还要决定以哪个父提交为基准，本章不把它当作普通提交练习。

如果后来修改与反向变化重叠，revert 也可能冲突。读懂冲突并修改、add 后用 git revert --continue 继续；决定放弃这次反向操作则用 git revert --abort。不要把上一章的 merge --abort 用到所有类型的冲突。反向提交也不擦除敏感信息历史，凭据暴露需要立即撤销凭据并另行处理。

## reset：移动本地草稿的位置

reset 的危险不在于名称叫“重置”，而在于某些形式会移动分支，让原来的提交不再位于当前分支线上。已经分享的分支这样改变，会让别人保留的历史与你冲突。

仅在本章临时仓库执行下面例子。我们先保留一个明确的备份分支，再把刚创建的草稿提交退回暂存状态：

~~~powershell
Add-Content note.txt 'A draft that needs a better explanation.' -Encoding utf8
git add note.txt
git commit -m "Draft"
git branch ch06/before-reset
git reset --soft HEAD~1
git status --short
git diff --cached
git log -2 --oneline
~~~

HEAD~1 表示当前提交的第一个父提交。--soft 移动当前分支的位置，但保留暂存区和工作区，所以草稿文字还在，显示为已暂存修改。现在可以把说明写准确，再重新提交：

~~~powershell
git commit -m "Explain the preserved draft paragraph"
git status --short
git log -3 --oneline
git log -1 --oneline ch06/before-reset
~~~

旧 Draft 提交仍可通过备份分支找到，新提交有不同标识。这不是 revert 的“增加一个抵消提交”，而是重新组织未分享的草稿历史。

对照理解即可，不要在真实项目中逐条试运行：--mixed 会同时把暂存区调整到目标提交，工作区保留；--hard 还会覆盖工作区中的受影响文件，可能移除挡路的未跟踪文件或目录。本章无需 --hard，也无需强制推送。[reset 各模式](https://git-scm.com/docs/git-reset)。

本地整理草稿还可能用交互式 rebase，把数条尚未分享的提交 squash 成一条。它会生成新的提交标识，后续提交也可能随之重写；适合提交前整理自己的草稿，不适合在别人正在依赖的共享分支上擅自使用。GitHub 合并 PR 时的 Squash and merge 则由第 8 章说明，不能把这两个操作的执行位置和影响混为一谈。本章的恢复目标不需要再运行一套交互式历史重写命令。[交互式 rebase 与 squash](https://git-scm.com/docs/git-rebase#_interactive_mode)。

若在本机误移动分支，可先运行 git reflog 查看近期引用位置，用 git show 核对找到的提交，然后为找到的提交建立一个新分支，保留恢复入口。实际语法例如下面这个**占位示例，不要原样执行**：

~~~text
git branch rescue-accidental-reset COMMIT_ID_FROM_REFLOG
~~~

reflog 是本机记录，会过期；它不能保证找回未提交内容，也不能当作远端备份。[reflog 的记录范围](https://git-scm.com/docs/git-reflog)。

## 暂存区与 stash 不是同一个东西

暂存区服务于下一次提交。stash 则用于暂时收起尚未完成的修改，好让工作区恢复干净处理其他事情。下面先保存，确认已保存，再取回；采用 apply 保留备份，确认无误后才 drop：

~~~powershell
Add-Content note.txt 'Work in progress to resume later.' -Encoding utf8
git stash push -m "ch06 unfinished paragraph"
git status --short
git stash list
git stash apply 'stash@{0}'
git diff -- note.txt
git add note.txt
git commit -m "Finish resumed paragraph"
git stash drop 'stash@{0}'
~~~

这里的引号避免 PowerShell 特殊语法干扰 stash 引用。默认 stash 不收纳未跟踪文件；需要包含它们时才加 -u，忽略文件又是另一种范围。应用到已变化的工作区可能冲突，apply 成功与否都先检查，不能习惯性立刻 drop。[stash 的保存与应用范围](https://git-scm.com/docs/git-stash)。

最后核验并返回：

~~~powershell
git status
git stash list
Set-Location -LiteralPath $projectRoot -ErrorAction Stop
git branch --show-current
git status
~~~

实验仓库应干净、stash 列表为空；真实项目仍在 main 且干净。能解释“我要恢复哪个位置、要保留哪些内容、别人是否已经依赖这个历史”，比记住一条万能撤销命令更能避免扩大错误。

---

[上一章：现代 GitHub：05 分支、远程同步与冲突](<现代 GitHub：05 分支、远程同步与冲突.md>) · [下一章：现代 GitHub：用 Issue 把需求变成可执行工作](<现代 GitHub：07 用 Issue 把需求变成可执行工作.md>) · [返回导读](<现代 GitHub：00 导读.md>)
