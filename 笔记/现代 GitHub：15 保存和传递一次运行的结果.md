---
title: 现代 GitHub：15 保存和传递一次运行的结果
summary: 保存资源页面产物，跨 job 传递条目数量与文件，并把下载结果追溯到指定仓库、提交和运行。
tags:
  - github
  - actions
created: 2026-11-18
status: learning
---

# 现代 GitHub：15 保存和传递一次运行的结果

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 15 章。[全书导读](<现代 GitHub：00 导读.md>) · [上一章](<现代 GitHub：14 用 CI 和合并门禁保护修改.md>) · [下一章](<现代 GitHub：16 按需求扩展和改进工作流.md>)

第 14 章的 CI 已在自己的 `YOUR_LOGIN/resource-nav` main 上工作，**Check resources** 已成为必需检查。现在的问题是：runner 结束后，怎样拿到它生成的页面？另一个 job 又怎样知道自己拿到的是正确结果？

本章只保存和传递结果，还不发布网站。继续使用 Python 3.12、PowerShell 7 和相同清单。九项测试与构建成功的 main 是起点。

## 小结果与文件走不同通道

`needs: check` 让下游 job 等待 check；它不会把 check 的磁盘复制过去。条目数量这样的小型字符串结果可以声明为 job output，index.html 这样的文件需要上传为 artifact，再下载。

Artifact 是某次运行保留的文件集合，不是永久发布渠道，也不是缓存。它可能到期或被删除。本章用七天保留期，下载结果的名字叫 `resource-site`；不同 run 可以有同名 artifact，因此查找时必须同时指定 run。[Artifact 概念](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

## 用完整流程替换，保留门禁契约

从干净且已更新的 main 创建 `lab/15-artifact`。打开本书附件 [ci.yml 完整源文件](./_assets/modern-github/workflows/ci.yml)，通过 Raw/下载保存，将它**整体替换自己仓库的 `.github/workflows/ci.yml`**。它是第 14 章流水线的扩展版，不要另存为第二个同时触发的 CI 文件。

文件保留了 Resource CI、job ID check 和 Check resources，同时增加以下链路：

```text
check: 校验 → 九项测试 → 构建 → 写追溯记录 → 上传 resource-site
                       │             │
                       │             └─ output: resource_count
                       └─ site/index.html + site/provenance.json
                                     ↓
verify: 下载到 received-site/ → 对照数量与运行身份
```

先读 `Record provenance` 步骤。它再次通过 `load_resources` 计算条目数量，并写出 JSON：repository、sha、run_id、run_attempt 和 resource_count。环境变量由 GitHub 提供，不要求读者手工填 SHA。run_attempt 区分同一 run 的重跑尝试。

同一步把 `resource_count=实际数量` 追加到 `GITHUB_OUTPUT`。`id: metadata` 让其他配置能定位这个 step；job 的 outputs 再把 `steps.metadata.outputs.resource_count` 暴露给下游。verify 通过 `needs.check.outputs.resource_count` 读取，并放入环境变量 EXPECTED_COUNT，由 Python 转成整数。[Job outputs 的声明和读取](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs)

Upload site 上传 site/ 的内容，保留默认归档行为；没有文件时明确报错。verify 下载同名 artifact 到 `received-site`，拿到的是 `received-site/index.html`，不是 `received-site/site/index.html`。它不 checkout，也不重新构建，因此检查对象确实来自下载。示例采用 GitHub.com 托管 runner，版本与路径行为见 [upload-artifact](https://github.com/actions/upload-artifact) 和 [download-artifact](https://github.com/actions/download-artifact)。

下载后用 HTMLParser 数出页面 li 数量，与 output、JSON 中的数量比对；同时核对仓库、SHA、run ID。这个检查适用于当前每条资源对应一个 li 的页面结构。它能发现文件缺失、数量或身份不一致，却不能证明每个链接内容正确，更不是签名或防篡改证明。JSON 是同一个流程写的自述信息，需要结合 GitHub 上的运行记录判断可信度。

## 观察两台机器之间的传递

确认差异只包含预期流程修改，用第 9 章的方法提交、推送并创建面向 main 的 PR。在 Checks 中等待 **Check resources** 和 **Verify artifact** 都成功。展开第二个 job 的下载步骤与校验步骤，确认打印实际数量和 SHA。

第 14 章的规则仍只要求 Check resources；Verify artifact 是新增检查，不会自动变成必需。此次先人工等待它通过再合并。如果以后团队把产物验证也设为强制门禁，应等真实检查出现后再添加规则，并持续保留该名称。本书后续主线不要求新增这条规则。

合并 PR 后，在 Actions 中选择 Resource CI 的 main、push 运行，等两个 job 完成。PR 运行可能对应测试合并 SHA，发布时优先使用已合并 main 的成功运行，避免把待审查分支的产物当成主线版本。

打开这次 run 的页面，在 Artifacts 区下载 resource-site。解压后应看到 index.html 与 provenance.json。用浏览器打开页面，核对资源数量和文字；JSON 的 repository 与 sha 应对应这次运行。页面好看或文件存在，都不能替代 run 中的成功结论。

## 在终端下载指定运行

以下命令在 PowerShell 7 执行。YOUR_LOGIN 替换为自己的账号；RUN_ID 替换为列表中那次成功 main push 运行的数字 ID，不要原样粘贴占位符：

```powershell
gh run list --repo YOUR_LOGIN/resource-nav --workflow ci.yml --branch main --event push --limit 5
gh run view RUN_ID --repo YOUR_LOGIN/resource-nav --json databaseId,headSha,event,conclusion,url
```

确认事件、SHA 和结论后，选择仓库外一个全新目录。下面用系统临时目录，避免误把下载结果提交为源码：

```powershell
$artifactDir = Join-Path $env:TEMP ('resource-nav-artifact-' + [guid]::NewGuid())
gh run download RUN_ID --repo YOUR_LOGIN/resource-nav --name resource-site --dir $artifactDir
if ($LASTEXITCODE -ne 0) { throw 'Artifact download failed' }
Get-ChildItem -LiteralPath $artifactDir
Get-Content -LiteralPath (Join-Path $artifactDir 'provenance.json')
Start-Process (Join-Path $artifactDir 'index.html')
```

指定单个 artifact 时，gh 将内容解压到给定目录；正文文件路径因此直接是 `$artifactDir/index.html`。不指定名称下载多个产物时目录结构不同。[gh run download](https://cli.github.com/manual/gh_run_download)

找不到产物时，检查仓库和 run、上传步骤是否成功、是否已经过期。不要改成下载最新的某个文件来掩盖来源不明。重跑同一个 run 后，也应核对最新尝试和 provenance 中的 run_attempt；严格留存不同尝试还需要设计带尝试编号的产物名。

本章结束时 main 保留这份完整 ci.yml：check 上传 resource-site，verify 下载校验，必需检查名不变。下一章可按需跳读；第 17 章从这份流水线和可追溯产物继续。
