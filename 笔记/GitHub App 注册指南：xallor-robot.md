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

## Webhook / 权限 / 安装范围（本页后半段）

向下滚动到与下图一致的区域后再填：

![Create GitHub App：Webhook、Permissions、安装范围](./_assets/github-app/create-github-app-webhook-perms.png)

图中现状通常是：

- **Active** 未勾选  
- **Webhook URL / Secret** 为空  
- **Permissions** 四个分组折叠未展开  
- 安装范围已选 **Only on this account**（正确，保持）

按下面三节逐项配置，再点绿色 **Create GitHub App**。

### Webhook

| 项 | 第一期建议 | 说明 |
| --- | --- | --- |
| Active | **先不勾选**（与截图一致） | 未勾选时 GitHub 不会投递事件；等 Plugin 有公网 HTTPS 入口后再勾选 |
| Webhook URL | 创建时可留空 | 就绪后填 Plugin 的 HTTPS 路径（如 Gateway `registerHttpRoute`）；本地调试可用 smee.io / ngrok 等隧道转发到本机 |
| Secret | **自备一串高熵随机口令，粘贴进输入框** | 页面上**没有**「生成」按钮。它是你与 GitHub 约定的共享口令，用来验 HMAC；与在哪台机器生成无关 |

> [!note] Secret 是什么、为什么「随便造一串」
> **不是**绑定某台机器、某次安装或某个仓库的硬件指纹。它只是一段双方都知道的口令：
>
> 1. 你填进 GitHub App 的 **Secret**  
> 2. 同一串再放进接收端（OpenClaw Plugin / 环境变量）  
> 3. GitHub 每次投递带签名；接收端用这串验签，证明请求来自 GitHub、内容未被改
>
> 因此：**在哪台电脑执行生成命令都行**（笔记本、跳板机、WSL 均可），输出拷走即可；命令本身不依赖特定环境。所谓「随便」是指**内容不必有业务含义**，不是可以随便用短密码或公开示例串——要用足够长、不可猜测的随机串。
>
> GitHub 创建页不会帮你点一下出串。任选一台可信机器跑：
>
> ```bash
> openssl rand -hex 32
> ```
>
> Windows PowerShell：
>
> ```powershell
> -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
> ```
>
> 把输出整段粘贴进 **Secret**，并另存到密码库 / 接收端环境变量（勿提交 Git、勿贴进公开 Issue）。

> [!tip] 为什么先关 Active、但仍可填 Secret
> Secret 与 URL 可分开准备：没有接收端时不要开 Active，避免投递失败堆积。创建时也可先留空 Secret，等有接收端再一起填——但一旦开始收事件，**GitHub 上的 Secret 与验签端必须是同一串**。

接收端就绪后的改法：App 设置页 → 勾选 Active → 填入最终 Webhook URL（及 Secret，若创建时未填）→ Save。

### 权限怎么点（Permissions）

截图里四个分组默认是折叠的。**第一期只动 Repository permissions**；下面三组整组保持默认（全部 No access / 不展开也可）：

| 分组 | 第一期 |
| --- | --- |
| **Repository permissions** | 展开，按细表改 |
| Organization permissions | **不改** |
| Account permissions | **不改**（那是用户 OAuth 流用的） |
| Enterprise permissions | **不改** |

#### 操作顺序

1. 点击 **Repository permissions** 展开长列表（每项右侧是下拉：`No access` / `Read-only` / `Read & write`）。  
2. 只改下表列出的几行；**列表里没点名的项一律保持 `No access`**。  
3. 改完权限后，同一页下方会出现 / 可勾选 **Subscribe to events**——事件勾选见下一节（权限不够时部分事件勾不上或无效）。  
4. 再确认安装范围为 Only on this account，最后点 **Create GitHub App**。

#### 第一期：Repository permissions 逐项

目标能力：**允许写仓库（推分支、改文件、开/评 PR）**；**禁止私自合入默认分支（`main` / `master`）**——后者不靠把 Contents 降成只读，而靠分支保护 + 接收端策略（见下节）。

| 页面上的权限名 | 下拉选 | 机器人因此能做什么 | 备注 |
| --- | --- | --- | --- |
| **Metadata** | `Read-only`（通常创建后强制具备） | 读仓库基础信息、列表已安装仓库 | 不含代码 / Issue / PR 正文 |
| **Contents** | **`Read & write`** | 读文件；**push 分支、API 改文件/提交**；发 release 等写接口 | 要「能写操作」就必须开 Write；只读挡不住合主分支，也挡不住写 |
| **Issues** | `Read & write` | 读/写 Issue；评论、关单、改标签等；**发 PR 评论常也依赖这项** | 只开 PR、不开 Issues 易 403 |
| **Pull requests** | `Read & write` | 读/写 PR、评论、开 PR；API 上也具备「合并 PR」的权限位 | **合不进主分支**靠仓库分支保护，不是靠这里选 Read |
| **Checks** | `Read-only`（可选；可先 `No access`） | 读 **Checks API** 结论（GitHub Actions 等多走这套） | 要机器人自己创建 Check Run 再开 Write |
| **Commit statuses** | 第一期 **`No access`**（可选以后 `Read-only`） | 旧版 **Status API**（commit 上的 pending/success/failure 小点） | 与 Checks 不是同一权限；写代码 / 评 PR **不需要**它。仅当要读仍走 Status API 的 CI，或机器人自己 `POST` 状态点时再开 Read / Write |

说明：

