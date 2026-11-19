---
title: 现代 GitHub：从需求到可执行计划：Issue、子任务和项目视图
summary: 把一次贡献入口改进写成可验收的 Issue，拆成子 Issue，表达依赖，并用项目视图跟踪实际进度。
tags:
  - github
  - issues
  - project-management
created: 2026-11-18
status: ready
---

# 现代 GitHub：从需求到可执行计划：Issue、子任务和项目视图

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

到本章为止，项目只有 README 和网页贡献的历史，还没有 Python 程序。我们先用不需要编程的任务学习 Issue、子 Issue 和 Projects：让新读者知道资源应该怎样提交。

## 从模糊想法写出完成条件

在自己的 resource-nav 仓库创建 Issue：

标题：

~~~text
让新贡献者知道如何提交资源
~~~

正文：

~~~markdown
## 现状
README 只说明项目用途，没有告诉新贡献者资源需要哪些字段、怎样提交和怎样验证。

## 预期结果
README 能说明资源格式和最小贡献路径。

## 范围
本次只修改 README 和贡献说明，不添加程序、不修改 Actions、不改变页面构建。

## 完成条件
- [ ] README 说明资源名称、链接和分类的填写要求
- [ ] README 先说明贡献入口，第二个子任务完成后再链接到 CONTRIBUTING.md
- [ ] Pull Request 关联本 Issue
- [ ] 修改通过网页可读性检查
~~~

Issue 现在描述的是无需编程即可验收的文档任务。这样第 5 章的 PR 有真实输入，第 7 章才会另行引入程序。

## 什么时候拆成子 Issue

把工作拆成两个可以独立评审的子项：

1. 在 README 增加资源格式和贡献步骤；
2. 建立 CONTRIBUTING.md，写清提交前检查和 PR 描述要求。

在父 Issue 页面底部选择 Create sub-issue，分别填写标题和完成条件。也可以选择 Add existing issue，把已经存在的 Issue 放入父项。GitHub 会在父 Issue 中显示子项数量和关闭进度。

子 Issue 不是正文里的普通编号引用。它有父子关系，可以在父项中展开，也可以在 Projects 中按层级分组。

## 表达依赖，而不是表达顺序

第二个子项依赖第一个子项确定的字段名称，因此把第二个子项设置为 blocked by 第一个子项。保存后重新打开两个 Issue，确认方向：

- A blocked by B：A 等待 B；
- A blocking B：A 阻塞 B。

如果账号或仓库没有 Issue dependencies，保留父子关系，并在父 Issue 中写明“先完成 README 字段约定，再写贡献指南”；不要为了展示按钮创建虚假的状态。

## 用 Projects 看工作在哪里

在仓库主页打开 Projects → New project，选择 Table，名称填写 Resource navigation work queue，然后创建。进入项目后：

1. 选择 Add item，搜索并加入父 Issue 和两个子 Issue；
2. 保留默认 Status 字段，并新增或启用 Assignees、Labels 和 Parent issue；
3. 将三个项目项初始设为 Todo；
4. 开始 README 子项时把它改为 In progress；
5. 合并对应 PR 后把它改为 Done；
6. 打开父 Issue 的层级信息，确认子项进度与项目视图一致。

如果你的仓库界面把 Projects 放在全局导航，先选择 New project，再用 Add item 搜索当前仓库的 Issue。项目回答“现在有哪些工作、谁在做、哪些被阻塞”；Issue 回答“为什么做、什么算完成”。不要复制一份正文代替项目状态。

## 用 gh 核对对象

网页操作完成后，在 Git Bash 中查看：

~~~bash
gh issue list --repo YOUR_LOGIN/resource-nav
gh issue view PARENT_ISSUE_NUMBER --repo YOUR_LOGIN/resource-nav
~~~

创建子 Issue 时，GitHub CLI 支持 parent 参数：

~~~bash
gh issue create --repo YOUR_LOGIN/resource-nav --title "补充贡献说明" --body "写清提交前检查" --parent PARENT_ISSUE_NUMBER
~~~

命令成功只代表请求被接受；仍要打开父 Issue，核对子项关系和依赖方向。

## 本章结束状态

进入下一章前应该有：

- 一个只涉及 README/贡献说明的父 Issue；
- 两个文档子 Issue；
- 一个明确的依赖方向；
- 一个 Projects 视图；
- main 中仍没有 Python 程序，下一章只交付文档。

下一章会完成第一个子 Issue 的 PR、评审和合并；第二个子 Issue 会让第 6 章的维护入口有真实文件可验收。
