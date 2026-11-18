---
title: 现代 GitHub：04 一次修改怎样成为提交
summary: 通过资源清单的一次修改理解工作区、暂存区、提交和历史，并观察忽略规则的实际边界。
tags:
  - GitHub
  - Git
created: 2026-11-18
status: learning
---

# 现代 GitHub：04 一次修改怎样成为提交

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章从第 3 章的本地 resource-nav 开始，Shell 为 PowerShell 7，当前分支 main 且工作区干净。我们在独立分支 ch04/catalog-title 中把资源标题写得更明确；练习提交保留在该分支，结束后回到干净的 main，不推送、不合并，后续章节仍以原来的两条资源为起点。

## 保存了文件，为什么还没有提交

编辑器保存只改变磁盘文件，也就是工作区。Git 不会把每次按下保存都当作一次正式版本。你先选择下一次提交要包含的内容，放入暂存区，再创建提交。提交记录那一刻暂存区中的快照，并带上说明、署名和前一个提交的关系。

这种分工让你可以同时编辑多个文件，却只提交一个完整意图。例如本次只修正资源标题，不把本机随手写的草稿带进去。开始前核验并建立分支：

~~~powershell
Set-Location -LiteralPath (Join-Path $HOME 'github-learning/resource-nav') -ErrorAction Stop
git status
git switch main
git switch -c ch04/catalog-title
~~~

若工作区有修改，先查明来源，不要强行切换。若分支已存在，说明做过本章；用 git switch ch04/catalog-title 查看已有进度，不要为了重跑而覆盖它。

用记事本打开文件：

~~~powershell
notepad resources.csv
~~~

只把 GitHub Docs 改成 GitHub Documentation，保持 URL、分类、表头和 Python 那一行不变，保存并关闭。然后观察：

~~~powershell
git status --short
git diff -- resources.csv
~~~

简短状态中通常出现第二列为 M 的 resources.csv。前面两列分别表示暂存区相对最近提交、工作区相对暂存区的状态；这里第二列的 M 表示尚未暂存的修改。差异里的减号行是旧内容，加号行是新内容，不是要写进 CSV 的符号。[状态格式](https://git-scm.com/docs/git-status)。

如果整个文件每一行都变化，先检查编辑器编码和换行方式。本次应只改变资源标题，不需要以“Git 能提交”为由接受无关格式变化。

## 选择内容，再看一次真正将提交的差异

~~~powershell
git add -- resources.csv
git status --short
git diff -- resources.csv
git diff --cached -- resources.csv
~~~

此时状态变为第一列的 M，普通 git diff 不再显示这一项，而 --cached 显示即将提交的标题变化。原因是两个命令比较的端点不同：前者比较工作区与暂存区，后者比较暂存区与当前提交。Git 里的 HEAD 通常指当前检出的提交，后面章节会用它表示“现在的版本”。[diff 比较范围](https://git-scm.com/docs/git-diff)。

暂存并不是给文件挂上一个“以后全部提交”的标志。若暂存后继续编辑，同一个文件可能同时拥有已暂存和未暂存变化；提交只包含上一次 add 时选入的内容。遇到 MM 时分别检查两种 diff，再决定是否再次 add。不要无条件用 git add . 把所有内容装进去。

确认暂存差异只有预期修改：

~~~powershell
git commit -m "Clarify GitHub resource title"
git status
git log -3 --oneline
git show --stat HEAD
git show HEAD -- resources.csv
~~~

commit 成功时显示新提交标识。这个标识是版本的名字，不需要抄成固定值；每个读者生成的值会不同。log 显示最近历史，show 展开一个提交的内容。长输出进入分页器时按 q 返回终端。工作区干净说明当前文件与暂存、提交之间没有待处理差异；它不说明提交已经上传到 GitHub。本章没有 push，网页不会出现这个新版本。

若提交提示缺少身份，返回上一章设置仓库本地姓名和邮箱，再执行 commit；已经暂存的内容仍在。若提示没有可提交内容，检查是否忘了保存、文件是否已经提交，而不是反复生成空提交。

## 忽略规则解决什么问题

编辑项目时，可能有不想纳入版本控制的本机草稿。先确认 reading-draft.tmp 不存在，再创建它观察：

~~~powershell
Test-Path -LiteralPath reading-draft.tmp
Set-Content -LiteralPath reading-draft.tmp -Value 'Only a local scratch note.' -Encoding utf8
git status --short
~~~

第一条应返回 False，若为 True，先换一个未占用文件名并同步调整下列命令。新文件出现为两个问号，即未跟踪文件。普通 diff 不展示未跟踪文件内容，因此“diff 没输出”不代表仓库里没有新文件。

项目级 .gitignore 用于共享忽略规则；当前只演示个人草稿，可以把精确文件名追加到本机专属的 .git/info/exclude：

~~~powershell
Add-Content -LiteralPath .git/info/exclude -Value '/reading-draft.tmp'
git status --short
git check-ignore -v reading-draft.tmp
~~~

最后一条显示命中的规则及来源。文件仍存在，只是 Git 不把它作为普通未跟踪候选列出。共同需要的构建目录规则会在后面的程序章节放进 .gitignore；本机私有规则不必提交给所有人。[忽略规则及其适用对象](https://git-scm.com/docs/gitignore)。

忽略只针对未跟踪文件。已经提交的文件不会因为加入 .gitignore 就从历史或暂存区消失；密钥一旦提交，添加忽略规则也无法撤回暴露。这里用的只是普通草稿。实验结束，用编辑器从 .git/info/exclude 删掉刚才添加的那一行，并删除我们刚创建的文件：

~~~powershell
notepad .git/info/exclude
Remove-Item -LiteralPath reading-draft.tmp
git status --short
~~~

不要删除整个 exclude 文件，其中可能已有其他个人规则。

## 回到下一章的起点

~~~powershell
git switch main
git status
Get-Content resources.csv
git log -1 --oneline ch04/catalog-title
~~~

切回 main 后，标题再次是 GitHub Docs。不是修改丢了，而是两个分支指向不同提交，Git 把工作区调整到当前分支的内容。最后一条仍能看到练习提交，证明它留在 ch04/catalog-title。

本章的成果是一条内容明确、可以解释的本地提交，以及一个干净的 main。下一章会让你看到分支如何继续推进，以及本地记录怎样与远端交换。

---

[上一章：现代 GitHub：03 准备本地工具与正确身份](<现代 GitHub：03 准备本地工具与正确身份.md>) · [下一章：现代 GitHub：05 分支、远程同步与冲突](<现代 GitHub：05 分支、远程同步与冲突.md>) · [返回导读](<现代 GitHub：00 导读.md>)