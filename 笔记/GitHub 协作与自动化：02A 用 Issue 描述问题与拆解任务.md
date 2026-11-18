---
title: GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务
summary: 从一条可执行的需求开始，使用 Issue、子 Issue 和依赖关系拆解工作，说明责任、进度与完成条件，并为下一篇 PR 实践准备具体任务。
tags:
  - github
  - issues
  - collaboration
created: 2026-11-18
status: learning
---

# GitHub 协作与自动化：02A 用 Issue 描述问题与拆解任务

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。前置：完成 [[GitHub 协作与自动化：02 Issue、分支与 Pull Request]]，当前实验仓库的 master 已有《GitHub 工作流实操记录》。继续使用自己的 fork，或获准操作的组织仓库；本篇只组织任务，下一篇再修改文件。

第一次练习只有“新增一份记录”，一个 Issue 足够。现在记录里有 PR、CI、Pages 三个目标，但新读者还不知道怎样算完成 PR，以及开始 CI 前要准备什么。把它写成“完善学习记录”后直接交给别人，仍然不够：对方不知道要补哪些内容，也不知道什么时候可以停止。

Issue 的用途是把这种模糊意图变成可以讨论和验收的工作。它可以记录 bug、功能需求、文档修改或调查任务；不是只有软件报错才可以开 Issue。以下按 GitHub 当前页面操作，资料核对日期为 2026-11-18。[GitHub Issues 入门](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/quickstart)

## 1. 先找已有讨论，再提出具体工作

在当前仓库的 Issues 列表搜索“学习记录”，同时查看 Open 和 Closed，确认不是重复提出第 02 篇已经解决的“创建文件”。已有 Issue 完全覆盖问题时，在原讨论补充信息；这次是文件创建后的新需求，可以新建。

点击 New issue，按仓库模板填写，或在允许时选择 Open a blank issue。本次标题为“让 GitHub 工作流学习记录对新读者可用”，正文如下：

```markdown
## 现状
master 已有《GitHub 工作流实操记录》，但只有三个学习目标。
新读者不知道 PR 应检查什么，也不知道第一次 Actions 练习需要准备什么。

## 希望得到的结果
在同一份记录中补充 PR 验收说明与首次 CI 练习前的准备说明。
本任务只补文档，不配置 Actions、不发布 Pages。

## 完成条件
- PR 说明能区分合并、Issue 关闭和人工确认结果。
- CI 准备说明写清操作仓库、master 分支和 Actions 入口。
- 两部分术语一致，原有学习目标仍然保留。
```

提交后记下编号。以下用 `#20` 表示父 Issue，`#21`、`#22` 表示稍后创建的两个子 Issue；这些都是教学占位号，实际操作必须记录页面分配的编号。

描述需求不必写成很长的规范。这里保留现状、希望改变的行为与完成条件，是为了让接手者有依据。如果报告 bug，最有用的往往是复现步骤、预期结果、实际结果与必要环境信息；不要只写“不能用”，也不要贴含凭据的日志。

## 2. 决定哪些内容值得独立跟踪

一句“检查错别字”可以留在正文的 Markdown 任务列表中。若一项工作需要独立负责人、讨论、PR 或关闭记录，就适合成为子 Issue（sub-issue）。父 Issue 说明整体目的，子 Issue 各自有编号和状态，仍然是完整的 Issue。

本例拆成两项，因为它们可以分别评审和合并：

| 子任务 | 要修改什么 | 什么时候算完成 |
| --- | --- | --- |
| A：补充 PR 验收说明 | 在原记录新增“PR 验收”小节 | 说明检查 master 文件、PR 的 Merged 状态和 Issue 的关闭记录；自动关闭不代表内容已经正确 |
| B：补充首次 CI 准备说明 | 在原记录新增“开始 CI 前”小节 | 说明确认实验仓库、master 已有记录、找到 Actions；不把“找到入口”写成“测试已通过” |

父子关系表示“这项工作由哪些部分组成”，不表示 A 必须先于 B，也不会自动给子任务创建代码分支。若两个任务很小、同一人一次就能完成，保留一个 Issue 也合理；拆分的目的在于让工作可跟踪。

### 在页面中真正建立父子关系

添加子 Issue 需要仓库至少 triage 权限；自己的仓库 owner 可以操作。只有读取权限的外部贡献者能提 Issue，不意味着能管理它的父子关系。

1. 打开刚创建的父 Issue，在描述下方点击 Create sub-issue。
2. 标题填写 A 的名称，描述写明修改的文件、小节和完成条件，点击 Create。
3. 回到父 Issue，以同样方式创建 B。可以使用 Create more sub-issues 连续创建。
4. 查看父 Issue 下方的子项列表，再打开 A、B，核对父 Issue 关系和各自的编号。

