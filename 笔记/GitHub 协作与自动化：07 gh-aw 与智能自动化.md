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

> 本篇实验基线：`docs/github-agent-channel-architecture`；实验分支：`lab/07-gh-aw`。本篇的新增文件和提交都在该实验分支完成，再按文中的 PR 步骤合并或关闭。前置：能读懂 [[GitHub 协作与自动化：03 Actions 与 Workflow]]，理解 [[GitHub 协作与自动化：06 Agents 与任务委派]]。

本篇是进阶选学。资料核对于 2026-11-16，配置和认证方式应随工具版本复核。

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

## 3. 本次练习的前提

在自己的练习仓库尝试一个“仓库活动报告”。该官方样例会创建 Issue，并包含定期执行配置，属于会持续产生记录的自动化。学习时先读配置，练习后按下文停用定时运行。

导入前还要了解一个写入行为：当前样例开启 `safe-outputs.create-issue.close-older-issues: true`。新报告成功创建后，会关闭同一 workflow 以前创建的匹配开放报告 Issue，并添加指向新报告的评论；这个设置不是任意关闭仓库里的其他 Issue。当前实现一次最多关闭 10 条匹配记录。若希望旧报告继续开放，在源 Markdown 中将该项设为 `false`，重新编译并提交后再运行。[样例源码](https://github.com/githubnext/agentics/blob/main/workflows/repo-status.md?plain=1) · [自动关闭范围](https://github.github.com/gh-aw/reference/safe-outputs/#auto-close-older-issues)

准备：仓库写权限、启用 Actions、GitHub CLI，以及所选 AI 引擎的有效认证。官方 quickstart 当前面向 Linux、macOS 或 **Windows + WSL**；Windows 用户本篇命令在 WSL 中运行，并在 WSL 内确认 `gh` 登录和仓库路径，不能假定继承 PowerShell 的认证状态。[官方 Quickstart](https://github.github.com/gh-aw/setup/quick-start/)

## 4. 安装与导入样例

如果前面一直在网页练习，现在需要在 WSL 中准备本地仓库。先按 [GitHub CLI 安装说明](https://github.com/cli/cli#installation) 安装适合 WSL 发行版的 `gh`，并确认已安装 Git，然后检查：

```bash
git --version
gh --version
gh auth status
```

如果尚未登录，按官方 quickstart 执行 `gh auth login --scopes repo,workflow` 并完成交互授权。已有登录但向导提示权限不足时，核对登录账号、仓库授权、组织策略及所用凭据权限；“已登录”不代表具备更新 workflow 的权限。[认证前提](https://github.github.com/gh-aw/setup/quick-start/)

在准备存放练习仓库的目录执行以下命令。本篇使用已核对过的 fork 和分支，不再替换占位符：

```bash
git clone https://github.com/xallor-ai/AI-Engineering-Notes.git AI-Engineering-Notes
# 如果组织仓库已经同步测试分支，再执行：
# git switch docs/github-agent-channel-architecture
cd AI-Engineering-Notes
git remote -v
git status
```

已有可用 checkout 时直接进入它，不需要再次 clone；确认远程地址是 `xallor-ai/AI-Engineering-Notes`，并根据第 01 篇选择 `master` 或已同步的 `docs/github-agent-channel-architecture`，工作区的既有修改已妥善处理。随后安装扩展：[克隆命令说明](https://cli.github.com/manual/gh_repo_clone)

```bash
gh extension install github/gh-aw
gh aw --help
```

然后使用官方示例向导：

```bash
gh aw add-wizard githubnext/agentics/repo-status
```

向导负责检查条件、选择引擎、配置认证、添加 Markdown 和生成文件，并可提交到仓库或通过 PR 引入，以及可选立即运行。它包含远端写入步骤；确认目标是自己的练习仓库，阅读向导摘要后选择适合的提交方式。看到日程配置时明确这会定期触发，练习后需要停用。

该样例会总结仓库活动、新建报告 Issue，并按第 3 节所述配置关闭匹配的旧报告。若要调整自动关闭或定时行为，跳过向导的立即运行选项，通过 PR 检查并修改配置、重新编译后再合并启用。向导操作、文件类型和预期输出依据 [官方样例流程](https://github.github.com/gh-aw/setup/quick-start/)。

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

完成后查看 Issues 中的报告，抽查其引用的 PR、Issue 或提交是否存在，是否正确反映仓库活动。run 成功说明流程完成，并不能替代对报告内容的核查。

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

仅关闭已生成的报告 Issue，不会停止下一次定时运行。

## 8. 最后的综合练习

回到 [[GitHub 协作与自动化：01 学习路线]]，用自己的练习仓库完成以下记录：

| 结果 | 要能解释的内容 |
|---|---|
| 一个需求 Issue | 希望改变什么，验收条件是什么 |
| 一个手工 PR | 代码来源与目标分支 |
| 一次失败和一次通过的 CI | 失败原因及修复提交 |
| 一次 Pages 部署 | 哪个提交生成了当前网页 |
| 一次 Agent session 和 PR | 委派要求、修改范围、验证结果 |
| 可选的一次 Agentic Workflow | 什么事件触发、运行在哪、写入什么结果、如何停用 |

做到这些，就能在一个陌生仓库里沿着“配置文件 → 触发事件 → 执行记录 → 检查或产物 → 合并或部署”查清流程，再逐步学习 matrix、复用 workflow、包发布和更多自动化。

下一篇：[[GitHub 协作与自动化：08 GitHub App 注册与权限配置]]，学习自建服务的仓库授权和接入。
