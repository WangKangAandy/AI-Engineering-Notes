---
title: GitHub 协作与自动化：05 构建、发布与部署
summary: 将静态页面构建并部署到 GitHub Pages，理解 artifact、tag、Release、部署和回滚的区别。
tags:
  - github
  - cd
  - deployment
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：05 构建、发布与部署

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。

> 本篇实验基线：`master`；实验分支：`lab/05-pages`。先按第 02 篇的方法从最新 master 创建该分支；完成本篇所需的 PR 合并后再进入依赖它的下一篇。前置：[[GitHub 协作与自动化：04 CI 与合并检查]] 中的三个 Python 文件已经进入 `master`。

目标：把 `build.py` 产生的页面部署到 GitHub Pages，并区分构建产物、版本发布和部署。

## 1. 这几个结果分别在哪里

| 对象 | 作用 | 本练习里的例子 |
|---|---|---|
| 构建目录 | 命令执行后生成的本地文件 | runner 工作目录中的 `site/index.html` |
| Artifact | 把输出保存下来或传给后续任务 | Pages 部署包 |
| Tag | 给 Git 历史中的某个点起名字 | `lab-v0.1.0` |
| Release | 围绕版本组织说明和可下载附件 | “首次发布练习页面” |
| Deployment | 将产物部署到目标环境 | Pages 上能访问的网站 |

runner 上存在文件不代表已经上传为 artifact。创建 Release 也不会自动部署，除非配置了对应流程。缓存服务于加速，不能替代发布产物。[Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

## 2. 先启用 Pages

在练习仓库 Settings → Pages → Build and deployment 中，将 Source 设为 **GitHub Actions**。如果当前套餐或组织策略不提供 Pages，需要先解决功能可用性，不能靠改 YAML 绕过。

本练习会发布静态 HTML。Pages 不负责运行 Python 后端：Python 在构建时生成 HTML，访问者获取的是生成后的页面。[Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

在 Settings → Environments → github-pages 中确认允许 `master` 部署；有必需审核时由指定人员批准。Pages 是仓库级站点，已有正式站点时不要用练习页面覆盖它，改在自己的 fork 验证。

## 3. 配置从检查到部署的流水线

通过 PR 新增 `.github/workflows/pages.yml`：

```yaml
name: Deploy Pages

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Test this revision
        run: python -m unittest discover -v
      - name: Configure Pages
        uses: actions/configure-pages@v5
      - name: Build site
        run: python build.py
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v4
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

`build` 负责检查当前提交、生成页面并上传包；`deploy` 通过 `needs` 等待构建成功。`pages: write` 用于 Pages 发布，`id-token: write` 允许获取部署身份令牌。环境记录关联 `github-pages`，输出 URL 显示在部署结果中。相关 action 版本与权限依据 [Pages 官方示例](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

这个示例故意在部署流程内再次测试：独立的 `ci.yml` 与 `pages.yml` 不会因为先后出现在 Actions 列表就形成依赖。这里确保测试、构建和部署关联同一次运行的提交。

手动运行时请选择 `master`；`build.if` 防止误选其他分支直接部署。以后改默认分支名时，需要同时修改 `branches` 与这个条件。

## 4. 观察发布全过程

1. 合并 PR，进入 Actions → Deploy Pages。
2. 确认运行对应合并后的 `master` 提交。
3. 在 build 日志中查看测试数量、构建文件和 artifact 上传结果。
4. 在 deploy 任务中查看成功结果，打开生成的 URL。
5. 页面应显示 `Hello, GitHub!`。首次发布可能需要稍等再访问。

项目站点通常位于账号域名下的仓库路径；使用部署实际输出的 URL，避免手猜路径。

## 5. 再创建一个 Release

在仓库 Releases 入口选择创建新版本：

1. 新建标签 `lab-v0.1.0`，选择刚才确认部署成功的提交。
2. 标题写 `lab-v0.1.0 - Workflow Lab`。
3. 正文说明功能、关联 PR 和验证结果，然后发布。

标签不存在时，页面可以在发布时创建标签。Release 自动提供的源码压缩包不等于编译好的程序；需要提供构建包时要显式上传相应附件。[管理 Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

本教程的部署触发条件是 `master` 的 push，因此新增 Release 本身不会再次触发该部署流程。

## 6. 持续交付、持续部署与回滚

本练习合并后自动部署，体现持续部署。团队也可以在生产环境前设置人工批准，保留发布决定，形成持续交付流程；环境的审核能力受仓库和套餐约束。[Deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

若要练习回滚，提交一个改变页面标题的 PR 并部署，再通过 revert PR 撤销该改动，检查恢复后的新部署。revert 会产生反向修改的新提交，保留历史。只有删除 Release 或移动标签，并不能保证正在运行的网站改变。

真实应用有数据库、状态和外部服务，回滚要同时考虑这些依赖；这里验证的是无持久状态的静态页面。

## 7. 故障定位

| 现象 | 看哪里 |
|---|---|
| Pages 未启用或找不到站点 | Settings → Pages 的 Source 与可用性 |
| deploy 找不到 artifact | build 是否上传成功；path 是否为 site；needs 是否存在 |
| 权限错误 | deploy 权限、仓库或组织限制、环境允许的分支 |
| 等待批准 | github-pages 环境是否配置 reviewer 或部署保护规则 |
| workflow 绿了但页面内容旧 | 打开的站点 URL、部署提交、浏览器缓存、发布传播时间 |

练习后停止发布时，先禁用 Deploy Pages workflow，另行取消正在运行的部署；在 Settings → Pages 取消发布站点。删除实验分支或 Release 不会下线已有页面。

## 8. 从网站追溯到代码

网站内容来自某次部署使用的 artifact。打开部署记录，可以找到对应的 workflow run 和提交，再从提交定位到 PR。Tag 为选定提交命名，Release 为版本提供说明和附件；两者与部署记录关联，但不会代替实际发布动作。

下一篇：[[GitHub 协作与自动化：06 Agents 与任务委派]]。
