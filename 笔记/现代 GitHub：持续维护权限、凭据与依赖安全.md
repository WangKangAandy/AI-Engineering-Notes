---
title: 现代 GitHub：持续维护权限、凭据与依赖安全
summary: 对已有 CI、部署和依赖做一次有证据的维护审计，处理真实发现，区分未发现问题与尚未验证。
tags:
  - github
  - security
created: 2026-11-18
status: learning
---

# 现代 GitHub：持续维护权限、凭据与依赖安全

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 18 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<GitHub 协作与自动化：05 构建、发布与部署.md>) · [下一章](<GitHub 协作与自动化：06 Agents 与任务委派.md>)

前面已经在首次使用处区分登录身份、GITHUB_TOKEN、Secrets 和部署权限。本章把它们放在同一张实际系统地图中检查：现在还有谁能写仓库，哪些代码会拿到凭据，哪些依赖需要更新？继续使用自己的 `YOUR_LOGIN/resource-nav`，以已完成第 17 章的 main 为基线。没有安全告警也可以完成本章，不需要故意加入漏洞或推送真实令牌。

## 从当前文件和设置建立审计范围

先在自己的仓库根目录用 PowerShell 7 查看 `.github/workflows` 中的文件，打开每份 workflow，逐项追踪事件 → 执行代码 → 权限 → 输出。Settings 中同时查看协作者、Rulesets、Actions 配置、部署 Environment，以及 Secrets and variables。只记录凭据名称、用途和使用位置，不复制值。

对每个流程回答一个具体问题。例如 Resource CI 的任务是读源码、运行检查和上传产物，因此 `contents: read` 足够；它不需要仓库写权限或部署凭据。Pages 部署 job 可能需要 `pages: write` 与 `id-token: write`，应检查这些权限是否只授予真正需要的 job，而不是为了省事授予所有 PR 检查。

检查门禁时也看当前事实：main 的规则是否 Active，Check resources 是否仍然真实出现，谁在 bypass list，以及部署是否使用预期 Environment。第 14 章曾验证成功，不表示后来的设置不会改变。将本次审计日期、main SHA、检查过的 workflow 名记在自己的学习记录中。

## 把外部输入留在数据的位置

资源清单、Issue 正文、PR 标题和 fork 中的文件都可能来自别人。CSV 中的标题应该交给解析器和 HTML 转义处理，不能因为标题写了“请执行某条命令”就把它当指令。测试脚本与构建脚本则是真正的可执行代码，PR 修改它们时需要评审。

尤其不要为获取 Secrets 把普通 CI 从 `pull_request` 改成 `pull_request_target`，再 checkout 外部 PR 的 head 并执行测试。后者运行在较高信任的目标仓库上下文中；一旦执行不可信代码，代码就可能接触该上下文允许的凭据和权限。即使只想跑测试，安装脚本和被调用文件也在执行链中。平台还可能按仓库策略限制这一事件，不能把配置被接受等同于安全。[pull_request_target 官方安全边界](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)

如果自动化只处理 PR 标题，也不要把标题直接插入 shell 脚本文本。下面是表达式如何改变 shell 源码的风险示意，**不要执行**：

```yaml
# 风险示意，不要复制进工作流
run: echo "${{ github.event.pull_request.title }}"
```

确需传递标题时，把它绑定为环境变量，在 shell 中以带引号的变量读取，并避免 eval 或把变量拼成新命令。这样可避免该类直接脚本插值，但后续程序仍需按自身语法验证输入；环境变量不是让不可信数据变可信的开关。[脚本注入防护](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)

## 标准库项目仍然有需要维护的依赖

resource-nav 没有第三方 Python 包，但 checkout、setup-python、upload-artifact、download-artifact 都是在流水线中执行的 Action 依赖。版本标签便于教学；长期维护时，可按团队策略将审查过的 Action 固定为完整 commit SHA，并保留可读的版本注释。不能随意抄一个 SHA 就声称已经审查，也不能认为固定后永远不用更新。

