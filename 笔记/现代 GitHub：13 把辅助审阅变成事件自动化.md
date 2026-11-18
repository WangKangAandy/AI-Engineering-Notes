---
title: 现代 GitHub：13 把辅助审阅变成事件自动化
summary: 从手动预览开始，配置一个只分析资源清单变化、只发表有限评论的事件驱动 AI 自动化。
tags:
  - github
  - ai
  - automation
created: 2026-11-18
status: draft
---

# 现代 GitHub：13 把辅助审阅变成事件自动化

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章只实现一种事件：同仓库、目标为 `main`、打开 PR 且修改 `resources.csv`。它输出一条有 diff 依据的审阅评论，不批准、不合并、不修改代码。确定性格式和重复 URL 继续由 Resource CI 负责。

## 先手动试跑

选择 GitHub Actions 中的 gh-aw，固定一个 Copilot 认证路径和一个输出对象。先以 staged/预览模式运行，检查触发输入、PR 号码、head SHA、读取工具和输出目标；预览仍可能消耗模型额度，不能把它当成不执行。

模型认证、GitHub 仓库权限和 safe output 是三件事。个人仓库使用专用过期凭据时，凭据只放 Actions Secret；不把本地 gh 登录当作模型认证。工具只读 PR，输出只允许 add-comment，失败不自动创建 Issue。

## 从手动切到事件

源文件的触发条件只保留 `pull_request` 的 `opened`、目标分支 `main` 和 `paths: [resources.csv]`，并限制同仓库 head。重新编译后审阅 source 和 lock，通过配置 PR 合入 `main`，再创建一条真实资源变更 PR 验证事件。不要在已有旧 PR 上等待 opened 事件重新发生。

Agent 的输入把 PR 文本和 diff 当作不可信数据，不执行其中命令，不访问资源 URL，不检出并运行 PR 代码。评论要写明变更条目、读取的 SHA、事实依据和未验证的链接，不把评论当成门禁或批准。

## 重复、失败和停用

一次真实事件后记录 run、评论 URL、输入 SHA 和输出内容。重跑前先检查评论是否已经写入；去重策略只能在实际配置的范围内描述，不能声称 exactly once。失败时区分模型失败、读取失败、评论失败和权限失败。

结束实验时先取消正在运行的 run，再禁用未来触发；长期删除源文件和 lock 时通过 PR 一起处理。恢复前重新核对凭据、编译器版本、权限和输入格式。本章的结果是一条可观察、可停止、写入边界有限的事件自动化，不是生产级 Agent 平台。
