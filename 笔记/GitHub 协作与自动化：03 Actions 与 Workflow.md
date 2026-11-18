---
title: GitHub 协作与自动化：03 Actions 与 Workflow
summary: 运行第一个 Actions workflow，理解事件、run、job、step 和 runner，以及任务依赖和执行边界。
tags:
  - github
  - actions
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：03 Actions 与 Workflow

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。

> 本篇实验基线：`master`；实验分支：`lab/03-actions`。先按第 02 篇的方法从最新 master 创建该分支；完成本篇所需的 PR 合并后再进入依赖它的下一篇。前置：能编辑练习仓库并通过 PR 合并。本篇先运行一句话，建立“配置 → 触发 → 执行 → 日志”的对应关系。

## 1. 从页面对应到对象

```text
Actions 平台
  workflow：一份流程定义
    run：这份定义的一次执行
      job：分配给 runner 的任务
        step：命令或可复用 action
```

一个 workflow 可以有多个 run。重新运行失败任务仍然属于执行记录和尝试次数的问题，不是创建新的流程定义。日志排查时先确定提交、事件和 run，再看 job 和 step。

**Job 是一组交给 runner 执行的步骤。** 例如“测试并构建”可以是一个 job，里面先获取代码、准备 Python，再执行测试和构建命令；也可以将测试和构建拆成两个 job，并用依赖关系连接。

## 2. 创建最小流程

在练习仓库新增 `.github/workflows/hello.yml`，通过 PR 合并到默认分支：

```yaml
name: Hello Actions

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Print a message
        run: echo "Hello from GitHub Actions"
```

逐行理解：`name` 是列表中的流程名；`on` 声明触发条件；`workflow_dispatch` 提供手动运行入口；`jobs.hello` 定义一个任务；`runs-on` 选择执行环境；`run` 执行命令。这里运行在 Ubuntu 上，本机使用 Windows 不影响它。

`permissions` 控制本次自动化所用 GitHub token 的权限，本例仅允许读取仓库内容。打印文字不需要 checkout，所以只有一个步骤。

完整语法以 [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) 为准。

## 3. 运行并查看日志

1. 打开仓库 Actions 页，在左侧找到 **Hello Actions**。
2. 点击 **Run workflow**，选择 `master`，再运行。
3. 打开新增的运行记录，找到 `hello` job。
4. 展开 **Print a message**，找到输出文字。
5. 记录这次运行的触发方式、分支、提交及结果。

手动运行要求 workflow 已存在于默认分支，并具有 `workflow_dispatch`；操作人也需要仓库写权限。只有分支中的新文件时，先合并再找入口。[手动执行说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)

## 4. `run` 和 `uses` 的区别

第一次 PR 已经合并。现在从更新后的 master 新建 `lab/03-actions-events`；本节和下一节都在这个新分支编辑 hello.yml，完成后创建第二个 PR。不要复用已经删除的旧分支。

`run` 写你要执行的命令；`uses` 引用可复用组件。要读取仓库中的文件，可以在原来的打印步骤前加：

```yaml
      - name: Get repository files
        uses: actions/checkout@v7
      - name: List files
        run: ls -la
```

