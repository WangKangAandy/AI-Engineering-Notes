# 换机 / 新环境部署清单

clone 本库后，Cursor 打开本目录可读取 rules、项目 skills 与 MCP 声明；Codex 从 `.agents/skills/` 发现项目技能，并按根 AGENTS.md 使用仓库约定。MCP 配置按客户端分别设置，不能假定共享。还需本机一次性配置：

## 1. Obsidian

1. 安装 Obsidian，打开本 vault
2. 启用社区插件 **Local REST API with MCP**（`community-plugins.json` 已声明；缺插件时从社区重装）
3. 开启 insecure HTTP（`27123`），复制 API Key

## 2. 环境变量（密钥，勿提交）

PowerShell（当前用户）：

```powershell
[Environment]::SetEnvironmentVariable("OBSIDIAN_REST_API_KEY", "<你的 API Key>", "User")
```

然后**重启 Cursor**。项目 `.cursor/mcp.json` 通过 `${env:OBSIDIAN_REST_API_KEY}` 注入，仓库内无明文密钥。

## 3. GitHub 免密（可选）

```powershell
winget install --id GitHub.cli -e
gh auth login
gh auth setup-git
```

## 4. 自检

- Cursor Settings → MCP：`obsidian` 已连接
- Agent 能 `vault_list` / 读一篇笔记
- `git push` 不再要密码（已 `gh auth`）

## 已进仓库 vs 仅本机

| 进 Git | 仅本机 |
|--------|--------|
| `.cursor/rules/` | `OBSIDIAN_REST_API_KEY` |
| `.agents/skills/` | `.obsidian/plugins/**/data.json` |
| `.cursor/mcp.json`（无密钥） | `~/.cursor/mcp.json` 里其它个人 MCP |
| `笔记/` 正文与 `AGENTS.md` | GitHub PAT / SSH key |

笔记：`笔记/<标题>.md` 平铺，文章资源按需放在 `笔记/_assets/<标识>/`。目录和写作约定以根 AGENTS.md 为准。

## 项目技能检查

Obsidian 默认在 `笔记/` 新建笔记，粘贴附件先进入 `笔记/_assets/`。全局设置不能按文章自动分组；发布或提交前将新增附件归入相应文章/系列目录并更新引用。不要把界面默认保存位置当成资源归档已经完成。

本库的写作技能与 Obsidian 工具技能只有 `.agents/skills/` 一份来源，不要复制回 `.cursor/skills/`。在 Cursor 技能列表和 Codex 技能选择器分别确认 `technical-note-writing` 与 `obsidian-markdown` 可见；发现列表未刷新时重新打开工作区。列表可见后仍需用实际写作任务验证。迁移旧 checkout 时先核对 Git 分支，不手工覆盖其他工作区。

