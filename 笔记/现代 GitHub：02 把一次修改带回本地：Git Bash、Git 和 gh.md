---
title: 现代 GitHub：把一次修改带回本地：Git Bash、Git 和 gh
summary: 在 Git Bash 中安装并核对 Git 与 gh，区分提交署名和登录身份，克隆 resource-nav，完成一次本地提交并推送。
tags:
  - github
  - git
  - gh
created: 2026-11-18
status: ready
---

# 现代 GitHub：把一次修改带回本地：Git Bash、Git 和 gh

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上一章的修改已经在 GitHub 上合入 main。本章把同一个项目带到本地，并说明文件、工作区、暂存区、提交、远程仓库之间的关系。

## 开始前

你需要上一章创建的 RESOURCE_REPO，并且它的 main 已经有更新后的 README。

本章的命令在 Git Bash 执行。Git Bash 是 Git for Windows 安装包提供的终端；打开后，命令提示符通常以美元符号开头。不要把 PowerShell 的变量、路径拼接表达式或 WSL 路径复制到这里。

## 安装并核对工具

从 Git for Windows 官方页面安装 Git。安装后在 Git Bash 执行：

~~~bash
git --version
~~~

能看到版本号，说明 Git 已经在 PATH 中。

GitHub CLI 的命令是 gh。安装 GitHub CLI 后执行：

~~~bash
gh --version
~~~

Git 和 gh 分工不同：

- Git 记录文件的版本、分支、提交和远程同步；
- gh 调用 GitHub 的仓库、Issue、Pull Request 和 Actions 接口。

网页、Git 和 gh 可以操作同一批对象，但身份和错误提示不完全相同。

## 区分三种身份

提交署名是写入 commit 的文字：

~~~bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
~~~

登录 GitHub 是让远程服务知道你是谁：

~~~bash
gh auth login
~~~

按照提示选择 GitHub.com、HTTPS 和浏览器登录。登录后核对：

~~~bash
gh auth status
~~~

提交署名不会自动完成 GitHub 登录；GitHub 登录也不会替你决定 commit 中显示的姓名和邮箱。提交后如果发现邮箱不对，先不要重写共享历史，下一章再处理安全的恢复选择。

## 克隆仓库并核对目录

在 Git Bash 中先进入你准备放项目的目录。例如：

~~~bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/YOUR_LOGIN/resource-nav.git
cd resource-nav
~~~

把 YOUR_LOGIN 换成自己的账号。不要在书中复制作者的仓库地址。

确认 Git 当前操作的是正确目录：

~~~bash
pwd
git remote -v
git branch --show-current
git status --short --branch
~~~

你应看到：

- 当前目录以 resource-nav 结尾；
- origin 指向自己的 resource-nav；
- 当前分支是 main；
- 工作区没有未提交修改。

如果 remote 指向了本书源仓库，先停止，不要继续 push。用 git remote set-url origin 修正地址后，再重新执行 git remote -v。

## 认识一次本地修改

用 Git Bash 的编辑器打开 README，或者在文件管理器中打开后保存。将末尾增加：

~~~markdown
## 添加资源

每项资源都应写明名称、用途和可访问的链接。
~~~

保存后执行：

~~~bash
git status --short
git diff -- README.md
~~~

status 告诉你哪些文件改变，diff 告诉你具体改变了什么。保存文件不等于创建提交；修改还在工作区。

把本次修改放入暂存区：

~~~bash
git add README.md
git diff --cached -- README.md
~~~

第二条命令检查“下一次提交真正会包含什么”。确认没有多余文件后创建提交：

~~~bash
git commit -m "docs: explain how to add resources"
git log -1 --oneline
~~~

现在 commit 在本地 main，但还没有上传。推送前再看状态：

~~~bash
git status --short --branch
git push origin main
~~~

如果 main 受到分支保护，push 会被拒绝。这是保护生效的信号，不要用强制推送绕过。此时提交仍在本地 main，远程 origin/main 没有它；先把提交保留到工作分支，再恢复本地 main：

~~~bash
git switch -c docs/local-readme
git push -u origin docs/local-readme
# 现在可以用 GitHub 网页或 gh 创建 Pull Request

git switch main
git fetch origin
git reset --hard origin/main
git status --short --branch
~~~

这样本地 main 回到远程的干净状态，提交仍在 docs/local-readme 中，可以按下一章的 PR 流程继续。reset 只作用于尚未共享的本地 main；不要对已经与他人共享的分支这样做。

## 用 gh 查看同一个项目

Git 负责本地版本，gh 负责 GitHub 对象。例如：

~~~bash
gh repo view YOUR_LOGIN/resource-nav
gh issue list
gh pr list
~~~

如果 gh 显示的仓库不是自己的 resource-nav，先检查 gh auth status 和 git remote -v。命令行不会自动帮你纠正账号和远程地址。

## 本章结束状态

本章结束时：

- 本地 resource-nav 来自自己的 GitHub 仓库；
- Git Bash 能运行 git 和 gh；
- 提交署名与 GitHub 登录分别配置；
- README 的修改已经形成一个本地 commit；
- 该 commit 已推送到自己的 main，或者被分支保护明确拒绝。

下一章会从干净的 main 创建工作分支，演示同步、冲突和恢复。开始前先保证 git status --short 没有输出。

