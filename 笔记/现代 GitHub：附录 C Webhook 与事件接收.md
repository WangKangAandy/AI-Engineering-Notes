---
title: 现代 GitHub：附录 C Webhook 与事件接收
summary: 用可运行的离线验签实验理解 Webhook 原始字节、事件过滤与 delivery ID 去重，并明确公网交付和业务幂等尚需哪些条件。
tags:
  - github
  - webhook
created: 2026-11-18
status: ready
---

# 现代 GitHub：附录 C Webhook 与事件接收

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

API 专题让我们主动询问“现在有哪些 PR”。如果每分钟查询一次，即使没有变化也要请求，还只能在下一轮发现新 PR。Webhook 则在订阅的事件发生时，由 GitHub 向配置好的服务发送 HTTP 请求。推送解决发现变化的入口问题；程序仍可能通过 API 读取当前状态或写评论，两者可以组合使用。[Webhook 概述](https://docs.github.com/en/webhooks/about-webhooks)

本篇是自建集成专题，前置为 [现代 GitHub：附录 B GitHub CLI、API 和 GitHub App](<现代 GitHub：附录 B GitHub CLI、API 和 GitHub App.md>) 和第 7 章的 Python 运行基础。主线 Copilot、Cursor 或 Actions 自动化不要求你搭建公网接收服务。我们使用 Python 3.12 标准库完成离线验签实验：没有服务器、隧道或远端写入，输出只落在进程内存。这样可以先理解信任边界，再决定是否值得部署服务。

## 签名证明的是哪一份内容

接收端不能因为请求里写着 `repository: YOUR_LOGIN/resource-nav` 就相信它。该字段任何人都能伪造。配置 Webhook 时，GitHub 和你的服务持有同一个随机 secret；GitHub 对请求正文的原始字节做 HMAC-SHA256，并放入 `X-Hub-Signature-256`。接收端重算并恒定时间比较，再解析 JSON。[官方验签指南](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)

关键顺序是“读原始 bytes → 验签 → 解析 → 记录 delivery 占位 → 检查仓库、事件与 action”。先解析 JSON 再序列化会改变空格、转义或字段顺序，虽然数据语义没变，字节却已不同。有效签名和非空 delivery 通过后，应先以 delivery ID 做原子占位，再进行事件过滤，避免同一 ID 先被当作 ignored、随后换事件头而重复处理。若接入 HTTP 框架，应使用它提供的原始请求正文接口；不要拿重新拼出的对象计算签名。

附件 [webhook_fixture.py](./_assets/modern-github/integration/webhook_fixture.py) 提供 `valid_signature` 和一个教学收件箱 `Inbox`。只有仓库匹配、事件为 `pull_request`、action 为 `opened` 的有效请求才会进入 `accepted` 列表。其他 action（例如 synchronize）不会因为属于 PR 事件就被当成“打开 PR”处理。secret 仅负责验签，不能作为调用 GitHub API 的访问令牌。

## 用反例检查验签与去重

把附件和 [test_webhook_fixture.py](./_assets/modern-github/integration/test_webhook_fixture.py) 下载到同一个本地目录，在该目录打开 Git Bash：

~~~bash
python --version
python -B -m unittest -v test_webhook_fixture
~~~

示例内的 `local-fixture-only` 是公开教学值，绝不能用于真实 Webhook。测试首先使用 GitHub 文档公布的固定向量，避免签名生成和验签函数出现同一种错误时互相蒙混过关。随后它检查以下行为：

| 输入变化 | 预期观察 | 说明 |
| --- | --- | --- |
| 正确正文与签名 | accepted | 本地验签和过滤通过 |
| 正文末尾增加一个空格 | bad-signature | JSON 仍可能可解析，但原始字节不同 |
| 使用错误 secret 或缺少签名 | 拒绝 | 未验签不能进入处理列表 |
| 相同 delivery ID 再投递 | duplicate，列表仍一项 | 当前进程识别了同一次交付 |
| 保留签名但改 delivery ID | 两次 accepted | 签名不覆盖该请求头；ID 去重不是全面防重放 |
| 重建 Inbox 后再次投递 | accepted | 内存记录在重启后丢失 |
| 换事件类型或目标仓库 | ignored / wrong-repository | 有效签名不等于符合业务条件 |

这组测试故意保留最后两个“不够强”的结果。`X-GitHub-Delivery` 可识别同一次交付，GitHub 的重投递沿用原 ID；但正文签名没有时间戳和完整请求头绑定，持有有效 payload 的重放不能只靠该 ID 消除。真实服务还需要持久记录和业务规则，例如以“仓库 + PR 编号 + 操作版本”标识同一条摘要。[交付最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)

即便把 ID 放进数据库，也不自动得到“评论只发一次”：如果先记录成功再发评论，崩溃可能漏发；先发评论再记录成功，崩溃可能重复发。需要明确处理状态、保留远端评论 ID，遇到不确定结果先读回。内存示例没有跨进程锁；真实服务需要数据库唯一约束或等价原子操作，再设计并发下的状态转换。对于本篇只有内存 append 的示例，不声称解决跨进程并发、事务或 GitHub 副作用幂等。

## 从实验走向真实接收服务时还缺什么

离线测试不会出现在 GitHub 的 Recent deliveries。`localhost` 也不是 GitHub 能访问的地址。真实接入需要你控制的公网 HTTPS 地址、有效 TLS 证书、原始正文保留、secret 安全存储、请求大小限制、日志与运行维护。本篇不提供生产 HTTP 服务实现，也不要求安装外部隧道。

当你已有这样的接收服务时，可以在自己的 `resource-nav` 仓库 Settings → Webhooks → Add webhook 配置完整地址，例如 `https://hooks.example.org/github`；这是占位符，须替换成你实际拥有且可达的地址。Content type 选 `application/json`，生成高熵 secret 并同时配置接收端，保持 SSL verification 开启，只订阅 Pull requests，勾选 Active。配置权限不足时需要仓库管理者操作。[创建 Webhook](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks)

保存后在 Recent deliveries 查看初始 ping；接收端应明确支持 ping 或返回不执行业务的成功响应。再在练习仓库打开一个 PR，核对 `pull_request` / `opened`、delivery ID、目标仓库和接收端处理记录。用 Redeliver 测试同 ID 去重，不能只看 GitHub 显示 2xx：它说明端点接受了 HTTP 请求，不代表后台任务或评论已经完成。异步处理应及时返回，并以队列和业务记录追踪后续结果。GitHub 建议在 10 秒内响应，失败交付需要自己的补偿或重投递策略。[测试 Webhook](https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/testing-webhooks) · [交付最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)

实验结束，在该 Webhook 设置取消 Active 并保存，或删除专用测试 Webhook；另行停止自己的接收服务并清理不再需要的 secret。停用推送不会撤销某个 API token，正如撤销 token 也不会自动停止所有事件接收。

完成离线部分后，你已验证字节验签、过滤和有限去重，并能说明尚未验证公网交付。若要让自建程序以机器人身份调用 API，继续 [现代 GitHub：附录 B GitHub CLI、API 和 GitHub App](<现代 GitHub：附录 B GitHub CLI、API 和 GitHub App.md>)；否则返回 [现代 GitHub：00 导读](<现代 GitHub：00 导读.md>)，无需为了主线去部署服务。

