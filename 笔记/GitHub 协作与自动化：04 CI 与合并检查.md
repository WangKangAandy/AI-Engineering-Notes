---
title: 现代 GitHub：用 CI 和合并门禁保护修改
summary: 把资源清单校验、测试和构建接入 CI，经历失败、门禁阻止、修复和合并，理解绿灯能证明什么。
tags:
  - github
  - actions
created: 2026-11-16
status: learning
---

# 现代 GitHub：用 CI 和合并门禁保护修改

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 14 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<GitHub 协作与自动化：03 Actions 与 Workflow.md>) · [下一章](<现代 GitHub：保存和传递一次运行的结果.md>)

前一章已经让 Actions 响应仓库事件，现在让它执行第 12 章的三条真实命令。本章继续操作自己的 `YOUR_LOGIN/resource-nav`，默认分支 `main`，终端为 PowerShell 7；程序和有效清单已合入 main。第 13 章的 hello.yml 可以保留，它不是本章必需检查。

CI（持续集成）让每次变更接受重复检查。检查的范围仍由我们编写：校验当前 CSV、测试程序行为、构建页面。单元测试使用自己的样例，因此即使九项测试全部通过，也不能替代对当前 resources.csv 的校验。构建成功也只说明生成文件成功，不说明网页已经发布或所有外部链接都能访问。

## 先让真实检查出现

在自己的 resource-nav 根目录确认 `git status --short` 没有未完成工作，再逐条执行；某条失败就停止处理原因，不继续创建或推送分支：

```powershell
git switch main
git pull --ff-only
git switch -c lab/14-ci
```

新建 `.github/workflows/ci.yml`，完整内容如下：

```yaml
name: Resource CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  check:
    name: Check resources
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Validate catalog
        run: python catalog.py resources.csv
      - name: Run tests
        run: python -m unittest discover -v
      - name: Build site
        run: python build.py

```

`Resource CI` 是流程名，`check` 是 job ID，`Check resources` 是显示名称，后面设置门禁时选择实际产生的检查项。三个 run 分开写，是为了在日志中直接定位数据校验、测试或构建哪一步失败。默认情况下前一步失败，后续普通步骤跳过；不要给它们加 `continue-on-error` 来制造绿灯。

