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

`run` 写你要执行的命令；`uses` 引用可复用组件。要读取仓库中的文件，可以在原来的打印步骤前加：

```yaml
      - name: Get repository files
        uses: actions/checkout@v7
      - name: List files
        run: ls -la
```

这段是 `steps` 下的插入片段，不是独立 workflow。`actions/checkout@v7` 中前半部分是 action 仓库，`@v7` 是版本引用。上游 README 已核对该引用；练习采用 GitHub 托管 runner。组织生产流程可按自身要求固定到审核过的完整 commit SHA。[checkout 官方仓库](https://github.com/actions/checkout)

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

自测：部署 job 写了 `needs: build`，是不是就能直接读取 build job 的 `site/`？答案是否定的。后续 Pages 示例会先上传 artifact，再由部署步骤获取该产物。

## 7. 先认识，暂不堆进练习的功能

| 功能 | 解决什么问题 |
|---|---|
| matrix | 用多种 Python 版本或操作系统运行同一套检查 |
| cache | 复用可重新生成的依赖等内容，减少重复下载 |
| artifact | 保存报告、安装包等本次执行的输出 |
| reusable workflow | 多个流程或仓库复用整套任务 |
| concurrency | 管理同组运行，避免过期任务同时部署 |
| secrets / variables | 为任务提供敏感凭据 / 普通配置 |

缓存丢失应只影响速度；artifact 是明确要保留或传递的结果。[Artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts) · [Caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)

## 8. 排错与验收

| 现象 | 排查顺序 |
|---|---|
| 看不到流程 | 文件位置和扩展名 → YAML 是否有效 → Actions 是否启用 |
| 没有 Run workflow | 默认分支是否有文件 → 是否声明手动事件 → 写权限 |
| 一直 queued | runner 是否可用 → 仓库或组织配额、并发限制 |
| 步骤红了 | 展开第一个失败步骤，读具体错误，不只看最后的退出码 |
| 新提交没触发 | 事件类型、目标分支、路径过滤、是否等待外部贡献者运行批准 |

验收：能自行修改打印内容，运行新版本，并找到对应提交的输出。

下一篇：[[GitHub 协作与自动化：04 CI 与合并检查]]。
