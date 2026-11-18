---
title: 现代 GitHub：10 从构建结果到可恢复发布
summary: 保存一次构建的产物和来源信息，将静态页面部署到 Pages，创建版本记录并演练回滚。
tags:
  - github
  - deployment
  - release
created: 2026-11-18
status: draft
---

# 现代 GitHub：10 从构建结果到可恢复发布

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

第 9 章证明了检查通过，但“检查通过”不是“已经发布”。本章把同一次构建的产物、提交、审批、网页和回滚连接起来。

## 先统一三个对象

构建目录是 runner 上生成的文件；artifact 是一次 run 保存或传递的输出；Deployment 是把产物放进运行环境；Release 是围绕版本组织说明和附件。它们有不同的生命周期，不能因为页面生成成功就说已经发布。

在 build job 中上传 `site/`，可用 job output 传递资源数量或摘要；部署 job 用 `needs` 等待 build，再下载 artifact。若不同 job 各自 checkout 和 build，会产生两次可能不同的结果，必须明确哪一个是发布依据。保存 provenance 时记录 repository、commit SHA、run ID、attempt 和资源数量；它是追溯信息，不是加密签名。

## 用 Pages 完成一次交付

在 Settings → Pages 选择 GitHub Actions。新增 Pages workflow：build 运行校验、测试和 build.py，上传 Pages 专用包；deploy 使用 `needs: build`、`pages: write`、`id-token: write` 和 `github-pages` Environment。Environment 的 required reviewer、分支限制和 wait timer 需要在设置页配置，YAML 中只写环境名不会自动创建保护规则。

合并 workflow 后打开 Actions，找到对应 main push 的 run。build 成功后，deploy 应等待审批；在 Review deployments 中核对提交和构建结果，再批准。打开站点，确认页面内容来自当前资源清单。拒绝另一次部署时，已有页面应保持旧版本；拒绝本次运行不是删除现有站点。

Artifact 下载时使用对应 run ID，而不是列表中随便一个同名产物；解压后核对 index.html 和 provenance。`gh run download` 的 `--repo` 应显式指向自己的 resource-nav，避免本地 checkout 的远端配置造成误取。

## Release 和回滚

从成功部署 run 的提交链接复制完整 SHA。创建 draft Release 时，标签和 target 必须指向这个已验证 SHA；Release 的源码压缩包不等于 Pages 构建包。发布说明写清 PR、run 和部署页面。

演练回滚时修改页面标题或资源显示，经 CI、合并和 Pages 审批后确认新版本，再从合并后的 PR 创建 Revert PR。若使用 Squash，回滚对象是进入 main 的新提交；若 revert 产生冲突，使用 `git revert --continue` 或 `git revert --abort`，不要在共享 main 上 reset 或强推。回滚也要重新走 CI 和部署审批，不能把“生成反向差异”当成已经恢复。

## 交付后的维护入口

记录部署 SHA、artifact/run、Release 和页面 URL。发现问题时先判断是输入、构建、artifact、审批、部署还是浏览器传播；每次修复产生新的提交和新的记录。本章结束时，你能从页面追到运行、产物、提交和 PR，并用新的反向提交恢复静态站点。