Ubuntu runner 与本机 Windows 不同，但两边选用 Python 3.12 和相同程序。本例只有标准库，所以无需 pip install，也不需要凭据。[setup-python 用法](https://github.com/actions/setup-python) · [Workflow 语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)

如果仓库已有第 10 章创建的 `CONTRIBUTING.md`，先编辑其中的验证方法，保留人工核对资源来源、用途和分类，并补上 `py -3.12 catalog.py resources.csv`、`py -3.12 -m unittest discover -v`、`py -3.12 build.py`；同时写明 启用必需检查规则后，PR 当前提交的 **Check resources** 必须通过才能合并。把这次指南更新和 workflow 一起加入本章 PR。若文件尚未存在，在 PR 描述中记录待办，完成第 10 章后再写入。

本地先按第 12 章用 `py -3.12` 依次校验、测试、构建，再检查并提交：

```powershell
git diff --check
if (Test-Path -LiteralPath CONTRIBUTING.md) { git add -- CONTRIBUTING.md }
git add .github/workflows/ci.yml
git diff --staged
git commit -m "ci: validate test and build resource catalog"
git push -u origin lab/14-ci
gh pr create --repo YOUR_LOGIN/resource-nav --base main --head lab/14-ci --title "Add resource CI" --body "Validate resources.csv, run unit tests, and build the static page."
```

把命令中的 YOUR_LOGIN 换成自己的账号。打开这个 PR 的 Checks，进入 **Check resources**，检查真实清单的条数、九项测试及 `Built site/index.html`。条数取决于前面加入了多少资源，不硬编码为两条。确认通过后合并初始化 PR，再从 main 拉取更新。不能把本地 YAML 能解析当成 Actions 已成功运行。

## 制造一次可解释的失败

从更新后的 main 新建 `lab/14-break-ci`。用编辑器做两项修改：

1. README.md 增加真实说明：“本仓库通过 CI 校验资源清单、运行单元测试并生成静态页面。”
2. resources.csv 中任意选一条有效记录，完整复制到文件末尾，故意产生重复 URL。

保留 README 改动有实际用途：修复重复行后，PR 仍有一项应该合并的说明更新。不要改校验程序来容忍重复，也不要删测试。

本地运行 `py -3.12 catalog.py resources.csv`，应出现 `duplicate URL`；紧接着运行 `$LASTEXITCODE` 应得到 1。确认 diff 只有上述改动后提交、推送，并创建面向 main 的 PR：

```powershell
git add README.md resources.csv
git diff --staged
git commit -m "docs: explain CI and demonstrate invalid catalog"
git push -u origin lab/14-break-ci
gh pr create --repo YOUR_LOGIN/resource-nav --base main --head lab/14-break-ci --title "Explain CI and exercise its failure gate" --body "Keep this PR open while observing the duplicate URL failure; remove the deliberate duplicate before merging."
```

在 PR 中找到新 run。预期 **Validate catalog** 失败，测试和构建步骤跳过。这里不是“九项单测失败”，而是当前输入在第一关就不合格。先保持红灯和打开的 PR，继续设置门禁。

## 把检查结果变成合并条件

检查结果与必须通过是两件事。管理员可以在 Settings → Rules → Rulesets 创建 branch ruleset。公开仓库在 GitHub Free 可使用 ruleset；私有仓库的可用性取决于套餐，组织还可能有额外策略。没有管理权限或当前套餐不支持时，记录“只观察到检查，尚未验证强制门禁”，不要声称失败已阻止合并。[Rulesets 可用条件](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)

在支持的个人练习仓库中设置：

1. 命名规则，例如 `Protect main`；Enforcement status 设为 **Active**。
2. Target branches 明确包含 `main`，确认没有排除它。
3. 启用 **Require a pull request before merging**。个人独自练习把 required approvals 设为 **0**，否则无法用自己的批准满足他人评审条件。
4. 启用 **Require status checks to pass**，从真实运行记录选择 **Check resources**。不要填 workflow 名 Resource CI、文件名 ci.yml 或 job ID check。
5. Bypass list 不添加自己的练习账号或管理员角色。保存后重新检查目标和启用状态。

回到仍然失败的 PR，确认当前提交的 Check resources 未通过，并观察普通合并被阻止的具体说明。若仍能直接合并，检查规则是否 Active、目标是否 main、账号是否绕过规则，以及选中的是否为真实检查。管理员可绕过的入口不等于检查通过。[必需检查规则](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)

此时才回到同一来源分支，删除刚复制的错误行，保留 README 说明；运行三条本地命令，检查 diff，提交修复并 push。新提交应触发新 run，不是重跑旧错误提交。等待新检查通过，再确认原先由 Check resources 造成的阻止已经解除。其他规则也满足时，正常合并 PR。

## 红灯消失后仍要看证据

PR 默认 checkout 通常检出平台生成的测试合并提交，用于检查目标分支与来源分支组合后的状态。因此 PR run 的 SHA 可能不是来源分支最新提交 SHA；合并后的 push run 又对应 main 的提交。[checkout 的 PR 行为](https://github.com/actions/checkout)

检查一直 pending 时，先看流程是否真的被触发、分支/路径过滤是否排除了这次变更，以及检查名称是否被改过。必需检查名称也是协作契约：后面章节保留 **Check resources**，避免规则等待一个再也不会出现的名字。不要用跳过、放宽规则或忽略失败来代替定位原因。

把失败 run、修复 run 和 PR 的地址记在自己的学习记录中，分别写清事件、提交、首次失败步骤和合并阻止原因。本章完成的证据链是：有效程序已入 main → 重复输入触发失败 → 规则阻止当前 PR → 新提交移除错误 → 最新检查通过 → PR 合并。只有前半段时，就只报告前半段；绿灯不代表没有未覆盖的缺陷。
