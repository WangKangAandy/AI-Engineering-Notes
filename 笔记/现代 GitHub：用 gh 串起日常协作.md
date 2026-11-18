---
title: 现代 GitHub：用 gh 串起日常协作
summary: 用明确的账号、仓库和对象编号操作 Issue 与 PR，通过正文文件完成一轮可核验的命令行协作。
tags:
  - GitHub
  - Git
created: 2026-11-18
status: learning
---

# 现代 GitHub：用 gh 串起日常协作

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

前两章已经解释怎样描述需求、评审和合并 PR。本章把相同对象搬到终端，并不另造一套协作流程。前置是第 3 章已安装、登录的 gh，以及第 8 章工作结束后的本地 resource-nav：main 已同步、工作区干净。Shell 为 PowerShell 7。

本章新建 ch09/reading-guidance 分支，在 README 加一段阅读指引，创建对应 Issue 和 PR，检查后合并，最终回到干净、已同步的 main。resources.csv 不变。不需要 Actions 检查或 Release；这些对象尚未成为当前项目的前置条件。以下 create、comment、merge 命令会真实写入读者自己的 GitHub 仓库，应逐步核验后执行。

## 先固定账号和仓库

git 操作提交、分支和文件历史，gh 操作 GitHub 上的仓库、Issue、PR 等对象。两者配合，却不能互相替代：git commit 不会创建 Issue，gh pr create 也不会替你审查本地所有未提交修改。

先将登录名替换为自己的账号：

~~~powershell
Set-Location -LiteralPath (Join-Path $HOME 'github-learning/resource-nav') -ErrorAction Stop
$repo = 'YOUR_LOGIN/resource-nav'
gh auth status --hostname github.com
git remote -v
git status
gh repo view $repo --json nameWithOwner,url,defaultBranchRef
~~~

