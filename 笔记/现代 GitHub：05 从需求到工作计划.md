---
title: 现代 GitHub：05 从需求到工作计划
summary: 使用 Issue、子任务、依赖和 Projects 把资源导航的工作组织成可完成、可追踪的计划。
tags:
  - github
  - collaboration
created: 2026-11-18
status: draft
---

# 现代 GitHub：05 从需求到工作计划

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章解决的是“下一步该做什么、谁负责、怎样判断完成”，不是把所有任务都拆成树。前置是资源导航已经有 README 和 resources.csv，并且你理解本地分支和 PR 的基本关系。

## 先把问题写成一个完成条件

假设资源列表里需要补充 Pro Git，并在 README 解释 Git、GitHub、Python 三个分类。Issue 不写“把项目完善一下”，而写清现状、结果和边界：

```markdown
## 现状
资源清单还没有 Pro Git，README 也没有解释三个分类的区别。

## 结果
新增 Pro Git 资源，并在 README 写出分类规则。

## 完成条件
- resources.csv 新增一条不重复的 Pro Git 资源，分类为 Git。
- README 说明 Git 是版本控制工具，GitHub 是托管与协作平台，Python 是编程语言。
- 本次不修改校验程序、不配置 Actions。
```

完成条件是给作者、评审者和未来维护者看的共同判据。它不要求预先决定实现细节，但要让接手者知道什么时候可以停止。

## 什么时候拆成子任务

如果一项工作可以由不同人独立提交 PR，或需要不同的讨论与验收，就可以拆成子 Issue。本例可拆成：A 新增 Pro Git，B 补 README 分类说明。B 依赖 A，是因为 README 要引用最终分类；如果两项由一个人一次完成，保留一个 Issue 也合理。

在父 Issue 中创建子 Issue 或添加已有 Issue，核对父子关系和编号。父项描述整体目的，子项描述可交付的片段；父子关系不会自动创建分支或 PR。依赖关系表达先后顺序，也不会替代 CI 或分支保护。[子 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) · [Issue 依赖](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)

## 让任务可被找到

给任务加负责人、标签或类型，是为了让团队找到它和判断责任，不是为了装饰页面。`Assignee` 回答谁推进，`Label` 回答涉及什么，`Project` 回答它在更大的工作视图中处于哪里。不要因为某个字段存在就强行填写一套组织流程。

Projects 的状态表示项目视图中的进度；Issue 的 Open/Closed 表示工作项状态；PR 的 Open/Merged 表示合并提案状态。三者相关但不是同一个事实。一个项目项可以显示 Done，而 Issue 仍需按完成条件验收，反过来也一样。

## 用 Projects 看下一步，而不是复制 Issue

当 A、B 都还没有完成时，把父项和子项加入一个简单的 Board 或 Table，保留 Todo、In Progress、Done 三个状态。将 B 标为被 A 阻塞，读者就能在看板上看到瓶颈；不需要先建复杂字段、路线图或自动化。

新建的开放任务可以实际拖动一次：从 Todo 移到 In Progress，完成 PR 后再移到 Done，并回到 Issue 检查它是否真的关闭。已有已关闭的任务保持 Done，不为练习重新打开；只有评论没有 Issue 对象时，评论只能当作证据，不能当作看板任务。

## 本章结束状态

本章只创建和组织 Issue、子任务、依赖及 Projects 视图，不修改资源文件。下一章将选择 A 或一项真实子任务，经过 PR 评审、合并和验收；父项只有在全部完成条件都满足后才关闭。即使你跳过 Projects，子任务和 PR 的主线仍然可以继续。
