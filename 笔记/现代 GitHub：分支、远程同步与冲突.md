---
title: 现代 GitHub：分支、远程同步与冲突
summary: 理解分支与远端跟踪关系，在隔离仓库中复现同步冲突、先中止再解决，最后回到干净的主线。
tags:
  - GitHub
  - Git
created: 2026-11-18
status: learning
---

# 现代 GitHub：分支、远程同步与冲突

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上一章的提交仍在 ch04/catalog-title，当前 resource-nav 的 main 干净，资源清单保持原来的两行。本章先在真实练习仓库理解远端，再用临时仓库模拟两个人同时工作。Shell 是 PowerShell 7。冲突不会发生在 GitHub 仓库里，结束时也不会留下进行到一半的合并。

## 分支是一条会向前移动的版本线索

分支不是把整个项目复制成另一个文件夹。一个分支记录当前走到哪个提交；在它上面创建新提交时，这个位置向前移动。两个分支可以共享一段历史，再分别发展。切换分支会相应更新工作区，因此切换前必须知道未提交修改属于什么任务。

远端同步还引入了一层容易混淆的名字：

| 名称 | 在哪里、表示什么 |
| --- | --- |
| main | 本地可继续提交的分支 |
| origin | 本地保存的远端地址名称 |
| origin/main | 本机最近一次获取到的远端 main 位置 |
| GitHub 上的 main | 服务器此刻真正保存的位置 |

