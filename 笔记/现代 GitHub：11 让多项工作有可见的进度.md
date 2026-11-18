---
title: 现代 GitHub：11 让多项工作有可见的进度
summary: 用一个小型 Projects 看板整理资源导航的已有任务，解释看板状态、Issue 关闭、里程碑与通知各自解决的问题。
tags:
  - github
  - projects
  - collaboration
created: 2026-11-18
status: learning
---

# 现代 GitHub：11 让多项工作有可见的进度

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

这是第 11 章，接续[从个人修改到共同维护](<现代 GitHub：10 从个人修改到共同维护.md>)。本章使用自己的 `YOUR_LOGIN/resource-nav` 和第 7、8 章产生的 Issue/PR，不改变资源清单或程序输入。只有一个任务时，Issues 列表往往已经够用；想同时看清“谁在做、等什么、下一项是什么”，再使用 Projects。跳过本章不影响第 12 章的代码实践。

Projects 是组织工作项的另一种视图。同一个 Issue 加入看板后，仍然保留原仓库的编号、正文和讨论。你可以在表格中按负责人查看，也可以在看板中按进度分列，不需要复制一套需求文本。[Projects 快速入门](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)

## 先确定要放进看板的工作

完成第 8 章的读者已经有父项“补齐 Git 入门资源与分类说明”，以及已关闭的 A“新增 Pro Git”和 B“说明资源分类与维护方法”。保留它们的真实完成状态，不要为了演示看板将已交付的任务重新打开。

下面完整的状态实验需要一条尚未完成、状态为 Open 的 Issue C。若这项检查尚未做，创建新 Issue，标题写“核对资源导航的新读者入口”，正文如下；若已有覆盖同一检查的 Open Issue，就使用它的实际编号，不重复创建。

```markdown
## 目的
检查 main 的首页能否让第一次访问的人找到资源清单与贡献指南。

## 完成条件
- 从 README 打开 resources.csv 和 CONTRIBUTING.md，确认链接可达。
- 核对 README 分类说明与当前清单一致。
- 在评论中写明检查的 main 提交及结果。
- 若发现内容错误，修正后再验收；不以发现了问题作为本任务完成。
```

C 可以是一项调查和验收任务，不一定产生文件修改或 PR。把自己设为负责人，确认页面确实为 Open，再执行后面的 Todo → In Progress → Closed/Done 实验。评论只能作为检查证据，不能当作可加入看板并切换状态的 Issue C。

如果第 10 章已经完成同一检查且存在 Closed Issue，就把它作为已完成记录加入 Done，跳过下面对 C 的拖动、执行和关闭实验，不将它重新打开。如果只有 PR 评论中的检查证据，就保留该证据，本次看板可以只加入父项、A、B；不为凑齐卡片重复制造任务。想完整练习状态流转时，等 main 的相关内容发生新变化后，再为该版本建立一次新的、尚未执行的入口检查。下文的四项和 Open 状态均以确有待完成 C 的主路径为前提。

## 创建自己的小看板

从 GitHub 个人资料进入 Projects，选择 New project，选择 Board 布局或空白项目后将视图切换为 Board。所有者选自己，名称写“资源导航维护”。这是账号下的 Project，不因为名称相同就自动包含 resource-nav 的所有 Issue。检查项目可见性，按练习需要选择；本例只放公开仓库的公开工作信息。

在项目中使用 Add item 或 Add items from repository，选择 `YOUR_LOGIN/resource-nav`，搜索实际编号并加入父项、A、B 和 C。若选择器先筛选了 Open，清除该限制再找已关闭的 A、B。也可以在每个 Issue 的 Projects 侧栏选择刚建的项目。加入后点击卡片标题，应能回到原 Issue，而不是打开另一个同名草稿。[创建项目与加入工作项](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)

项目中的 draft item 是暂记想法，还不是某个仓库的 Issue。本例用已有 Issue，因而不直接在底部输入标题后把草稿当成已创建任务。若误建草稿，可以移除该草稿再添加真实 Issue；不要删除原仓库对象来修复看板显示。

保留内置 Status 字段，只使用 Todo、In Progress、Done 三个值；界面若显示其他名称，按其实际值操作，或在字段设置中统一这三个名称。新增 Board 视图时选择按 Status 分组。将已验收的父项、A、B 放在 Done；只有待完成的 Open C 放在 Todo，复用的已完成 Issue 保持 Done。卡片上显示 Assignees 即可。这里不需要另设优先级、迭代、预估工时和多个审批阶段。

## 先看自动化，再移动卡片

