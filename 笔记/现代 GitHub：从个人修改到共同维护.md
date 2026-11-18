---
title: 现代 GitHub：从个人修改到共同维护
summary: 从外部贡献的 fork 路径出发，为资源导航建立简明贡献约定、Issue 表单和 PR 模板，理解访问权限与评审责任的边界。
tags:
  - github
  - collaboration
  - maintenance
created: 2026-11-18
status: learning
---

# 现代 GitHub：从个人修改到共同维护

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

这是第 10 章，前置是[PR 评审](<GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并.md>)和[gh 日常协作](<现代 GitHub：用 gh 串起日常协作.md>)。我们继续维护自己的公开 `YOUR_LOGIN/resource-nav`：main 已有资源清单和分类说明。本章不改变清单格式，而是回答别人来贡献时，会从哪里找到约定、需要提供什么、由谁决定接收。

自己记得“Git 与 GitHub 分开分类”还不够。协作者可能只看到首页，第一次打开 Issue 也不知道该写什么。共同维护的第一步，是把重复解释变成能找到、能执行的约定。

## 外部贡献者怎样把修改送回来

此前你有自己仓库的写权限，可以直接推送任务分支。对别人的公开仓库，你通常只能读取，不能推送。这时 fork 提供一个属于你的远端副本；在自己的 fork 创建分支，再向原仓库提出 PR。克隆只是把仓库下载到本机，不会产生 GitHub 上的 fork，也不授予写权限。[通过 fork 贡献](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)

先读目标项目的 README、CONTRIBUTING、许可证和相关 Issue，确认它接受这种修改。一个已经归档、只收安全修复，或维护者明确拒绝该方向的仓库，不适合直接提交新功能。公共项目不是实验用消息箱；有真实改进才提交，纯练习可以找愿意配合的同伴使用各自的 resource-nav。

以下是一条完整的外部路径。先在目标仓库网页点击 Fork，Owner 选择自己，记下实际 fork 名称。下面的 `UPSTREAM_OWNER/UPSTREAM_REPO` 与 `YOUR_LOGIN/FORK_NAME` 都是占位符，先替换。外部贡献使用一个独立父目录，不能放进主线 resource-nav；这里选用户目录下的 `github-contributions`，并检查它不属于其他 Git 仓库。

在 PowerShell 7 中整段执行以下代码。花括号让检查和后续操作处于同一个执行块；任何 `throw` 都会停止本块。目标目录已存在时立即停止，不复用、不覆盖；若 clone 失败留下目录，先检查失败原因和已有文件，再自行选择另一个全新目录重试。

```powershell
& {
    $contributionParent = Join-Path $env:USERPROFILE 'github-contributions'
    $contributionTarget = Join-Path $contributionParent 'external-contribution'
    $contributionForkUrl = 'https://github.com/YOUR_LOGIN/FORK_NAME.git'
    if ($contributionForkUrl -match 'YOUR_LOGIN|FORK_NAME') {
        throw '先将 fork URL 占位符替换为自己的实际地址。'
    }
    if (Test-Path -LiteralPath $contributionTarget) {
        throw "目标已存在，停止：$contributionTarget"
    }
    New-Item -ItemType Directory -Path $contributionParent -Force -ErrorAction Stop | Out-Null
    git -C $contributionParent rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0) {
        throw '父目录位于另一个 Git 仓库内，请选择独立父目录。'
    }
    git clone $contributionForkUrl $contributionTarget
    if ($LASTEXITCODE -ne 0) { throw 'clone 失败，停止；不要继续切目录或添加远端。' }
    Set-Location -LiteralPath $contributionTarget -ErrorAction Stop
    $contributionRoot = git rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0) { throw '无法确认克隆仓库根目录。' }
    if ([System.IO.Path]::GetFullPath($contributionRoot) -ne [System.IO.Path]::GetFullPath($contributionTarget)) {
        throw '当前仓库根目录不是新克隆目标，停止。'
    }
    $contributionOrigin = git remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $contributionOrigin -ne $contributionForkUrl) {
        throw 'origin 与预期 fork 地址不一致，停止。'
    }
    git remote -v
}
```

确认输出中的 origin 是自己的 fork，然后为**这个新克隆**配置提交署名。第 3 章使用 `--local`，其配置只保存在 resource-nav 的 `.git/config`，不会随另一个仓库的 clone 自动带过来。下面两项必须替换为你的真实署名，以及 GitHub Settings → Emails 中已验证的邮箱或该账号提供的 noreply 邮箱；不要直接提交占位文本，也不要依赖机器碰巧存在的全局身份。

```powershell
git config --local user.name '你的署名'
git config --local user.email '从 GitHub 设置中复制的邮箱'
git config --show-origin --get user.name
git config --show-origin --get user.email
```

查看两项最终值和来源，确认是当前仓库的 `.git/config`。署名与 GitHub 网络认证仍是两件事，详见[第 3 章](<现代 GitHub：准备本地工具与正确身份.md>)。完成根目录、origin 和身份检查后，才添加上游远端；先替换下面的上游占位地址：

