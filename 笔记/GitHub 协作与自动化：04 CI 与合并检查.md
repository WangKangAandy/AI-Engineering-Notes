---
title: GitHub 协作与自动化：04 CI 与合并检查
summary: 用 Python 示例接入 CI，经历失败、合并规则阻止、修复和通过，学习用检查保护主分支。
tags:
  - github
  - ci
created: 2026-11-16
status: learning
---

# GitHub 协作与自动化：04 CI 与合并检查

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[[GitHub 协作与自动化：01 学习路线]]。

> 本篇实验基线：`docs/github-agent-channel-architecture`；实验分支：`lab/04-ci`。本篇的新增文件和提交都在该实验分支完成，再按文中的 PR 步骤合并或关闭。前置：[[GitHub 协作与自动化：03 Actions 与 Workflow]]。

本篇完成一个关键练习：故意提交错误，看到 PR 检查失败，再通过新提交修复，并理解如何要求检查通过后才能合并。

## 1. CI 实际检查什么

CI 把项目已有的检查命令接入每次变更。检查内容由项目自己定义，不会因为启用了 Actions 就自动产生充分的测试。

| 检查 | 发现什么问题 | 常见局限 |
|---|---|---|
| 格式 / lint | 风格或静态规则问题 | 通过不代表逻辑正确 |
| 单元测试 | 给定输入是否产生期望结果 | 没写到的场景可能漏掉 |
| 集成测试 | 多个模块或服务是否配合工作 | 依赖测试环境 |
| 构建 | 能否生成目标产物 | 生成成功不等于运行正常 |

本练习采用 Python 标准库测试和静态页面构建，避免先安装应用框架。

## 2. 准备三个文件

在练习仓库根目录添加以下文件，并通过一个初始化 PR 合并到 `docs/github-agent-channel-architecture`。

`app.py`：

```python
def greeting(name):
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must not be blank")
    return f"Hello, {cleaned}!"
```

`test_app.py`：

```python
import unittest

from app import greeting


class GreetingTests(unittest.TestCase):
    def test_normal_name(self):
        self.assertEqual(greeting("GitHub"), "Hello, GitHub!")

    def test_trims_spaces(self):
        self.assertEqual(greeting("  GitHub  "), "Hello, GitHub!")

    def test_rejects_blank(self):
        with self.assertRaises(ValueError):
            greeting("   ")


if __name__ == "__main__":
    unittest.main()
```

`build.py`：

```python
from html import escape
from pathlib import Path

from app import greeting


output = Path("site")
output.mkdir(exist_ok=True)
message = escape(greeting("GitHub"))
page = (
    '<!doctype html><html lang="en"><head>'
    '<meta charset="utf-8"><title>Workflow Lab</title>'
    '</head><body>'
    f'<h1>{message}</h1>'
    '</body></html>'
)
(output / "index.html").write_text(page, encoding="utf-8")
print("Built site/index.html")
```

如果本地安装了 Python，在练习仓库根目录执行：

```powershell
python -m unittest discover -v
python build.py
```

Windows 只有 `py` 启动器时，把本地命令中的 `python` 换成 `py`；workflow 内仍用 `python`。没有本地 Python 也可以把文件提交后交给 Actions 执行。

预期：发现并通过 3 个测试，产生 `site/index.html`。这些 Python 文件和生成目录只用于本次实验；若不想把它们作为仓库长期内容，可以在验收后通过一个清理 PR 删除，并保留 CI 运行链接。

## 3. 接入 CI

同一个初始化 PR 中新增 `.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [docs/github-agent-channel-architecture]
  pull_request:
    branches: [docs/github-agent-channel-architecture]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test-and-build:
    name: Test and build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v7
      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Run tests
        run: python -m unittest discover -v
      - name: Build site
        run: python build.py
```

