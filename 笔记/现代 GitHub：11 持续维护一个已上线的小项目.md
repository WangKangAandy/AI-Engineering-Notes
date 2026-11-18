---
title: 现代 GitHub：11 持续维护一个已上线的小项目
summary: 围绕反馈、失败运行、权限、依赖、费用和退出，建立小项目的持续维护节奏。
tags:
  - github
  - maintenance
  - security
created: 2026-11-18
status: draft
---

# 现代 GitHub：11 持续维护一个已上线的小项目

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

上线一次页面不等于项目完成。维护者要知道怎样处理反馈、失败运行、依赖更新、权限变化、成本提醒和实验退出。

## 维护循环

收到资源错误时，先开 Issue 描述来源、当前条目和预期修正；小范围修正走 PR，CI 通过后再部署。构建失败时先查看当前 SHA 的首个失败 step；不要重跑旧提交来掩盖新提交的错误。页面异常时沿部署记录回到 artifact 和 commit。

## 做一次维护审计

按真实状态逐项检查：

- workflow 的 `permissions` 是否只包含当前任务需要的权限；
- Secrets、Variables、Environment secrets 是否仍有用途；
- 第三方 action 是否有更新或组织策略限制；
- Dependabot、secret scanning、code scanning 当前是否可用，哪些尚未启用；
- Self-hosted Runner 或 AI 自动化是否仍在运行，谁可以触发并写入什么；
- Actions、artifact、缓存和模型调用是否有持续费用或预算影响。

没有安全告警不等于没有风险；没有启用某项工具也不能写成“已经保护”。审计记录应写检查了什么、发现或未发现什么、采取了什么处理。

## 退出和恢复

停止运行、禁用未来触发、撤销凭据、移除 App、取消 Pages 和删除实验文件是不同动作。结束本书练习时先确认没有其他任务依赖这些资源，再逐项停用。恢复自动化前重新核对凭据、版本、权限和输入格式，不只重新打开 workflow。

本章结束时，你能把一次上线后的问题放回正确记录，并完成一次有证据的权限、依赖、成本和退出审计。按需工程化的 matrix、cache、reusable workflow 和 concurrency 不属于本章必修，放在 S5。