- 下拉只有三档时，选表中那一档即可。  
- Metadata 若界面已锁在 Read-only，无需也无法关掉。  
- **Workflows** 仍保持 No access：Contents Write 已够改普通文件；改 `.github/workflows` 需要另开 Workflows，风险更大，第一期不开。

#### 「能写」但「不能私自合主分支」怎么拆

| 机制 | 作用 |
| --- | --- |
| App：**Contents = Read & write** | 允许往**非保护分支**写提交、推 feature 分支 |
| App：**Pull requests = Read & write** | 允许开 PR、评论；权限位上也能调「合并」API |
| **仓库分支保护**（Settings → Branches） | 对 `main`/`master`：禁止直接 push；要求 PR；要求评审/CI；**不要**把 `xallor-robot` 放进 bypass 名单 |
| **接收端策略**（Plugin / Agent 规则） | 代码层拒绝 `merge` 到默认分支、拒绝 `push` 到 `main`；双保险 |

> [!important] Contents Write ≠ 自动能改主分支
> GitHub App 的 Contents Write 只表示「有写仓库内容的 API 能力」。默认分支是否接得住这次 push / merge，由**分支保护规则**决定。没有保护时，Write 确实可能直接推到 `main`——所以装 App 的仓库务必给默认分支上保护。

#### 第一期明确保持 No access 的（常见项）

这些在 Repository 列表里很容易误开，**全部保持 `No access`**：

| 权限名（常见英文） | 为什么先不开 |
| --- | --- |
| Administration | 改仓库设置、协作者；还可能削弱保护相关配置 |
| Actions | 读/写 workflow 运行；非第一期目标 |
| **Discussions** | 管的是仓库 **Discussions 论坛**（问答/公告帖），**不是** Issue / PR 评论。第一期机器人只走 Issue/PR，保持 `No access`；以后要在 Discussions 里回帖再开 Read/Write，并另订 `discussion` / `discussion_comment` 事件 |
| **Code quality** | 读/写 **代码质量 / 扫描类结果**（质量门禁、相关分析结果），不是 Contents 写文件，也不是普通 PR 评论。第一期不靠它做自动化，保持 `No access`；以后要按质量结论自动评论或改状态再开 Read（或 Write） |
| Secrets / Dependabot secrets / Environments 等 | 密钥与部署环境 |
| Workflows | 改 `.github/workflows`；与 Contents Write 叠加风险大 |
| Deployments / Packages / Pages | 发布与制品面 |
| Members / Single file 等 | 非机器人主路径；需要再单开 |

#### 权限与能力对照（方便自检）

| 你想做的事 | 至少需要 |
| --- | --- |
| 收到 PR 开/改/关事件 | `Pull requests` Read + 订阅 `Pull request` |
| 在 PR / Issue 下发评论、关 Issue | `Issues` **Write**（+ 视情况 `Pull requests` Write） |
| Agent 读仓库里的 md / 代码 | `Contents` Read（已含在 Write 里） |
| 推 feature 分支 / API 改文件 | `Contents` **Write** |
| 开 PR、更新 PR | `Pull requests` Write |
| 读 Actions / Check Run 是否红了 | `Checks` Read（或以后再开 Actions Read） |
| 读旧版 commit status 小点 | `Commit statuses` Read（与 Checks 分开；多数新 CI 可先不开） |
| 机器人自己打 status / Check | `Commit statuses` Write 或 `Checks` Write |
| **阻止私自合入 / 直推主分支** | **不是**关掉 Contents Write；用分支保护 + 禁止 App bypass + 接收端拒合主分支 |

### 订阅事件（Subscribe to events）

在 **Repository permissions** 设好之后，勾选事件。第一期只勾下面两项（名称以页面英文为准）：

- [x] **Pull request**  
- [x] **Issue comment**

其余先不勾。按需再开：

| 事件（页面名） | 何时再勾 |
| --- | --- |
| **Issues** | 要监听开/关 Issue、改标签等，而不只是评论 |
| **Pull request review** / **Pull request review comment** | 要处理 Approve / 行内 Review 评论 |

注意：

- **有权限 ≠ 会推送**：还要 Webhook **Active** + 有效 URL。创建时 Active 关闭也可以先勾事件，等于「就绪清单」。  
- **有事件 ≠ 能回写**：回评论仍依赖上面的 Issues / Pull requests **Write**。  
- `Issue comment` 覆盖 Issue 与多数 PR 时间线评论；行内 diff 评论要另开 review comment 类事件。

### 安装范围（Where can this GitHub App be installed?）

| 选项 | 第一期 |
| --- | --- |
| **Only on this account** | **选这个**（仅 `@xallor-ai`） |
| Any account | 不要选；公开可装会扩大攻击面与支持面 |

与截图一致即可，创建后一般也不改成 Any account。

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
- [ ] Webhook：创建时 Active 关闭；Secret 已用本机命令生成并粘贴（页面无生成按钮），或创建后补填  

- [ ] 只展开并修改 Repository permissions；Org / Account / Enterprise 未改  
- [ ] Contents / Issues / Pull requests = Read & write；Administration、Workflows、Secrets 等 = No access  
- [ ] Checks 仅在需要读 CI 时开 Read-only，否则 No access  
- [ ] 目标仓库默认分支已开保护：禁直推、需 PR；`xallor-robot` 不在 bypass 名单  
- [ ] 事件：勾选 `Pull request` + `Issue comment`；其余先不勾  


- [ ] 安装范围：Only on this account  
- [ ] 创建后保存 App ID、私钥 `.pem`、Webhook secret  
- [ ] Install App 到目标仓库，记下 Installation ID  
- [ ] Plugin 就绪后再打开 Active 并写入真实 Webhook URL  
