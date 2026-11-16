# 来源与设计取舍

核对日期：2026-11-16。以下是本库写作方法的设计依据，不是需要每次写作全部阅读的任务表。技能正文为针对本库编写的综合指引，没有整份复制上游技能；修改时重新核对相关来源及适用条件。

| 来源 | 采用 | 未直接采用及原因 |
| --- | --- | --- |
| [Google Technical Writing：Audience](https://developers.google.com/tech-writing/one/audience) | 从读者已有知识到完成目标所缺的知识，决定解释深度 | 不把受众分析表固定放进每篇正文 |
| [Google：Organizing large documents](https://developers.google.com/tech-writing/two/large-docs) | 渐进展开，概念与实践可以交替，按理解依赖组织 | 不强制每篇都长文、拆篇或带目录 |
| [Diátaxis](https://diataxis.fr/) 与 [Tutorials](https://diataxis.fr/tutorials/) | 区分学习、办事、查阅与理解；教程给出可观察结果 | 本库博客可以结合讲解与操作，不把一种文体视为唯一合法结构 |
| [Sentry blog-writing-guide](https://github.com/getsentry/skills/blob/main/skills/blog-writing-guide/SKILL.md) | 内容回答真实问题，说明机制、取舍与局限；评审给具体改写 | 不继承品牌语气、SEO 配额、传播指标或强制幽默 |
| [HuggingFaceFW finephrase AGENTS.md](https://huggingface.co/spaces/HuggingFaceFW/finephrase/blob/main/AGENTS.md) | 公式配直观解释，图表与论述关联，定义术语，视觉检查 | 不继承 MDX 路径和组件，不删除科学结论必要的不确定性 |
| [NihilDigit writing-style](https://github.com/NihilDigit/writing-style/blob/main/SKILL.md) | 中文语序、信息取舍、减少作者过程与虚构叙事 | 不把词语偏好变成覆盖所有文体的禁令 |
| [Composio content-research-writer](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md) | 从研究到提纲、正文和局部反馈；保留作者风格 | 不建立逐文章目录，不要求逐节确认，不将研究待办作为成稿 |
| [obra writing-clearly-and-concisely](https://github.com/obra/the-elements-of-style/blob/master/skills/writing-clearly-and-concisely/SKILL.md) | 具体表达，段落聚焦，删除冗词 | 英文语法规则不机械翻译为中文约束 |
| [Andy Matuschak：Evergreen notes](https://notes.andymatuschak.org/Evergreen_notes) | 围绕概念、建立有效连接、持续修订 | 私人思考笔记与公开教学文章分开处理，不据此预建 Inbox 或强制拆成碎片 |

## 仓库与客户端设计

- 正文平铺、资源按文章或系列归组，是本库已确认的选择；不是所有知识库都必须采用的普遍规则。主题可交叉，tags 与导航比深目录更适合当前内容规模。
- `AGENTS.md` 记录长期约定，Skill 提供写作方法，Cursor rule 提供入口与客户端操作。规则不在三个地方复制，维护一处后由其他入口引用。
- [Codex 技能发现](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) 和 [Cursor 技能目录](https://cursor.com/docs/skills#skill-directories) 均说明支持项目 `.agents/skills/`。使用一份项目技能，避免符号链接和重复定义；这是文档支持，不代替在具体客户端中的发现测试。
- [OpenAI：Rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) 强调明确触发边界、按需加载及避免过度规定步骤。本技能不要求每次小编辑先读全库或逐节询问。
- [Obsidian 内部链接](https://help.obsidian.md/links) 说明双链、Markdown 链接及块引用边界。本库沿用双链，但发布到其他阅读入口时须检查兼容性，不以本地解析代替公开导航验证。

## 使用与更新边界

社区技能是设计材料，其自述和仓库热度不能证明质量。采用某项方法要说明它改善哪个真实问题；行为验证与语法校验分别报告。来源变化时只更新受影响的方法，不为“保持最新”重写整个技能。

图表、示例和来源检查依据请求的范围进行。没有运行条件时明确证据限制；不通过安装软件、开启付费服务或修改远端来补一个未经授权的“验证”。
