---
title: 现代 GitHub：让资源导航可以运行和验证
summary: 将已经维护的资源清单接入小型 Python 校验与页面生成程序，理解输入、输出、测试、失败和构建，为 CI 准备真实命令。
tags:
  - github
  - python
  - testing
created: 2026-11-18
status: learning
---

# 现代 GitHub：让资源导航可以运行和验证

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本书第 12 章。[全书导读](<GitHub 协作与自动化：01 学习路线.md>) · [上一章](<现代 GitHub：让多项工作有可见的进度.md>) · [下一章](<GitHub 协作与自动化：03 Actions 与 Workflow.md>)

此前我们靠人检查资源清单。条目增多后，漏填分类、重复添加链接会变得难以察觉；每次手工排版页面，也会重复同样的劳动。本章给已有的 `resources.csv` 加一套小程序：先检查输入，再把有效数据变成静态页面。

前置是自己的 `resource-nav` 本地仓库，main 中已有 README 和资源清单。Projects 可以跳过，不影响本章。你不需要先学完 Python；本章只解释看懂和修改这个例子所需的概念。

## 先分清三种结果

```text
resources.csv ──校验──> 一组有效资源 ──构建──> site/index.html
                         ↑
                 测试检查程序的预期行为
```

校验当前清单，回答“这份数据是否符合约定”；单元测试，回答“程序面对给定案例时是否按预期处理”；构建页面，回答“当前有效清单能否生成网页文件”。它们各有作用，不能互相代替。测试全通过时，真实清单仍可能存在错误，所以 CI 中三条命令都会运行。

本例的规则是：表头按顺序为 `title,url,category`，至少有一条资源，每行恰好三个非空字段；链接使用带主机名的 HTTP(S) 地址；去除首尾空白后，完全相同的 URL 不能重复。分类是可维护的文字，不强制只有 GitHub、Git、Python 三种。

我们不联网访问这些链接。通过校验不代表网址可访问、内容可信或永不失效；此处验证的是约定的本地数据形态。程序也没有数据库、账号系统或网页服务器。

## 准备解释器与工作分支

在 PowerShell 7 中先检查是否已有 Python 3.12：

```powershell
py -3.12 --version
```

