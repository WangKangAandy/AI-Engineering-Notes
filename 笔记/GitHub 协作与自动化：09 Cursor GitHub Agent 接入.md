---
title: GitHub 协作与自动化：09 Cursor GitHub Agent 接入
summary: 以 Cursor 为例，说明如何通过现成 GitHub App 接入仓库，并使用 Bugbot、Cloud Agents 与 Automations 完成 PR 审查和任务处理。
tags:
  - cursor
  - github
  - bugbot
  - automation
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：09 Cursor GitHub Agent 接入

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。本篇可在目标仓库的 `lab/09-cursor` 分支记录配置说明；Cursor App 的安装和自动化触发会作用于实际授权的仓库。前置阅读 [[GitHub 协作与自动化：08 GitHub App 注册与权限配置]]，先区分“注册自己的 App”和“安装并使用现成服务的 App”。本篇以 Cursor 为例，讲解第三方 App 接入后的 Agent、审查和自动化。

Cursor 通过官方 GitHub App 访问仓库，提供 PR 审查、Issue 调查和自动化任务。

| 需求 | 使用功能 |
|---|---|
| 自动检查 PR 变更、给出修改建议 | Bugbot |
| 在 Issue 或 PR 中指派调查、修复任务 | Cloud Agents，评论 `@cursor` |
| 根据事件执行自定义任务 | Automations |

## 1. 连接仓库

准备具有目标仓库授权权限的 GitHub 账号，以及可使用所需功能的 Cursor 账号。组织仓库可能需要管理员批准安装。