Issue 的 Open/Closed 属于仓库对象；Project 的 Status 是进度字段。二者能够通过工作流联动，但不能仅凭“Done”这个词推断 Issue 已关闭。当前 Projects 提供内置工作流，新项目通常启用“关闭的 Issue/PR 设为 Done”和“合并的 PR 设为 Done”；也提供按状态变化关闭 Issue 的自动化。因此，必须先确认自己项目启用了什么。[内置自动化](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations)

打开项目右上角菜单 → Workflows。查看关闭、合并后更新 Status 的规则；本例保留它们。若已启用“状态改变就关闭 Issue”的工作流，先关闭这条反向规则，再继续以下实验。这样，C 的关闭由验收决定，Done 用于反映结果。不要根据模板名称猜测规则是否启用。

以下操作只用于前面确认尚待完成的 Open C；已完成路径跳至“用视图回答一个具体问题”，不执行状态实验。将 C 从 Todo 拖到 In Progress，再打开原 Issue：它仍应 Open。回到 main 的 README，点击两个入口并核对分类。到 Code 页面查看最新提交，复制其链接，在 C 评论里记录实际提交、检查内容和结果。示例记录形式是：

```text
检查 main 的提交：粘贴实际提交链接。
README → resources.csv：能打开，分类与说明一致。
README → CONTRIBUTING.md：能打开。
本次为人工页面检查，未运行自动测试。
```

不要复制“能打开”来代替自己点击。若发现坏链接，先保持 C 为 In Progress，按第 8 章从分支修复、评审、合并，再对合并后的提交重查。全部完成后关闭 C，回到项目观察是否自动变为 Done。若未变化，查看规则是否启用、对象是否确实加入此项目；也可在确认 Issue 记录后手动设 Done，并如实区分自动同步和手工调整。

这个过程留下了三种不同证据：看板说明工作的安排，Issue 保存检查结果，main 提交确定被检查的版本。任何一种都不能单独代替另外两种。特别是“关闭但未合并”的 PR 也可能被工作流放进 Done，Done 不等于代码已经交付。

## 用视图回答一个具体问题

在筛选栏试用 `assignee:@me`，查看自己的工作；再试用 `status:"In Progress"`，只看正在推进的项目项。字段值的名称若不同，应改用当前值。保存这个视图并命名“进行中的工作”。C 完成后，视图空了是合理结果；清除过滤后，实际加入的项目项仍应存在。跳过 C 实验的路径同样可以用这些筛选检查已完成记录。

如果还想看所有未关闭 Issue，可用 `is:issue is:open`。它筛的是原 Issue 状态，而 `status:Todo` 筛的是 Project 字段，这两个集合不保证相等。新需求出现时，可以因此发现“看板已 Done，但 Issue 还 Open”的不一致，再调查是否漏了验收或自动化设置。筛选与分组改变视图，不会删除工作项。[筛选 Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/filtering-projects)

第 7 章的依赖仍应在 Issue 中维护。B 等待 A 的原因不需要复制成一个新标签；阅读卡片时打开原 Issue 查看关系和讨论。Project 帮你发现阻塞，但不能自行解决前提。

Milestone 适合回答“某个版本或阶段包含哪些工作”，例如以后要交付“资源导航首版页面”，可以在仓库 Issues → Milestones 新建该阶段并把相关 Issue 归入。同一阶段可以包含 Todo、In Progress、Done 三种进度，因而 Milestone 与 Status 不是替代品。当前四项练习无需额外建立里程碑；更不要把一个截止日期当成系统会自动发布的指令。[关于里程碑](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)

## 通知负责提醒，不能代替安排

看板需要主动查看；通知用于提示有人提及你、请求评审或更新了你订阅的讨论。在仓库 Watch 菜单选择适合自己的范围，通常从参与及被提及的通知开始；需要持续跟进某条 Issue 时，在该 Issue 选择 Subscribe。通知偏好中还可决定在 GitHub、邮件或其他支持的入口接收哪些消息。[配置通知](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications)

不要为了练习向陌生人 @。有协作者时，让对方针对实际任务提出反馈，收到通知后点回原 Issue 或 PR，再判断是回答问题、更新需求还是修改文件。把通知标记已读或 Done 只是整理收件箱，不会关闭原 Issue，更不会把看板卡片改成 Done。

本章的完成结果是：你能从看板找回原 Issue，解释每项为何在当前列，知道自动化是否同步状态，并完成 C 的真实人工核对；若复用既有成果，则准确保留 Done，并明确本次未重做状态流转实验。之后只需保持字段和工作流能帮助决定下一步，不为看板形式新增维护负担。继续第 12 章：[让资源导航可以运行和验证](<现代 GitHub：12 让资源导航可以运行和验证.md>)。
