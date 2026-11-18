---
title: 现代 GitHub：将协作方法迁移到 Cursor
summary: 将资源导航的一次受控任务迁移到 Cursor Cloud Agents，核对独立的账号、GitHub 授权、环境和验收结果。
tags:
  - cursor
  - github
  - agents
created: 2026-11-16
status: learning
---

# 现代 GitHub：将协作方法迁移到 Cursor

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[现代 GitHub：00 导读](<现代 GitHub：00 导读.md>)。

这是第五部分的替代路线。你已经会描述有边界的任务、读 diff、运行测试和验收 PR；现在把这些方法迁移到 Cursor。选择现成服务不需要先注册自己的 GitHub App。你需要授权 Cursor 已有的集成访问练习仓库，不能把“安装服务 App”和“自己开发 App”混为一谈。

## 接入的是同一个仓库，不是同一个会话

Cursor Cloud Agents 在云端独立 VM 中克隆仓库、建立分支并推送修改。它不继承 Copilot 的会话、PAT 或 Cloud 环境；本地 Cursor 中可用的 Python，也不能证明云端已经可用。[Cloud Agents 概述](https://cursor.com/docs/cloud-agent)

准备自己的 Cursor 账号，查看当前 Cloud Agent 资格、计费和可用模型。登录 Cursor Dashboard，在 Integrations 的 GitHub 连接入口授权现成 Cursor GitHub App；GitHub 安装页优先选 **Only select repositories**，只勾选自己的 `resource-nav`。确认实际安装账号、仓库和请求权限后完成。若仓库不在列表，先看安装范围和当前 Cursor 账号，不要为排错直接扩大到所有仓库。[GitHub 集成](https://cursor.com/docs/integrations/github)

授权让服务有能力读写被选择的仓库，不能证明每次任务都得到你的合并许可。本专题仍要求 Agent 只交付分支与 PR。

## 完成一次小任务

进入 [Cursor Agents](https://cursor.com/agents)，或在桌面 Agent 输入框下选择 **Cloud**。选择 `YOUR_LOGIN/resource-nav` 和基础 `main`，核对环境。若出现环境准备向导，让它先验证 Python 3 和三条项目命令，不安装无关框架或外部服务。Cloud 环境可通过快照或环境配置维护；本项目只用标准库，不需要为展示功能添加依赖。[环境设置](https://cursor.com/docs/cloud-agent/setup)

如果尚未做第 19 章，使用其中的空 category 测试任务。如果已经合并该测试，改用下面这个仍然有价值的小任务：

```text
读取 test_catalog.py，检查空白字段是否已覆盖 url。
如果缺少该用例，只在测试文件新增一项空 url 被拒绝的测试；
如果已覆盖，说明具体测试位置，不制造无意义改动。
不要修改 catalog.py、workflow 或 resources.csv。
在仓库根目录执行 python -m unittest discover -v、
python catalog.py resources.csv、python build.py。
有变更时创建面向 main 的 PR，不批准或合并；
报告最终 diff、实际命令及结果，不能运行的项目明确说明。
```

在 Agent 页面查看日志与 diff。检查它用的是项目根目录，不是空目录里的另一个新项目；测试必须发现并执行已有用例。如果只有“建议运行命令”而没有结果，要求补充实际输出或由自己在 PR 分支运行。

从 Agent 的结果打开 PR；没有 PR 时通过其受支持的创建 PR 操作交付分支。核对 base `main`、改动范围和 Resource CI 当前提交的结果，再按第 8 章完成评审。Cursor 的总结、GitHub PR 检查和人工验收仍是三个独立事实。

## 规则只迁移需要的部分

Cursor 支持根 `AGENTS.md` 和 `.cursor/rules/*.mdc`。如果仓库已经用 AGENTS.md 维护共同事实，先检查客户端实际读取，不要复制成另一份长期漂移的规则。第 20 章的 `.github/copilot-instructions.md` 是 Copilot 专属入口，不能假定 Cursor 自动应用；可以把共同事实移到 AGENTS.md，再让各自入口只指向它，并用只读问答和日志验证读取。迁移必须通过 PR，保留唯一事实来源。[Cursor Rules](https://cursor.com/docs/rules)

规则不是权限。即使规则写着“不合并”，最终仍要检查授权范围和仓库门禁。网上找到的 Skill 还可能带脚本和外部调用，先阅读再启用；本练习无需安装额外 Skill。

## Cloud Agent、Bugbot 与 Automations

Cloud Agent 是执行具体任务的入口。Bugbot 主要面向 PR 审查；Automations 是按触发条件重复调用任务的产品能力。这三个入口解决不同问题，不要在首次 Cloud 任务中同时启用，再把三份输出当成一次任务的结果。[Cloud Agents](https://cursor.com/docs/cloud-agent)

需要自动化时，复用第 22、23 章的方法：先限定事件和写入对象、预览一次、核对结果，再考虑重复触发与预算。但 Cursor 的触发器和凭据必须按自身产品配置；gh-aw 的 Markdown 与 lock 不会自动变成 Cursor 自动化。

## 结束和撤销

不再需要任务时，在该 Agent 页面停止运行，并确认状态。随后检查它已经推送的分支和 PR；停止不撤回已有修改，归档也不表示取消了任何独立自动化。如果只做本次实验，回到 GitHub 的 Installed GitHub Apps 管理入口，移除 `resource-nav` 授权或卸载 Cursor App；同时查看 Cursor 是否另有运行中的任务和已启用自动化，分别停止。

本专题的完成结果是一次独立的 Cursor 任务、对应 diff 与实际测试证据，以及清楚的授权和退出状态。不要求重做整套 Actions，也不要求注册自有 App。

本文依据 2026-11-18 官方文档核对入口与能力，未启动 Cursor Cloud 任务或安装远端 App。账号资格、费用和实际运行结果以读者当前服务页面为准。
