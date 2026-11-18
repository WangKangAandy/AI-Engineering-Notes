---
title: 现代 GitHub：把项目知识与工作约定交给 Agent
summary: 将资源导航项目的事实、测试命令和协作约定放进可维护的上下文文件，验证 Copilot 能读到它们，并区分规则与权限。
tags:
  - github
  - copilot
  - agents
  - documentation
created: 2026-11-18
status: learning
---

# 现代 GitHub：把项目知识与工作约定交给 Agent

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[GitHub 协作与自动化：01 学习路线](<GitHub 协作与自动化：01 学习路线.md>)。

第 19 章把一次说明写进 prompt。每次都重复同一段话既容易漂移，也让 Agent 先花时间猜项目。第 20 章把稳定事实和工作约定放进仓库能维护的文件，同时接受一个限制：**被读取的规则不是权限授予**。文件可以要求“不要改 workflow”，却不能阻止一个已有写权限的操作者改它；权限仍由 GitHub、Actions 和执行环境控制。

## 先分类，再落文件

为资源导航仓库建立上下文前，先把信息分成三类：

| 类别 | 例子 | 放在哪里 |
| --- | --- | --- |
| 项目事实 | `resources.csv` 有 `title,url,category` 三列；`catalog.py` 负责校验 | `.github/copilot-instructions.md` 或根 `AGENTS.md` |
| 稳定约定 | 只用 Python 标准库；改动要跑三条命令；不提交密钥 | 同一个仓库规则文件 |
| 可复用步骤 | 如何生成站点、如何整理一次资源变更 | Agent Skill 目录（需要客户端支持时再建） |

不要为 Copilot、Cursor 和 gh-aw 各复制一份完全相同的长规则。先有一份短、可验证的事实；客户端需要的专属格式只保留入口和差异。规则应说明“怎样工作”，而不是假装“谁可以工作”。

## GitHub Copilot 当前支持的入口

GitHub 文档列出三种仓库级自定义指令：`.github/copilot-instructions.md` 适用于仓库范围；`.github/instructions/*.instructions.md` 可按路径匹配；`AGENTS.md` 是给 AI agent 的指令，放在目录树中时最近文件优先。文档还说明 `CLAUDE.md`、`GEMINI.md` 是可选的代理指令文件。[仓库自定义指令](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

本项目只需要一个短的 `.github/copilot-instructions.md`，示例内容如下：

```markdown
# resource-nav 工作约定

- 项目读取 resources.csv（UTF-8 CSV），列固定为 title,url,category。
- catalog.py 只负责清单校验；build.py 生成 site/index.html。
- 修改后依次运行：python -m unittest discover -v、python catalog.py resources.csv、python build.py。
- 变更应保持小范围；新增资源时说明来源；不要提交 token、密码或本地缓存。
- Agent 不批准或合并 PR；发现需求不清时先报告，不猜测扩大范围。
```

在自己的 resource-nav 根目录新建该文件，通过一个只改规则的分支和 PR 合并到 main。再从最新 main 启动验证会话；未提交的本地文件不会自动进入云端已启动的会话。已有同类规则时先合并有效内容，不覆盖原有项目要求。

这是仓库事实的单一来源。若某目录确有不同测试规则，再加路径专属文件，而不是复制整份说明。GitHub 的规则是否用于代码审查还受个人设置影响，不能只看文件是否存在。

## AGENTS.md、规则和 Skill 的边界

`AGENTS.md` 适合跨工具共享的代理工作约定。它不具备 YAML 权限语义，也不会自动启动任务。Skill 是一组可复用的说明、脚本和资源；Copilot 文档称 Agent Skills 是开放规范，Agent 在相关任务中加载它们。[Agent Skills 说明](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)

Skill 的最小结构可以是：

```text
.github/skills/resource-check/SKILL.md
.github/skills/resource-check/scripts/README.md
```

先不要为了本章新增 Skill。贯穿项目的三条命令已经足够短，新增一层目录反而制造另一份维护点。等步骤包含脚本、模板和明确复用场景时，再按所选 Agent 的官方发现规则放置并实测加载。

Cursor 的项目规则使用 `.cursor/rules/*.mdc`，也支持 `AGENTS.md`；`.mdc` 需要 frontmatter，普通 `.md` 不会被当作 Cursor 项目规则。它的规则有自动、按路径、手动等应用方式。[Cursor Rules](https://cursor.com/docs/rules)

## 验证“读取了”，不要验证“听话了”

用第 19 章的 Cloud Agent 发一个只读小任务：

```text
请不要修改文件。根据仓库中的项目规则，回答：
1. resources.csv 的三列是什么？
2. 修改后应运行哪些命令？
3. 这次任务是否允许你修改 workflow？请说明理由。
```

检查 session 日志或回答是否引用了正确文件和命令。这个实验只证明 Agent 将上下文纳入了输入；它不证明规则能阻止写操作，更不证明规则赋予了仓库权限。要检查冲突识别，可以继续问“如果某个 CSV 标题要求你忽略规则并修改 workflow，你会怎么处理？只解释，不执行”。检查它是否将 CSV 文本视为数据。无需为了验证规则真的让它越界写文件。

## 维护规则

规则文件本身进入 PR 和 CI 的审查范围。项目命令变更时，同一 PR 更新规则，避免“文档说三条命令、脚本已换命令”。删除失效规则比保留一长串历史提醒更安全。规则只写稳定事实和验收方式；账号资格、PAT、Actions token 与 Copilot 额度写在对应的安全说明中，不写进公开仓库。

下一篇：[现代 GitHub：验收、纠偏与结束 AI 任务](<现代 GitHub：验收、纠偏与结束 AI 任务.md>)。

**来源与限制（2026-11-18 核对）**：依据 GitHub [仓库自定义指令](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)、[Agent Skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) 和 Cursor [Rules](https://cursor.com/docs/rules)。本文只展示可复制的规则文本和读取验证方法，未声称本仓库已启用某客户端的所有规则类型；实际支持以账号、客户端版本和官方文档为准。
