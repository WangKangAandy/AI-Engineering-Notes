---
title: GitHub 协作与自动化：07 gh-aw 与智能自动化
summary: 学习 gh-aw 如何将 Markdown 编译为 Actions 自动化，完成安装准备、报告样例导入、结果检查与停用。
tags:
  - github
  - agents
  - automation
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：07 gh-aw 与智能自动化

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。

> 本篇在当前操作仓库的最新 `master` 上启动向导，由向导创建配置 PR；PR base 必须是同一仓库的 master。fork 实验在自己的 fork 中完成，不将定时报告直接提交到组织默认分支。

本篇是进阶选学。资料核对于 2026-11-17，配置和认证方式应随工具版本复核。

## 1. gh-aw 项目在做什么

`github/gh-aw` 是 GitHub Agentic Workflows 项目。它让你用带 YAML frontmatter 的 Markdown 描述自动化任务，再编译为 GitHub Actions 可执行的 workflow。

```text
Markdown：触发条件、工具与权限、任务要求
    ↓ gh aw compile
生成 .lock.yml：Actions 可执行定义
    ↓ push / schedule / workflow_dispatch 等配置事件
Actions runner 执行 Agent
    ↓
输出报告、Issue、PR 等允许的结果
```

Markdown 源文件和生成的 `.lock.yml` 都需要纳入版本控制。修改生成文件不是维护任务要求的常规入口；应改源文件并重新编译。[GitHub 官方教程](https://docs.github.com/en/actions/tutorials/develop-agentic-workflows-in-github-actions)

## 2. 什么时候用哪种方式

| 需求 | 起点 |
|---|---|
| 每次 PR 都运行固定测试命令 | 普通 Actions workflow |
| 现在请 AI 修复一个具体问题 | Agents 中发起一次 session |
| 定期阅读仓库活动并写有上下文的总结 | Agentic Workflow |
| 新 PR 出现时分析测试覆盖是否充分 | Agentic Workflow 或相应评审产品 |

Agentic Workflow 仍然依赖事件、runner、权限和日志这些基础。它不能替你决定测试是否充分，也不会让外部服务认证自动消失。

## 3. 运行前需要准备什么

在自己的练习仓库尝试一个“仓库活动报告”。该官方样例会创建 Issue，并包含定期执行配置，属于会持续产生记录的自动化。学习时先读配置，练习后按下文停用定时运行。

导入前还要了解一个写入行为：当前样例开启 `safe-outputs.create-issue.close-older-issues: true`。新报告成功创建后，会关闭同一 workflow 以前创建的匹配开放报告 Issue，并添加指向新报告的评论；这个设置不是任意关闭仓库里的其他 Issue。当前实现一次最多关闭 10 条匹配记录。若希望旧报告继续开放，在源 Markdown 中将该项设为 `false`，重新编译并提交后再运行。[样例源码](https://github.com/githubnext/agentics/blob/main/workflows/repo-status.md?plain=1) · [自动关闭范围](https://github.github.com/gh-aw/reference/safe-outputs/#auto-close-older-issues)

准备：仓库写权限、启用 Actions、GitHub CLI，以及所选 AI 引擎的有效认证。官方 quickstart 当前面向 Linux、macOS 或 **Windows + WSL**；Windows 用户本篇命令在 WSL 中运行，并在 WSL 内确认 `gh` 登录和仓库路径，不能假定继承 PowerShell 的认证状态。[官方 Quickstart](https://github.github.com/gh-aw/setup/quick-start/)

### 本例采用 Copilot 的个人令牌认证

本例选择 Copilot 引擎，并使用名为 `COPILOT_GITHUB_TOKEN` 的 repository secret。先确认账号能使用所需 Copilot 能力且有预算；本地 gh 登录用来操作仓库，模型推理认证另行配置。

1. 在 GitHub 个人 Settings → Developer settings → Personal access tokens → Fine-grained tokens 创建令牌，填写用途和合理过期时间。
2. 在 Account permissions 中找到 **Copilot Requests**，设为 **Read**；按当前官方 Copilot 认证要求创建。不要为这个模型凭据额外授予仓库 Contents/Administration 写权限。
3. 复制令牌后，在**当前操作仓库** Settings → Secrets and variables → Actions → Secrets → New repository secret 中填 Name `COPILOT_GITHUB_TOKEN`，Secret 填令牌，保存。不要放在第 05 篇的 github-pages 环境里，否则不引用该环境的报告 job 读不到它。
4. 保存后只能查看名称和更新时间，不能再次读取明文。名称存在只说明已保存，首次运行的认证步骤与模型响应才证明可用。令牌过期或认证失败时更新此 Secret，不把令牌贴到 Issue 或日志。

若创建页面没有该 Account permission 或组织禁止这种凭据，停止这条认证路径并核对资格/政策；有组织集中计费的团队可改用官方的 copilot-requests 路径，但它与此 PAT 方案不同，不能只换 Secret 名称。本文不要求同时配置两种认证。[官方认证路径](https://github.github.com/gh-aw/setup/quick-start/#configuring-authentication)

## 4. 安装与导入样例

如果前面一直在网页练习，现在需要在 WSL 中准备本地仓库。先按 [GitHub CLI 安装说明](https://github.com/cli/cli#installation) 安装适合 WSL 发行版的 `gh`，并确认已安装 Git，然后检查：

```bash
git --version
gh --version
gh auth status
```

如果尚未登录，按官方 quickstart 执行 `gh auth login --scopes repo,workflow` 并完成交互授权。已有登录但向导提示权限不足时，核对登录账号、仓库授权、组织策略及所用凭据权限；“已登录”不代表具备更新 workflow 的权限。[认证前提](https://github.github.com/gh-aw/setup/quick-start/)

如果还没有本地 checkout，有组织仓库权限的成员可以执行：

```bash
git clone https://github.com/xallor-ai/AI-Engineering-Notes.git
cd AI-Engineering-Notes
git switch master
git pull --ff-only
git remote -v
git status
```

已有 checkout 时直接进入它，确认 origin、当前分支和干净的工作区。使用 fork 的读者沿用第 02 篇的 fork checkout；不要又 clone 组织仓库。先确认当前操作仓库已完成前置配置，再安装扩展：

```bash
gh extension install github/gh-aw
gh aw --help
gh repo set-default
gh aw add-wizard githubnext/agentics/repo-status
```

`gh repo set-default` 用于选择 CLI 默认仓库。fork 同时连接上游时，明确选自己的 fork，避免 gh 命令默认作用于组织仓库。

向导会添加 Markdown 源文件及 .lock.yml，并可推送或创建 PR。按以下顺序完成本练习：

1. 确认向导识别的是当前操作仓库；没有组织写权限时应为自己的 fork。引擎选择 Copilot，认证选择 COPILOT_GITHUB_TOKEN 路径并复用刚配置的 Secret；不选择组织计费。
2. 选择通过 PR 引入配置，不选择直接写默认分支；接受向导创建的工作分支，无需预设 `lab/07-gh-aw`。确认 PR 的 base 为该仓库 `master`。
3. 向导创建 PR 后，在评审与合并确认环节暂停：先不确认合并，也不启用自动合并。原样例包含定时触发，仅在后面跳过手动运行不能阻止定时任务生效。
4. 另开终端进入同一 checkout，执行 `git fetch origin`，再 `git switch 分支名`（换成该 PR 的实际来源分支）。在 `.github/workflows/repo-status.md` 中，将整个 `on` 配置改为仅 `workflow_dispatch`，并将 `safe-outputs.create-issue.close-older-issues` 设为 `false`，保留其他必需设置。
5. 执行 `gh aw compile`，检查生成的 .lock.yml 也只有手动触发；将修改后的 .md 和 .lock.yml 提交并推送到该 PR。检查 PR 最新差异和检查结果后，才合并到同一仓库的 `master`。
6. 回到暂停的向导继续完成后续认证和状态步骤，确认使用前述 Copilot Secret；若出现立即运行选项，选择跳过。最后进入 Actions，选择对应报告流程、Run workflow、master，手动触发。向导具体提示随版本变化，必须保持“修改并编译 → 检查 PR → 合并 → 运行”的顺序。[向导生命周期说明](https://github.github.com/gh-aw/setup/cli/#add-wizard)


源文件是 `.github/workflows/repo-status.md`，编译结果为 `.github/workflows/repo-status.lock.yml`。保存源文件后，在当前 PR 分支的仓库根目录执行：

```bash
gh aw compile
git diff -- .github/workflows/repo-status.md .github/workflows/repo-status.lock.yml
git add .github/workflows/repo-status.md .github/workflows/repo-status.lock.yml
git commit -m "chore: make repo status report manual"
git push
```

若向导另有辅助文件，分别确认用途和差异；不要把整个工作区无差别加入提交。`git push` 的 upstream 应是向导 PR 的来源分支，先用 `git status -sb` 核对。若当前来源分支尚未设置 upstream，确认 origin 是本次 PR 所在仓库后用 `git push -u origin HEAD` 建立跟踪，不向 master 直推。

`on` 的替换片段位于 Markdown 文件的 YAML frontmatter 中，不是独立 workflow：

```yaml
on:
  workflow_dispatch:
```

向导也可能添加辅助文件，提交前逐项检查。认证和 Secrets 属于仓库配置，不会因为 PR 尚未合并就自动撤销。[官方样例流程](https://github.github.com/gh-aw/setup/quick-start/)

### 读懂导入的源文件

| 源文件部分 | 本例检查什么 |
| --- | --- |
| on | 仅保留 workflow_dispatch，没有 schedule |
| engine | 向导所选 Copilot；以当前生成文件的引擎表示为准 |
| permissions | 读取仓库活动所需的 GitHub 权限，不等于模型账号资格 |
| tools | Agent 可调用的工具范围，不能由任务正文随意增加权限 |
| safe-outputs.create-issue | 允许把报告写成 Issue；close-older-issues 为 false |
| frontmatter 后的 Markdown | 给 Agent 的任务要求，例如总结范围、语言、引用链接 |

源文件中的读取权限与最终写 Issue 不应只看一行判断；gh-aw 会编译出受控输出处理步骤。检查生成的 workflow 和运行日志，确认写入的是本仓库的报告 Issue。正文中文要求可以改，编译产物不作为手写任务的维护入口。

## 5. 认证与权限分别解决什么

| 配置 | 回答的问题 |
|---|---|
| AI 引擎认证 | 以谁的身份调用模型，使用谁的 AI 额度 |
| GitHub token 权限 | 自动化可以读取或修改哪些仓库对象 |
| 工具和输出限制 | Agent 可以使用哪些工具、提交哪些结果 |

认证方式随引擎和组织配置变化。跟随当前向导及对应引擎文档，不把个人电脑上“能聊天”视为 runner 已认证，也不把账户订阅与 API 凭据当作同一回事。

需要密钥时放入 GitHub Actions Secrets，不放入 Markdown 或提交历史。普通 CI 练习使用 `pull_request`；不要为了获得密钥而直接改成 `pull_request_target` 并执行外部 PR 的代码，因为后者处于更高信任的仓库上下文。[事件权限说明](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)

## 6. 从运行结果回到配置

打开 Actions，选择生成的报告流程，查看最近一次 run；也可以在仓库目录执行：

```bash
gh aw status
gh run watch
```

打开该 run，先区分失败发生在配置/认证、Agent 执行还是输出阶段：401/403 先检查 Secret 名称、过期时间、Copilot 权限与政策；模型步骤成功但没有报告时，看受控输出处理步骤是否成功以及是否允许 create-issue。不要只重复运行整个流程。

完成后查看 Issues 中新出现的报告，抽查其引用的 PR、Issue 或提交是否存在，是否正确反映仓库活动。run 成功说明流程完成，并不能替代对报告内容的核查。

可以在样例 Markdown 的任务正文中补充自己的要求，例如：只总结最近的 PR；使用中文；每条结论附相关链接；没有活动就直接说明。

修改后，在练习仓库运行：

```bash
gh aw compile
git diff
```

检查源码与生成文件的差异，提交这两个文件并通过适用流程送入远端。然后使用生成的 workflow 的手动运行入口，或按当前版本 CLI 帮助执行手动运行。frontmatter 修改后必须重新编译；统一在修改后编译可以避免漏掉配置变化。

## 7. 用完如何停下来

在 Actions 中选择该 workflow，从菜单中禁用，可以阻止后续触发。若要长期保留手动练习，则在 Markdown 的触发配置中移除定时事件、保留手动事件，重新编译并提交源文件和生成文件。

**禁用 workflow 不会取消已经存在的 run。** 要立即停止当前执行，还需打开那次运行并选择取消。禁用期间也不能重新运行已有 run 或其中的 job，需要先重新启用。[禁用与启用说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)

本例已经移除定时事件，后续只有手动触发。若以后恢复 schedule，仅关闭报告 Issue 不会停止后续运行。实验彻底结束且没有其他流程使用此令牌时，可删除仓库 Secret，并在个人令牌设置中撤销对应 PAT。

## 8. 在哪里查看各阶段的结果

到这里，仓库里会出现几类不同的记录。排查问题时，先找到对应阶段的记录，而不是只看最后一个绿色状态：

| 记录 | 可以回答的问题 |
|---|---|
| 一个需求 Issue | 希望改变什么，验收条件是什么 |
| 一个手工 PR | 代码来源与目标分支 |
| 一次失败和一次通过的 CI | 失败原因及修复提交 |
| 一次 Pages 部署 | 哪个提交生成了当前网页 |
| 一次 Agent session 和 PR | 委派要求、修改范围、验证结果 |
| 可选的一次 Agentic Workflow | 什么事件触发、运行在哪、写入什么结果、如何停用 |

这些记录把配置文件、触发事件、执行过程和最终产物连接起来。Workflow run 成功表示流程执行结束，报告内容仍需核对其引用的 Issue、PR 和提交。

下一篇：[[GitHub 协作与自动化：08 GitHub App 注册与权限配置]]，学习自建服务的仓库授权和接入。
