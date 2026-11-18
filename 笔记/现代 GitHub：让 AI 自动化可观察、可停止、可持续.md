---
title: 现代 GitHub：让 AI 自动化可观察、可停止、可持续
summary: 通过资源审阅 workflow 理解重复运行、输出去重、失败重试和停止边界，建立可追溯的成本与维护记录。
tags:
  - github
  - automation
  - agents
created: 2026-11-18
status: learning
---

# 现代 GitHub：让 AI 自动化可观察、可停止、可持续

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

学习路线：[GitHub 协作与自动化：01 学习路线](<GitHub 协作与自动化：01 学习路线.md>)。

第 22 章让一个新 PR 产生一条资源审阅评论。现在考虑第二次运行：用户点击 Re-run、模型超时、写评论后网络断开，分别会怎样？如果每次只看 run 的绿色或红色，容易把已有写入再做一次。可持续自动化首先要回答“哪一步发生了什么”，然后才是重跑。

## 观察同一件事的四个标识

每次记录 workflow 源码版本、PR 号码和 head SHA、run ID 与 attempt、评论 URL。PR 号码标识讨论对象，head SHA 标识代码版本，run ID 和 attempt 标识执行，评论 URL 标识副作用。PR 更新后原评论可能仍在，但它的分析依据已经过期。

用第 9、13 章的 gh 工具读取一次运行。以下在已确认账号的终端执行，把数字替换为自己的实际值：

```bash
gh run list --repo YOUR_LOGIN/resource-nav --workflow resource-review.lock.yml --limit 10
gh run view 123456789 --repo YOUR_LOGIN/resource-nav
gh run view 123456789 --repo YOUR_LOGIN/resource-nav --log-failed
gh pr view 25 --repo YOUR_LOGIN/resource-nav --comments
```

日志、summary 和评论分别回答执行过程、输出处理结果与实际写入。不要复制 token 到诊断记录。网页如果显示失败，先打开失败 job，再判断是否已有评论。

## 去重不是“永远只写一次”

第 22 章 `max: 1` 只限制一次运行中允许的评论数量；Re-run 是另一轮处理，仍可能新增评论。`opened` 不监听每次 push，因此不会在普通代码更新时自动重新评论，但人工重跑仍然存在。

对持续维护的资源摘要，可以在 `safe-outputs.add-comment` 内增加：

```yaml
    replace-older-comments: true
```

修改后的完整输出片段是：

```yaml
safe-outputs:
  report-failure-as-issue: false
  allowed-domains: [skills.github.com, git-scm.com]
  add-comment:
    target: triggering
    max: 1
    replace-older-comments: true
```

重新编译并审阅 lock 后合并。当前 gh-aw 通过作者与 workflow 标记查找匹配评论，存在时更新最近的一条；没有时创建。保留生成的 footer，它帮助追溯来源。此选项不能同时使用 `hide-older-comments`。[评论替换语义](https://github.github.com/gh-aw/reference/safe-outputs/#comment-creation-add-comment)

这是工具内置的输出替换，不是“根据 PR + head SHA 确保只消费一次模型”的承诺。模型仍会运行并计费；API 查询与写入之间也可能发生并发和失败。若业务需要按 SHA 记录处理状态，那是额外状态存储和原子性设计，本书不把一个自然语言“不要重复”伪装成该机制。

可以在配置合并后的新资源 PR 上做一次有限实验：先等待首次评论完成，记录评论 URL；再在 Actions 对这次运行手动 Re-run 一次，比较最终评论 URL、内容中的 SHA 和 run 链接。出现新评论就检查编译版本、标记和匹配范围，不声称去重已验证。实验有两次模型成本，先确定额度。

## 并发与失败重试

gh-aw 当前提供 workflow 级和 engine 级并发控制，输出 job 也可单独串行。它们负责限制同时进行的任务；不能撤回已经写出的评论，也不是全局事务。第 22 章配置使用编译器默认值，应检查当前 lock，而不是凭记忆声称所有运行都会自动取消或排队。[并发控制](https://github.github.com/gh-aw/reference/concurrency/)

| 最后可确认的阶段 | 合理动作 |
| --- | --- |
| 编译失败，未部署新 lock | 修复源码并编译，不重跑旧配置假装测试了新版本 |
| 模型认证失败，尚未产出业务输出 | 检查 token 权限、过期时间与额度，修复后只重试一次 |
| 模型输出无依据或引用错 PR | 修正输入和提示，重新预览；不靠重试碰运气 |
| 输出校验拒绝，确认没有写评论 | 检查目标和输出格式，修复后再运行 |
| 日志超时，无法确定评论是否已写 | 先查目标 PR 和评论标记；状态未确认前不要盲目重跑 |
| 评论已经写入，收尾 job 失败 | 保留已有评论，定位收尾失败，不把整体红灯等同“全部没做” |

“可重试”描述某类错误，不代表副作用安全可重放。运行被取消时也可能正处于 API 请求已到达、回执尚未收到的窗口。没有取得证据时写“输出状态未知”，继续查询目标对象；本章不承诺 exactly-once。

## 成本和人工边界

本练习的限流策略是自己制定的：只监听一个 `opened` 事件、只匹配资源文件、Agent 执行步骤超时十分钟、单次至多一条输出、实验只重跑一次。编译器负责落实支持的字段，平台负责实际账单；这些策略不能构成固定金额上限。超时前已发生的模型请求仍可能计费；该字段不等于整次 workflow 十分钟结束，初始化、检测、输出 job 有各自时限。

开始实验前查看 Copilot 使用量与 Actions 用量，记录当期可用预算，并在账户提供硬限制时按自己承担得起的额度配置。先观察一次调用，再决定是否继续；不要为收集“更稳定结果”打开 `synchronize`、schedule 或对所有仓库批量启用。[gh-aw 成本管理](https://github.github.com/gh-aw/reference/cost-management/)

自动评论应保持建议身份。AI 可以指出资源分类可能不合适；批准、合并与部署审批继续使用前面章节的人工责任和仓库门禁。评论看起来合理不应自动触发合并。

## 停用未来触发，取消当前运行

停用 workflow 和取消 run 是两个动作。在 Actions 的 Resource review 页面菜单选择 **Disable workflow**，阻止后续启动；随后到仍在执行的 run 选择 **Cancel workflow**。也可以显式指定对象：

```bash
gh workflow disable resource-review.lock.yml --repo YOUR_LOGIN/resource-nav
gh run cancel 123456789 --repo YOUR_LOGIN/resource-nav
```

检查 workflow 已 disabled，并确认该 run 的最终状态；取消请求发出不等于执行已经停止。既有评论、提交和已消耗额度都不会回滚。若怀疑凭据泄露，在个人 token 页面撤销令牌，并删除 repository secret；删除 secret 不等同撤销已经发出的凭据。

计划长期不用时，经 PR 删除本任务的 Markdown 与 lock，避免以后重新编译时“复活”。不要只删除源文件留下可执行 lock。恢复时先核对凭据、模型资格、编译器版本及当前数据结构，再从 staged 手动预览开始；临时停用后可以使用 `gh workflow enable`，但不要绕过上述核对。

这章结束时应能拿出一次 run 到评论的对应记录、一项有证据的重跑结论，以及已确认的停止状态。尚未实际执行的步骤仍标为未验证；与此相反，单纯读过配置不能算完成自动化实验。

返回实践：[独立完成一个新的需求](<现代 GitHub：独立完成一个新的需求.md>)。
