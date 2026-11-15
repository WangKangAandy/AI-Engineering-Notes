# Agent Notes — Cursor / Agent 约定

Obsidian vault + Git。细则：`.cursor/rules/vault.mdc`（建设与编辑）、`.cursor/rules/obsidian-stack.mdc`（Skill/MCP）。换机：`.cursor/SETUP.md`。

- 笔记只在 `笔记/`，默认平铺 `笔记/标题.md`
- 保留 `AGENTS.md`、`.cursor/`、`.obsidian/`、Git
- 不预建 Inbox / 编号夹 / 附件 / 模板；没有的配置不加
- 有歧义先问；只做被要求的事；「以后再说」则现在不做
- 推送或往某 PR 分支继续提交前，先确认远端 PR 状态（`open` / `merged` / `closed`）。已合入或已关闭的 PR **禁止**再往其头部分支推；后续改动从最新 default 开新分支并开新 PR
- 命名范围须等于内容范围：标题/规范名覆盖多宽，正文就写多宽；禁止大词小用
- 笔记正文只写读者要跟着做的内容与结论。禁止把与 Agent 的纠偏、格式/语法争论、工具限制辨析、编辑过程说明写进正文；这类取舍在对话或本文件解决，正文直接采用正确写法
- Markdown 加粗内容以括号等标点结尾且后面紧接正文时，将标点移出加粗范围（如 `**反向传播**（Backpropagation）沿……`）或在结束的 `**` 后加空格，避免 CommonMark 无法识别加粗闭合。

## 笔记 metadata 规范

每篇博客笔记（`笔记/**/*.md`）须有 YAML frontmatter，并遵守下列字段约定；新建或编辑时补齐、勿无故删除。不适用于 `AGENTS.md`、`SKILL.md` 等项目配置或指令文件。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 文章标题，通常与一级标题一致 |
| `summary` | 是 | 一两句摘要：主题是什么、读者能得到什么 |
| `tags` | 是 | 主题标签列表 |
| `created` | 是 | 创建日期，`YYYY-MM-DD` |
| `status` | 是 | 如 `evergreen` / `ready` / `published` 等，表示文档状态 |

```yaml
---
title: 示例标题
summary: 一两句摘要，说明主题与读者收益。
tags:
  - example
created: 2026-11-15
status: evergreen
---
```

## 笔记开头规范

每篇 Markdown 笔记（`.md`）都应在正文一级标题后、文章内容前放置以下仓库介绍，使用 Markdown 引用块和可点击链接；新建或编辑笔记时补齐，已有时不重复添加。本规则适用于笔记正文文件，不适用于 `AGENTS.md`、`SKILL.md` 等项目配置或指令文件。

```markdown
> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。
```
