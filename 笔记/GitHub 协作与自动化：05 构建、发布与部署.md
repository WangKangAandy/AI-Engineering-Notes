---
title: 现代 GitHub：从构建产物到发布、部署与回滚
summary: 将静态页面构建并部署到 GitHub Pages，理解 artifact、tag、Release、部署和回滚的区别。
tags:
  - github
  - cd
  - deployment
created: 2026-11-16
status: learning
---

# 现代 GitHub：从构建产物到发布、部署与回滚

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 17 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<现代 GitHub：按需求扩展和改进工作流.md>) · [下一章](<现代 GitHub：持续维护权限、凭据与依赖安全.md>)

资源导航已经能生成 site/index.html，并在 CI 保存构建结果。现在把页面交付给访问者，同时保留“谁批准了哪个提交”的记录。本章操作自己的公开 `YOUR_LOGIN/resource-nav`，默认分支 main；第 15 章已完成，第 16 章的按需优化可以跳过。

从最新 main 创建 `lab/17-pages`。README、resources.csv、catalog.py、test_catalog.py、build.py 与 ci.yml 均已在 main；本章新增 pages.yml，不删除已有 CI 或改动必需检查名称。

## 1. 这几个结果分别在哪里

| 对象 | 作用 | 本练习里的例子 |
|---|---|---|
| 构建目录 | 命令执行后生成的本地文件 | runner 工作目录中的 `site/index.html` |
| Artifact | 把输出保存下来或传给后续任务 | Pages 部署包 |
| Tag | 给 Git 历史中的某个点起名字 | `lab-v0.1.0` |
| Release | 围绕版本组织说明和可下载附件 | “首次发布练习页面” |
| Deployment | 将产物部署到目标环境 | Pages 上能访问的网站 |

第 15 章保存的 resource-site 是普通 workflow artifact；本章改用 Pages 专用上传步骤产生 github-pages 包。两者都保存构建结果，但名称和打包约定不同，不能把旧运行里的普通 artifact 名称直接交给 Pages 部署步骤。