1. 打开 [Cursor Integrations](https://cursor.com/dashboard/integrations)，在 GitHub 下点击 **Connect**；已连接时选择 **Manage Connections**。
2. 登录 GitHub，完成账号关联。
3. 安装或配置 [Cursor GitHub App](https://github.com/apps/cursor)，选择仓库所属的个人账号或组织。
4. 选择 **Only select repositories**，勾选目标仓库并授权。
5. 返回 Cursor 后台，确认目标仓库可选。

首次 Connect 只关联 GitHub 身份，仍需完成 App 的仓库授权。后续增加仓库时，修改 App 的访问范围即可。[GitHub 集成文档](https://cursor.com/docs/integrations/github)

## 2. 开启 PR 审查

打开 [Automations](https://cursor.com/automations)，进入 **From Cursor → Bugbot**，启用目标仓库并选择自动审查或仅手动触发。连接仓库后 Bugbot 可能已经启用，先检查当前设置。只需要审查时，将 **Autofix** 设为关闭。

在一个有实际变更的 PR 中，由用户发表评论：

```text
cursor review
```

`bugbot run` 也可以触发审查。运行后查看 PR 评论、**Cursor Bugbot** 检查和后台记录；没有发现问题时不一定产生行内评论。机器人账号发布的触发命令会被忽略。

需要统一审查要求时，在仓库中添加 `.cursor/BUGBOT.md`，例如：

```markdown
请使用中文审查。
优先报告影响正确性、安全性和可维护性的实际问题。
每个问题说明位置、触发条件和修改建议。
避免重复评论和纯个人风格偏好。
```

Bugbot 使用专用的 `BUGBOT.md` 规则，不读取 `.cursor/rules/*.mdc` 作为审查规则。审查频率等选项也可通过 `.cursor/config/bugbot.yaml` 管理；该 YAML 从 PR 的目标分支读取。`oncePerPr` 表示每个 PR 自动审查一次；仅手动运行应使用后台对应设置。[Bugbot 文档](https://cursor.com/docs/bugbot)

## 3. 在 Issue 或 PR 中调用 Agent

连接仓库并启用 Cloud Agents 后，在评论中通过 `@cursor` 指派任务。

分析问题：

```text
@cursor 请结合仓库代码分析这个问题，说明原因和解决方案。
```

执行修复：

```text
@cursor 请修复这个问题，补充必要测试，并提交 PR。说明修改内容和测试结果。
```

Agent 在云端环境中工作。需要执行构建或测试时，先在 [Cloud Agents](https://cursor.com/agents) 中配置项目依赖、初始化命令和必要的 Secrets，确保测试命令可运行。[Cloud Agents 文档](https://cursor.com/docs/cloud-agent)

## 4. 配置自定义自动化

在 [Automations](https://cursor.com/automations) 创建任务，设置触发条件、仓库、指令和工具，保存并激活。

例如，创建一条自定义 PR 审查任务：

| 设置 | 示例 |
|---|---|
| 触发条件 | Pull request opened、Pull request pushed |
| 仓库 | 需要审查的仓库 |
| 工具 | Comment on pull request；无需自动审批时关闭审批能力 |
| 指令 | 见下方示例 |

```text
审查本次 PR 的变更，并阅读必要的上下文。
检查正确性、边界条件和测试覆盖，用中文说明有依据的问题。
每条意见包含文件位置、影响和修改建议；避免重复已有评论。
仅发表审查意见，不修改代码或创建 PR。
```

配置后新建或更新一个 PR，在运行记录中确认任务被触发、完成并发表预期结果。自定义审查与 Bugbot 按需要选用，避免两个任务重复检查同一批问题。

Issue 可使用 **Issue label changed** 或 **Issue comment** 事件触发任务，例如添加 `agent-review` 标签后分析问题。创建任务时还需配置可向 Issue 发布结果的工具或集成；PR 评论工具用于 PR。使用评论事件时，应过滤机器人自身的回复，避免重复触发。

当前 Cursor Automations 支持 GitHub 的 PR 打开、更新、合并、评论、标签变化、CI 完成、Issue 评论、PR 评审评论和评审提交等触发器，也支持由 push、定时或 webhook 触发。GitHub 普通 Issue 的“创建”不应按一个已验证的内置触发器来配置；需要监听该事件时，可用 GitHub Actions 的 `issues.opened` 调用 Automation webhook，或使用 Cursor CLI。配置前以 [Automations 触发器文档](https://cursor.com/docs/cloud-agent/automations) 为准。

## 5. 常见问题

| 现象 | 检查项 |
|---|---|
| Cursor 中找不到仓库 | GitHub 身份是否关联；App 是否获准访问该仓库；组织是否批准安装 |
| 提示 installation 已绑定其他 Cursor 账号 | 确认原绑定的账号或团队，在其集成设置中管理该安装；仅切换 GitHub 登录态不会转移绑定 |
| PR 未触发审查 | Bugbot 是否启用、触发模式是否正确、PR 是否为草稿、套餐和用量是否可用 |
| 手动命令无响应 | 命令是否发布在 PR 中，且由用户账号发出；查看后台失败记录 |
| Agent 无法执行测试 | 云端环境是否安装依赖，测试命令和所需 Secrets 是否配置正确 |

Bugbot 和 Cloud Agents 会产生相应使用量。启用自动触发前，在 Cursor 后台确认套餐、可用额度及费用限制；具体计费以当前[官方价格与账号套餐](https://cursor.com/pricing)为准。

## 6. 与系列其他章节的关系

- 第 08 篇讲注册自己的 GitHub App，适合需要自建机器人身份、Webhook 和 API 服务的场景。
- 本篇讲安装并使用 Cursor 提供的现成 App，通常不需要自己生成私钥或实现 Webhook 接收服务。
- 第 06 篇讲 GitHub Agents 页面中的 session；Cursor 的 Cloud Agents、Bugbot 和 Automations 是 Cursor 产品入口，不要因为都含有 Agent 就假定它们共享同一个 Sessions 列表。

验收时分别确认：GitHub App 是否已安装到目标仓库、Cursor 后台是否能选择仓库、PR 事件是否触发预期功能、评论或 PR 是否确实产生。没有实际触发时，只记录配置完成，不记录为运行成功。

返回：[[GitHub 协作与自动化：01 学习路线]]。
