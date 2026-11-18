---
title: 现代 GitHub：从需求到可执行计划：Issue、子任务和项目视图
summary: 把一次资源导航升级写成可验收的 Issue，拆成子 Issue，表达依赖，并用项目视图跟踪实际进度。
tags:
  - github
  - issues
  - project-management
created: 2026-11-18
status: draft
---

# 现代 GitHub：从需求到可执行计划：Issue、子任务和项目视图

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

Issue 不是“把想法发在网上”。它应该让接手工作的人知道现状、预期结果、完成条件和下一步。子 Issue 解决的是一项工作太大、不能由一个 Pull Request 清楚完成的问题；Projects 用来观察进展，不是复制一份 Issue 内容。

## 从模糊想法写出完成条件

先在自己的 resource-nav 仓库创建 Issue：

标题：

~~~text
让资源导航按类别分组
~~~

正文：

~~~markdown
## 现状
当前页面按 CSV 文件顺序展示资源，读者需要通读列表才能找到同一类别的资源。

## 预期结果
页面按 category 分组，并在页面上显示每组资源数量。

## 范围
本次只修改资源数据、校验程序和页面输出，不引入数据库或新的前端框架。

## 完成条件
- [ ] CSV 中每项资源有非空 category
- [ ] 校验程序拒绝缺少 category 的行
- [ ] 页面按 category 分组
- [ ] 测试覆盖一个空 category 的失败样例
- [ ] Pull Request 关联本 Issue
~~~

这几个部分分别回答为什么改、改成什么样、不改什么、如何判断完成。没有完成条件的 Issue 很容易在评审时变成“看起来差不多”。

## 什么时候拆成子 Issue

如果一个 PR 可以在不依赖另一个 PR 的情况下独立评审，就可以拆成一个子 Issue。为本次需求创建两个子项：

1. 增加 category 数据并检查缺失值；
2. 修改页面生成逻辑并补测试。

在父 Issue 页面底部选择 Create sub-issue，分别填写标题和完成条件。也可以使用 Add existing issue，把已经存在的 Issue 放入父项。GitHub 会在父 Issue 中显示子项数量和关闭进度。

子 Issue 不是普通的编号引用。它有父子关系，可以在父项中展开，也可以在 Projects 中按层级分组。不要只在正文里写“见 #2”来代替关系。

## 表达依赖，而不是表达顺序

页面生成依赖数据校验，因此第二个子项要等第一个子项提供 category 数据后才能完成。在子 Issue 的 Relationships 或 Development 区域添加依赖，选择“blocked by”或“blocking”时先读清方向：

- A blocked by B：A 等待 B；
- A blocking B：A 阻塞 B。

保存后重新打开两个 Issue，确认父项、子项和依赖方向都显示正确。方向错误会让项目视图给出相反的进度判断。

如果你的账号或仓库还没有 Issue dependencies，正文中保留一个明确的文本说明，并用父 Issue 和 PR 关联完成主线；不要为了展示按钮创建虚假的状态。

## 用 Projects 看工作在哪里

为仓库创建一个项目视图，至少保留：

- Status：Todo、In progress、Done；
- Assignees；
- Labels；
- Parent issue 或 Sub-issue progress。

将父 Issue 和两个子 Issue 加入项目，状态初始为 Todo。开始第一项时只移动第一项为 In progress；完成后再移动为 Done。父 Issue 的完成度应来自子项，而不是手工复制一段进度文字。

项目视图回答的是“现在有哪些工作、谁在做、哪些被阻塞”。Issue 正文回答的是“为什么做和什么算完成”。两者职责不同。

## 用 gh 创建和核对对象

网页操作完成后，在 Git Bash 中查看同一对象：

~~~bash
gh issue list --repo YOUR_LOGIN/resource-nav
gh issue view ISSUE_NUMBER --repo YOUR_LOGIN/resource-nav
~~~

创建子 Issue 时，GitHub CLI 支持 parent 参数：

~~~bash
gh issue create --repo YOUR_LOGIN/resource-nav --title "增加 category 数据" --body "Closes parent requirement" --parent PARENT_NUMBER
~~~

先使用网页核对父子关系，再用 gh issue view 读回；命令成功只代表请求被接受，不代表关系方向正确。

## 本章结束状态

在进入下一章前，应该有：

- 一个父 Issue，写清现状、预期、范围和完成条件；
- 两个子 Issue，分别代表数据校验和页面改造；
- 一个明确的依赖方向；
- 一个 Projects 视图，能看到 Todo、In progress 和 Done；
- 你知道下一步先完成哪个子 Issue。

下一章会选择第一个子 Issue，走完分支、PR、评审、合并和关闭关键词。父 Issue 会在所有子项完成后才作为整体验收，不会因为第一个 PR 合并就假装完成。

