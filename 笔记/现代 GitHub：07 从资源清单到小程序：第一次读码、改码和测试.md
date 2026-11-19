---
title: 现代 GitHub：从资源清单到小程序：第一次读码、改码和测试
summary: 在不先学习完整 Python 的前提下，读懂 CSV 到 HTML 的最小链路，先制造一个失败测试，再完成一次可验证的代码修改。
tags:
  - github
  - python
  - testing
created: 2026-11-18
status: ready
---

# 现代 GitHub：从资源清单到小程序：第一次读码、改码和测试

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

前六章已经让你能提出需求、评审文档并建立贡献入口。本章第一次创建可运行程序：先把完整的 resource-nav 示例放进自己的仓库，再理解 CSV 到 HTML 的链路，最后改进错误信息并用测试证明它。

这不是完整 Python 课程。你只需要理解变量、函数、列表、字典、异常和断言在这个项目中的作用。

## 准备 Python

从 Python 官方网站安装 Python 3.12 或更新的 3.x 版本，安装时勾选将 Python 加入 PATH。重新打开 Git Bash 后检查：

~~~bash
python --version
~~~

如果命令不存在，先修复安装或 PATH，不要把 py、PowerShell 和 WSL 的路径混在一起。创建一个临时虚拟环境不是本章必须步骤；依赖只有 Python 标准库，先让读者理解程序和测试。

在 resource-nav 的工作分支上准备一个新的程序任务：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git switch -c feature/validate-resources
~~~

将随书示例完整放进自己的仓库。对每个附件链接打开文件页面，点击 Raw，再将文件保存到 resource-nav 根目录；不要只复制其中一段函数：

- [catalog.py](<_assets/modern-github/resource-nav/catalog.py>) 读取并检查 CSV；
- [build.py](<_assets/modern-github/resource-nav/build.py>) 调用 catalog.py 并生成 site/index.html；
- [test_catalog.py](<_assets/modern-github/resource-nav/test_catalog.py>) 用 unittest 验证输入和 HTML 转义；
- [resources.csv](<_assets/modern-github/resource-nav/resources.csv>) 是程序真正读取的数据；
- [.gitignore](<_assets/modern-github/resource-nav/.gitignore>) 防止把生成目录提交到仓库。

保存后先确认四个 Python/CSV 文件和 .gitignore 都在仓库根目录：

~~~bash
find . -maxdepth 1 -type f -print | sort
python -m unittest discover -s . -p 'test_*.py' -v
~~~

如果文件不在根目录，先移动它们再运行测试；不要让程序依赖一个只存在于书稿资源目录的路径。

## 先看输入如何变成输出

resources.csv 的表头是：

~~~text
title,url,category
~~~

catalog.py 的 load_resources 函数逐行读取 CSV，去掉字段两端空白，检查：

- 表头必须是 title、url、category；
- 每个字段不能为空；
- URL 必须是 HTTP 或 HTTPS；
- URL 不能重复；
- 文件至少有一行资源。

build.py 调用 load_resources，收到列表后将每一项转成 HTML。escape 的作用是把标题、链接和 category 中的特殊字符转成安全的 HTML 文本；这不是页面设计，而是避免输入直接变成标签。

test_catalog.py 中的每个 test_ 方法都是一个可重复的判断。self.assertRaises 期待某种输入失败，self.assertIn 期待输出包含某段安全文本。

### 零基础读码只需要抓住五个连接

- resources 是一个列表；load_resources 每读一行，就创建一个 row 字典并追加到列表。
- for raw in reader 表示逐行处理 CSV，不是一次把整个文件变成字符串。
- row["category"] 取出当前字典的一个字段；if not 判断它是否为空。
- raise ValueError 会让当前命令失败；reader.line_num 提供出错行号。
- unittest.TestCase 是测试的父类，self 表示当前测试对象；测试方法必须缩进在 CatalogTests 类中。

先只追踪一行数据如何从 resources.csv 进入 row，再追踪 row 如何进入 render_page。不要试图在第一次阅读时理解所有标准库 API。

## 先运行已有测试和构建

在 Git Bash 中：

~~~bash
cd ~/projects/resource-nav
python -m unittest discover -s . -p 'test_*.py' -v
python catalog.py resources.csv
python build.py
~~~

成功时应看到 9 个测试通过、Validated 2 resources 和 site/index.html 被生成。实际数量以你仓库中的 resources.csv 为准；不要把示例输出当成未执行过的事实。

打开生成的 site/index.html，确认标题和资源链接出现。这个 HTML 是构建结果，不应手工编辑；想改变页面，就改 CSV 或 build.py 后重新运行。

## 用一个更具体的失败测试理解需求

程序已经会拒绝空 category。本次改进要求错误信息同时指出输入行号，方便维护者定位数据。先在 test_catalog.py 中增加一个测试：

~~~python
def test_reports_line_for_missing_category(self):
    with self.assertRaisesRegex(ValueError, r"Line 2:.*category"):
        self.load("title,url,category\nDocs,https://example.com/,\n")
~~~

运行：

~~~bash
python -m unittest discover -s . -p 'test_*.py' -v
~~~

如果测试失败，读失败信息判断是测试写错还是实现没有把行号和字段写进错误。这里的测试必须先失败，修改实现后再通过；否则你没有真正验证本次改动。

## 做一个可观察的行为改进

为了让错误信息包含字段名称，把通用的 fields must not be blank 改为能指出 category：

~~~python
if not row["category"]:
    raise ValueError(f"Line {reader.line_num}: category must not be blank")
if not row["title"] or not row["url"]:
    raise ValueError(f"Line {reader.line_num}: title and url must not be blank")
~~~

将这段逻辑放在 catalog.py 的逐行检查位置，保留原来的 URL 和重复检查。重新运行：

~~~bash
python -m unittest discover -s . -p 'test_*.py' -v
python catalog.py resources.csv
python build.py
git diff --check
~~~

成功观察包括：

- 测试全部通过；
- 正常 CSV 仍能生成页面；
- 人为删除 category 时，命令以非零状态结束并指出行号；
- diff 中没有意外的换行或临时文件。

## 形成一次代码 PR

查看并暂存完整的首次程序交付：

~~~bash
git status --short
git add resources.csv catalog.py build.py test_catalog.py .gitignore
git diff --cached --stat
git diff --cached -- resources.csv catalog.py build.py test_catalog.py .gitignore
~~~

确认 staged diff 同时包含数据、校验器、构建器、测试和忽略规则后再提交：

~~~bash
git add resources.csv catalog.py build.py test_catalog.py .gitignore
git commit -m "test: report missing resource category lines"
git push -u origin feature/validate-resources
~~~

在 PR 描述中写清：

~~~markdown
## What changed
- 首次引入 resources.csv、catalog.py、build.py、test_catalog.py 和 .gitignore。
- 对空 category 给出包含行号的明确错误。
- 增加空 category 的失败测试。

## Verification
- python -m unittest discover -s . -p 'test_*.py' -v
- python catalog.py resources.csv
- python build.py
~~~

完成评审后合并 PR。合并前不要把 site/index.html 当作手工产物提交到主线，除非第 9 章的发布流程明确把它作为构建输出。

## 本章结束状态

main 已包含可读的错误信息和对应测试，resource-nav 的数据仍可被程序读取，页面可以重新构建。你已经完成了第一次“读输入—理解函数—修改行为—用测试验证—通过 PR 交付”的代码闭环。

下一章会把本机已经运行过的命令交给 GitHub Actions，让每个 Pull Request 自动执行相同的验证。

