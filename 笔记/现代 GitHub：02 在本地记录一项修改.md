---
title: 现代 GitHub：02 在本地记录一项修改
summary: 安装 Git 与 gh，配置本地身份，克隆 resource-nav，并通过工作区、暂存区和提交历史理解一次修改如何被记录。
tags:
  - github
  - book
created: 2026-11-18
status: learning
---

# 现代 GitHub：02 在本地记录一项修改

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书主线章节。全书导读：[00 导读](<现代 GitHub：00 导读.md>)。

## 你要解决的问题

网页提交让你完成了第一次贡献，但本地开发需要知道文件当前处于什么状态：哪些是未保存的工作、哪些已经暂存、哪些已经提交、哪些还没有推送。本章只处理这一条链路，不提前讲冲突、恢复或 PR 评审。

前置是第 1 章的 resource-nav 已有 README、resources.csv 和一次合并记录。开始前在 GitHub 页面确认 `main` 中能看到它们。

## 安装工具并区分身份

在 Windows PowerShell 7 中检查：

```powershell
git --version
gh --version
```

没有安装时，从 Git 官方安装页面和 GitHub CLI 官方页面获取当前版本。安装后重新打开终端。Git 提交中的 user.name/user.email 是提交署名，GitHub 登录账号决定远端访问权限，两者不是同一个设置。[Git 基础](https://docs.github.com/en/get-started/git-basics) · [GitHub CLI](https://cli.github.com/manual/)

用 gh 登录 GitHub，选择 `github.com` 和 HTTPS 或浏览器认证；完成后核验当前账号：

```powershell
gh auth login
gh auth status
```

`gh auth` 的认证用于 CLI 调用 GitHub；Git 传输也可以由 Git Credential Manager 或 gh 配置，但不要因为网页登录成功就假设所有终端工具已经登录。[gh auth login](https://cli.github.com/manual/gh_auth_login) · [gh auth setup-git](https://cli.github.com/manual/gh_auth_setup-git)

## 克隆并核对远端

建立一个专用学习目录，避免把仓库克隆到其他项目中：

```powershell
$workRoot = Join-Path $HOME 'github-learning'
New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
Set-Location -LiteralPath $workRoot -ErrorAction Stop
git clone https://github.com/YOUR_LOGIN/resource-nav.git
Set-Location -LiteralPath (Join-Path $workRoot 'resource-nav') -ErrorAction Stop
git remote -v
git branch --show-current
git status --short
```

把 `YOUR_LOGIN` 换成你的 GitHub 用户名。`origin` 应指向自己的 resource-nav，当前分支应是默认分支，工作区应为空。任何一步失败先停下来；不要在错误目录中继续执行后面的 Git 命令。

克隆并进入仓库后，再设置本项目的提交署名：

```powershell
git config --local user.name 'Your Name'
git config --local user.email 'YOUR_EMAIL'
git config --local --get-regexp '^user\.(name|email)$'
```

如果你不确定提交邮箱是否应公开，使用 GitHub 账号设置中提供的 noreply 地址。这里设置的是提交显示信息，不会自动授予仓库写权限。

## 修改、暂存和提交

在 README 的“目前使用 resources.csv 人工维护”后增加一句：

```markdown
每条资源先人工核对来源、用途和分类，再提交修改。
```

先观察状态和未暂存差异：

```powershell
git status --short
git diff -- README.md
```

`git status` 告诉你文件相对 HEAD 的状态；`git diff` 默认查看工作区尚未暂存的修改。确认只改了 README 后暂存它，再看暂存区差异：

```powershell
git add -- README.md
git diff --cached -- README.md
git commit -m 'docs: explain resource review'
git log --oneline -3
```

`git add` 只是把当前内容放进下一次提交，`commit` 才把暂存区保存成新的历史快照。提交成功后，工作区干净，但远程 main 还没有这个提交；下一步明确推送前，先查看本地与远端的关系：

```powershell
git status
git push origin main
```

如果仓库设置禁止直接推送 main，命令会被拒绝；不要绕过规则。本章的主要目标是观察提交状态，若团队要求 PR，应从本地分支推送并按第 6 章创建 PR。

## 本章结束状态

你能区分工作区、暂存区、提交和远端。下一章会在同一个本地仓库中建立分支、同步别人修改并处理冲突；本章不提前演示恢复历史，也不把一次提交扩展成完整协作流程。
