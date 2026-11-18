---
title: 现代 GitHub：09 让每个 PR 接受自动检查
summary: 把资源校验、单元测试和页面构建接入 Actions，并让失败检查阻止合并。
tags:
  - github
  - actions
  - ci
created: 2026-11-18
status: draft
---

# 现代 GitHub：09 让每个 PR 接受自动检查

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

前置是第 8 章已经在资源导航项目中运行三条本地命令：校验 CSV、运行测试、生成页面。本章不再介绍产品入口，而是回答“怎样让每个 PR 自动得到同样的证据”。

## 一个 workflow 如何产生检查

workflow 是仓库中的 YAML 定义；事件触发一次 run，run 中有 job，job 中有 step，step 在 runner 上执行命令或 action。`pull_request` 检查待合并的改动，合入 `main` 后的 `push` 检查主线的新状态；它们可能对应不同 SHA。

在 `.github/workflows/ci.yml` 中配置一个 `check` job，按顺序运行：

```yaml
name: Resource CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
jobs:
  check:
    name: Check resources
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - run: python catalog.py resources.csv
      - run: python -m unittest discover -v
      - run: python build.py
```

`permissions`只给读取仓库内容的权限。`setup-python`选择 Actions 环境中的解释器；本地 Windows 的 `py -3.12` 与 workflow 里的 `python`是两个执行环境，不能混为一次验证。[Actions 概念](https://docs.github.com/en/actions/concepts)

## 先观察失败，再设置门禁

在资源清单中复制一条已有 URL，创建 PR。Check resources 应在第一条校验命令失败，后续步骤因前一步失败而不再运行。此时记录当前提交、失败 step 和错误信息，保留 PR 打开。

在 Settings → Rules → Rulesets 为 `main` 创建 Active 规则，启用 Require a pull request 和 Require status checks to pass，选择真实产生的 **Check resources**。单人练习的批准人数可以为 0；规则的重点是经过 PR 和检查，而不是强行制造第二个评审者。只有支持该规则并且你有管理权限时，才能声称门禁已经建立。

回同一来源分支删除重复行，提交并推送。新提交应重新运行 Check resources，当前检查通过后才允许普通合并。合并后 main 的 push run 是另一条证据，不能拿失败 PR run 的绿灯替代它。

## Job 边界和失败判断

同一 job 的 steps 默认共享工作区；不同 job 需要 checkout 或 artifact。`needs`只建立顺序，不复制文件。一个成功的 shell 命令也不等于测试覆盖了需求；检查日志中的测试数量、清单条数和构建输出。

常见故障按这个顺序查：workflow 是否在默认分支、事件目标分支是否正确、检查名称是否变化、当前提交是否触发、规则是否 Active、账号是否有 bypass。不要因为 YAML 能解析或本地测试通过，就跳过云端检查的结果。

本章结束时，resource-nav 有一条真实 CI、一个可识别的必需检查，以及一轮失败→阻止→修复→合并记录。产物如何跨 job 保存和怎样发布，放在下一章。
