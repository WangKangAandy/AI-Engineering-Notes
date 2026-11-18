---
title: 现代 GitHub：建立练习仓库，完成第一次网页贡献
summary: 在自己的 resource-nav 仓库用网页建立资源清单，完成 Issue、分支、提交、PR、合并和关闭状态核验，为全书准备统一起点。
tags:
  - github
  - collaboration
created: 2026-11-16
status: learning
---

# 现代 GitHub：建立练习仓库，完成第一次网页贡献

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 2 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<现代 GitHub：看懂 GitHub 上的一个项目.md>) · [下一章](<现代 GitHub：准备本地工具与正确身份.md>)

本章只需要 GitHub 账号与浏览器。我们创建自己的 `resource-nav` 仓库，用一项很小的需求完成第一次贡献。后续章节继续使用这个仓库，不要求你获得本书所属组织的写权限。

## 建立自己可控制的实验仓库

在 GitHub 右上角创建菜单中选择 New repository。Owner 选自己的个人账号，Repository name 填 `resource-nav`，说明可以写“跟随《现代 GitHub》维护学习资源导航”。主线选择 Public，并初始化 README。只放准备公开的练习内容；私有代码、个人信息和凭据不进入这个仓库。

公开仓库便于后续演示 Pages 和协作能力。私人项目当然可以使用 Private，但某些后续权限与产品能力会受套餐影响；如果用私有仓库学习，需要按相关章节核对资格。本书的自托管 Runner 另用独立私有仓库，不把个人电脑直接注册到这个公开仓库。