这里使用 GitHub 托管的 Ubuntu runner。`setup-python` 的作用是选择 Python 版本，不负责替你编写测试；本例仅用标准库，所以没有安装依赖步骤。[setup-python 官方仓库](https://github.com/actions/setup-python)

配置合并后，打开 Actions → CI，验证日志确实出现 3 个测试和构建输出。**零个测试的成功退出也可能显示绿灯**，所以要看执行了哪些测试。

## 4. 制造失败，先保留红灯

1. 从最新 `docs/github-agent-channel-architecture` 创建 `exercise/break-greeting`，并在 `笔记/GitHub Agent Channel 架构与阶段计划.md` 末尾增加一句“本仓库通过 CI 检查 greeting 函数并构建练习页面”。保留这项说明性改动，避免修复故意制造的错误后，整个 PR 与 main 完全相同而没有可合并内容。
2. 仅把 `app.py` 的返回值改为 `return f"Hi, {cleaned}!"`，不修改测试。
3. 提交并创建面向 `docs/github-agent-channel-architecture` 的 PR。
4. 打开 PR 的检查区域，进入 **Test and build**，展开 **Run tests**。
5. 应看到期望 `Hello` 与实际 `Hi` 不一致；本例前两个测试失败，后续构建步骤默认跳过。
6. 先保持这个 PR 打开且检查失败，继续下一节配置规则。此时不要修复或合并。

重新运行旧提交的失败任务并不会自动修复代码。先改变原因，再运行验证。

## 5. 让红灯真正阻止合并

有检查结果和“必须通过”是两件事。在有管理权限且支持 ruleset 的练习仓库中：

1. 打开 Settings → Rules → Rulesets，创建面向默认分支的 branch ruleset。
2. 将执行状态设为 Active，目标选择默认分支或 `docs/github-agent-channel-architecture`。
3. 启用要求通过 PR 合并的规则。
4. 启用要求状态检查通过，选择先前真实运行出现过的 **Test and build** 检查。
5. 保存后回到仍然失败的练习 PR，确认当前提交的 **Test and build** 未通过，并观察普通合并被阻止。记录当前提交和阻止原因，不使用历史失败 run 代替这一步。
6. 在同一个来源分支把返回值改回 `Hello`，保留 README 的说明，提交并 push。
7. 等待新提交的检查通过，确认该必需检查不再阻止合并。若没有其他未满足的规则，此时可以正常合并这个 PR。

个人练习仓库不必要求另一人批准，否则只有自己时可能无法满足评审条件。管理者若有 bypass 权限，界面可能仍提供绕过入口；要区分“规则生效”和“某账号有例外权限”。套餐或组织策略不支持该设置时，可以先理解检查结果，但不能声称已经配置强制门禁。[Ruleset 规则说明](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)

如果当前仓库不能配置 ruleset，仍可执行修复并观察检查通过，只将“阻止合并”的验收记为未完成。完整练习顺序是：**失败 → 配置规则 → 确认阻止合并 → 修复 → 检查通过 → 合并**。

## 6. 常见误解

| 误解 | 应怎样检查 |
|---|---|
| Agent 说测试通过就够了 | 看当前提交的 CI 结果和具体测试日志 |
| 本地通过就必然云端通过 | 对比 Python 版本、系统、依赖和环境变量 |
| 所有 PR 检查测试的都是来源分支单独状态 | 默认 PR checkout 通常检出测试合并提交，结合 base + head 检查 |
| 必需检查永远 pending 就是 runner 慢 | 看 workflow 是否被过滤、检查名称是否已变更 |
| 测试失败就改成允许失败 | 先判断测试还是实现出了问题；跳过检查改变了验证含义 |

PR 默认检出行为见 [checkout](https://github.com/actions/checkout)。

## 7. 验收

保存一个失败 run 和一个修复后成功 run 的链接，指出它们对应的不同提交，并说明失败原因。若启用了规则，同时保留修复前被阻止合并的记录；修复后的旧失败日志不能证明当前提交仍被阻止。

下一篇：[[GitHub 协作与自动化：05 构建、发布与部署]]。
