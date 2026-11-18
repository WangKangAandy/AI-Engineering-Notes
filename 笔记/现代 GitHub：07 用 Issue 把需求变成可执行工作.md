---
title: 现代 GitHub：用 Issue 把需求变成可执行工作
summary: 把新增学习资源的想法写成可验收的需求，再用子 Issue、依赖和负责人组织实际工作，为 PR 评审准备清楚的目标。
tags:
  - github
  - issues
  - collaboration
created: 2026-11-18
status: learning
---

# 现代 GitHub：用 Issue 把需求变成可执行工作

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

这是第 7 章。前一章是[改错以后如何恢复](<现代 GitHub：06 改错以后如何恢复.md>)；全书入口见[导读](<现代 GitHub：00 导读.md>)。

前六章已经让你能在自己的 `YOUR_LOGIN/resource-nav` 仓库修改和同步文件。现在 `main` 上有 README 和 `resources.csv`，清单至少包含 GitHub Docs、Python Docs 两条资源。我们要补充 Git 学习资源，并让新读者知道这些分类的区别。本章先把任务讲清楚，下一章再修改文件。

“丰富资源导航”听起来合理，但接手的人会立刻遇到三个问题：加什么、放在哪、怎样才算结束？Issue 是保存这场讨论及其结论的地方。它既能记录软件故障，也能承载文档、资源整理和调查工作。不必等代码出现错误才使用它。[Issues 入门](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/quickstart)

## 从模糊想法写到可验收的需求

先在仓库 Issues 中搜索 `Git`，同时查看 Open 和 Closed。已经有人提出同一需求时，应阅读原讨论，补充缺少的证据，而不是再建一份。第 2 章完成的初始清单任务与这次新增资源不同，可以分别跟踪。

点击 New issue，选允许的空白 Issue 或按现有模板填写。标题写“补齐 Git 入门资源与分类说明”，正文如下：

```markdown
## 现状
resources.csv 已收录 GitHub Docs 和 Python Docs，但缺少 Git 本身的学习资源。
README 还没有解释 Git 与 GitHub 分类的区别。

## 预期结果
新增 Pro Git 在线书籍，并在 README 中说明资源分类和人工维护方法。
这次只改清单与说明，不引入 Python 程序、CI 或网页部署。

## 完成条件
- resources.csv 中恰有一条 Pro Git，链接为 https://git-scm.com/book/en/v2。
- Pro Git 使用 Git 分类；已有 GitHub Docs、Python Docs 及其他有效条目保留。
- 表头仍为 title,url,category，每条资源保留这三个字段。
- README 解释 Git、GitHub、Python 分类，并说明新增资源前要检查重复链接。
- 说明与 main 上的实际清单一致。
```

