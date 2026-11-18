---
title: 现代 GitHub：12 委派约束并验收一个 Agent 任务
summary: 把一个小测试改进交给 Copilot Cloud Agent，统一处理上下文、规则、分支、PR、纠偏和最终验收。
tags:
  - github
  - ai
  - copilot
created: 2026-11-18
status: draft
---

# 现代 GitHub：12 委派约束并验收一个 Agent 任务

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章把一次 Agent 任务写成完整闭环，而不是把启动、规则和验收拆成三个互不相认的状态。任务是为资源清单增加空 `category` 的测试；它足够小，能让你检查每一步。

## 先写任务契约

任务契约包含：只允许修改 `test_catalog.py`；保持现有实现和 CSV 格式；运行测试、清单校验和构建；创建面向 `main` 的 PR；不批准、不合并；结束时报告实际文件、命令、结果和未执行检查。规则文件可以补充项目事实，但不会自动授予写权限或绕过仓库规则。

## 发起并观察 Cloud 任务

在 Copilot Agents 中选择自己的 `resource-nav`、基础分支 `main` 和 Cloud 环境。Cloud 是隔离执行环境，不是本机终端，也不是 Actions 的 Environment 审批。启动前核对账号资格、仓库授权和预算。

任务完成后先看 session 日志，再看 PR。Cloud 的修改不会出现在本地工作区；若需要本地复核，取得实际 PR head 分支并核对 SHA：

```powershell
$prNumber = 123
git status --short
if (git status --porcelain) { throw '先处理本地未提交修改' }
git fetch origin "pull/$prNumber/head:agent/$prNumber"
git switch "agent/$prNumber"
git rev-parse HEAD
git diff main...HEAD -- test_catalog.py
```

不要猜分支名，也不要在 `main` 上寻找尚未合并的云端修改。

## 规则和结果分开验收

规则可以告诉 Agent 文件边界、测试命令和禁止操作；它不是权限系统。用只读问题或会话日志确认 Agent 是否看到了约定，再用 diff 和测试确认它是否遵守。模型正确回答一个文件名，不足以证明规则加载成功。

PR 验收至少检查：只有 `test_catalog.py` 改动；新增测试确实传入空 `category`；当前 head SHA 的测试、清单校验和构建都通过；Agent 没有合并 PR。单人练习可以留下 Comment，自查不等于独立批准。

## 纠偏和结束

如果 diff 越界，发送一次具体纠偏；如果仍越界或测试失败，停止会话，在 PR 分支人工处理。决定结束时明确是合并、关闭还是保留等待评审，并记录 session、PR、diff、测试结果和未验证项。停止会话不会撤销已推送的提交。

本章结束时，一个 Agent 任务有唯一的输入、执行环境、PR、验收证据和结束状态；下一章才把一个人工验证过的辅助审阅任务放进 Actions 事件自动化。
