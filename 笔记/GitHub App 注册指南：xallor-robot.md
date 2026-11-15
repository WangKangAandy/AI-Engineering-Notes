---
title: GitHub App 注册指南：xallor-robot
summary: 在 xallor-ai 组织创建安装型 GitHub App（xallor-robot）的字段填写、权限与事件建议，以及创建后需保存的凭证；供后续 OpenClaw Plugin 接入使用。
tags:
  - github-app
  - openclaw
  - automation
created: 2026-11-15
status: ready
---

# GitHub App 注册指南：xallor-robot

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本文记录在 GitHub 组织 `xallor-ai` 下注册安装型 App `xallor-robot` 的实操填写。目标形态是：GitHub 负责身份与事件投递；接收与读写由后续 OpenClaw Plugin 完成。

## 先分清两层

| 层 | 在哪做 | 性质 |
| --- | --- | --- |
| GitHub App | GitHub Developer Settings | 配置：工牌、权限、Webhook 地址 |
| 接收端 | 本机 / OpenClaw Plugin | 开发：验签、换 Token、调 API、唤醒 Agent |

在 GitHub 网页上「Create GitHub App」只完成上一层。

## 入口

组织设置 → Developer settings → GitHub Apps → **New GitHub App**  
（或：`https://github.com/organizations/xallor-ai/settings/apps/new`）

## 基本信息怎么填

参考已填写示意：

![Create GitHub App 基本信息填写示意](./_assets/github-app/create-github-app-basic.png)

| 字段 | 建议值 | 说明 |
| --- | --- | --- |
| GitHub App name | `xallor-robot` | 全局唯一；显示名可与此相同 |
| Description | `xallor-ai 仓库自动化机器人` | 可选；给安装者看的简介 |
| Homepage URL | `https://github.com/xallor-ai` | 必填；无独立产品站时用组织页即可 |
| Redirect URI | `https://github.com/xallor-ai` | 第一期不做「用户 OAuth 登录」时作占位 |
| Allow wildcard matching | 不勾选 | — |
| Expire user authorization tokens | 勾选 | 默认即可 |

第一期使用 **Installation（装到仓库）** 身份，不是用户 OAuth。若页面出现 **Request user authorization (OAuth) during installation**，不要勾选。

## Webhook

| 项 | 建议 |
| --- | --- |
| Active | 接收端未就绪时可先关闭；或用临时隧道 URL（如 smee.io）调试 |
| Webhook URL | 指向 OpenClaw Plugin 暴露的 HTTPS 路径（例如 Gateway 上 `registerHttpRoute` 的路径）；本地调试可用隧道转发到本机 |
| Webhook secret | 自行生成长随机串并妥善保存；与私钥同等敏感 |

创建 App 时若尚无公网 URL，可先填占位并关闭 Active，等 Plugin 就绪后再改。

## 仓库权限（第一期）

| Permission | 级别 |
| --- | --- |
| Metadata | Read-only |
| Contents | Read-only |
| Issues | Read & write |
| Pull requests | Read & write |
| Checks | Read-only（可选） |

权限遵循最小够用；需要 Checkout / Push 代码时再另行扩大 Contents 等权限。

## 订阅事件（第一期）

建议先开：

- `Pull request`
- `Issue comment`

需要 Issue 自动化时再开 `Issues`。行内 Review 评论需要时再开 `Pull request review` / `Pull request review comment`。

## 安装范围

选择 **Only on this account**（仅 `xallor-ai`），避免被装到无关账号。

## 创建后立刻保存的材料

1. **App ID**（设置页可见）  
2. **Private key**（Generate a private key，下载 `.pem`，勿提交到 Git）  
3. **Webhook secret**（与创建时一致）  
4. 安装到目标仓库后的 **Installation ID**（安装页 URL 或 API 可查；Webhook Payload 里也会带）

密钥只放本机密钥库 / 环境变量 / OpenClaw SecretRef，不要写进笔记正文或仓库。

## 安装到仓库

App 设置 → **Install App** → 选择 `xallor-ai` → 勾选需要的仓库（例如 `AI-Engineering-Notes`）→ Install。

## 与后续 OpenClaw 的关系

```text
GitHub App（本文）
  → Webhook
  → OpenClaw Plugin（验签 / Token / Tools）
  → OpenClaw Agent（现有模型与 Skills）
```

本文只覆盖 App 注册与安装配置；Plugin 开发另文记录。

## 检查清单

- [ ] 基本信息与示意一致（名称、主页、Redirect 占位）  
- [ ] 未开启「安装时请求用户 OAuth」  
- [ ] 权限与事件按第一期表格设置  
- [ ] 仅限本组织安装  
- [ ] App ID、私钥、Webhook secret 已离线保存  
- [ ] 已安装到目标仓库  
- [ ] Webhook Active 与 URL 与接收端就绪状态一致  
