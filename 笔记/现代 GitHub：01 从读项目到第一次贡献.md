---
title: 现代 GitHub：01 从读项目到第一次贡献
summary: 从阅读 GitHub 仓库开始，建立自己的学习资源导航项目，并用网页完成第一次 Issue、分支、提交和 PR。
tags:
  - github
  - book
created: 2026-11-18
status: learning
---

# 现代 GitHub：01 从读项目到第一次贡献

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书主线章节。全书导读：[00 导读](<现代 GitHub：00 导读.md>)。

## 你要解决的问题

第一次打开 GitHub，最容易发生的事情是直接点 Code 或下载 ZIP，却不知道项目说明、源码、讨论、版本和修改提案分别在哪里。本章先学会判断一个项目，再用一个很小的需求完成第一次贡献。整个过程只使用浏览器，不要求安装 Git 或会写 Python。

本书的练习项目是 `resource-nav`：用一份简单的资源清单记录标题、链接和分类，之后再逐步加上校验、页面和自动化。本章只创建项目说明和清单，不提前引入程序。

## 认识仓库中的几类事实

仓库保存文件和版本历史；README 说明项目用途；Issue 记录问题、需求和决定；Pull Request（PR）提出把一个分支的修改合入另一个分支；Release 围绕某个版本组织说明和附件。它们不是同一条记录，看到一个绿色状态也不能替代其他事实。

Git 负责记录文件版本，GitHub 在 Git 之上提供托管、讨论、评审、自动化和发布。你可以先在网页上完成一次 GitHub Flow，再到下一章学习本地 Git。[GitHub 的工作方式](https://docs.github.com/en/get-started/start-your-journey/what-is-github)

打开任意公开仓库，先确认地址栏中的 owner/repository，再看 Code 页面的分支选择器。默认分支是项目主要整合位置，名字可能是 `main`、`master` 或其他值；不要把本书的 `main` 约定当成 GitHub 的固定规则。

## 读一个项目再决定怎么参与

先读 README，回答项目解决什么问题、支持什么环境、从哪里开始。再看文件列表和最近提交，确认当前默认分支是否仍在维护。想知道某个问题是否有人处理，去 Issues；想看具体修改如何进入主线，去 Pull requests；想找已经发布的可用版本，去 Releases。源码归档不一定是安装包，许可证也不能被“公开可见”替代。[GitHub 入门](https://docs.github.com/en/get-started/start-your-journey/hello-world)

在仓库内搜索时先限定目标仓库，再打开实际文件或 Issue 核对上下文。搜索结果和 README 都可能随版本变化；需要引用时记下提交或页面地址，而不是只记一个模糊标题。[GitHub 搜索](https://docs.github.com/en/search-github/getting-started-with-searching-on-github/about-searching-on-github)

## 创建自己的练习仓库

在自己的 GitHub 账号创建公开仓库 `resource-nav`，初始化 README。它是你自己的实验对象；不要把练习 Issue、PR、Actions 或 Secrets 发到本书源仓库。创建后检查地址栏确实是自己的账号，默认分支约定为 `main`。

再创建 Issue，标题写“建立资源导航清单”，正文写清现状、预期和完成条件：

```markdown
目前仓库只有项目说明，还没有资源清单。

希望新增 resources.csv，收录 GitHub Docs 和 Python Docs 两条公开学习资源。

完成条件：main 中有 README.md 和 resources.csv；CSV 表头为 title,url,category，并包含两条资源。本次不创建程序或网站。
```

提交 Issue 后记下实际编号。`#1` 只是示例，不能假设你的编号一定是 1。

## 在网页上走完第一次 PR

从 `main` 创建 `lab/01-first-contribution`。在这个分支把初始化 README 改成下面内容，再创建 `resources.csv`：

```markdown
# 学习资源导航

整理 GitHub、Git 与 Python 的学习资料，记录每项资源的标题、链接和分类。

目前使用 resources.csv 人工维护，后续会增加校验、静态页面和自动化检查。
```

然后创建 `resources.csv`：

```csv
title,url,category
GitHub Docs,https://docs.github.com/,GitHub
Python Docs,https://docs.python.org/3/,Python
```

分别提交 README 和 CSV，提交说明说清这次保存了什么。切回 `main` 时，暂时看不到分支上的文件，这是分支隔离，不是提交丢失。

进入 Pull requests → New pull request，确认 base 是自己的仓库 `main`，compare 是 `lab/01-first-contribution`。差异应只有 README 和 CSV。PR 正文说明改动与检查方式，并写 `Closes #实际编号`。关闭关键词只有在 PR 合入默认分支并且仓库允许自动关闭时才会改变 Issue 状态；创建 PR 本身不会关闭 Issue。[关联 PR 与 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

打开 Files changed，逐项检查文件；在没有 CI 的情况下，内容和差异检查就是本章证据。确认满足 Issue 后合并 PR，再回到 Code → `main` 打开 README 和 CSV，最后检查 Issue 是否按仓库设置关闭。自动关闭没有发生时，先核对关键词、目标分支和设置，不要把页面状态误判成文件没有合并。

## 本章结束状态

你现在有一个自己拥有的 resource-nav 仓库、一个合并的 PR、一份 README 和一份资源清单。下一章把这份远程项目带到本地，学习提交、暂存区和工作区；本章不要求你安装 Git，也不要求你创建第二套项目。
