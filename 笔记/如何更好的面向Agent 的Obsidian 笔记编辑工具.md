---
title: 如何更好的面向Agent 的Obsidian 笔记编辑工具
summary: 区分本库写作技能、Obsidian 格式技能与可选 MCP 操作入口，说明项目配置和使用边界。
tags:
  - agent
  - obsidian
  - mcp
  - skill
created: 2026-07-29
status: evergreen
---

# 如何更好的面向Agent 的Obsidian 笔记编辑工具

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

本库把内容写作、Obsidian 格式和文件操作分开：写作技能帮助组织解释，工具技能处理语法，可用的 MCP 连接提供 vault 操作入口。本地文件工具也能完成编辑。

| 组件 | 仓库 | 作用 |
|------|------|------|
| **写作 Skill** | 本库 `.agents/skills/technical-note-writing/` | 研究、解释、改稿与内容评审 |
| **格式与操作 Skills** | [obsidianmd/obsidian-skills](https://github.com/obsidianmd/obsidian-skills) | 教 Agent 正确写 Obsidian 语法（wikilink、callout、properties、Bases、Canvas 等） |
| **MCP** | [coddingtonbear/obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) | 让 Agent 通过工具读写/搜索本 vault（Obsidian 需保持打开） |

Vault 是当前打开的仓库目录。使用隔离 worktree 时，先确认 Obsidian 打开的也是目标 checkout；本地命令的工作目录与 MCP 实际连接的 vault 不一定相同。

---

## 1. Skill：`kepano/obsidian-skills`

### 有啥用

- 改笔记时遵守 Obsidian Flavored Markdown，而不是当普通文本乱改
- 正确处理 `[[wikilink]]`、embed、callout、YAML properties
- 需要时还能处理 Bases / JSON Canvas / Obsidian CLI

### 项目中如何使用

本库的技能位于项目 `.agents/skills/`，由 Git 管理；Cursor 和 Codex 可从同一位置发现，不需要分别复制一份。

内容任务使用 `technical-note-writing`。涉及特定格式或工具时，再按需加载 `obsidian-markdown`、`obsidian-bases`、`json-canvas`、`obsidian-cli` 或 `defuddle`。语法技能中的项目清单只是格式示例，不作为博客的默认结构。

在客户端技能列表中确认相应名称可见；列表未刷新时重新打开工作区。换机与 MCP 配置见仓库 `.cursor/SETUP.md`，上游更新应核对实际文件后单独进行，不在普通写作中重装插件。

---

## 2. MCP：`obsidian-local-rest-api`

### 有啥用

- Agent 可 list / read / search / create / append / patch 本 vault 笔记
- 通过已配置的服务读写当前 vault；工具调用仍需检查目标文件与修改范围，不能保证内容或格式自动正确

### Obsidian 侧

1. 用 Obsidian **打开本库** `Agent-Notes`（须保持运行）
2. 设置 → **社区插件** → 关闭安全模式（若提示）
3. 确认安装并启用了本库配置所需的 Local REST API 服务及 MCP 接口；配置文件存在不代表本机服务已运行
4. 设置 → 该插件 → 打开 **Enable non-encrypted (HTTP) server**（按本机插件实际设置确认，运行数据不随 Git 分发）
5. 在插件设置里查看 **API Key**（密钥只留本机：插件运行配置或环境变量，**不要写进笔记或提交 Git**）

HTTP MCP 地址：`http://127.0.0.1:27123/mcp/`

### Cursor 侧

本库 `.cursor/mcp.json` 已声明连接，认证来自 `OBSIDIAN_REST_API_KEY`。下方仅展示配置结构，不是完整配置文件；其他客户端需使用各自的配置格式。

```json
"obsidian": {
  "url": "http://127.0.0.1:27123/mcp/",
  "headers": {
    "Authorization": "Bearer <从 Obsidian 插件设置复制 API Key>"
  }
}
```

然后：**Cursor Settings → MCP** 刷新/重启，看到 `obsidian` 为已连接。

### 自检

1. Obsidian 已打开 `Agent-Notes`
2. 浏览器或 curl 访问：`http://127.0.0.1:27123/`（应有 API 响应；未授权会 401，属正常）
3. Cursor Agent 能列出 Obsidian MCP 工具并读一篇笔记

---

## 3. 怎么一起用

1. Obsidian 打开本 vault
2. Cursor Agent 编辑笔记时：
   - **写作 Skill** 指导内容，**Obsidian Skills** 处理特定语法
   - 已核对 vault 的 **MCP** 或本地文件工具执行读写
3. 不要关着 Obsidian 还指望这个 MCP 工作（它跑在 Obsidian 进程里）
