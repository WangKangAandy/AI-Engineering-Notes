---
title: 现代 GitHub：从贡献者到维护者：让项目可以被别人继续使用
summary: 建立贡献指南、Issue/PR 模板、权限责任和外部贡献边界，让小项目能够被别人持续维护。
tags:
  - github
  - governance
  - maintenance
created: 2026-11-18
status: draft
---

# 现代 GitHub：从贡献者到维护者：让项目可以被别人继续使用

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

前一章完成了需求、子任务和 PR。本章把这些入口写进项目本身，让陌生贡献者知道如何参与，维护者知道如何分配责任，并能在权限、模板和外部贡献之间保持边界。

## 写清三个贡献入口

在 resource-nav 的 main 中维护 README、CONTRIBUTING.md 和模板目录：

- README 说明项目用途、资源格式和页面入口；
- CONTRIBUTING.md 说明收录标准、提交前检查和 PR 描述要求；
- Issue 表单收集资源标题、URL、category 和来源理由；
- PR 模板要求作者列出差异、测试和未验证内容。

这些文件应通过一个正常 PR 进入 main。文件存在不等于 GitHub 页面已经加载模板；合并后再打开 New issue 和 New pull request 验证。

## 最小贡献指南

CONTRIBUTING.md 可以从以下内容开始：

~~~markdown
# 贡献指南

1. 先搜索已有 Issue，避免重复需求。
2. 每个资源必须有 title、绝对 HTTP(S) URL 和 category。
3. 提交前运行 python -m unittest discover -s . -p 'test_*.py' -v。
4. Pull Request 说明修改文件、测试结果和未验证部分。
5. 不提交 Secrets、生成目录或个人凭据。
~~~

Issue 表单和 PR 模板只收集完成工作所需的字段，不要把所有规则复制三遍。

## 谁可以做什么

公开可读不等于任何人可以推送或修改规则。个人仓库 owner 可以调整设置和合并；collaborator 的权限取决于授予的角色。组织仓库还会有 triage、write、maintain、admin 等角色，不能把组织权限界面机械套到个人仓库。

评审责任和机器门禁是两回事：维护者负责判断需求和差异，Actions 负责执行确定性检查。CODEOWNERS 可以表达路径责任，但不替代分支保护、测试或人工验收。

## 外部贡献的边界

对别人的公开仓库，通常只能读取，不能向其分支推送。fork 是你管理的远端副本；在 fork 中创建分支、提交并推送，再向上游创建 PR。fork 不会继承上游的 Secrets、Pages、Rulesets 或 App 安装。

外部贡献前先读目标仓库的 README、CONTRIBUTING、许可证和相关 Issue。外部克隆放在独立目录，进入后核对仓库根目录、origin 和提交署名。你可以在 fork 中验证，但不能把 fork 的绿色结果写成上游已验证。

## 验收维护制度本身

合并入口文件后，从新建 Issue 和新建 PR 页面验证模板是否出现；从 README 链接验证贡献指南是否可达；从 Settings 验证分支规则和权限边界。若页面没有显示，先检查默认分支、路径和模板格式。

本章结束时，陌生贡献者能找到项目用途、提出结构化 Issue、创建合格 PR，并知道怎样报告测试结果。下一章才把程序和 CI 接回这些入口。
