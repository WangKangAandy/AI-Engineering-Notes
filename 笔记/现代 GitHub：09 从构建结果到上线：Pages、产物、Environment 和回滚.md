---
title: 现代 GitHub：从构建结果到上线：Pages、产物、Environment 和回滚
summary: 把资源导航构建为可下载产物和 Pages 网站，配置 release Environment 审批，记录提交来源，并演练一次可验证回滚。
tags:
  - github
  - actions
  - pages
  - deployment
  - release
created: 2026-11-18
status: ready
---

# 现代 GitHub：从构建结果到上线：Pages、产物、Environment 和回滚

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

CI 通过只说明代码通过了检查。上线还要回答三个问题：构建出来的是什么、它来自哪次提交、谁批准它进入发布环境。本章把这三个问题放进一条 Pages 流程，并用一次回滚验证结果可以恢复。

## 先统一三个对象

- Artifact 是某次 workflow run 保存的文件，例如 site/；
- Environment 是部署目标及其保护规则，例如 release；
- Release 是面向版本的发布记录，通常关联一个 tag 和一组说明。

Artifact 不等于 Release，Environment 也不等于 Pull Request 审批。PR 审批决定代码能否合入；Environment reviewer 决定某次 job 能否进入被保护的部署环境。

## 配置 release Environment

在自己的仓库打开 Settings → Environments → New environment，填写：

- Name：release；
- Required reviewers：选择能够批准部署的账号；
- Deployment branches and tags：选择 Selected branches and tags，并只允许 main；
- 本章不使用 tag 部署；如果另设 v* tag 流程，必须另建 workflow 和 Environment 规则；
- Allow administrators to bypass protection rules：关闭；
- Wait timer：本练习不设置；
- Environment secrets：本练习不放秘密。

保存后，Environment 页面应显示名称、审批人和分支/tag限制。单人练习时，如果把自己设置为 reviewer，部署 job 会等待你在运行页面点击审批；如果仓库策略禁止自己审批，改用第二个有权限的账号，或把审批练习作为可选项，不要把流水线锁死后继续宣称成功。

## 构建、记录来源并上传产物

在 .github/workflows/pages.yml 中加入：

~~~yaml
name: Publish resource site

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.event_name == 'pull_request' && format('pages-pr-{0}', github.event.pull_request.number) || 'pages-deploy' }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  build:
    name: Build site
    runs-on: ubuntu-latest
    permissions:
      contents: read
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
      - name: Record provenance
        run: |
          python - <<'PY'
          import json
          import os
          from pathlib import Path
          record = {
              "repository": os.environ["GITHUB_REPOSITORY"],
              "sha": os.environ["GITHUB_SHA"],
              "run_id": os.environ["GITHUB_RUN_ID"],
              "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
          }
          Path("site/provenance.json").write_text(
              json.dumps(record, indent=2) + "\n", encoding="utf-8"
          )
          PY
      - name: Upload site artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    name: Deploy site
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: release
      url: ${{ steps.deployment.outputs.page_url }}
    permissions:
      pages: write
      id-token: write
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
~~~

这个示例中的 provenance.json 是本流程真实生成的文件，包含仓库、提交 SHA、run ID 和尝试次数。它不是签名证明，也不替代 artifact attestations；它只是让读者能从页面追到这次构建的来源。

将 pages.yml 放入工作分支，提交并创建 PR。PR 事件只运行 build，deploy job 会跳过；合入 main 或手动从 main 运行时才进入 release Environment。这样可以先验证构建，再决定是否部署。

## 启用 Pages

在仓库 Settings → Pages → Build and deployment 中：

1. Source 选择 GitHub Actions；
2. 保存；
3. 确认默认分支、仓库可见性和组织策略允许 Pages；
4. 回到 Actions：先打开合并前的 PR run，确认 build 成功且 deploy 显示 Skipped；合入 main 后再打开 push run，确认 deploy 进入 release Environment。手动运行时在 Run workflow 页面选择 main；若选择其他分支，按分支规则预期拒绝或不进入部署。

build 完成后，deploy job 会显示 Waiting。点击 Review deployments，选择 release，确认批准。批准后，deploy-pages action 才会执行。等待时间和页面生成时间取决于 GitHub 环境，不能用本地 YAML 解析代替。

## 观察一条完整证据链

在 workflow run 中按顺序记录：

1. commit SHA；
2. build job 的测试和构建日志；
3. site artifact 或 Pages artifact；
4. provenance.json 中的 SHA 和 run ID；
5. release Environment 的审批记录；
6. deploy job 输出的 page_url；
7. 打开的页面内容。

从页面下载或打开 provenance.json，检查其中的 sha 是否等于本次运行的 GITHUB_SHA。如果页面内容和来源不一致，先停止发布，不要用“Actions 是绿色的”解释问题。

## 创建 Release 记录

当 main 上的变更准备作为一个版本发布时，在 GitHub 的 Releases → Draft a new release 中：

1. Create new tag，填写 v0.1.0；
2. Target 选择 main 的已验证提交；
3. 填写本版本包含的资源、校验和已知限制；
4. 发布 Release。

Release 是给人阅读和回看的版本记录；Pages 部署可以继续由 main 的 push 触发，两者不要混写为同一个对象。

## 演练回滚

先在 main 上做一个可观察的小修改，例如把页面标题改成“临时标题”，走完整 PR、CI 和部署。记录：

- 修改前的提交 SHA；
- 修改后的提交 SHA；
- 两次 Pages URL 内容；
- 两次 provenance.json 的 SHA。

如果新版本需要撤回，在 Git Bash 中从 main 创建回滚分支：

~~~bash
git switch main
git pull --ff-only origin main
git switch -c revert/temporary-title
git revert NEW_COMMIT_SHA
git push -u origin revert/temporary-title
~~~

为这个分支创建 Revert PR，等待 CI 通过并合入 main。合入后再次观察 Pages、run ID 和 provenance。回滚的成功条件是线上内容恢复、且恢复动作本身仍有可追溯提交；不要直接删除远程历史。

## 故障排查顺序

- 没有看到 Pages：先检查 Settings → Pages 的 Source；
- deploy 等待：检查 release Environment 的 reviewer、分支和 tag 规则；
- artifact 缺失：检查 upload-pages-artifact 的 path 是否与 build 输出相同；
- 页面内容旧：比较部署 SHA、缓存和实际打开的 URL；
- provenance 不存在：说明生成步骤没有执行或路径不在上传目录；
- required check 阻止合并：回到第 8 章读日志，不要绕过规则。

## 本章结束状态

你已经把代码变更连接到构建结果、来源记录、Environment 审批、Pages URL、Release 和回滚提交。下一章会处理上线后的现实问题：失败运行、依赖、权限、Actions 用量和退出。

本章只在实际运行过相应云端步骤后才能写“部署成功”。如果你只完成了 YAML 和本地构建，应把结论写成“配置已准备，云端仍需验证”。