如果 A、B 已经独立创建，不要再复制一份：在父 Issue 的 Create sub-issue 旁展开菜单，选择 Add existing issue，搜索实际编号或标题并选中。需要跨仓库组织时，可在选择器中切换到有权访问的仓库；本例全部留在同一仓库。[添加子 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)

正文写 `- [ ] #21` 可以作为可点击的任务引用，但不能据此认定已建立原生父子关系。应检查页面的子 Issue 列表与父项信息，而不是只看文字中出现了编号。把现有 Issue 加入父项也不等于复制它，其原编号和讨论继续使用。

## 3. 需要先后顺序时，再添加依赖关系

假设你要求 B 沿用 A 确定的 PR 验收术语，希望先完成 A 再验收 B。这是本练习额外设定的依赖；只有确实存在这种前提，才需要设置。

打开 **B**，在右侧 Relationships 选择 Mark as blocked by，搜索并选择 **A**。含义是“B 被 A 阻塞”。回到 B 检查 Blocked by 指向 A，再到 A 查看对应的 Blocking 关系。不要将方向选反，否则会把前后顺序表达反了。[Issue 依赖关系](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)

父子关系与依赖关系可以同时存在：A、B 都属于父项，而 B 的完成又以 A 为前提。依赖关系用来表达工作状态，不能代替分支保护或 CI；是否允许合并 PR，仍由仓库规则和 PR 当前状态决定。

后来发现两项可以独立推进时，回到 B 的 Relationships → Change blocked by，取消 A。无需为了保留一张“完整关系图”而留下已经不存在的阻塞。创建依赖同样需要至少 triage 权限；没有入口时先检查权限和当前仓库，而不是去添加 Actions 脚本。

## 4. 用少量字段让任务找得到、有人接

先在 A 的右侧 Assignees 选择自己，表示这项工作由你推进；自己无法设置时由有权限的人分派。再按需要在 Labels 中选择已有的 documentation 标签，方便从一堆 Issue 中找到文档工作。标签不存在时可暂时不设，不必为了练习重建一套分类。

这些字段回答不同问题，不能互相替代：

| 字段 | 回答什么 | 本例是否需要 |
| --- | --- | --- |
| Assignees | 谁负责推进 | 给 A 指定自己，B 可等准备执行时再分派 |
| Labels | 涉及什么主题或特征 | 有 documentation 就使用；可以有多个标签 |
| Type | 这是哪类工作，例如 Task、Bug、Feature | 入口可用且已有 Task 时可选；不必修改账号或组织类型设置 |
| Milestone | 希望在哪个阶段或版本完成 | 两个小任务无需先建里程碑 |
| Projects | 如何在表格或看板中集中安排工作 | 多仓库或更多任务出现后再使用 |

Issue types 与标签不是同一个字段，当前官方支持在组织和个人账号管理类型；它用于统一工作类别，不必把每个主题都做成一个 Type。[管理 Issue types](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/managing-issue-types)

回到仓库 Issues 搜索框，可以用 `is:issue is:open assignee:@me` 找分派给自己的未关闭工作，再按需要加 `label:documentation`。筛选不到时先去掉标签条件检查，不要把“没有筛选结果”误认为 Issue 被删除。

## 5. 持续更新状态，保留决定的理由

在 A 下发一条具体的进展评论，例如“准备在原记录末尾新增 PR 验收小节，保留已有三个目标”。如果协作者指出范围遗漏，先更新描述中的完成条件，再继续实施；讨论结论只埋在几十条评论里，后来接手的人很容易遗漏。

Open 表示尚未关闭，不等于完全没人开始。负责人、进展评论、关联 PR 和 Projects 状态可以补充进度信息；本篇不要求先配置看板。需要别人参与时再 @ 对方，mention 会产生通知，不把它当作文字装饰。

下一篇先为 A 提交一个 PR，只声明解决 A。B 和父 Issue 此时仍保留未完成状态。完成所有子任务后，再回父 Issue 对照整体条件检查：是否存在跨任务遗漏，是否真的形成了一份可用记录。父项的验收不能被子项的数量或百分比代替。

最终确认完成，可以在父 Issue 底部选择适当关闭原因并 Close issue；决定不做则说明理由并选择 Not planned，不将放弃说成已实现。若后来发现工作没有完成，在有权限时使用 Reopen issue，并补充新证据。关闭与重新打开只改变工作项状态，不会自动回滚或修改仓库文件。[关闭 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue)

本篇结束时应有一条父 Issue、两条实际子 Issue，知道谁负责 A，以及是否需要 B 被 A 阻塞。它们还没有改变任何笔记内容。下一篇：[[GitHub 协作与自动化：02B 让 PR 关联 Issue 并完成评审合并]]。