origin/main 不是实时联网视图。如果有人刚在网页合并 PR，你本地的记录不会自动变化。fetch 获取远端对象并更新远端跟踪引用，但不会直接把当前工作文件改成远端版本。[fetch 官方说明](https://git-scm.com/docs/git-fetch)。

~~~powershell
Set-Location -LiteralPath (Join-Path $HOME 'github-learning/resource-nav') -ErrorAction Stop
git status
git switch main
git remote -v
git fetch origin
git log --oneline main..origin/main
git diff main origin/main -- README.md resources.csv
~~~

两个点的 log 范围表示“远端跟踪分支有、本地 main 没有的提交”。如果没有新提交，输出为空是正常结果。确认来自预期仓库后，更新本地主线：

~~~powershell
git pull --ff-only origin main
git status
~~~

pull 将获取与整合组合起来；这里明确使用 --ff-only，只允许把本地指针沿现有历史向前移动。如果本地和远端已经各有新提交，它会拒绝，避免悄悄替你决定合并策略。拒绝时先看 git log --oneline --graph --all，不要用强制覆盖消除差异。[pull 的整合策略](https://git-scm.com/docs/git-pull)。

## 把一条工作分支送到远端

创建独立分支，并给 README 追加一句本地工作约定。若本章已做过，应检查既有分支而不是重复执行追加操作。

~~~powershell
git switch -c ch05/local-workflow
Add-Content -LiteralPath README.md -Value 'Local edits are reviewed with git diff before committing.' -Encoding utf8
git diff -- README.md
git add -- README.md
git diff --cached
git commit -m "Document local review habit"
git push -u origin ch05/local-workflow
git branch -vv
~~~

push 传送提交并请求更新远端分支；-u 设置当前分支跟踪的上游分支。以后在这条分支执行不带目标的 push/pull，就有了对应关系。branch -vv 应显示 ch05/local-workflow 对应 origin/ch05/local-workflow。GitHub 上会多一个分支，main 不变，因为 push 分支不等于合并 PR。[push 与 upstream 设置](https://git-scm.com/docs/git-push)。

若推送被拒绝，先区分认证失败、分支规则限制、远端已有新提交。前两项检查账号与仓库规则；第三项先 fetch、比较历史，再决定整合。不要因为看到 rejected 就添加 --force。

本次只练习同步，不创建另一轮 PR。切回主线保留这条练习分支：

~~~powershell
git switch main
git status --short
~~~

现在 main 仍干净。下面的冲突实验完全离开这个仓库；实验分支稍后可以在网页确认用途结束后删除，不影响 main。

## 用两个克隆制造一次真实冲突

仅在同一个目录里切分支，也能产生冲突；但两个克隆更容易看清“别人的提交从哪里来”。下面创建临时远端 remote.git，alice 与 bob 作为两个独立工作副本。bare 仓库只保存 Git 数据，没有日常编辑工作区，适合作为这次本机模拟的服务器。它不是 GitHub 服务，不会测试网页权限或 PR。

~~~powershell
$projectRoot = (Get-Location).Path
$labRoot = Join-Path ([IO.Path]::GetTempPath()) ('github-ch05-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $labRoot
git init --bare --initial-branch=main (Join-Path $labRoot 'remote.git')
git clone (Join-Path $labRoot 'remote.git') (Join-Path $labRoot 'alice')
Set-Location -LiteralPath (Join-Path $labRoot 'alice') -ErrorAction Stop
git config --local user.name 'Alice Lab'
git config --local user.email 'alice@example.invalid'
git config --local commit.gpgsign false
Set-Content -LiteralPath README.md -Value 'Audience: beginners' -Encoding utf8
git add README.md
git commit -m "Start shared note"
git push -u origin main
git clone (Join-Path $labRoot 'remote.git') (Join-Path $labRoot 'bob')
Set-Location -LiteralPath (Join-Path $labRoot 'bob') -ErrorAction Stop
git config --local user.name 'Bob Lab'
git config --local user.email 'bob@example.invalid'
git config --local commit.gpgsign false
~~~

第一次 clone 提示空仓库是预期情况，Alice 随后创建了初始提交。实验身份仅写进各自仓库，不改变全局设置。接下来 Bob 在工作分支修改同一行并提交：

~~~powershell
git switch -c ch05/bob-audience
Set-Content -LiteralPath README.md -Value 'Audience: first-time Git users' -Encoding utf8
git add README.md
git commit -m "Clarify Git audience"
~~~

再让 Alice 从共同起点做另一种修改，推到模拟远端：

~~~powershell
Set-Location -LiteralPath (Join-Path $labRoot 'alice') -ErrorAction Stop
Set-Content -LiteralPath README.md -Value 'Audience: first-time GitHub users' -Encoding utf8
git add README.md
git commit -m "Clarify GitHub audience"
git push origin main
Set-Location -LiteralPath (Join-Path $labRoot 'bob') -ErrorAction Stop
git fetch origin
git status
git merge origin/main
~~~

最后一条应失败并报告 README.md 的内容冲突。这次失败正是实验要观察的结果：两条历史对共同祖先的同一行作了不同改写，Git 无法替读者决定最终措辞。Bob 的分支仍在，只是合并尚未完成。

## 先中止一次，再完成一次

先不要编辑冲突内容，观察后中止：

~~~powershell
git status
Get-Content README.md
git merge --abort
git status
Get-Content README.md
~~~

中止后应回到 Bob 的句子，工作区干净；Alice 已推送的提交仍在远端和 origin/main，中止不会撤销它。Git 官方提醒：若合并前就有未提交修改，abort 不一定能重建所有原始内容。这就是我们先提交、确认干净再开始实验的原因。[合并中止的边界](https://git-scm.com/docs/git-merge)。

再次合并，练习解决：

~~~powershell
git merge origin/main
Get-Content README.md
~~~

文件中会出现形如下面的标记。代码围栏中的标记行加了两个空格，仅为避免本书被工具误判为未解决冲突；真实 Git 文件里的标记没有这两个前导空格：

~~~text
  <<<<<<< HEAD
  Audience: first-time Git users
  =======
  Audience: first-time GitHub users
  >>>>>>> origin/main
~~~

HEAD 一侧来自当前 Bob 分支，另一侧来自这次合入的 origin/main。这些标记展示待决定的两种内容，不能原样提交。这里我们理解双方意图后，把整行写成兼顾 Git 与 GitHub 新手的句子：

~~~powershell
Set-Content -LiteralPath README.md -Value 'Audience: first-time Git and GitHub users' -Encoding utf8
git add README.md
git diff --cached
git status
git commit -m "Merge audience descriptions"
git push -u origin ch05/bob-audience
git log --oneline --graph -5
git status --short
~~~

add 表示该文件冲突已经解决，commit 完成合并。状态应干净，图形历史应显示两条线汇入合并提交。真正项目中，删除标记只证明语法层面没有标记；仍需阅读最终文字或运行项目测试，确认两边的需求都得到保留。

## 名字相似，关系不要混淆

上面 -u 设置的 upstream branch 是本地分支的跟踪关系。外部贡献中还经常把原作者仓库的远端命名为 upstream，而把自己的 fork 命名为 origin。这是另一层命名约定：fork 是 GitHub 上的仓库关系，remote 是本地地址配置，二者都不自动授予写权限。第 10 章会在实际外部贡献中使用；当前自己的仓库不必先 fork 一份。

结束实验，回到真实项目：

~~~powershell
Set-Location -LiteralPath $projectRoot -ErrorAction Stop
git branch --show-current
git status
~~~

应看到 main 和干净工作区。临时目录路径保存在 $labRoot，可留着比较 Alice/Bob 历史；其中没有凭据，也不会上传 GitHub。下一章讨论误改与误提交，继续使用隔离环境，不通过抹掉共享历史“解决”错误。

---

[上一章：现代 GitHub：一次修改怎样成为提交](<现代 GitHub：一次修改怎样成为提交.md>) · [下一章：现代 GitHub：改错以后如何恢复](<现代 GitHub：改错以后如何恢复.md>) · [返回导读](<GitHub 协作与自动化：01 学习路线.md>)