```powershell
& {
    $contributionUpstreamUrl = 'https://github.com/UPSTREAM_OWNER/UPSTREAM_REPO.git'
    if ($contributionUpstreamUrl -match 'UPSTREAM_OWNER|UPSTREAM_REPO') {
        throw '先替换实际上游地址。'
    }
    git remote add upstream $contributionUpstreamUrl
    if ($LASTEXITCODE -ne 0) { throw '添加 upstream 失败，停止并检查已有远端。' }
    git remote -v
    git fetch upstream
    if ($LASTEXITCODE -ne 0) { throw '获取 upstream 失败，停止。' }
    git remote show upstream
    if ($LASTEXITCODE -ne 0) { throw '无法读取上游信息，停止。' }
}
```

`origin` 应指自己的 fork，`upstream` 应指原仓库。最后一条输出中的 HEAD branch 帮你确认上游默认分支。以下假设它是 main；实际名称不同就替换：

```powershell
git switch -c docs/clarify-category upstream/main
```

只做已经确认有价值的修改，按第 8 章检查、提交，再推到自己的 fork：

```powershell
git push -u origin docs/clarify-category
```

创建 PR 时，base repository 是原仓库，base 是维护者指定的目标分支；head repository 是自己的 fork，compare 是刚推送的任务分支。不要沿用第 8 章“两边都是自己的仓库”的选择。差异应只包含本次工作，若出现大量无关提交，先停止并检查起点与 base。

之后复用第 8 章的评审和原分支修订流程。贡献者可以解释决定、响应反馈、关闭自己的提案，但是否接收、何时发布由维护者决定。fork 中显示的合并不表示原仓库已经接收；最终核验原仓库的 PR 和目标文件。有同伴时可以交换这两个角色，没有同伴就完成本章后面的自身仓库维护，不虚构外部批准。

## 把重复解释放到读者会找的位置

外部贡献结束后，当前终端可能仍在 external-contribution，先显式回到第 3 章建立的主线仓库：

```powershell
$mainLabPath = Join-Path $HOME 'github-learning/resource-nav'
Set-Location -LiteralPath $mainLabPath -ErrorAction Stop
git rev-parse --show-toplevel
git remote -v
git status --short
```

如果第 3 章选择了其他学习目录，先把 mainLabPath 改为那个 resource-nav 的实际绝对路径。核对根目录就是自己的主线仓库，origin 指向自己的 resource-nav，工作区没有未完成修改；任何一项不符就先停下处理，不继续创建分支。确认后从最新 main 开始：

```powershell
git switch main
git pull --ff-only
git switch -c docs/contributing
```

每条 Git 命令成功后再执行下一条。以下文件都属于读者的练习项目，不是本书笔记库的配置：

```text
README.md
CONTRIBUTING.md
.github/
  ISSUE_TEMPLATE/
    resource.yml
  pull_request_template.md
```

README 面向使用者，说明项目是什么以及如何读资源；CONTRIBUTING 面向贡献者，解释提交约定；表单收集需求信息；PR 模板提示作者交代差异和证据。它们职责不同，不需要把整套流程复制四遍。

在 README 保留原有内容，增加一个入口：

```markdown
## 参与维护

欢迎修正资源信息和推荐学习资料。提交前请阅读 `CONTRIBUTING.md`。
资源清单位于 `resources.csv`，目前按 Git、GitHub、Python 分类。
```

新建 `CONTRIBUTING.md`，完整内容可以从下面开始：

```markdown
# 贡献指南

本项目维护学习资源导航。优先收录可公开访问、来源清楚的学习资料。

## 提出需求

先搜索已有 Issue 和 resources.csv 中的 URL，避免重复。
新增资源请说明标题、完整链接、建议分类，以及它能解决什么学习问题。
批量改变分类或增加程序行为前，先通过 Issue 讨论范围。

## 修改文件

resources.csv 使用 UTF-8，表头保持 title,url,category。
Git 表示版本控制工具，GitHub 表示托管平台，Python 表示语言学习资料。
保留其他有效条目，不把个人笔记、凭据或临时文件加入清单。

有写权限时在本仓库创建任务分支；没有写权限时从 fork 提出 PR。
PR 目标是 main，一次解决一个清楚的问题。
仅当完成整个 Issue 时使用 Closes；部分进展使用普通引用。

## 检查与评审

提交前检查 git diff：标题、URL、分类应与说明一致，不能重复或遗漏已有资源。
目前以人工检查为主，请在 PR 中写明实际检查了什么，不声称自动测试已通过。
维护者核对范围、来源和分类后决定是否合并；合并后核对 main 与 Issue 完成条件。
```

将来第 12～14 章引入程序和测试后，应更新这份指南的验证方法；不要今天就要求贡献者运行尚不存在的命令。

## 用表单减少来回追问

在 `.github/ISSUE_TEMPLATE/resource.yml` 写入以下完整 YAML。YAML 依靠缩进表示结构，请用空格保留层次：