这里选择的是 Git 官方网站托管的 [Pro Git 在线书籍](https://git-scm.com/book/en/v2)。链接属于 Git 本身的学习资料，所以分类为 Git；GitHub Docs 讲托管平台，仍归 GitHub。分类没有天然唯一答案，但一个仓库需要可解释、能持续使用的约定。

提交后记下真实编号。本书接下来用父项 `#20`、子项 A `#21`、子项 B `#22` 表示关系，**这些是占位编号**，不能照抄到实际仓库。若你之前自行增加过 Pro Git，应先核对是否已经满足要求；不要为了复现教程制造重复资源。可以把 A 改为纠正现有条目的标题、链接或分类，再按实际差异继续。

## 何时拆成子 Issue

一个人一次提交就能完成的小修改，通常一个 Issue 足够。本例为了学习分别评审清单和说明，把父任务拆为两个能独立验收的部分：

| 工作 | 改动与完成条件 |
| --- | --- |
| A：新增 Pro Git 资源 | 仅修改 resources.csv；新增指定标题、链接和 Git 分类，保留现有有效内容及三个字段 |
| B：说明资源分类与维护方法 | 仅修改 README；解释 Git、GitHub、Python 分类，以及新增前检查链接重复、提交时核对差异的方法 |

子 Issue 有自己的编号、讨论、负责人和状态。父子关系表示组成关系，不自动创建分支，也不表示谁必须先做。只有一条“检查拼写”的提醒可以写成正文的 `- [ ]` 任务列表；需要独立讨论、负责人或 PR 时，再给它一个独立 Issue。

在父 Issue 描述下方选择 Create sub-issue，为 A 填写标题和上表的完成条件；再创建 B。如果先前已创建这两项，用旁边菜单的 Add existing issue 选择它们，避免复制。最后分别打开 A、B，确认其父项指向实际的父 Issue；父页面应列出两项。管理子 Issue 需要至少 triage 权限，自己拥有的练习仓库可以操作。仅在正文写 `- [ ] #21` 是引用，不能代替原生父子关系。[添加子 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)

## 用依赖表达真正的前提

我们要求 B 的说明以已经合并的清单为准，因此本例将 B 的最终验收放在 A 之后。这是工作约定：B 的文字可以先起草，但 A 的资源和分类尚未确定时，不应宣告说明已与最终清单一致。

打开 **B**，在右侧 Relationships 选择 Mark as blocked by，再选择 **A**。B 的 Blocked by 应指向 A；A 相应显示 Blocking B。方向选反会表达完全不同的前提。父子关系回答“属于什么”，依赖回答“在等什么”，它们可以同时存在。[创建 Issue 依赖](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)

依赖关系是协作信息，不是阻止合并的技术门禁。如果后来决定两项能独立完成，回到 Relationships 调整依赖，并说明决定即可。添加依赖同样需要至少 triage 权限；找不到入口时先检查仓库与权限，不需要安装机器人来完成本章。

## 少量字段就能让工作找得到

在 A 的 Assignees 选择自己，表示由你负责推进。给 B 也可以选择自己，但这不要求你立刻同时开始两件事。负责人是推进责任，并不表示只有这个人可以贡献。

Labels 是可叠加的标签，用来按主题检索。说明任务 B 可选已有的 `documentation`；A 可用已有的 `enhancement`，没有合适标签时暂留空也不影响工作。不要把“未设标签”理解成“不能提交 PR”。

Type 则是工作类别，例如 Task、Bug、Feature。当前 GitHub 支持组织和个人账号管理 Issue types；有 Task 可选时，本例选 Task，没有时按当前界面继续，不必为三条练习任务先设计全套分类体系。[管理 Issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types)

回到 Issues 列表，输入：

```text
is:issue is:open assignee:@me
```

你应看到分派给自己的未关闭任务。再加 `label:documentation` 会缩小到说明类工作；若结果消失，先移除标签筛选，而不是重新创建 Issue。Milestone 用于归集一个阶段或版本的工作，Projects 用于跨任务安排进度，第 11 章再用它们解决真实的组织问题。

## 进展记录要能改变下一步判断

在 A 下写“准备新增 Pro Git，先核对是否已有相同 URL；完成后只提交 resources.csv”，比“处理中”更能帮助协作者判断范围。如果反馈要求更换链接，先更新完成条件，再实施；后来接手的人不应靠翻遍评论猜当前决定。

Open 只表示尚未关闭。一个 Open Issue 可能还没开始，也可能已经有待评审的 PR。需要别人处理具体问题时才 @ 对方，提及会带来通知。

本章结束时，应有一个描述整体目的的父 Issue，以及 A、B 两个子 Issue；B 的依赖指向 A，A 有负责人，三项都还未完成。仓库文件没有因为创建这些对象而变化。下一章的第一个 PR 只完成 A，因此只声明关闭 A；第二个 PR 完成 B，最后再对照父项整体验收。关闭但选择 Not planned 表示不再计划做，并不是已经实现；Reopen 也只改变工作项状态，不会回滚文件。[关闭 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue)

继续阅读第 8 章：[用 PR 完成评审与验收](<现代 GitHub：08 用 PR 完成评审与验收.md>)。