创建后检查地址栏为 `https://github.com/你的账号/resource-nav`。记住这个账号和仓库组合；后文的 `YOUR_LOGIN/resource-nav` 都指它，而不是书的源仓库。若同名仓库已存在且正在使用，另建一个空实验仓库，并在后文一致替换名称，不把原项目当练习现场。[创建仓库](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

本书示例统一使用默认分支 `main`。创建后在 Code 的分支选择器核对；如果账号的默认设置生成了其他名称，可在这个全新仓库的分支管理页重命名默认分支为 main，或者全文一致使用你的实际名字。main 是本书约定，不是所有仓库的强制名称。[重命名分支](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/renaming-a-branch)

## 用 Issue 写清第一次要改什么

进入 Issues → New issue。如果有模板选择页，选适合的模板或允许的空白 Issue。标题写“建立资源导航清单”，正文写：

```markdown
目前仓库只有初始化说明，还没有实际资源。

希望补齐项目用途，并新增 resources.csv，收录 GitHub Docs 与 Python Docs 两项资源。

完成条件：main 中能打开 README.md 与 resources.csv，清单包含标题、链接、分类三列及上述两条资源。本次不创建程序或网站。
```

提交后记下 Issue 的实际编号。下面用 `#1` 举例，必须换成你看到的编号；同一个数字在不同仓库指向不同对象。Issue 提交成功只表示需求已记录，仓库文件还没有改变。

若看不到 Issues，检查是否在自己刚创建的仓库，以及 Settings → General → Features 是否启用了 Issues。不要去另一个组织仓库改变设置。[创建 Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue)

## 让修改先留在自己的分支

回 Code，先选 main，再在分支选择器输入 `lab/02-first-pr`，选择从 main 创建该分支。分支是一条开发线；创建后它暂时与 main 相同，后续提交才使二者不同。

在 `lab/02-first-pr` 打开 README.md，点击编辑。将初始化说明完善为：

```markdown
# 学习资源导航

整理 GitHub、Git 与 Python 的学习资料，并记录每项资源的标题、链接和分类。

目前使用 resources.csv 人工维护。后续会增加清单校验、静态页面与自动化检查。

## 当前范围

仅保存公开学习资源，不保存账号凭据或个人信息。
```

点击 Commit changes，填写说明 `docs: describe resource navigation project`，确认提交到当前实验分支。网页保存会直接产生 GitHub 上的提交，不需要本机执行 push。

继续在同一分支选择 Add file → Create new file，文件名填 `resources.csv`，内容为：

```csv
title,url,category
GitHub Docs,https://docs.github.com/,GitHub
Python Docs,https://docs.python.org/3/,Python
```

第一行是列名，后两行各是一条资源。逗号分隔字段；以后字段本身包含逗号时，需要使用 CSV 的引号规则，本章这两行不涉及这种情况。此处只维护文字数据，还没有任何 Python 程序。

提交说明可写 `docs: add initial learning resources`，仍提交到 `lab/02-first-pr`。现在分支有两个提交。切回 main 检查：main 仍是初始化内容，这说明尚未合并，不是提交丢失。

## 请求把分支修改合入 main

进入 Pull requests → New pull request，核对：

| 字段 | 本次选择 | 含义 |
| --- | --- | --- |
| base repository | 自己的 resource-nav | 修改准备进入的仓库 |
| base | main | 修改准备进入的分支 |
| head / compare | lab/02-first-pr | 保存这次修改的来源分支 |

PR 的全称是 Pull Request，是合并提案，不是下载请求，也不是终端中的 `git pull` 命令。打开 PR 不会立即改变 main。

差异中应只有 README.md 的说明变化和新增 resources.csv。检查两条资源的标题、链接和分类，确认没有意外文件，再创建 PR。标题写“建立资源导航的说明与初始清单”，正文可以这样写：

```markdown
补齐项目用途，新增包含 GitHub Docs、Python Docs 的资源清单。
已在网页检查两份文件及三列内容；尚未配置程序或 CI。

Closes #1
```

将 `#1` 换为本仓库实际 Issue 编号。`Closes` 是 GitHub 内置的关联规则，不需要 Actions。目标为默认分支且自动关闭开启时，合并会关闭对应 Issue；仅创建 PR 不会关闭它。自动关闭的其他方式与边界在第 8 章深入说明。[PR 与 Issue 关联](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)

## 合并前后分别看什么

在 Files changed 逐项读差异，在 Conversation 查看描述和当前合并条件。自己可以自查和评论，但不能批准自己提交的 PR；个人新建实验仓库通常可以自行合并，若设置了需要他人批准的规则，就要满足该规则。不要把自查说成独立评审。

本章没有添加 workflow，因此没有本例的自动测试是正常的。确认修改符合 Issue 完成条件后，使用页面允许的合并方式并确认；此时不必修改仓库的合并策略。三种合并方式的历史差异将在本地 Git 和 PR 章节展开。

合并成功应看到 Merged。然后分别打开：

1. Code → main：README 是新说明，resources.csv 有表头和两条资源。
2. Issue：通常显示 Closed，并能追到对应 PR。
3. PR：保留描述、两个提交或合并后的历史记录以及文件差异。

若 Issue 没关闭，先确认关键词在 PR 描述中、编号和仓库正确、PR 真正合入默认分支；还要核对 Settings → General → Issues 的自动关闭设置。这个开关由有管理权限的人决定，不必为符合教程而改变别人的仓库策略。内容验收后也可以说明原因并手动关闭 Issue。[自动关闭设置](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-auto-closing-issues)

删除已合并的实验分支可清理分支列表；它不会删除已经进入 main 的文件，也不会抹去 PR 讨论。保留整个仓库，下一章要把它克隆到本地。

## 卡住时先确定对象与状态

| 现象 | 检查顺序 |
| --- | --- |
| 修改后 PR 没有差异 | 是否在实验分支提交；base/compare 是否正确；是否已经合并过 |
| main 已经出现修改，却没有 PR | 是否在编辑时直接提交到了 main；下一项需求从新分支重新练习，不伪造旧流程 |
| 页面不能合并 | 是否存在未满足的规则或冲突；新仓库是否真由自己管理 |
| 看到的文件还是旧内容 | 当前分支和提交是否为 main 的最新状态 |
| Issue 提示关闭，但内容不对 | 自动关闭只执行平台规则，仍需按完成条件核对文件 |

本章结束时，你有自己的资源导航仓库、一个已经完成的需求、一次合并记录，以及可以继续维护的两份文件。还没有网站、CI 或 AI 任务；这些会随着项目需要逐步加入。