runner 上存在文件不代表已经上传为 artifact。创建 Release 也不会自动部署，除非配置了对应流程。缓存服务于加速，不能替代发布产物。[Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

## 2. 先启用 Pages

在练习仓库 Settings → Pages → Build and deployment 中，将 Source 设为 **GitHub Actions**。如果当前套餐或组织策略不提供 Pages，需要先解决功能可用性，不能靠改 YAML 绕过。

本练习会发布静态 HTML。Pages 不负责运行 Python 后端：Python 在构建时生成 HTML，访问者获取的是生成后的页面。[Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

Pages 是仓库级站点。先确认没有正在服务的正式站点；已有正式站点时先使用没有站点的独立练习仓库，不改共享站点的 Source。自己的 resource-nav 由自己管理；在组织项目操作时，需要相应 admin 权限。

### 给上线过程加一个人工决定

本篇采用一个具体需求：测试与构建自动完成，只有 main 的产物可以上线，上线前由指定人员确认。保护的是 deploy job，build 不需要等待审批。

打开 Settings → Environments。如果已有 `github-pages`，点击进入；否则 New environment，填写 `github-pages` 并进入配置页。按下表设置后保存：

| 设置 | 本例取值及原因 |
| --- | --- |
| Required reviewers | 选择自己作为个人练习审批人；团队可选择实际发布负责人 |
| Prevent self-review | 单人练习不启用，否则自己触发后无法批准；团队需要双人制时启用并指定另一人 |
| Deployment branches and tags | 选择 Selected branches and tags，Add deployment branch or tag rule 中 Ref type 选 Branch，名称为 main |
| Allow administrators to bypass protection rules | 关闭，让实验中的管理员也走批准流程 |
| Wait timer | 本例不启用；需要冷静期才设置延迟，它不会代替审批 |
| Environment secrets | 本例留空；Pages 使用下方声明权限的 GITHUB_TOKEN 和部署身份令牌，不需要额外 PAT |

审批能力受套餐与仓库可见性限制；公开仓库是本系列的练习前提。若当前仓库没有 Required reviewers，仍可做自动部署，但无法完成本节的审批实验，不能把直接上线误记为审批通过。

环境名必须与下方 `jobs.deploy.environment.name` 对应。仅在 YAML 写 environment 不会自动生成上述保护规则；运行时创建的空环境也不能替代页面配置。`main` 是 Branch 规则，不要照标签发布教程填 Tag `v*`：本篇 workflow 由 main push 或选择 main 的手动运行触发。[环境创建与保护设置](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)

若真实部署需要生产密钥，应在对应环境的 Environment secrets → Add secret 中保存，并让受保护 job 通过 secrets 上下文读取；审批通过前该 job 无法取得环境密钥。第 13 章已演示仓库级配置的引用方式。不要为本篇没有使用的凭据创建 Secret。

## 3. 配置从检查到部署的流水线

在 `lab/17-pages` 新增以下完整 `.github/workflows/pages.yml`，通过 PR 合入 main：

```yaml
name: Deploy Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: read
    steps:
      - name: Checkout
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Validate current catalog
        run: python catalog.py resources.csv
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

build 的 `contents: read` 用于获取代码，`pages: read` 显式允许 configure-pages 读取站点配置；发布写权限只给 deploy。公开资源的读取允许不具备 Pages read 权限，本例仍将依赖声明清楚。增加这项权限不代表整个流程已适配私有仓库，Pages 与环境审批的可用条件仍须分别核对。[读取 Pages 配置的权限](https://docs.github.com/en/rest/pages/pages#get-a-github-pages-site)

这个示例故意在部署流程内再次测试：独立的 `ci.yml` 与 `pages.yml` 不会因为先后出现在 Actions 列表就形成依赖。这里确保测试、构建和部署关联同一次运行的提交。

手动运行时请选择 `main`；`build.if` 防止误选其他分支直接部署。以后改默认分支名时，需要同时修改 `branches` 与这个条件。

## 4. 观察发布全过程

1. 合并包含 pages.yml 的 PR，进入 Actions → Deploy Pages，打开对应 main 提交的 run。
2. build 应先通过测试、生成页面并上传 artifact。deploy 应显示等待保护规则/审批；此时没有开始本次上线。
3. 回到该 run 的概要，点击 **Review deployments**，勾选 `github-pages`，核对提交与构建结果，点击 **Approve and deploy**。
4. deploy 随后执行。成功后打开环境输出 URL，页面应显示“学习资源导航”以及当前清单的资源标题和分类；首次发布可能需要等待传播。
5. 从 Run workflow 再选择 main 发起一次，等到审批入口后选择 **Reject**。本次运行应失败，已上线的页面保持此前版本；拒绝不会撤下现有部署。

审批在 Actions run 页面完成，不是在 PR 的 Approve review 中完成。PR 门禁决定能否合并，Environment 规则决定 deploy job 能否执行。多人审批列表通常只需其中一位批准；开启 Prevent self-review 后不能批准自己发起的部署。若要取消正在执行的运行，使用该 run 的 Cancel workflow。[审批与拒绝](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments)

### 下载本次构建的文件

打开成功运行的概要，在 Artifacts 区域点击 `github-pages` 下载。浏览器下载的归档解压后通常包含 `artifact.tar`；再展开 tar，可找到 `index.html`，其中应含“学习资源导航”和你当前清单的条目。这份文件与 build 日志属于同一次 run。下载需要登录并有仓库读取权限；产物有保留期限，不是永久版本下载地址。

也可以用 GitHub CLI 下载。以下在本机 PowerShell、仓库 checkout 内执行，将 123456 替换为浏览器运行 URL 中 `/actions/runs/` 后的数字；每次使用一个新的空输出目录：

```powershell
$runId = 123456
$outDir = Join-Path $env:TEMP ("pages-artifact-" + [guid]::NewGuid().ToString('N'))
gh run download $runId --repo YOUR_LOGIN/resource-nav -n github-pages -D $outDir
if ($LASTEXITCODE -ne 0) { throw "Artifact download failed" }
tar -tf (Join-Path $outDir 'artifact.tar')
tar -xf (Join-Path $outDir 'artifact.tar') -C $outDir
Get-Content (Join-Path $outDir 'index.html')
```

命令中的 YOUR_LOGIN 要替换为自己账号；--repo 显式限定这次运行所属的 resource-nav，不依赖本地 checkout 的默认目标。如果 artifact 过期，重新构建并记录新的 run，不把另一轮产物当成原部署的证据。[下载 workflow 产物](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)

## 5. 再创建一个 Release

先打开刚才**部署成功**的 run，点击提交链接，复制完整 commit SHA。拒绝的那次运行不作为发布依据。这里给已验证的提交打标签，并发布版本说明；它不会再次部署 Pages。

网页与 CLI 路径二选一，都先保存 draft，再从共同的核对步骤发布。

网页路径：仓库 Code 页侧栏 Releases → Draft a new release → Choose a tag → 输入尚未使用的 `lab-v0.1.0`。若 Target 选择 main，先确认 main 当前最新 SHA 与刚复制的 SHA 相同；若相同，填写标题 `lab-v0.1.0 - Resource Navigator` 和版本说明，选择 **Save draft**。若不同，不保存这个指向新提交的草稿，改用下面的精确 SHA 路径。

CLI 路径：在已登录 gh 的本机 PowerShell 中，将部署 SHA 替换为真实值，创建 draft：

```powershell
$deployedSha = '替换为成功部署的完整commit-SHA'
gh release create lab-v0.1.0 --repo YOUR_LOGIN/resource-nav --target $deployedSha --draft --title 'lab-v0.1.0 - Resource Navigator' --notes "静态页面练习版本；部署提交：$deployedSha"
```

命令中的 YOUR_LOGIN 必须替换；--repo 与部署 run 所在的仓库一致。使用前确认该标签不存在；`--target` 不会重新定位已有标签。无论采用哪条路径，接下来都在 Releases 打开保存的 draft，核对目标提交；发布后还要从标签页面确认它指向已记录的部署 SHA。草稿中补上 PR 和成功 run 链接，确认无误再 Publish release。

Release 自动提供的源码压缩包不是构建包；需要下载成品时，在 draft 的附件区域上传从已验证 run 得到的构建包，再发布。这个静态页面练习可以只发布说明和源码。Artifact 是运行输出，tag 命名提交，Release 组织说明和附件，三个对象有各自的生命周期。[Release 页面操作](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) · [CLI 的 target 与 draft](https://cli.github.com/manual/gh_release_create)

## 6. 持续交付、持续部署与回滚

本练习构建完成后仍需人工批准上线，体现保留发布决定的持续交付流程；取消该审批且所有变更通过检查后自动上线，才体现持续部署。环境的审核能力受仓库和套餐约束。[Deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

从最新 main 创建 `lab/17-change-title`，将 build.py 中 `<title>` 内的 `Learning Resource Navigator` 改为 `Learning Resource Navigator v2`，提交 PR。为便于本次网页回滚练习，仓库允许时选择 Create a merge commit 合并。批准它的 Pages 部署，打开页面确认浏览器标签标题已经改变，并记下 run 和 SHA。

回到这个已合并 PR 的 Conversation 页，在合并信息附近选择 **Revert**，检查 GitHub 生成的反向差异，然后 Create pull request，目标仍为 main。等待 CI 通过并合并，再批准新的 Pages 部署。打开网页确认标题恢复，部署 SHA 应是新的回滚提交。revert 保留历史，并不会把 main 的提交指针退回旧位置。

如果这次采用 Squash and merge 或页面没有 Revert 按钮，先查看 PR 的合并记录，找到实际进入 main 的那一条新提交，而不是来源分支里的旧提交。对这个普通提交，可从最新 main 新建回滚分支，按第 6 章的 revert 小节生成反向提交；冲突时解决后用 `git revert --continue`，放弃这次反向提交用 `git revert --abort`，再走 PR、CI、合并与部署审批。若实际是有多个父节点的 merge commit，不能照搬单父提交命令，优先使用网页生成的回滚 PR；手动处理需先核对主线父节点。第 5 章只帮助阅读冲突标记，不替代 revert 的继续/中止流程。不要通过 reset/force push 改写共享 main。[Revert PR 操作](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/reverting-a-pull-request)

删除 Release 或移动标签不会使本例网站回滚，因为部署触发的是 main 的新提交。

真实应用有数据库、状态和外部服务，回滚要同时考虑这些依赖；这里验证的是无持久状态的静态页面。

## 7. 故障定位

| 现象 | 看哪里 |
|---|---|
| Pages 未启用或找不到站点 | Settings → Pages 的 Source 与可用性 |
| deploy 找不到 artifact | build 是否上传成功；path 是否为 site；needs 是否存在 |
| 权限错误 | deploy 权限、仓库或组织限制、环境允许的分支 |
| 等待批准 | github-pages 环境是否配置 reviewer 或部署保护规则 |
| workflow 绿了但页面内容旧 | 打开的站点 URL、部署提交、浏览器缓存、发布传播时间 |

后面的 AI 章节仍可能修改资源导航；保留此 workflow 和环境时，每次 main 更新都可能再次产生待批准部署。只想练习代码审查时，可以保持审批等待或取消那次部署，不把任务完成当成已上线。全部练习结束后停止发布时，先禁用 Deploy Pages workflow，另行取消正在运行的部署；在 Settings → Pages 取消发布站点。删除实验分支或 Release 不会下线已有页面。

## 8. 从网站追溯到代码

网站内容来自某次部署使用的 artifact。打开部署记录，可以找到对应的 workflow run 和提交，再从提交定位到 PR。Tag 为选定提交命名，Release 为版本提供说明和附件；两者与部署记录关联，但不会代替实际发布动作。

下一章：[持续维护权限、凭据与依赖安全](<现代 GitHub：持续维护权限、凭据与依赖安全.md>)。