确认 active account 是预期账号，nameWithOwner 是自己的仓库，默认分支为 main。gh 许多命令会从当前目录推断仓库；本章为对象操作显式传入 --repo，减少在多个项目间切换时的歧义。--repo 指定请求目标，不会改写本地 origin，也不会增加权限。[gh 的仓库参数与环境](https://cli.github.com/manual/gh)、[仓库查看命令](https://cli.github.com/manual/gh_repo_view)。

只读命令可以先建立对照：

~~~powershell
gh issue list --repo $repo --state all --limit 10
gh pr list --repo $repo --state all --limit 10
gh repo view $repo --web
~~~

在网页找到之前完成的对象。编号只在一个仓库内有意义，另一个仓库的同号 Issue 不是同一项工作；终端与网页 URL 应指向同一个目标。

## 从一份正文创建 Issue

这次需求是让首次读者知道 README 的用途和清单入口。正文有真实换行时，用文件传给 --body-file 比把多行内容塞进一个复杂参数更可靠。先建立仓库外的临时目录，避免把协作草稿误提交：

~~~powershell
$bodyRoot = Join-Path ([IO.Path]::GetTempPath()) ('github-ch09-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $bodyRoot
$issueBody = Join-Path $bodyRoot 'issue.md'
@'
## 现状
README 尚未明确告诉首次读者如何开始浏览资源。

## 预期
增加一个阅读指引段落，说明项目收录学习资源，并指向 resources.csv。

## 完成条件
- 阅读指引能独立理解。
- 指向 resources.csv 的相对链接可以打开。
- 不修改资源清单数据。
'@ | Set-Content -LiteralPath $issueBody -Encoding utf8
Get-Content -LiteralPath $issueBody
~~~

上面的 @' 与 '@ 是 PowerShell 的单引号 here-string 边界，结束标记放在行首，内部文字保留换行。确认内容后创建：

~~~powershell
$issueUrl = gh issue create --repo $repo --title '补充资源导航阅读指引' --body-file $issueBody
if ($LASTEXITCODE -ne 0) { throw 'Issue 创建未确认，先检查远端列表。' }
$issueUrl
$issueNumber = ($issueUrl.Trim() -split '/')[-1]
gh issue view $issueNumber --repo $repo
gh issue view $issueNumber --repo $repo --web
~~~

成功返回的 URL 是后续定位依据，不能预先假定这次一定是 Issue #3。页面应显示刚才的完整正文。[issue create 参数](https://cli.github.com/manual/gh_issue_create)。

如果请求超时，不能直接判断“没有创建”。先用 issue list 和网页核对标题、时间及作者；若对象已经存在，记录其 URL 并继续，避免重复创建。只在确认未写入后重试。

## 用 Git 产生改动，用 gh 说明改动

先同步主线，再建立本章专用分支。若上一章仍有未处理修改，先完成或妥善保存，不要把它们带进本章：

~~~powershell
git switch main
git pull --ff-only origin main
git status
git switch -c ch09/reading-guidance
~~~

用编辑器在 README 末尾增加下面这一段。若同样的阅读指引已存在，应调整本次 Issue 为一个尚未完成的小改进，而不是机械重复段落。

~~~markdown
## 阅读指引

这里收录 GitHub 与 Python 的入门学习资源。请从`resources.csv`选择主题，再打开对应的官方文档。
~~~

保存后核对并推送：

~~~powershell
git diff -- README.md
git add -- README.md
git diff --cached
git commit -m "Add resource reading guidance"
git push -u origin ch09/reading-guidance
~~~

现在远端分支已有提交，创建 PR 不需要再猜测是否应自动推送。写 PR 正文，关联这次实际生成的 Issue：

~~~powershell
$prBody = Join-Path $bodyRoot 'pr.md'
@"
## 修改
增加首次阅读指引，链接到 resources.csv。

## 核验
已检查 README 差异，资源清单数据未改变。
合并前仍需在网页预览中点击资源清单链接。

Closes #$issueNumber
"@ | Set-Content -LiteralPath $prBody -Encoding utf8
Get-Content -LiteralPath $prBody
$prUrl = gh pr create --repo $repo --base main --head ch09/reading-guidance --title '增加资源导航阅读指引' --body-file $prBody
if ($LASTEXITCODE -ne 0) { throw 'PR 创建未确认，先检查远端列表。' }
$prUrl
$prNumber = ($prUrl.Trim() -split '/')[-1]
~~~

这里用双引号 here-string，是为了让 $issueNumber 替换成真实编号。base 是要合入的 main，head 是提交所在分支；显式指定可以避免在错误目录中猜错方向。仓库启用自动关闭时，Closes 关联的 Issue 在 PR 合入默认分支后自动关闭；创建 PR 本身不代表需求完成。[PR 创建参数](https://cli.github.com/manual/gh_pr_create)、[关联与自动关闭条件](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)。

## 读差异、看对象状态，再决定合并

~~~powershell
gh pr view $prNumber --repo $repo
gh pr diff $prNumber --repo $repo
gh pr view $prNumber --repo $repo --json state,isDraft,baseRefName,headRefName,url
gh pr view $prNumber --repo $repo --web
~~~

检查 PR 是 OPEN、不是 Draft、目标为 main、来源为 ch09/reading-guidance。差异应该只有 README 的阅读指引；在网页的文件预览中打开 resources.csv 相对链接，确认落在预期仓库及分支的清单。没有程序测试的文档修改，仍然可以通过内容与链接核验；不要写“CI 已通过”来代替尚不存在的检查。

需要修改时，回到当前分支编辑、commit、push；同一个 PR 会随 head 分支的新提交更新，不必为一次修订重建 PR。需要记录检查结果时也用正文文件：

~~~powershell
$commentBody = Join-Path $bodyRoot 'review-note.md'
@'
已核对：差异仅涉及 README，阅读指引可以理解，资源清单链接可以打开，CSV 内容未改变。
这是作者自查记录，没有声称获得另一位维护者批准。
'@ | Set-Content -LiteralPath $commentBody -Encoding utf8
gh pr comment $prNumber --repo $repo --body-file $commentBody
~~~

只有真的完成了这些核验才发送这段评论。单人练习可自查并在有权限时合并，但作者不能批准自己的 PR。真实团队应由其他评审者按第 8 章的方法检查；CLI 的 review 子命令不绕过这一约束。

满足当前仓库规则后合并：

~~~powershell
gh pr merge $prNumber --repo $repo --squash --delete-branch
gh pr view $prNumber --repo $repo --json state,mergedAt,mergeCommit
gh issue view $issueNumber --repo $repo --json state,url
~~~

本章个人练习仓库未启用合并队列时，预期 PR 为 MERGED；自动关闭开启时，Issue 为 CLOSED。若已有合并队列，命令可能只把 PR 加入队列或开启等待条件满足后的自动合并；必须继续查询，看到 MERGED 后才进入下一步。如果仓库不允许 squash、需要其他评审者或有现行规则，命令会拒绝；按规则处理或选择被允许的策略，不为了练习关闭保护。命令返回失败或网络中断时先查询实际状态，避免把重试当作唯一恢复手段。[PR 合并选项](https://cli.github.com/manual/gh_pr_merge)。

如果 PR 已是 MERGED，但 Issue 仍为 OPEN，先核对关键词、目标分支和 Settings → General → Issues 的自动关闭开关。前面章节允许保留关闭的开关，所以这不必然表示 CLI 合并失败。确认 README 已满足需求后，可以在 Issue 页面说明验收结果并手动关闭，或执行：

~~~powershell
gh issue close $issueNumber --repo $repo --reason completed --comment '已核验合并后的 README 内容和资源链接，需求完成。'
gh issue view $issueNumber --repo $repo --json state,url
~~~

只有实际完成验收才执行这段命令，不用关闭状态掩盖遗漏。[仓库自动关闭设置](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-auto-closing-issues)

## 让本地也回到完成状态

~~~powershell
git switch main
git pull --ff-only origin main
git status
Get-Content README.md
git branch --list ch09/reading-guidance
~~~

README 应包含已合并指引，工作区干净。--delete-branch 会请求清理分支；若本地工作分支仍在，可以先保留。squash 合并不会保持原分支提交与主线一一相同，所以 git branch -d 有时会拒绝；不要因为清理分支而引入强制删除和历史丢失风险。

遇到陌生参数，先查当前安装版本的帮助：

~~~powershell
gh issue create --help
gh pr create --help
gh pr merge --help
~~~

403 通常要检查权限或政策，404 要检查对象、仓库及读取权限，登录失败则回到 auth status。没有输出也可能只是当前筛选没有匹配项。把账号、仓库、对象编号、分支状态分别核对，才能判断错误发生在哪一层。

本章完成后，网页和终端应展示同一组事实：一个需求、一条已合并 PR、主线中可读的说明，以及本地同步后的干净工作区。后面的外部贡献会改变仓库归属和权限边界，这些对象定位方法仍然适用。

---

[上一章：现代 GitHub：用 PR 完成评审与验收](<GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并.md>) · [下一章：现代 GitHub：从个人修改到共同维护](<现代 GitHub：从个人修改到共同维护.md>) · [返回导读](<GitHub 协作与自动化：01 学习路线.md>)
