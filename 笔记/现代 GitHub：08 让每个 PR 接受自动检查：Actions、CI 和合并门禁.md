---
title: 现代 GitHub：让每个 PR 接受自动检查：Actions、CI 和合并门禁
summary: 把本机的资源校验、测试和构建接入 Pull Request workflow，读懂运行日志，并把成功检查设为合并条件。
tags:
  - github
  - actions
  - ci
created: 2026-11-18
status: ready
---

# 现代 GitHub：让每个 PR 接受自动检查：Actions、CI 和合并门禁

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

第 7 章已经在本机执行过验证。本章把同样的命令放到 GitHub Actions，让每个 Pull Request 都接受一致检查。先理解一次运行如何由 workflow、job、step 和 runner 组成，再配置合并门禁。

## 一个 workflow 如何产生检查

一个 workflow 是仓库中的 YAML 文件，通常放在 .github/workflows/ 下。它由事件触发，包含一个或多个 job；job 在 runner 上运行；job 又按顺序执行 steps。

本章的主线关系是：

~~~text
pull_request → Resource CI workflow → check job → validate/test/build steps
                                      → verify job → downloaded artifact check
~~~

Actions 页面中的 workflow run 是一次运行；job 是运行中的一组任务；step 是日志中最小的执行单位。Job 之间不是共享工作区的，若要把文件从一个 job 传给另一个 job，必须使用 artifact 或重新 checkout。

## 创建最小 CI

在自己的 resource-nav 工作分支中创建 .github/workflows/ci.yml。可以先复制随书的 [ci.yml](<_assets/modern-github/workflows/ci.yml>)，再逐段阅读。基础版本如下：

~~~yaml
name: Resource CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  check:
    name: Check resources
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Validate catalog
        run: python catalog.py resources.csv
      - name: Run tests
        run: python -m unittest discover -s . -p 'test_*.py' -v
      - name: Build site
        run: python build.py
~~~

这里的 runs-on 决定执行环境；run 执行 shell 命令；uses 使用社区或官方 action。permissions 只授予读取仓库内容的 GITHUB_TOKEN 权限，先从最小范围开始。

在 Git Bash 中从最新 main 创建本章分支：

~~~bash
git switch main
git pull --ff-only origin main
git switch -c ci/resource-checks
mkdir -p .github/workflows
~~~

打开本章前面的完整 YAML，复制到仓库的 .github/workflows/ci.yml；不要使用未定义的 path/to/ci.yml 占位路径。保存后核对文件确实在仓库中：

~~~bash
git status --short
git diff -- .github/workflows/ci.yml
git add .github/workflows/ci.yml
git diff --cached -- .github/workflows/ci.yml
git commit -m "ci: validate resources on pull requests"
git push -u origin ci/resource-checks
~~~

在 GitHub 打开该分支的 PR，进入 Actions 页面，找到 Resource CI。

## 读懂一次运行

先看最上方的触发事件和提交 SHA，再展开 check job。按顺序核对：

1. checkout 是否拿到了 PR 的代码；
2. setup-python 使用的版本；
3. Validate catalog 是否报告资源数量；
4. Run tests 的测试数量和失败位置；
5. Build site 是否生成 site/index.html。

绿色勾只表示该 step 的退出码为 0；它不证明页面已经部署，也不证明需求已经满足。红色 step 的下一步是打开日志而不是重复点击 Re-run。

## 制造一次可解释的失败

在工作分支中复制一条已有 URL，让 catalog.py 拒绝重复 URL：

~~~text
title,url,category
第一条,https://example.com/,Git
第二条,https://example.com/,Python
~~~

提交并推送后，PR 的 Resource CI 应该失败。点开 Validate catalog，确认日志指出 duplicate URL 和行号。然后恢复 CSV，重新提交并推送，确认新的 run 通过。

这次失败证明了检查确实读取了 PR 分支的文件。若你修改 main 后才发现失败，说明触发器或分支流程没有按本章目标配置。

## 把构建结果传给另一个 job

如果第二个 job 需要检查 site/index.html，不能假设它仍在 check job 的工作区。将构建目录上传为 artifact：

~~~yaml
      - name: Upload site
        uses: actions/upload-artifact@v4
        with:
          name: resource-site
          path: site/
          if-no-files-found: error
          retention-days: 7
~~~

第二个 job 使用 needs 和 download-artifact：

~~~yaml
  verify:
    name: Verify artifact
    needs: check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: resource-site
          path: received-site
      - name: Check generated page exists
        run: test -s received-site/index.html
~~~

needs 只表达执行依赖，不会自动复制文件。artifact 是明确的文件通道。第 9 章会在这个通道上增加 provenance、Pages 部署和回滚。

## 设置 required check

本书选择 Rulesets 作为唯一配置路径。在仓库 Settings → Rules → Rulesets 中：

1. 点击 New ruleset，选择 New branch ruleset；
2. Name 填 main pull request protection；
3. Enforcement status 选择 Active；
4. Target branches 选择 Include default branch，确认匹配 main；
5. 开启 Require a pull request before merging；本书单人主线将 required approvals 设为 0，避免作者无法批准自己的 PR；需要第二名协作者时，再把数量提高到 1 作为扩展练习；
6. 开启 Require status checks to pass，等待 Resource CI 至少成功运行一次后，选择 Check resources；
7. 开启 Require branches to be up to date；
8. 对 Bypass list 和管理员绕过作出明确选择，然后点击 Create。

保存规则后，用一个故意失败的 PR 验证 Merge 按钮是否被阻止，再修复它并确认按钮恢复。打开 PR 的 Checks 区域，确认规则选择的检查名与 workflow job 的 name 一致。不要只看规则页面写了必需检查；必须让一次红灯真正影响合并。

如果检查名称找不到，先让 workflow 至少成功运行一次，确认 job 的 name 与规则中选择的名称一致。修改 workflow 名称后，旧规则可能仍指向旧检查。

## 本章结束状态

现在每个面向 main 的 PR 都会触发 Resource CI；失败的资源或测试会阻止合并；通过的运行会生成可下载的构建 artifact。你能从 Actions 页面追到提交 SHA、job、step 和日志。

下一章会把 artifact 变成可上线的页面，并说明 Environment 审批和回滚如何建立在同一条证据链上。

