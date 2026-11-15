---
title: GitHub App 注册指南：xallor-robot
summary: 在 xallor-ai 创建安装型 App xallor-robot：基本信息、Webhook、按当前创建页名称配置的 Repository permissions 清单，以及创建后凭证与主分支保护要点；供自建 OpenClaw GitHub Plugin 使用。
tags:
  - github-app
  - openclaw
  - automation
created: 2026-11-15
status: ready
---

# GitHub App 注册指南：xallor-robot

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

在组织 `xallor-ai` 注册安装型 App `xallor-robot`。架构：GitHub App 只做身份、权限上限与事件投递；验签、换 Token、调 API、唤醒 Agent 由自建 OpenClaw GitHub Plugin 完成。

权限名称以**当前 Create GitHub App 页 Repository permissions 展示名为准**（勿与 REST 文档里的旧别名混用）。

## 两层分工

| 层 | 在哪 | 做什么 |
| --- | --- | --- |
| GitHub App | Developer settings | 工牌、权限上限、Webhook |
| OpenClaw Plugin | 自建接收端 | 验签、签发更小范围的 Installation Token、调 API、跑 Agent |

页面上 Create 只完成上一层。App 权限是能力上限；具体请求仍可用 Installation Token 再收窄仓库与权限。

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

## Webhook / Permissions / 安装范围

![Create GitHub App：Webhook、Permissions、安装范围](./_assets/github-app/create-github-app-webhook-perms.png)

### Webhook

| 项 | 建议 |
| --- | --- |
| Active | 先不勾选；Plugin 有公网 HTTPS 后再开 |
| Webhook URL | 创建时可空；就绪后填 Plugin 路由（本地可用隧道） |
| Secret | 页面无「生成」按钮。本机造高熵随机串粘贴；与接收端同一串，用于 HMAC |

生成示例（任意可信机器即可，与运行环境无关）：

```bash
openssl rand -hex 32
```

```powershell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
```

离线保存；勿进 Git。接收端就绪后：勾选 Active → 填 URL（及 Secret）→ Save。

### Repository permissions

只展开 **Repository permissions**。名称按下表与页面逐项对齐；**未列出的项一律 `No access`**。

目标：Agent 能读改代码、处理 Issue/PR、跑/管 CI、参与协作；**不把**仓库管理权、Actions/Dependabot/Codespaces 密钥、GitHub 自带 Agent 相关权限交给 App。禁止私自合入默认分支靠**分支保护**（禁直推、需 PR；`xallor-robot` 不进 bypass）+ Plugin 策略，不是靠关掉 Contents Write。

#### 建议 Read and write

| 页面名称 | 用途 |
| --- | --- |
| Actions | 查看 Workflow / 运行 / 日志；触发或管理工作流 |
| Checks | 查看与创建 Check Runs / Suites |
| Commit statuses | 读取与设置 Commit Status |
| Contents | 读代码；建分支、提交、推送 |
| Issues | 创建/修改/关闭 Issue；评论与标签 |
| Pull requests | 创建/修改 PR；评论与 Review（合并能力受分支保护约束） |
| Discussions | 参与仓库 Discussions（扩展协作） |
| Deployments | 创建与管理部署记录 |
| Pages | 管理 GitHub Pages |
| Variables | 管理 Actions Repository Variables（**不是** Secrets） |
| Custom properties | 管理仓库自定义属性 |

#### 建议 Read-only

| 页面名称 | 用途 |
| --- | --- |
| Metadata | 仓库基础信息（必需；界面常已锁定） |
| Code scanning alerts | 代码扫描告警 |
| Dependabot alerts | 依赖漏洞告警 |
| Secret scanning alerts | 密钥扫描告警 |
| Environments | 部署环境配置（只读） |
| Repository security advisories | 仓库安全公告（只需读时保持 Read；要维护公告再升 Write） |

#### 单独设置

| 页面名称 | 设置 | 说明 |
| --- | --- | --- |
| Workflows | **Write**（页面常仅此档） | 与 Actions 不同；改 `.github/workflows` 必须另开此项 |

#### 明确 No access

| 页面名称 | 原因 |
| --- | --- |
| Administration | 仓库设置、成员、删除等高危管理 |
| Agent secrets / Agent tasks / Agent variables | GitHub 自带 Agent 体系；非 OpenClaw 自建 Plugin 所需 |
| Secrets | Actions Secrets，敏感 |
| Dependabot secrets | Dependabot 密钥 |
| Webhooks | 仓库级 Webhook 管理；App 自身 Webhook 在 App 配置里 |
| Codespaces / Codespaces lifecycle admin / Codespaces metadata / Codespaces secrets | 非当前目标 |
| Artifact metadata | 除非要管构建产物元数据 |
| Attestations | 除非要管构建来源证明 |
| Code quality | 除非要读/管 GitHub Code Quality 数据 |

列表中若还有未点名项，默认也保持 `No access`。

### Organization / Account / Enterprise

全部 **No access**。仓库级权限已够当前方案；不开放组织成员、组织 Secrets、组织 Webhooks 等。

### 订阅事件

权限设好后勾选（名称以页面为准）。建议至少：

- **Pull request**
- **Issue comment**

按需再开：`Issues`、`Pull request review`、`Pull request review comment`、`Discussion` / `Discussion comment`、`Check run` / `Check suite`、`Workflow run` 等。Active 未开时勾选只作就绪清单。

### 安装范围

选 **Only on this account**（仅 `@xallor-ai`）。不要选 Any account。

## 创建后保存

1. App ID  
2. Private key（`.pem`，Generate a private key）  
3. Webhook secret  
4. 安装后的 Installation ID  

只放本机密钥库 / 环境变量 / OpenClaw SecretRef。

## 安装与主分支

App 设置 → **Install App** → `xallor-ai` → 勾选仓库 → Install。

对默认分支启用分支保护：禁止直推、必须 PR、按需要求评审/CI；不要把本 App 加入 bypass。

## 与 OpenClaw

```text
GitHub App（本文）
  → Webhook
  → OpenClaw Plugin（验签 / 收窄 Token / Tools）
  → OpenClaw Agent
```

Plugin 另文。官方参考：[Choosing permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app) · [Permissions required for GitHub Apps](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps) · [Webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads)

## 核对清单

- [ ] 基本信息按上表；未开安装时用户 OAuth  
- [ ] Webhook：Active 暂关；Secret 已自备并保存  
- [ ] R/W：Actions、Checks、Commit statuses、Contents、Issues、Pull requests、Discussions、Deployments、Pages、Variables、Custom properties  
- [ ] Read：Metadata、Code scanning / Dependabot / Secret scanning alerts、Environments、Repository security advisories  
- [ ] Workflows = Write  
- [ ] Administration、Agent\*、Secrets、Dependabot secrets、Webhooks、Codespaces\*、Artifact metadata、Attestations、Code quality = No access  
- [ ] Organization / Account / Enterprise = No access  
- [ ] 事件至少 Pull request + Issue comment  
- [ ] Only on this account；已安装目标仓库；默认分支已保护且 App 不在 bypass  
- [ ] App ID / `.pem` / Webhook secret / Installation ID 已离线保存  
- [ ] Plugin 就绪后再开 Active 并填 Webhook URL  
