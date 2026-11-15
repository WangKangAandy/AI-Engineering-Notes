---
title: OpenClaw GitHub Plugin 架构与阶段计划
summary: 将 GitHub 接入与 Agent 能力解耦：多 Integration Adapter（App / 仓库 Webhook）、统一事件与凭据、@机器人入口、Repo-scoped Session、Plugin 执行边界与 Skills 任务流程；含阶段里程碑与安全约束。
tags:
  - openclaw
  - github-app
  - architecture
created: 2026-11-15
status: ready
---

# OpenClaw GitHub Plugin 架构与阶段计划

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

配套实操：[[GitHub App 注册指南：xallor-robot]]。本文定架构与阶段，不写 Plugin 运行时代码。

## 原则

1. **Plugin** 提供能力与执行边界（Tools / Operations / Policy / 凭据 / 调用方鉴权）。  
2. **Skills** 与 **`AGENTS.md`** 定义如何完成任务；**既有 OpenClaw Agent** 负责理解与编排。  
3. **GitHub App 不是唯一前置**，而是一种接入 Adapter；仓库级 Webhook 是另一种。  
4. **Webhook ≠ 写仓授权**：事件传入与 API/Git 凭据解耦。  
5. V1 核心交互：`@机器人` + 自然语言 → 统一事件层 → Agent → Skill → Tools → 回写。  
6. 指令不是安全边界；**外部无权限用户高危操作直接拒绝**。  
7. **第一天按多 Adapter 接口设计；V1 先完整实现 GitHub App**，再补仓库 Webhook；不拆成两个 Plugin。

## 分层

| 层 | 职责 |
| --- | --- |
| Integration Adapters | GitHub App（Webhook + Installation Token）；Repository Webhook（验签 + 仓绑定） |
| Unified Event | 标准化、去重、Inbox、路由 |
| Agent Channel | Mention 识别、调用方鉴权、Repo Session、Handoff |
| Capability | 精选 Tools、Operations、Policy、Git Workspace |
| Credential Provider | 按 `connectionId` 取凭据；与事件来源解耦 |

依赖：Adapter 不直调 Agent；Agent 不知 Adapter 种类；Tools 不绑死一种认证；Policy 不因接入方式降级。

```text
@机器人 + 自然语言
  → Adapter（App 或仓库 Webhook）
  → Event Normalizer → Inbox
  → Mention + 调用方鉴权
  → Agent（Repo Session）
  → Skill → Tools（经 Credential Provider）
  → 回写 GitHub
```

## 接入方式

| 模式 | 事件 | API/Git 写 | 说明 |
| --- | --- | --- | --- |
| GitHub App | App Webhook | Installation Token | **推荐**；多仓、权限模型清晰 |
| Webhook Only | 仓库 Webhook | 无 | 仅 Payload 内有限分析；**不是**完整写仓 Agent |
| Webhook + PAT | 仓库 Webhook | 用户配置的 PAT | 轻量路径；须最小 scope，不作默认正式方案 |

统一事件需含：`source`、`repository`、`deliveryId`、`actor`、原始 `payload`、`authorization.connectionId`（App 时可带 `installationId`）。

## @机器人入口

- 主事件：`issue_comment.created`；行内：`pull_request_review_comment.created`。  
- **默认**无 mention 不唤醒；忽略机器人自己的评论；`delivery_id` + `comment_id` 去重；编辑评论 V1 默认不重跑。  
- Mention Handler **只**做识别、抽文本、鉴权、投递；**不**选 Skill、不解析任务剧本。  
- 先短回「处理中」，异步执行，结果回写；任务关联原 Comment。

## 调用方授权

Mention ≠ 授权。在 Handoff **前**校验作者对仓库的 GitHub 权限（+ 可选 allowlist）。

| 调用方 | 默认 |
| --- | --- |
| 外部无协作写权限 | **拒绝唤醒**（或显式开启只读分析，默认关） |
| 有 push/maintain/admin 等 | 可写非默认分支、开 PR、Review 等（按矩阵） |
| 任意人 | **禁止** push/merge 默认分支（Policy + 分支保护） |

每次任务独立注入请求者与授权；**不从 Session 历史继承权限**。

## Session

- **Repo-scoped 主 Session**：一仓一主会话，共享协作上下文。  
- Key：`github:connection-{connectionId}:repo-{repositoryId}:agent-{agentId}`。  
- 任务用独立执行上下文；同仓 Handoff V1 **串行**。  
- 不做独立「仓库知识库」产品；上下文 = 主 Session + 可选摘要。

## Policy（摘要）

| 操作 | 默认分支为目标/base |
| --- | --- |
| Push | 拒绝 |
| Create PR | **允许** |
| Merge PR | 拒绝 |

无裸 Git push 凭据注入通用 Shell。

## 捆绑 Skills（可覆盖）

`github-pr-review` · `github-pr-development` · `github-issue-triage` · `github-actions`  
只写工作方法，不写鉴权。Agent 自选 Skill。

## 精选 Tools（任务型，非一 API 一 Tool）

读：`search` / `get_repo` / `get_issue` / `get_pr`（复合）/ `get_workflow`  
写：`create|update_issue` / `create_pr` / `add_comment` / `submit_review` / `merge_pr`（拒默认分支 base）/ `dispatch_workflow`  
Git：`checkout_branch` / `commit_changes` / `push_branch`  

不向 Agent 暴露无限制 `github_api`。

## 里程碑

| 阶段 | 内容 |
| --- | --- |
| M0 | 本文 + 锁 OpenClaw 版本；Handoff / Skills 打包 / 授权矩阵；Connection·Event·Credential 接口草案 |
| M1 | Integration 骨架 |
| M2 | GitHub App Adapter |
| M2.1 | Repository Webhook Adapter（可后置） |
| M3 | 统一 Inbox / Mention / Session / Handoff |
| M4 | Tools / Operations / Policy / Git |
| M5 | Skills + E2E（App 必过） |

工程仓名约定：`openclaw-github-app`（或同名）；本笔记库不放运行时代码。

## 对抗结论（摘要）

- 多 Adapter **要**，V1 **不必**两种实现齐活。  
- Webhook Only **不得**伪装成完整 Agent。  
- PAT 可作轻量，**不作**默认正式路径。  
- 不为 GitLab 提前开工；只保留接入层可扩展。  
- 安全不因「只是 Webhook」放宽。
