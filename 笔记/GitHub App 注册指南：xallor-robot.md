---
title: GitHub App 注册指南：xallor-robot
summary: 在 xallor-ai 创建安装型 App xallor-robot 的逐步填写说明：基本信息、Webhook、权限与事件、私钥与安装；供 GitHub Agent Channel 的 App Adapter 使用。
tags:
  - github-app
  - openclaw
  - automation
created: 2026-11-15
status: ready
---

# GitHub App 注册指南：xallor-robot

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

在组织 `xallor-ai` 创建安装型 App `xallor-robot`：页面怎么填、权限怎么选、创建后保存什么。整体产品架构见 [[GitHub Agent Channel 架构与阶段计划]]。

权限名称以 **Create GitHub App** 页 **Repository permissions** 展示名为准。

## 入口

组织设置 → Developer settings → GitHub Apps → **New GitHub App**  
`https://github.com/organizations/xallor-ai/settings/apps/new`

## 基本信息

![Create GitHub App 基本信息填写示意](./_assets/github-app/create-github-app-basic.png)

| 字段 | 建议值 |
| --- | --- |
| GitHub App name | `xallor-robot` |
| Description | `xallor-ai 仓库自动化机器人` |
| Homepage URL | `https://github.com/xallor-ai` |
| Redirect URI | `https://github.com/xallor-ai`（占位；不做用户 OAuth） |
| Allow wildcard matching | 不勾选 |
| Expire user authorization tokens | 勾选 |
| Request user authorization (OAuth) during installation | 不勾选 |

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

**Only on this account**（仅 `@xallor-ai`）。不要选 Any account。

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

**Install App** → `xallor-ai` → 勾选仓库 → Install。

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
