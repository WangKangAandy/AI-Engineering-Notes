---
title: 现代 GitHub：终章 一次完整升级
summary: 不再学习新功能，独立把一个新需求从 Issue、修改、PR、CI 和发布走到人工验收，并决定是否使用 Agent。
tags:
  - github
  - practice
  - capstone
created: 2026-11-18
status: ready
---

# 现代 GitHub：终章 一次完整升级

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新。欢迎通过 Issue 交流和纠错。

终章不再介绍新的 GitHub 产品。你要独立完成一项范围明确的新需求，并用前面建立的证据链交付。

## 新需求

让页面在标题下显示“共 N 项资源”，其中 N 来自经过 catalog.py 校验的资源数量。

完成条件：

- resources.csv 的校验规则保持不变；
- build.py 使用已加载的资源数量生成页面摘要；
- test_catalog.py 或新的构建测试覆盖数量为 2 的结果；
- 如果要测试空列表渲染，明确这是 render_page 的函数层测试；catalog.py 仍拒绝空 CSV；
- Pull Request 关联新的 Issue；
- CI 在 PR 上通过；
- Pages 页面显示与当前资源清单一致的数量，或明确记录因账号/环境限制无法完成的验证；
- 交付说明包含提交 SHA、run URL、页面 URL 或失败边界。

这项需求与第 4～5 章已经完成的文档协作任务不同，也不重复第 7 章的输入校验；它只增加构建结果中的数量摘要。

## 先确认起点

在 Git Bash 中：

~~~bash
cd ~/projects/resource-nav
git switch main
git pull --ff-only origin main
git status --short --branch
python -m unittest discover -s . -p 'test_*.py' -v
~~~

如果 main 不干净、测试不能通过或远程地址不是自己的仓库，先回到第 2～4 章处理，不要从坏状态开始终章。

## 先写 Issue 再分工

创建 Issue，写出现状、结果、范围和完成条件。可以把工作拆为两个子 Issue：

1. 在 build.py 中生成数量摘要；
2. 为 render_page 和页面验收补测试与说明。

如果你使用 Agent，只把第二个子项交给它，明确允许文件和禁止文件；如果不使用 Agent，就在自己的分支中完成同一契约。工具入口不同，验收标准不变。

## 选择工作路径

人工路径：

~~~bash
git switch -c feature/resource-count
~~~

Agent 路径：

- 从 Issue 启动任务；
- 让 Agent 先给计划；
- 核对分支和允许文件；
- 让它运行第 7 章的测试；
- 回到 PR 进行人工验收。

不论选择哪条路径，都要查看实际 diff。不要用 Agent 的自述替代文件和运行证据。

## 交付顺序

按前面章节的边界完成：

1. 修改数据和程序；
2. 添加或修改测试；
3. 本机运行测试和 build；
4. 创建 Pull Request；
5. 让 CI 运行并修复失败；
6. 评审差异和权限；
7. 合并；
8. 观察 Pages 或记录无法访问的原因；
9. 回到 Issue 核对所有完成条件。

每一步都记录一个可回看的对象：Issue、commit、PR、run、artifact、页面或明确的失败说明。

## 交付记录

最终在 Issue 或 PR 评论中写：

~~~markdown
## 结果
- Issue：#ISSUE_NUMBER
- PR：#PR_NUMBER
- 合并提交：COMMIT_SHA
- CI：RUN_URL
- 页面：PAGE_URL 或未完成原因

## 验收
- [x] 数据校验
- [x] 测试通过
- [x] PR 已评审并合并
- [ ] Pages 已访问（如果账号或环境限制，请说明）
- [x] 变化范围与需求一致
~~~

把占位符替换成自己的对象。若没有云端证据，使用“未完成原因”，不要编造 URL 或运行编号。

## 复盘

回答三个问题：

1. 哪个对象最早让需求变得可验收；
2. 哪次失败最早暴露了真实问题；
3. 哪一步适合自动化，哪一步必须保留人的判断。

如果你发现某一步只能依赖书中作者的仓库、分支、Issue、Secrets 或产品计划，说明主线仍未完成可迁移设计，应回到对应章节修正。

本书的目标不是记住所有 GitHub 按钮，而是能够在真实项目中保持一条可追溯、可验证、可恢复的工作链。

