---
title: 现代 GitHub：08 把资源清单变成可测试程序
summary: 在指导下阅读并修改小型 Python 校验与页面生成程序，经历测试先失败、修改实现、构建验证和 PR 交付。
tags:
  - github
  - python
  - testing
created: 2026-11-18
status: draft
---

# 现代 GitHub：08 把资源清单变成可测试程序

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本章把前面人工维护的 `resources.csv` 变成一个可以重复验证的小程序。目标不是学习完整 Python，而是经历一次完整的“需求 → 测试 → 失败 → 修改 → 通过”循环。

## 先看懂输入和输出

输入是一份 CSV 清单，字段为 `title,url,category`。程序要完成两件事：拒绝不符合规则的数据，并把有效资源生成 `site/index.html`。测试检查程序行为，构建检查当前清单能否产出页面；二者都不能证明外部链接可访问。

第 12 章的附件包含 `catalog.py`、`build.py`、`test_catalog.py`、`.gitignore` 和一个初始 `resources.csv`。在自己的 resource-nav 中使用这些文件，先以 `py -3.12` 检查解释器，然后运行：

```powershell
py -3.12 catalog.py resources.csv
py -3.12 -m unittest discover -v
py -3.12 build.py
```

先让这三条命令通过，再开始修改程序。`catalog.py` 使用标准库读取 CSV，检查表头、空字段、HTTP(S) 主机和重复 URL；`build.py` 使用同一套有效数据生成页面；测试用临时文件构造错误输入，不会改写你的资源清单。

## 一次指导式代码改进

现在做一个小而完整的改进：页面标题下增加资源总数。这个需求有明确输入、输出和测试，不需要数据库或外部服务。

先在 `test_catalog.py` 增加一个失败测试。测试文件中已有 `render_page` 的测试，加入：

```python
    def test_page_shows_resource_count(self):
        rows = self.load("title,url,category\nDocs,https://example.com/,Git\n")
        self.assertIn("共 1 项资源", render_page(rows))
```

运行定点测试：

```powershell
py -3.12 -m unittest test_catalog.CatalogTests.test_page_shows_resource_count -v
```

此时应失败，因为页面还没有这段文字。失败的原因要和语法错误区分：如果提示找不到方法或导入失败，先修正测试位置；如果断言失败，说明测试真正测到了尚不存在的行为。

再修改 `build.py` 的 `render_page`，在标题下面加入由 `len(resources)` 生成的文本。不要改变 CSV 校验、链接转义或列表结构。重新运行定点测试，再运行完整测试、清单校验和构建：

```powershell
py -3.12 -m unittest discover -v
py -3.12 catalog.py resources.csv
py -3.12 build.py
```

打开生成的 `site/index.html`，确认页面文字和列表都存在。测试通过证明程序对这个输入产生了预期文字；页面检查确认构建结果实际包含它。不要把“测试绿了”写成页面已经部署。

## 观察一次真实失败

把 `len(resources)` 临时改成 `len(resources) + 1`，只运行资源数量测试。它应失败，说明测试能识别错误实现。恢复正确表达式，再完整运行三条命令。故障练习不需要推送到远端，恢复后检查 `git diff` 只包含本次功能和测试。

如果你发现测试通过但页面不对，先确认打开的是本次 `site/index.html`，再查看构建命令的退出码和文件修改时间。旧页面残留不代表新构建成功；下一章的 CI 也必须用当前提交重新生成它。

## 通过 PR 交付这次代码改进

从最新 main 创建 `lab/08-resource-count`，提交 `catalog.py`、`test_catalog.py` 和必要的 README 说明，创建面向 main 的 PR。PR 描述写清新增行为、测试命令和未验证的外部链接；不要把生成的 `site/`、缓存或虚拟环境提交进去。

合并后 main 才拥有这项行为。下一章会把这三条命令接入 Actions，并让错误清单阻止合并；如果你跳过本章的代码练习，不能直接声称已经具备独立修改 Python 行为的能力。

