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

学习路线：[[GitHub 协作与自动化：01 学习路线]]。Cursor App 的安装和自动化触发会作用于实际授权的仓库。前置阅读 [[GitHub 协作与自动化：08 GitHub App 注册与权限配置]]，先区分“注册自己的 App”和“安装并使用现成服务的 App”。本篇以 Cursor 为例，讲解第三方 App 接入后的 Agent、审查和自动化。

Cursor 通过官方 GitHub App 访问仓库，提供 PR 审查、Issue 调查和自动化任务。

| 需求 | 使用功能 |
|---|---|
| 自动检查 PR 变更、给出修改建议 | Bugbot |
| 在 Issue 或 PR 中指派调查、修复任务 | Cloud Agents，评论 `@cursor` |
| 根据事件执行自定义任务 | Automations |

## 1. 连接仓库

准备具有目标仓库授权权限的 GitHub 账号，以及可使用所需功能的 Cursor 账号。组织集成按 Cursor 文档要求由具备 Cursor 管理权限和 GitHub 组织管理权限的人员配置；普通仓库写权限不等于可管理组织集成。

1. 打开 [Cursor Integrations](https://cursor.com/dashboard/integrations)，在 GitHub 下点击 **Connect**；已连接时选择 **Manage Connections**。
2. 登录 GitHub，完成账号关联。
3. 安装或配置 [Cursor GitHub App](https://github.com/apps/cursor)，选择仓库所属的个人账号或组织。
4. 选择 **Only select repositories**，勾选目标仓库并授权。
5. 返回 Cursor 后台，确认目标仓库可选。

首次 Connect 只关联 GitHub 身份，仍需完成 App 的仓库授权。后续增加仓库时，修改 App 的访问范围即可。[GitHub 集成文档](https://cursor.com/docs/integrations/github)

启用之前，在 Cursor 后台查看当前账号/团队的套餐、使用量与预算限制。本篇会产生审查或 Cloud Agent 用量，App 安装成功不表示包含无限运行额度。以下所有操作选当前实验仓库，fork 的结果不计为组织仓库验证。

## 2. 开启 PR 审查

打开 [Automations](https://cursor.com/automations)，进入 **From Cursor → Bugbot**，启用目标仓库并选择自动审查或仅手动触发。连接仓库后 Bugbot 可能已经启用，先检查当前设置。只需要审查时，将 **Autofix** 设为关闭。

先从最新 master 创建 `lab/09-review`，在第 02 篇的实操记录中补一句本次想检查的问题，提交并创建面向 master 的普通 PR，暂不合并。Bugbot 本次选择仅手动触发，并关闭 Autofix。在这个有实际变更的 PR 中，由用户发表评论：

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

### 先让云端环境能够运行本仓库的检查

复用第 04 篇已合入 master 的三个 Python 文件；不依赖第 06 篇是否已修改 greeting。本次选择 Cursor 托管的 Cloud Agents，不选择自托管机器。

1. 打开 [Cloud Agents](https://cursor.com/agents)，进入新环境的引导式配置入口，选择当前实验仓库，仅选这一个仓库。
2. 选择让 Agent 帮助配置环境的方式。在设置说明中填写下方要求，观察共享终端中的安装与检查过程。
3. 本例只用 Python 标准库，没有 API、数据库或私有包，不添加 Secrets。需要真实服务凭据的项目以后在 Cursor 的 Secrets 设置中配置，它不会自动读取 GitHub Actions Secrets。
4. 等待环境验证和 Build 成功，在环境配置页确认当前 active Build。找不到 Python 或检查失败时先修复环境并重新 Build，不开始后面的代码任务。

```text
为当前仓库准备 Python 3.12 环境。仓库根目录已有 app.py、test_app.py 和 build.py，只使用标准库，不需要安装 pip 依赖或添加密钥。
在仓库根目录执行 python --version、python -m unittest discover -v、python build.py。
若 python 命令不可用，先准备解释器；不要通过修改测试来使环境验证通过。
说明实际使用的版本、测试数量及构建结果。仅设置执行环境，不修改或合并仓库代码。
```

此时测试数量取决于是否已完成第 06 篇，至少应包含原有三个测试，不能把“运行了零个测试”当成功。build.py 应生成 site/index.html。Cursor 的保存环境及 Build 会供后续任务使用；若项目已有个人或团队环境，先确认选中的正是刚配置的环境，避免配置了一个却运行另一个。[官方环境配置](https://cursor.com/docs/cloud-agent/setup)

### 用一个 Issue 发起任务

在当前仓库新建 Issue“补充 greeting 的中文名字测试”，正文写清：在 test_app.py 新增 `greeting("世界") == "Hello, 世界!"` 的测试，不改变实现或 workflow。由已关联且有权限的用户在 Issue 中评论：

```text
@cursor 请处理本 Issue：以 master 为基础，新建工作分支，只在 test_app.py 增加中文名字“世界”的测试；已有相同测试时说明，无需重复添加。运行 python -m unittest discover -v 和 python build.py，创建面向 master 的 PR，不要合并。返回实际命令、测试数量和结果。
```

点击机器人回复中的任务链接，进入 Cursor 查看日志和 diff；从任务结果打开 PR，确认只包含预期测试，再检查 GitHub 的 CI。机器人没有回复时，先核对评论账号关联、App 仓库访问范围、Cloud Agents 资格和用量，不用连续发相同命令。若任务没有使用预期环境，在 Cursor 的任务/环境设置中核对当前仓库绑定并重新发起一次明确任务。

CI 通过后再按仓库规则合并。若保留 Pages 审批，它会因 master 更新而再次等待上线批准；本次只新增测试，可以在判断后取消不需要的部署。停止代码任务使用 Cursor 任务详情中的停止操作，随后检查是否已有提交/PR；关闭 Issue 不等于停止云端任务。[GitHub 集成](https://cursor.com/docs/integrations/github)

## 4. 配置自定义自动化

本节单独配置“新 PR 打开时，用中文检查变更并发表一条摘要”，不使用 Issue 事件，也不与 Bugbot 同时自动审查。先保持 Bugbot 为仅手动模式，并使用前面能运行测试的实验仓库环境。

1. 打开 [Automations](https://cursor.com/automations)，创建自己的自定义 automation，不进入 From Cursor → Bugbot。
2. 名称填写“实验仓库 PR 中文审查”，配置如下表；保存前再次核对仓库和执行身份。团队若显示 Run as，本例使用自己的身份，不切换团队服务账号。
3. 填入下方指令，保存并激活。记录该 automation 的页面链接，以便查看运行与停用。
4. 激活之后，从最新 master 创建 `lab/09-automation`，修改实操记录中的一段说明并提交，创建**非 Draft** PR。已经打开的旧 PR 不会因为新建 automation 自动补触发。
5. 回到此 automation 的运行列表，打开关联这个 PR 的运行，检查触发事件、仓库、执行日志和最终状态，再到 PR Conversation 查找摘要评论。

| 字段 | 本例值 |
| --- | --- |
| Trigger | Pull request opened，仅选择此事件 |
| Repository | 当前实验仓库；fork 用户选自己的 fork |
| Tools | Comment on pull request；不启用审批工具 |
| Prompt | 下方指令，约束只审查和评论 |
| 执行环境 | 当前仓库已验证可用的环境；有选择器时核对，不跨仓库复用凭据 |

```text
审查触发本任务的 PR，读取 diff 和必要上下文。
用中文在该 PR 的时间线发表一条摘要评论：说明检查范围、发现的问题，以及没有执行的验证；没有实质问题时也明确说明，而不是不输出。
问题须说明位置、影响和依据。不要重复已有评论；如果已有本次运行的摘要，不再添加第二条。
只读代码并评论，不修改代码、不创建 PR、不批准、不合并。
```

本例使用 opened 事件，所以只推送新提交不会再次触发；这是预期行为。若确需每次 PR 更新都检查，再添加 Pull request pushed，并考虑重复评论和额外用量。没有运行记录先查是否激活、仓库是否正确、PR 是否为草稿以及事件是否匹配；有运行但无评论时，查任务失败原因、评论工具是否启用及 App 是否有 PR 写权限。一次绿色运行不能代替检查实际评论内容。

评论事件、Issue 事件和 webhook 属于后续扩展，输出到 Issue 时需要适合 Issue 的工具，不能沿用 PR 评论工具。此处不把未完成配置的扩展列为已会使用的能力。[官方创建步骤与触发器](https://cursor.com/docs/cloud-agent/automations)

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

GitHub App 安装成功后，Cursor 后台应能选择获授权的仓库。提交或更新 PR 后，再到对应功能的运行记录查看触发状态和结果：仓库可选表示连接已建立，实际出现的审查、检查或新 PR 才能说明任务执行到了哪一步。

返回：[[GitHub 协作与自动化：01 学习路线]]。

## 7. 停止练习

先处理 `lab/09-review` 和 `lab/09-automation` 的实验 PR：有保留价值的改动经检查后合并，其余关闭；这不会删除已发表的评论。

在 Cursor Automations 中停用本次自定义任务，并关闭目标仓库的 Bugbot 自动审查或改为仅手动。检查并单独停止仍在运行的 Cloud Agent 任务；关闭 PR 不等于停止所有自动化。若不再需要仓库连接，在 GitHub Installed GitHub Apps 中移除该仓库的授权，或暂停/卸载 Cursor App。先确认没有其他团队任务依赖这次安装。用户身份授权可在 Authorized GitHub Apps 单独撤销。[GitHub App 管理](https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps)