这段是 `steps` 下的插入片段，不是独立 workflow。`actions/checkout@v7` 中前半部分是 action 仓库，`@v7` 是版本引用。本例采用 GitHub 托管 runner；该版本的用法和环境要求见上游 README。组织生产流程可按自身要求固定到审核过的完整 commit SHA。[checkout 官方仓库](https://github.com/actions/checkout)

## 5. 把手动触发改为事件触发

将前例的整个 `on` 部分替换为：

```yaml
on:
  workflow_dispatch:
  push:
    branches: [master]
  pull_request:
    branches: [master]
```

现在有三种入口：手动运行、推送到 `master`、指向该分支的 PR 发生受支持的变动。`pull_request.branches` 筛选的是 PR 的目标分支；更新 PR 来源分支通常会引起一次新检查。

在 PR 阶段和合并后各运行一次很常见：前者检查待合并变更，后者检查主分支的新状态。触发行为以 [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) 为准。

将 checkout、List files 和新的 on 配置一起提交，创建面向 master 的 PR。在 PR 的 Checks 中打开 Hello Actions：事件应为 pull_request，日志能列出仓库文件。再把打印文字改成另一句话并提交到同一来源分支，新 run 应显示新文字。

检查通过后合并 PR，回到 Actions 找到 push 事件的运行。打开运行详情，对比触发事件、提交和日志：PR 运行用于检查待合并改动，push 运行对应合并后的 master。两者可能使用不同 SHA；PR 的默认 checkout 通常是测试合并提交。最后从 Run workflow 选择 master 再运行一次，事件应为 workflow_dispatch。

## 6. 并行和依赖

独立的 job 可以并行执行；有顺序要求时使用 `needs`。例如：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test placeholder"
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: echo "build placeholder"
```

这是结构示意，不是真实测试。`build` 默认等待 `test` 成功；不同 job 不应假设共享工作目录，需要重新 checkout，或使用 artifact 传递文件。

### Job 的执行边界

| 范围 | 默认共享或保留什么 | 不要作什么假设 |
|---|---|---|
| 同一 job 的 steps | 默认依次执行，共享 runner 的工作区；前一步生成的文件可供后一步读取 | 不是每个 step 都自动拿到全新的文件系统 |
| 不同的 `run` 步骤 | 工作区中的文件可保留 | 每个 `run` 启动新的进程和 shell，前一步的普通 `export` 或 `cd` 不会自动延续 |
| 不同 job | 可以通过明确声明的机制交换数据 | `needs` 只建立依赖，不会自动复制文件或环境变量 |

例如前一个 step 执行 `export MODE=test`，后一个 step 不能据此假定 `$MODE` 已设置。固定环境变量可用 `env`；运行时为后续 steps 设置变量可写入 `GITHUB_ENV`。传递跨 job 的小型结果用 job outputs，传递构建包等文件用 artifact。[步骤执行语义](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsrun) · [环境文件](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#environment-files)

### Job ID 和显示名称

后续 CI 示例中的 `jobs.test-and-build` 定义 job ID `test-and-build`，其 `name: Test and build` 是显示名称。`needs` 引用 ID，Actions 页面和必需检查设置中通常看到显示名称。配置合并规则时，选择实际运行产生的检查项，而不是凭文件名猜测。

部署 job 即使写了 `needs: build`，也不能直接读取另一个 job 的 `site/`。后续 Pages 示例先上传 artifact，再由部署步骤获取产物；依赖顺序和文件传递需要分别配置。

## 7. 流程变复杂后会用到的功能

| 功能 | 解决什么问题 |
|---|---|
| matrix | 用多种 Python 版本或操作系统运行同一套检查 |
| cache | 复用可重新生成的依赖等内容，减少重复下载 |
| artifact | 保存报告、安装包等本次执行的输出 |
| reusable workflow | 多个流程或仓库复用整套任务 |
| concurrency | 管理同组运行，避免过期任务同时部署 |
| secrets / variables | 为任务提供敏感凭据 / 普通配置 |

缓存丢失应只影响速度；artifact 是明确要保留或传递的结果。[Artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts) · [Caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)

## 8. 身份、权限、配置和执行环境

这些词回答不同的问题：谁在操作、允许做什么、输入什么配置、在哪里执行。不要把 GitHub 登录、Actions 身份和第三方 Agent 账号视为一个身份。

| 对象 | 作用与配置位置 |
| --- | --- |
| GITHUB_TOKEN | GitHub 为 job 提供的临时仓库凭据，通常无需手工创建；workflow 的 permissions 调整其可用权限 |
| PAT | 用户创建的个人访问令牌；由使用它的工具决定所需权限，第 07 篇给出具体案例 |
| GitHub App installation token | 以某次 App 安装身份调用 API；由 App 服务换取，第 08 篇区分其与私钥 |
| Secrets | 保存敏感输入，可在仓库、组织或部署环境级配置；不会自动授予凭据本身没有的权限 |
| Variables / env | Variables 是 GitHub 保存的非敏感配置，通过 vars 引用；env 把值提供给步骤进程 |
| 部署 Environment | job 引用的发布规则与配置集合，可要求审批、限制分支，不是运行程序的服务器 |
| runner / Agent 执行环境 | 实际执行命令的机器或沙箱；GitHub Actions、Copilot Cloud、Cursor 各自配置，不自动共享 Secrets |

### 用一个不含真实凭据的示例理解配置引用

在当前仓库 Settings → Secrets and variables → Actions 的 Variables 标签中新建 `LAB_MESSAGE`，值为 `Hello config`；在 Secrets 标签中新建 `LAB_TOKEN`，填入任意无敏感性的练习值。这里不需要购买服务或生成真正的访问令牌。

从最新 master 建立 `lab/03-config`，在 hello.yml 的 steps 最后插入：

```yaml
      - name: Check configuration
        env:
          LAB_MESSAGE: ${{ vars.LAB_MESSAGE }}
          LAB_TOKEN: ${{ secrets.LAB_TOKEN }}
        run: |
          printf '%s\n' "$LAB_MESSAGE"
          test -n "$LAB_TOKEN" || { echo "LAB_TOKEN is missing"; exit 1; }
          echo "Practice value is available; its value is not printed"
```

通过 PR 合并后手动运行 master。日志应显示 `Hello config` 和存在性检查通过；这只能证明配置传入了步骤，不能证明真实 API 认证成功。删除 LAB_TOKEN 再运行会看到明确的缺失提示，恢复后通过。最后移除该练习步骤并合并，再删除两项练习配置，以免影响后续运行。

这里的 PR 来源分支在同一操作仓库内。来自另一个 fork 的 PR 默认无法获得普通 Secrets；不要用提高事件信任级别来绕过它。仓库 Secret 与第 05 篇的 environment secret 作用域不同；GitHub 中保存的 Secret 也不会自动出现在 Cursor 中。[Secrets 配置与引用](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)

## 9. 常见问题与结果检查

| 现象 | 排查顺序 |
|---|---|
| 看不到流程 | 文件位置和扩展名 → YAML 是否有效 → Actions 是否启用 |
| 没有 Run workflow | 默认分支是否有文件 → 是否声明手动事件 → 写权限 |
| 一直 queued | runner 是否可用 → 仓库或组织配额、并发限制 |
| 步骤红了 | 展开第一个失败步骤，读具体错误，不只看最后的退出码 |
| 新提交没触发 | 事件类型、目标分支、路径过滤、是否等待外部贡献者运行批准 |

修改打印内容并提交后，新运行的日志应显示修改后的文字。若仍是旧输出，先检查 run 对应的分支和提交；重新执行旧 run 并不会自动改为运行最新提交。

需要特殊工具链、本机硬件或把私有项目的部分计算迁回本地时，选学 [[GitHub 协作与自动化：03A 用自己的电脑运行 CI：Self-hosted Runner]]。它使用独立私有实验仓库；普通 CI 主线继续下一篇。

下一篇：[[GitHub 协作与自动化：04 CI 与合并检查]]。