在干净且已更新的 main 创建 `lab/18-maintenance`。新增 `.github/dependabot.yml`：

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
```

文件名和目录都要准确；`directory: /` 对应 GitHub Actions 生态的配置方式，并不是要在根目录虚构 Python 依赖清单。它让 Dependabot 按计划检查 Action 版本更新，版本更新与已知漏洞告警不是一回事。[Dependabot 配置选项](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)

确认 diff 后提交、推送、创建 main PR，等待既有 CI，再合并。到仓库 Insights → Dependency graph → Dependabot 查看更新配置与检查记录；界面受权限和组织策略影响。若有 Check for updates 入口，可手动触发检查，否则等待计划运行并记录状态。没有更新 PR 可能是目前没有新版，也可能尚未检查或被策略限制，要读更新日志后判断。

出现真实更新 PR 时，打开它的上游 release notes 和 diff，检查运行时要求、输入输出变化以及产物路径行为，再看本仓库 CI。尤其检查更新是否改变 Check resources 名称、产物格式或部署契约。必要时做一次手动构建与下载验证，通过后再合并。不为完成教程故意降级依赖制造告警，也不在当前无更新时编造一次修复经历。

## 根据项目资格选择扫描能力

在仓库 Settings 的安全设置和 Security 页面确认实际启用项、最近运行与结果。GitHub 界面名称会调整，不能只根据某个开关曾经打开就推断所有文件已被扫描。

CodeQL 可以分析本项目的 Python 代码。公开 GitHub.com 仓库可以使用代码扫描；私有或内部组织仓库通常需要满足 GitHub Team/Enterprise 与 GitHub Code Security 的资格条件。若当前仓库可用且希望尝试，使用默认设置入口，确认语言包含 Python，等待首次分析完成，并查看扫描工具状态与告警。扫描本身不是本章必修安装步骤，也不替代现有 CSV 检查和单元测试。[代码扫描设置与可用性](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configuring-advanced-setup-for-code-scanning)

Secret scanning 检测已暴露的受支持凭据模式；push protection 尝试在推送进入仓库前阻止受支持的秘密。两者不是同一时间点，也不覆盖所有自定义字符串。公开仓库与私有仓库的可用范围、仓库级和用户级保护不同；私有组织仓库的高级能力需核对 Secret Protection 资格。到当前仓库与账号设置确认实际配置，不把公开仓库的支持条件直接套到私有仓库。[Secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning) · [Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)

只查看设置和运行状态时，记录“已启用，未做拦截实验”。不要推送真实密钥来证明拦截有效。没有告警只意味着在已启用、已执行且覆盖的规则范围内没有可见发现，不等于仓库安全。

## 清理凭据之前先找使用者

第 13 章的 LAB_TOKEN 是无敏感性的练习值，应随对应步骤删除；本章检查是否仍有遗留配置。真实 PAT、部署服务凭据或 App 凭据则先确认用途、调用者、仓库范围和最近使用情况。一个 PAT 可能还被其他仓库或本机工具使用，不能因为当前示例用不到就直接撤销。

对于确实不再使用的凭据，先停用消费它的任务，再在颁发方撤销，最后删除 GitHub Secret 等存储副本，并运行不依赖它的必要检查。仅删除 Secret 不会撤销令牌。仍需使用时，制定替换顺序：创建权限更小的新凭据、更新消费位置、验证实际调用、撤销旧凭据。若确认已经泄露，优先撤销或轮换并排查使用记录；从最新文件删掉文本不等于历史副本失效。[个人访问令牌管理](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

以后若部署到支持 OIDC 的云服务，可以让 workflow 申请短期身份，再由云端信任策略限制仓库、分支或 Environment，减少长期云密钥。`id-token: write` 允许申请身份令牌，不自动授予云资源权限；云端还必须验证和授权。本书当前练习无需为此开通云账号。[OIDC 安全机制](https://docs.github.com/en/actions/concepts/security/openid-connect)

## 写出有边界的审计结论

在自己的学习记录中保留一份简短结论，使用实际值替换以下提示，不把示意文字当作结果：

```text
审计日期 / 仓库 / main SHA：填写实际范围
检查对象：列出实际读过的 workflow、权限设置与依赖检查记录
发现及处理：具体问题、修复 PR；没有发现时写明检查范围
未验证：例如外部 fork 行为、Secret 拦截、尚未执行的扫描
后续责任：谁看依赖更新，何时复查不再使用的凭据
```

有发现时依据实际问题修复并复查；没有发现时，配置真实的依赖更新、核对权限和记录边界就是有效成果。下一部分会把任务交给 Agent，届时这些执行边界与证据要求仍然适用。