找不到时，从 [Python 官方下载页](https://www.python.org/downloads/) 安装 Windows 的 Python install manager，安装后重新打开终端。当前安装管理器可使用 `pymanager install 3.12` 获取指定运行时，再执行上面的版本检查。已有旧版 py 启动器时，不要把它误当成提供 install 子命令的新管理器；`pymanager` 可以区分二者。企业设备按实际软件管理要求安装。[Windows 官方安装说明](https://docs.python.org/3/using/windows.html)

本章本机命令明确使用 `py -3.12`。后面的 Actions 在准备好 Python 3.12 后使用 `python`；命令名称不同不代表用另一套源码。本例只依赖标准库，没有 pip 安装步骤。其他系统可用实际安装的 Python 3.12 命令运行相同脚本。

进入自己的 resource-nav 目录，先检查工作区。存在未完成修改时，按本地 Git 章节保存或完成，不直接覆盖：

```powershell
git status --short
git switch main
git pull --ff-only
git switch -c lab/12-program
```

## 把完整示例放进自己的仓库

以下链接是本书维护的源文件，不是让你在笔记库根目录运行的程序。打开每个文件，使用 Raw/下载入口保存为原文件名，放到自己 resource-nav 的仓库根目录；不要保存 GitHub 的整张 HTML 页面，也不要在扩展名后加 `.txt`。

| 文件 | 用途 |
| --- | --- |
| [catalog.py](./_assets/modern-github/resource-nav/catalog.py) | 读取 CSV，校验内容，并提供命令行结果 |
| [build.py](./_assets/modern-github/resource-nav/build.py) | 使用校验后的数据生成 HTML |
| [test_catalog.py](./_assets/modern-github/resource-nav/test_catalog.py) | 为正常输入、错误输入和 HTML 转义提供测试 |
| [.gitignore](./_assets/modern-github/resource-nav/.gitignore) | 排除 Python 缓存、本地产物和虚拟环境 |

仓库已有 .gitignore 时，合并示例中的规则，不覆盖其他有效规则。保留你前面维护的 resources.csv；跳读者可从[初始清单](./_assets/modern-github/resource-nav/resources.csv)恢复到两条资源，但不要用它覆盖已有有效条目。

此时仓库根目录应有 README.md、resources.csv，以及刚加入的四个文件。源码是长期维护对象，运行生成的 site/ 是可以重新产生的结果，不把它当成手工维护的第二份清单。

## 读懂输入如何变成输出

打开 catalog.py，先定位 `load_resources(path)`。`def` 定义一个函数，相当于给一段可重复执行的工作起名字；`path` 是调用者传入的文件路径。函数读取文件，返回一组资源。`row["title"]` 表示取这一条资源的 title 字段。

文件不是按字符串随意切逗号。程序用标准库 `csv.DictReader`，它认识 CSV 的列名与引号规则；例如标题包含逗号时可以写成 `"Git, a guide"`。读取使用 UTF-8，并兼容 UTF-8 BOM。[CSV 读取规则](https://docs.python.org/3/library/csv.html)

当输入不符合要求，函数用 `raise ValueError(...)` 报告错误。例如重复 URL 不会悄悄丢弃其中一条，而是明确指出问题行。命令行入口捕获这类错误，打印说明并返回非零退出码，后续 CI 才能据此判断失败。

再打开 build.py。它先调用相同的校验函数，然后由 `render_page(resources)` 把资源转换为 HTML，最后写到 site/index.html。路径相对于命令执行目录，所以必须从 resource-nav 根目录运行。

清单里的标题是文字，不应变成网页脚本。因此渲染使用 `html.escape` 转义标题、分类和链接属性值；例如 `<` 会变成对应的 HTML 转义形式。允许 HTTP(S) 地址与转义属性是不同的检查，需要分别处理。[HTML 转义](https://docs.python.org/3/library/html.html)

你暂时不必掌握每个 Python 语法。先能找到输入、校验函数、错误处理、输出路径，就能判断后续改动影响了哪个环节。

## 运行三条真实命令

从仓库根目录依次运行，每条都确认成功后再继续：

```powershell
py -3.12 catalog.py resources.csv
py -3.12 -m unittest discover -v
py -3.12 build.py
```

第一条应打印 `Validated N resources`，N 是你当前清单的实际条数。初始清单是两条；完整做过协作章节后可能多了 Pro Git，不能机械要求所有读者都是同一个数。

第二条从 `test_*.py` 中发现测试，初始示例有 9 项，最后显示 OK。测试通过临时文件构造不同输入，不修改你正在维护的清单。`assertEqual` 比较结果，`assertRaises` 要求坏输入确实报错；没有执行任何测试时，即便退出成功，也不能算完成这一步。[unittest 的发现与断言](https://docs.python.org/3/library/unittest.html)

第三条生成 site/index.html。用文件管理器打开它，页面应显示资源标题、链接和分类。查看源文件可以看到 HTML，但访问者看到的是浏览器渲染后的页面。当前只是本地文件，还没有部署到 GitHub Pages，也没有给其他人提供在线地址。

## 让错误发生一次，再恢复

先在编辑器中把 resources.csv 中任意一条有效资源完整复制到末尾，暂不提交，重新运行校验命令。预期看到 duplicate URL 提示。紧接着在 PowerShell 查询：

```powershell
$LASTEXITCODE
```

应为 1。只有紧接失败命令读取时，它才代表那条命令的退出状态；执行其他原生命令可能改变这个值。

再运行 build.py，它也应失败。若此前 site/index.html 已生成，它可能仍然留在磁盘上；旧文件存在不代表本次构建成功。以后部署只上传成功构建的产物，不能通过“目录里有文件”来忽略失败。

删除刚加的重复行，恢复有效清单，再依次运行三条命令，应恢复通过。用 `git diff -- resources.csv` 确认没有留下故意制造的错误。此时你已经看过成功、真实数据失败和恢复，而不只是看到一次绿色结果。

## 把程序通过 PR 送入主线

如果第 10 章已经创建了 `CONTRIBUTING.md`，先编辑它的“本地验证”段落，保留人工核对资源来源、用途和分类，并补上下面三条命令；如果文件尚未创建，就在本章 PR 描述中记录待办，不引用不存在的文件。这样指南的更新会和程序一起进入同一个 PR。

```powershell
git status --short
git diff --check
git add catalog.py build.py test_catalog.py .gitignore
if (Test-Path -LiteralPath CONTRIBUTING.md) { git add -- CONTRIBUTING.md }
git diff --staged --stat
git commit -m "feat: validate catalog and build resource page"
git push -u origin lab/12-program
```

stage 列表不应包含 site/、__pycache__/ 或任何凭据。若清单有本次真实、已验证的修正，单独检查后再明确加入，不使用无差别添加来掩盖范围。

按前面学过的方式创建面向自己仓库 main 的 PR，描述本地使用的 Python 版本、测试数量、构建结果，以及尚未配置 CI。检查后合并，回本地 main 拉取，再重跑三条命令。

```text
py -3.12 catalog.py resources.csv
py -3.12 -m unittest discover -v
py -3.12 build.py
```

本章结束时，可运行程序、测试与有效清单都在 main；下一章开始把执行交给 Actions。
