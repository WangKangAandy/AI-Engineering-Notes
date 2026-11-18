---
title: 现代 GitHub：按需求扩展和改进工作流
summary: 通过独立手动实验理解多版本检查、可复用工作流和并发控制，根据真实瓶颈决定是否需要缓存。
tags:
  - github
  - actions
created: 2026-11-18
status: learning
---

# 现代 GitHub：按需求扩展和改进工作流

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 16 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<现代 GitHub：保存和传递一次运行的结果.md>) · [下一章](<GitHub 协作与自动化：05 构建、发布与部署.md>)

本章是工程化深化，可以直接跳到第 17 章。入口是第 15 章的 resource-nav main、ci.yml 和 resource-site 产物；出口仍保持这些对象不变。只有实际出现兼容性、重复配置或过期任务的问题，才需要采用对应方案。

以下可选实验新增两个 workflow，不替换 ci.yml，也不改 **Check resources**。单次运行 Python 3.12 与 3.13 是兼容性观察，不自动构成支持所有 Python 版本的承诺。

## 用一个独立实验理解 matrix 和复用

假设准备回答“同一套资源校验在 3.12 与 3.13 是否都通过”。复制两份完整 job，以后改命令就容易漏掉一份。matrix 把同一个 job 展开为多个参数组合；reusable workflow 则把一整套 job 定义放到可被调用的文件。前者解决组合，后者解决复用，作用不同。

从自己仓库干净且更新后的 main 建立 `lab/16-compatibility`。新建 `.github/workflows/resource-check-call.yml`：

```yaml
name: Reusable resource check
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string
permissions:
  contents: read
jobs:
  compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ inputs.python-version }}
      - run: python catalog.py resources.csv
      - run: python -m unittest discover -v
      - run: python build.py
```

新建调用者 `.github/workflows/compatibility.yml`：

```yaml
name: Resource compatibility lab
on:
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: compatibility-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  versions:
    strategy:
      fail-fast: false
      matrix:
        python: ['3.12', '3.13']
    uses: ./.github/workflows/resource-check-call.yml
    with:
      python-version: ${{ matrix.python }}
```

调用发生在 job 的 uses，不是 steps 里的 action 调用。相对路径引用同一提交里的被调用文件，因此修改调用者和被调用者能一同评审；跨仓库调用还需要明确引用版本和访问权限。本例没有 secrets，也不用 `secrets: inherit` 传播无用权限。[工作流复用](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)

matrix 会展开两个调用，各自准备解释器、运行三条命令。`fail-fast: false` 让其中一个版本失败时，另一个仍能提供结果，方便比较；它不意味着失败可以忽略。增加操作系统维度会乘法增加 job 数量和成本，因此本章只用 Ubuntu 与两个版本。[矩阵策略](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)

检查新增的两个文件，提交、推送并创建 main PR。现有 Resource CI 仍应通过。合并后从 Actions 选择 **Resource compatibility lab** → Run workflow → main。手动入口要求文件已在默认分支。打开 run，分别核对两个版本的 setup-python 日志、测试数量和构建结果。两项成功才能记录“当前提交在这两个版本的这些检查通过”；尚未手动运行时只记录“配置已合并”。

## 为什么新任务可以取消旧任务

并发配置把同一个 workflow、同一个 ref 分到一组；新运行进入时，`cancel-in-progress: true` 允许取消同组进行中的旧运行。保留 workflow 名和 ref 可以避免不同流程或不同分支相互误取消。这里取消的是可重新运行的检查，不包含发布或不可逆写入。[并发行为](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)

可以连续手动触发两次 main，观察前一次是否仍在运行并变成 Cancelled、后一次完成。如果第一次已经结束，就没有可取消的任务；这不是配置失效，也不能记录为已观察到取消。要受控观察，可暂时在被调用流程末尾增加 `- run: sleep 45`，经 PR 合并后再连续触发，观察后通过 PR 移除等待步骤。此命令在 Ubuntu runner 上执行，不是在 PowerShell 本机等待。

取消不是事务回滚：已经上传的文件或外部服务写入可能仍存在。对部署任务直接套用这项设置可能中断交付，应按第 17 章的部署串行与恢复需要单独设计；不要把实验的并发组改成全仓库统一的固定字符串。

## 现在为什么不加缓存

本例没有第三方 Python 包，没有 requirements.txt，也没有耗时的依赖下载。此时加 `cache: pip` 不会改善主要流程，还会引入缓存键与依赖文件的配置负担。先在 Actions 日志中比较 checkout、解释器准备、校验和构建耗时，判断真正花时间的是哪里。

如果将来项目确实新增第三方依赖，再让缓存围绕真实依赖清单与版本工作，例如用 setup-python 的 pip 缓存能力并提供正确依赖文件；缓存命中也仍然执行依赖安装，让环境符合声明。缓存不承诺永远存在，清空缓存后的任务也应正常完成。它不能替代 resource-site 这种需要交付和追溯的 artifact。[依赖缓存](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching) · [setup-python 缓存说明](https://github.com/actions/setup-python#caching-packages-dependencies)

## 选择结束状态

只想理解原理时，可以不添加任何文件，带着第 15 章 ci.yml 继续。完成实验后，可保留仅手动触发的 compatibility.yml，按需查看兼容性；不再使用时，通过 PR 同时删除调用者和被调用者，不留下失效引用。不要把实验检查名设为主线必需检查。

检查最终 diff：ci.yml 的三条检查、Check resources 名称、resource-site 上传和 verify job 都应仍在。记录本次选择及证据，例如“暂不缓存，因为没有第三方依赖下载”，或“在某 run 的 3.12/3.13 两个 job 均通过”。决定不启用某功能，也可以是有依据的工程结果。
