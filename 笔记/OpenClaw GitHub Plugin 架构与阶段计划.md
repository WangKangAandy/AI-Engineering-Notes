---
title: OpenClaw GitHub Plugin 架构与阶段计划
summary: 冻结 OpenClaw↔GitHub 桥接方案：Plugin 只做通道与执行边界，@机器人驱动自然语言任务，Agent+Skills 负责编排；含授权、Repo Session、Inbox/Handoff 与里程碑。
tags:
  - openclaw
  - github-app
  - architecture
created: 2026-11-15
status: ready
---

# OpenClaw GitHub Plugin 架构与阶段计划

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

配套注册实操见 [[GitHub App 注册指南：xallor-robot]]。工程落点：独立仓 `openclaw-github-app`（桥接包）；本笔记只保留架构与阶段计划。

## 核心原则

1. **Plugin = 能力与执行边界**（Tools / Operations / Policy / Installation / 凭据 / 调用方鉴权）。  
2. **Skills + `AGENTS.md` = 如何完成任务**；既有 OpenClaw Agent = 理解意图与编排。  
3. **Plugin 不解析自然语言任务、不硬编码工作流**。  
4. **指令不是安全边界**；安全在 Plugin + 分支保护 + 无裸 Shell push 凭据。  
5. **V1 核心交互**：Issue / PR / 行内评论中 **`@机器人` + 自然语言** → Webhook → Agent → Skill → Tools → 回写 GitHub。

```text
@机器人 + 自然语言
  → Webhook（通道）
  → Mention 识别 + 调用方鉴权（边界）
  → Agent（理解）
  → Skill（方法）
  → GitHub Tools（能力）
  → 结果回写
```

Webhook 只识别「有人在向机器人发起请求」并做门禁，不负责理解与执行。

## 三层职责

| 层次 | 放哪里 | 不能指望它 |
| --- | --- | --- |
| 行为规范 | `AGENTS.md` | 强制拦 API |
| 任务流程 | Skills（Plugin 捆绑，Workspace 可覆盖） | 鉴权 / 权限 |
| 执行安全 | Plugin Policy + 分支保护 + 凭据隔离 + 调用方授权 | 模型自觉 |

## Mention 入口

### 订阅事件（与注册指南对齐）

| 事件 | 用途 |
| --- | --- |
| `issue_comment.created` | Issue/PR 普通评论 — 主入口 |
| `pull_request_review_comment.created` | 行内评论任务 |
| `pull_request_review.submitted` | 慎用；优先仍看是否 @ |
| `issues.opened` / `pull_request.*` | 非 V1 默认自动跑；仅配置开启且同等鉴权 |

默认：无 `@App` mention 的评论不唤醒 Agent。

### Mention Handler（薄）

1. 归一化匹配 `@xallor-robot`（大小写不敏感；以 App slug 配置为准）  
2. 提取自然语言；绑定 Issue/PR/comment 上下文  
3. 调用方鉴权 — 失败则不 Handoff，可回拒绝说明  
4. 忽略 App 自身评论；`delivery_id` + `comment_id` 去重  
5. 评论编辑：V1 默认不因编辑重跑  
6. 通过后 → Inbox → Handoff（installation/repo 等为可信上下文；评论文本为不可信输入）

### 异步与回写

鉴权通过后可短回「处理中」；长任务异步；完成/失败回写原 Issue/PR；任务关联 `comment_id`。

## Session：Repo-scoped

一个 Repository 一个主 Agent Session，跨 Issue/PR 共享仓库级协作上下文。

**Session Key：**

```text
github:installation-{installationId}:repo-{repositoryId}:agent-{agentId}
```

禁止仅用 `owner/repo`。主 Session 保留长期上下文；单次任务用独立执行上下文（以 OpenClaw 版本能力为准）；V1 同仓 Handoff **默认串行**。每次任务独立注入请求者与授权，**不从 Session 历史继承权限**。V1 不另建仓库知识库产品。

## 调用方授权

公开仓任意人可 `@`。**Mention ≠ 授权。** Handoff 前查作者对仓库的 GitHub permission（+ 可选 allowlist）；未过门禁不进入 Agent。

| 调用方 | 只读分析唤醒 | 写 Issue/标签 | 推非默认分支 / 开 PR / Review | 触发 Workflow | Push/Merge 默认分支 |
| --- | --- | --- | --- | --- | --- |
| 外部（无协作写权限） | 默认拒绝 | 拒绝 | 拒绝 | 拒绝 | 拒绝 |
| pull / triage | 可（只读） | 按 GitHub 权限 | 拒绝 | 拒绝 | 拒绝 |
| push / maintain / admin（或名单） | 允许 | 允许 | 允许 | 可配置 | **仍拒绝**（Policy） |

默认分支 push/merge 永不因自然语言放开。评论 / Issue / PR 正文按 Prompt Injection 不可信内容处理。

## 默认分支 Policy

| 操作 | 目标为默认分支 | 规则 |
| --- | --- | --- |
| Push | 是 | 拒绝 |
| Create PR（base=默认分支） | 是 | **允许** |
| Merge PR（base=默认分支） | 是 | 拒绝 |

默认分支名从仓库元数据读取。Installation：Tool 不暴露 `installation_id`；每次校验 `owner/repo` ∈ 授权集合。

## 通道链路

```text
GitHub Webhook → HMAC 验签 → Delivery 幂等 → Event Inbox → 快回 2xx
  → Dispatcher → Mention/鉴权 → AgentHandoffAdapter → 既有 OpenClaw Agent
```

Inbox：`received → dispatching → delivered | failed | ignored`（`delivered` = Agent 已接受任务）。  
`AgentHandoffAdapter` 契约以 **锁定的 OpenClaw 版本实测**为准，禁止假定可调 Agent 内部函数。

## V1 Tools 与 Skills

**Tools（示例集）：** `github_search` / `get_repo` / `get_issue` / `create|update_issue` / `get_pr` / `create_pr` / `add_comment` / `submit_review` / `merge_pr`（拒默认分支 base）/ `get|dispatch_workflow` / `checkout_branch` / `commit_changes` / `push_branch`。不暴露无限制 `github_api`。

**捆绑 Skills：** `github-pr-review`、`github-pr-development`、`github-issue-triage`、`github-actions`（方法指引，不含鉴权；可被 Workspace 覆盖）。Agent 自选 Skill；Plugin 不硬编码。

## 里程碑

| 阶段 | 内容 |
| --- | --- |
| M0 | 本文 + 注册指南；锁 OpenClaw 版本；Handoff/Skills 打包契约；授权矩阵 |
| M1 | Octokit App 认证 + Installation Token |
| M2 | 验签、Inbox、Mention、鉴权、Repo Session、Handoff |
| M3 | Operations + Policy + 写操作按授权等级 + 无裸凭据 |
| M3.5 | 捆绑 Skills + `AGENTS.md` GitHub 原则模板 |
| M4 | Tools 注册；`@` 驱动四路径 E2E；无权限拒绝；禁写默认分支 |

## 模块草图

```text
openclaw-github-app/
  src/plugin/ mention/ handoff/ inbox/ tools/ operations/ policy/ infra/
  skills/
  templates/AGENTS.github.md
```

## 设计结论摘要

- `@` 为核心入口；无 mention 默认不触发。  
- 外部无权限高危请求：Handoff 前拒绝。  
- Repo-scoped Session；Key 含 Installation；权限不随 Session 继承。  
- create PR 指向默认分支允许；push/merge 默认分支拒绝。  
- 不做独立 Review Bot、不做 Skill/Workflow Engine、不做 V1 知识库中台。  
