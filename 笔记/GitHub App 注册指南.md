---
title: GitHub App 注册指南
summary: 说明 GitHub App 是什么、适合做什么，并逐步演示如何在组织下创建安装型 App：基本信息、Webhook、权限与事件、私钥与安装。截图以 xallor-robot 为例，字段可替换。
tags:
  - github-app
  - github
  - automation
created: 2026-11-15
status: ready
---

# GitHub App 注册指南

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

## GitHub App 是什么

GitHub App 是 GitHub 提供的一种**一等集成身份**：以「应用」而不是某个个人账号去访问仓库。创建后装到组织或仓库上，用自己的权限集与 Webhook 收事件，再用私钥换短期 Installation Token 调 API。

和常见替代比：

| 方式 | 特点 |
| --- | --- |
| Personal Access Token (PAT) | 绑在个人用户上，权限面往往偏大，轮换与审计麻烦 |
| OAuth App | 偏「用户登录授权」；仓库自动化也能做，但安装型机器人场景更绕 |
| **GitHub App** | 独立身份、按仓库安装、权限可细到资源类型、事件经 Webhook 推送；适合机器人与自动化 |

本文默认做**安装型**用法：装到仓库后以 Installation 身份读写与收事件，**不**做「安装时请求用户 OAuth 登录」。

## 能做什么、怎么用

典型能力：

1. **收事件**：PR、Issue、评论、Checks / Actions 等变更推到你配置的 Webhook URL。  
2. **调 API**：读仓库、评 PR、开 Issue、推分支、触发 Workflow 等（取决于你勾的权限）。  
3. **身份隔离**：权限是 App 的上限；Token 还可再收窄；卸装即收回访问。

常见用法：CI 机器人、PR Review / 评论机器人、Issue 分流、把 GitHub 事件接到自建服务或 Agent。  
流程可以记成：

```text
注册 App → 设权限与事件 → 生成私钥 → 安装到仓库
  →（可选）打开 Webhook → 自建服务验签并调 API
```

下文按创建页从顶到底填写。截图与示例来自 `xallor-robot`（组织 `xallor-ai`），请换成你自己的名称与主页。权限名称以页面 **Repository permissions** 展示名为准。

若你的场景是把 GitHub 接到 Agent 通道，可另见 [[GitHub Agent Channel 架构与阶段计划]]；**不是**读本文的前提。

## 入口

目标组织（或用户）→ Settings → Developer settings → GitHub Apps → **New GitHub App**  
组织示例：`https://github.com/organizations/<你的组织>/settings/apps/new`

## 基本信息

![Create GitHub App 基本信息填写示意](./_assets/github-app/create-github-app-basic.png)

| 字段 | 建议 | 示例 |
| --- | --- | --- |
| GitHub App name | 全局唯一；与机器人对外名一致即可 | `xallor-robot` |
| Description | 可选简介 | `xallor-ai 仓库自动化机器人` |
| Homepage URL | 无独立产品站时用组织或项目页 | `https://github.com/xallor-ai` |
| Redirect URI | 不做用户 OAuth 时作占位 | 同 Homepage |
| Allow wildcard matching | 不勾选 | — |
| Expire user authorization tokens | 勾选 | — |
| Request user authorization (OAuth) during installation | 不勾选 | — |

## Webhook

向下滚到 Webhook / Permissions 区域（示意见下图）：

![Create GitHub App：Webhook、Permissions、安装范围](./_assets/github-app/create-github-app-webhook-perms.png)

| 项 | 建议 |
| --- | --- |
| Active | 先不勾选；接收端有公网 HTTPS 后再开 |
| Webhook URL | 创建时可空；就绪后填接收端 HTTPS 路径（本地可用隧道） |
| Secret | 页面**无**生成按钮；本机造高熵随机串粘贴，与接收端同一串做 HMAC |

```bash
openssl rand -hex 32
```

```powershell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
```

Secret 离线保存，勿进 Git。就绪后：勾选 Active → 填 URL → Save。

## Repository permissions

只改 **Repository permissions**；**未列出的项一律 `No access`**。Organization / Account / Enterprise 全部 **No access**。

默认分支安全靠仓库**分支保护**（禁直推、需 PR；本 App 不进 bypass），不是靠把 Contents 设成只读。

### Read and write

| 页面名称 | 用途 |
| --- | --- |
| Actions | Workflow / 运行 / 日志；触发或管理工作流 |
| Checks | Check Runs / Suites |
| Commit statuses | Commit Status |
| Contents | 读代码；建分支、提交、推送 |
| Issues | Issue 与评论、标签 |
| Pull requests | PR、评论与 Review |
| Discussions | Discussions |
| Deployments | 部署记录 |
| Pages | GitHub Pages |
| Variables | Actions Repository Variables（不是 Secrets） |
| Custom properties | 仓库自定义属性 |

### Read-only

| 页面名称 | 用途 |
| --- | --- |
| Metadata | 仓库基础信息（必需；常已锁定） |
| Code scanning alerts | 代码扫描告警 |
| Dependabot alerts | 依赖漏洞告警 |
| Secret scanning alerts | 密钥扫描告警 |
| Environments | 部署环境（只读） |
| Repository security advisories | 安全公告（要维护再升 Write） |

### 单独设置

| 页面名称 | 设置 | 说明 |
| --- | --- | --- |
| Workflows | **Write**（常仅此档） | 与 Actions 不同；改 `.github/workflows` 须另开 |

### No access（明确关掉）

Administration；Agent secrets / Agent tasks / Agent variables；Secrets；Dependabot secrets；Webhooks；Codespaces 及相关项；Artifact metadata；Attestations；Code quality。其余未点名项也保持 `No access`。

## 订阅事件

建议至少：

- **Issue comment**（Issue / PR 普通评论）
- **Pull request review comment**（行内评论）
- **Pull request**

按需：`Issues`、`Pull request review`、`Check run` / `Check suite`、`Workflow run` 等。Active 未开时勾选只作就绪清单。

## 安装范围

**Only on this account**（仅当前创建 App 的账号/组织）。不要选 Any account。

点绿色 **Create GitHub App**。

## 创建后：凭证与安装

保存：

1. **App ID**（General）  
2. **Private key**（`.pem`，见下）  
3. **Webhook secret**  
4. **Installation ID**（安装后；安装页 URL / API / Webhook payload）

只放本机密钥库或环境变量；勿提交 Git、勿写进公开笔记。

### 生成 Private key

App 设置 → **Credentials** → **Key pairs** → **New key**

![Credentials → Key pairs → New key](./_assets/github-app/credentials-new-key.png)

浏览器下载 `.pem`。私钥只在此刻可下；丢失需再 New key。

### 安装到仓库

**Install App** → 选择你的组织/账号 → 勾选仓库 → Install。

对默认分支开分支保护：禁直推、必须 PR；不要把本 App 加入 bypass。

## 核对清单

- [ ] 基本信息与 OAuth 相关项按上表  
- [ ] Webhook：Active 暂关；Secret 已生成并保存  
- [ ] Repository / Org / Account / Enterprise 权限按上表  
- [ ] 事件至少 Issue comment + Pull request review comment（及 Pull request）  
- [ ] Only on this account；已安装目标仓；默认分支已保护且 App 不在 bypass  
- [ ] 已下载 `.pem`；App ID / Webhook secret / Installation ID 已离线保存  
- [ ] 接收端就绪后再开 Active 并填 Webhook URL  

参考：[Choosing permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app) · [Permissions required for GitHub Apps](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps) · [Webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads)
