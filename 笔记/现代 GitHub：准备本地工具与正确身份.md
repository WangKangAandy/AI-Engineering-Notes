---
title: 现代 GitHub：准备本地工具与正确身份
summary: 在 PowerShell 中安装 Git 与 gh，区分提交署名和账号权限，并克隆、核验自己的练习仓库。
tags:
  - GitHub
  - Git
created: 2026-11-18
status: learning
---

# 现代 GitHub：准备本地工具与正确身份

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上一章已经在自己的公开仓库 YOUR_LOGIN/resource-nav 中合并了第一次网页修改，main 至少包含 README.md 和 resources.csv。本章把这个项目带到电脑上。所有 YOUR_LOGIN 都要换成自己的 GitHub 登录名，不是昵称，也不是本书作者的账号。本章不创建工作分支；结束时停在本地 main，文件与远端一致，没有未提交修改。

## 先知道命令在哪里执行

终端是输入和显示命令的窗口，Shell 是解释这些命令的程序。Windows Terminal 可以打开不同 Shell；看到一个终端窗口，并不意味着已经在 PowerShell 7。本书本地主线使用 PowerShell 7，代码块不含提示符，复制时只复制命令。一行失败就先处理错误，不要继续执行依赖它的下一行。

在开始菜单打开 PowerShell，运行：

~~~powershell
$PSVersionTable.PSVersion
~~~

若主版本是 5，先在当前窗口安装 PowerShell 7：

~~~powershell
winget install --id Microsoft.PowerShell --source winget
~~~

安装完成后重新打开开始菜单中的 **PowerShell 7**，再检查版本。没有 winget 时，从 [Microsoft 的 Windows 安装说明](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows)选择官方安装包；安装需要的权限遵循本机管理政策。这里不要求另装 Git Bash，也不把 Bash 命令混入后续步骤。

命令通常相对于“当前目录”工作。先建立专门的学习目录：

~~~powershell
$workRoot = Join-Path $HOME 'github-learning'
New-Item -ItemType Directory -Path $workRoot -Force
Set-Location -LiteralPath $workRoot -ErrorAction Stop
Get-Location
Get-ChildItem
~~~

$HOME 是当前用户的主目录，Join-Path 将它与子目录名拼成路径；$workRoot 保存这个结果。Set-Location 改变当前目录，Get-Location 显示它，Get-ChildItem 列出目录内容。这里的 -Force 允许目录已存在，不会清空目录。路径有空格时用引号，例如 Set-Location 'D:\My Learning'。新开窗口后，变量和目录状态不一定还在，需要重新设置。

## Git 保存版本，gh 连接 GitHub

Git 在本机记录文件版本；GitHub 托管仓库和协作对象；gh 是 GitHub 的命令行客户端。安装 Git 不会自动拥有 GitHub 权限，安装 gh 也不等于已经登录。

先检查，已有工具就不必重复安装：

~~~powershell
git --version
gh --version
~~~

如果某个命令找不到，用对应安装命令：

~~~powershell
winget install --id Git.Git -e --source winget
winget install --id GitHub.cli -e --source winget
~~~