```yaml
name: 推荐学习资源
description: 提交一个来源清楚、用途明确的资源建议
title: "[资源] "
body:
  - type: input
    id: resource-title
    attributes:
      label: 资源标题
      placeholder: 例如某份官方教程
    validations:
      required: true
  - type: input
    id: resource-url
    attributes:
      label: 资源链接
      placeholder: https://example.com/tutorial
    validations:
      required: true
  - type: dropdown
    id: category
    attributes:
      label: 建议分类
      options:
        - Git
        - GitHub
        - Python
        - 需要讨论的新分类
    validations:
      required: true
  - type: textarea
    id: reason
    attributes:
      label: 推荐理由与完成条件
      description: 说明帮助谁解决什么问题，以及如何确认收录完成。
    validations:
      required: true
```

`example.com` 是提示占位，不是要加入清单的资源。`required` 要求填写信息，并不判断链接真实性；表单也没有检查 CSV 是否重复。这里不设自动 labels、assignees 或 projects，避免依赖尚未创建的标签、人员或看板。Issue 表单的 name、description、body 和字段结构见[官方语法](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)。

在 `.github/pull_request_template.md` 中写入：

```markdown
## 解决什么问题

相关 Issue：
<!-- 只有完整解决该任务才使用 Closes #实际编号。 -->

## 主要修改

说明修改了哪些资源或约定，为什么这样改。

## 实际检查

- [ ] 已检查差异只涉及本次范围
- [ ] 已核对资源标题、链接、分类及重复情况（不适用时说明）
- [ ] 已确认未删除其他有效内容

其他检查与未验证部分：
```

PR 模板只是预填描述，不会强迫人认真评审，也不能证明勾选内容真实。文件需进入默认分支，后续新建 PR 才能使用；本次添加模板的 PR 仍需自己写清说明。[PR 模板的位置与生效条件](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)

合并方式也属于需要公开的维护约定。维护者应在 CONTRIBUTING 中说明是保留原始分支提交、按 PR 合成一个提交，还是要求提交已经整理成可重放的独立步骤；选择依据见第 8 章。对于本书这个短期、小任务分支，可以补充“一个完整资源变更通常使用 Squash and merge；需要保留各提交关系时先在 PR 中说明”。这是一条可讨论的项目约定，不是必须对所有贡献强制采用 squash。维护者确认合并时，还需核对最终提交说明，贡献者则以目标仓库实际生成的提交追踪交付版本。
## 访问权限与评审责任分别配置

自己能管理 resource-nav，是因为你是所有者。个人仓库区分 owner 与 collaborators；组织仓库还有更细的角色，不能把组织的 triage、maintain 等界面逐项套到个人仓库。公开可读也不等于所有人能改文件或管理设置。只在确实需要共同维护时邀请可信协作者，不要为了获得一次评审就授予不必要的管理权限。[个人仓库权限](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)

如果长期由某人负责某些路径，可以使用 `.github/CODEOWNERS`。下面是可替换后使用的完整小例子；`YOUR_LOGIN` 必须改成真实用户名：

```text
/README.md @YOUR_LOGIN
/CONTRIBUTING.md @YOUR_LOGIN
/resources.csv @YOUR_LOGIN
/.github/ @YOUR_LOGIN
```

所有者必须有对应仓库的写权限；把名字写进文件并不授予权限。GitHub 使用 PR 目标分支上的 CODEOWNERS 判断应请求谁评审；Draft 转为可评审状态时也会涉及代码所有者请求。单人仓库给自己列责任可以作为说明，但不会让你拥有批准自己 PR 的能力，也不保证自己的 PR 得到自动自我评审请求。[CODEOWNERS 的条件与行为](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

本章主线只需贡献说明和模板，CODEOWNERS 可在有稳定协作者时再加入。文件表达责任，必需代码所有者批准属于另外的合并规则。等第 14 章拥有真实检查及可行的评审安排后再配置门禁；只有一个参与者时，不要求自己等待不存在的第二位批准者。

## 从新贡献者的入口验收

检查差异，提交上述四个文件的变化，复用第 8 章流程开 PR 并合入 main。不要将外部贡献目录中的改动混进来。合并后从仓库首页点击贡献指南，确认相对链接能打开；点击 New issue，选择“推荐学习资源”，确认四个输入区可见。可以填写草稿检查必填提示，不必提交一条无真实需求的 Issue。

下一次有真实修改时，检查新 PR 描述是否预填模板；不要把模板文件已经存在等同于已验证平台加载。若没有出现，先看文件路径与默认分支，再检查是否通过其他模板选择入口创建。没有第二位读者实际试用时，只能说入口和内容已自查，不能说协作流程已由他人验证。

完成后，资源导航有了可阅读的贡献入口、可填写的需求表单和可说明证据的 PR 模板。接下来可学第 11 章[让多项工作有可见的进度](<现代 GitHub：让多项工作有可见的进度.md>)；若暂时只有一个任务，可直接进入第 12 章[让资源导航可以运行和验证](<现代 GitHub：让资源导航可以运行和验证.md>)。