安装后关闭并重新打开 PowerShell 7，让窗口获得新的程序搜索路径，再运行版本检查。没有 winget 时分别使用 [Git 官方 Windows 安装入口](https://git-scm.com/install/windows)和 [GitHub CLI 官方安装说明](https://github.com/cli/cli#installation)。不要求版本号与作者完全一致，但后续需要支持 git switch、git restore 和所列 gh 参数。

如果仍提示找不到命令，运行 Get-Command git 或 Get-Command gh 检查解析到的程序路径。不要把“命令不存在”当作仓库权限问题。

## 登录权限与提交署名是两回事

推送时 GitHub 检查“谁在访问、能否写这个仓库”；提交记录中的姓名和邮箱则回答“这次修改署名是谁”。后者是 Git 配置字段，不能授予权限。把 user.name 设置成某个维护者的名字不会使你获得维护者身份。

本书采用 HTTPS 与浏览器登录这一条主线：

~~~powershell
gh auth login --hostname github.com --git-protocol https --web
~~~

按终端给出的提示完成浏览器授权，确认浏览器里是自己的账号。如果问是否为 Git 操作使用 GitHub 凭据，选择同意。然后运行：

~~~powershell
gh auth setup-git
gh auth status --hostname github.com
~~~

setup-git 配置 Git 使用 gh 的凭据助手；登录结果应显示预期账号和 HTTPS 协议。gh 默认尝试将凭据放入系统凭据存储；系统存储不可用时可能退回明文文件，需留意终端提示。不要把访问令牌写进仓库或为了截图执行显示令牌的命令。[认证流程与存储说明](https://cli.github.com/manual/gh_auth_login)、[Git 凭据助手配置](https://cli.github.com/manual/gh_auth_setup-git)。

若登录了多个账号，可用 gh auth switch --hostname github.com --user YOUR_LOGIN 切换已保存账号，再检查状态。认证成功只证明账号可用，仓库访问仍受仓库权限、组织策略等约束。公开仓库通常可以匿名读取，所以“clone 成功”也不能证明自己有写权限。

SSH 是另一种 Git 传输方式，适合已有密钥管理习惯的读者；它需要生成或选择密钥、登记公钥并核验主机。本章无需再配置一套 SSH。若已经使用 SSH，可保留自己的配置，但后续不要将 HTTPS 与 SSH 的认证错误混为一谈；gh 访问 GitHub API 也有独立认证。

## 克隆已有仓库，而不是另建一个空仓库

回到学习目录，把登录名填入变量，再克隆：

~~~powershell
$workRoot = Join-Path $HOME 'github-learning'
Set-Location -LiteralPath $workRoot -ErrorAction Stop
$loginName = 'YOUR_LOGIN'
git clone "https://github.com/$loginName/resource-nav.git"
Set-Location -LiteralPath resource-nav -ErrorAction Stop
git status
git branch --show-current
git remote -v
~~~

克隆会创建 resource-nav 目录、取得历史，并建立名为 origin 的远端配置。远端是本地记录的地址；origin 只是惯用名称，没有“官方仓库”的特殊含义。不要在这个目录里再运行 git init，也不要因为目录已存在而删除它重来。若提示目标目录非空，先检查是否已经克隆过，或为新副本选择另一个不存在的目录名。

预期当前分支为 main，git status 表示工作区干净，remote -v 的 fetch/push 地址都指向自己的 resource-nav。进一步核对：

~~~powershell
git rev-parse --show-toplevel
Get-Content README.md
Get-Content resources.csv
~~~

仓库根目录应是刚才的克隆目录。资源清单应保持上一章的格式：

~~~csv
title,url,category
GitHub Docs,https://docs.github.com/,GitHub
Python Docs,https://docs.python.org/3/,Python
~~~

若看到其他项目，先停止操作并检查地址。Repository not found 可能来自地址拼错、仓库改名或无权访问；先在浏览器以同一账号打开仓库，再判断凭据。

## 为这个仓库设置署名

在 GitHub 账号 Settings → Emails 中选择已验证邮箱，或复制 GitHub 提供的 noreply 地址，以免把私人邮箱写进公开提交。noreply 地址格式可能因账号而异，不要照抄他人的数字和用户名。[GitHub 提交邮箱说明](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)。

只给练习仓库设置身份，替换下面两个字符串后执行：

~~~powershell
git config --local user.name '你的署名'
git config --local user.email '从 GitHub 设置中复制的邮箱'
git config --show-origin --get user.name
git config --show-origin --get user.email
git status --short
~~~

--local 把设置写进当前仓库的 .git/config，不会改变其他仓库的默认身份。最后一条没有输出，表示没有待提交文件。这些设置影响今后产生的提交，不会自动修正历史中的署名。

现在你应能分别回答四个问题：工具装在哪里、当前目录是什么、提交用什么署名、网络操作使用哪个 GitHub 账号。下一章开始真正修改文件；若这些答案还混在一起，先通过上述检查明确它们。

---

[上一章：现代 GitHub：建立练习仓库，完成第一次网页贡献](<GitHub 协作与自动化：02 Issue、分支与 Pull Request.md>) · [下一章：现代 GitHub：一次修改怎样成为提交](<现代 GitHub：一次修改怎样成为提交.md>) · [返回导读](<GitHub 协作与自动化：01 学习路线.md>)