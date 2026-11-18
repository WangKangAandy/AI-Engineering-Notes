---
title: 现代 GitHub：通过 API 操作仓库对象
summary: 从 gh api 的请求与响应理解仓库、Issue 和 PR，再对自己的练习 Issue 完成一次可读回核验的评论写入。
tags:
  - github
  - api
created: 2026-11-18
status: ready
---

# 现代 GitHub：通过 API 操作仓库对象

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新，也欢迎通过 Issue 交流和纠错。

读过 [现代 GitHub：用 gh 串起日常协作](<现代 GitHub：用 gh 串起日常协作.md>) 后，你已经能用 `gh issue view` 查看需求。API 专题进一步回答：当现成命令没有提供某个字段，程序怎样访问同一个对象？本篇仍使用自己的公开仓库 `YOUR_LOGIN/resource-nav`，终端为 PowerShell 7，`gh` 已安装并登录。API 操作远端对象，不取决于当前 Git 分支；即使本地停在 `main`，评论也不会变成一次 Git 提交。

## 从网页对象走到请求与响应

一次 REST 请求至少有方法和地址。`GET` 读取，`POST` 常用于创建，`PATCH` 更新，`DELETE` 删除；具体动作由端点定义，不能只凭方法猜副作用。响应包含状态码、响应头与正文。JSON 正文里的对象用字段名访问，数组用位置或遍历访问；`null` 表示当前字段没有值，并非命令失败。

先把账号占位符替换成你自己的登录名，确认请求目标：

```powershell
$repo = 'YOUR_LOGIN/resource-nav'
gh auth status
gh api "repos/$repo" --jq '{name: .full_name, branch: .default_branch, url: .html_url}'
```

你应看到自己的仓库和 `main`。`--jq` 只筛选显示结果，不改变服务器返回的数据或权限。去掉它可观察完整 JSON；加 `--include` 可看状态码与限流响应头。`gh api` 复用 gh 的认证，环境变量 `GH_TOKEN` 等也会影响所用凭据，因此不要把“网页登录的是我”当成 CLI 身份证据。[gh api 手册](https://cli.github.com/manual/gh_api)与[CLI 环境变量说明](https://cli.github.com/manual/gh_help_environment)列出了具体行为。

```powershell
gh api --method GET "repos/$repo/issues?state=all&per_page=10" --jq '.[] | {number, title, pull_request}'
gh api --method GET "repos/$repo/pulls?state=all&per_page=10" --jq '.[] | {number, title, merged_at}'
```

这里必须解释一个看似异常的结果：Issues 列表可能包含 PR。GitHub 把 PR 的标题、正文、标签和时间线评论纳入 Issue 公共模型；有 `pull_request` 字段的项目是 PR。PR 的 diff、提交和行内评审则有专用端点。想只看普通 Issue，可筛选 `select(.pull_request == null)`。因此以后给 PR 发普通评论仍会调用 `/issues/{number}/comments`，不是行内 review comments。[Issue comments API](https://docs.github.com/en/rest/issues/comments)

## 列表为何可能缺了一半

`per_page=10` 是一页的条数，不是仓库总数。列表接口可能通过响应头里的下一页链接继续返回结果。对自己的小练习库，可以这样遍历所有页：

```powershell
gh api --method GET --paginate "repos/$repo/issues?state=all&per_page=100" --jq '.[] | select(.pull_request == null) | [.number, .title] | @tsv'
```

`--paginate` 会增加请求次数；没有必要在大型仓库反复全量扫描。默认输出可能是连续多页 JSON，若要把整个结果交给 JSON 解析器，应加 `--slurp` 收成外层数组，再考虑每页数组的层级。本篇逐页用 jq 提取行，因此不用假设输出天然是一份数组。[分页说明](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)

`gh api` 添加 `-f` 或 `-F` 参数时，默认方法会从 GET 切到 POST。读取时显式写 `--method GET`，让参数成为查询条件；写入时显式写 `--method POST`，让代码审阅者一眼看出会产生副作用。JSON 输入用文件传递，避免 PowerShell 和 JSON 的两层引号互相干扰。

## 只给自己的一条练习 Issue 发评论

回到网页，在自己的 `resource-nav` 选择前面练习建立的一个普通 Issue。复制其编号，先执行读取确认；下面的 `1` 只是示例，必须换成实际编号。

```powershell
$issueNumber = 1
gh api "repos/$repo/issues/$issueNumber" --jq '{number, title, html_url, pull_request}'
```

确认 URL、标题和归属都是预期，且这是允许你留言的练习对象。公开可读不代表拥有写权限。细粒度凭据须包含该仓库，并满足端点所列权限；本例普通 Issue 评论使用 Issues 写权限。gh 默认用户登录或其他令牌的授权方式不同，遇到拒绝先查身份与目标，不要直接扩大到所有权限。[创建评论权限](https://docs.github.com/en/rest/issues/comments#create-an-issue-comment)

下一段会真正发布一条公开评论。先生成本地请求文件并阅读；它保存在系统临时目录，避免混入项目文件：

```powershell
$bodyPath = Join-Path ([IO.Path]::GetTempPath()) 'resource-nav-api-comment.json'
$marker = 'api-lab-' + [guid]::NewGuid().ToString()
@{ body = "API 练习：已核对资源导航 Issue 的目标。标记：$marker" } |
    ConvertTo-Json | Set-Content -LiteralPath $bodyPath -Encoding utf8NoBOM
Get-Content -LiteralPath $bodyPath
```

确认正文后运行写入。`--input` 读取的是完整 JSON 对象，不能直接给一个纯文本文件；不要将 API token 写进这个文件。

```powershell
$response = gh api --method POST "repos/$repo/issues/$issueNumber/comments" --input $bodyPath
if ($LASTEXITCODE -ne 0) { throw '评论请求未确认成功；先查远端，不要直接重跑' }
$comment = $response | ConvertFrom-Json
$comment | Select-Object id, html_url, body
gh api "repos/$repo/issues/comments/$($comment.id)" --jq '{id, author: .user.login, body, html_url}'
```

用返回的 `html_url` 打开网页，核对作者、正文标记和 Issue。请求成功的回执与再次 GET 读回共同说明这条评论确实存在；仅终端没有报错不够。若 POST 超时，服务器可能已经完成写入而响应丢失。先列出评论并搜索 `$marker`，确认是否已有记录，再决定要不要重试；POST 评论没有由这段代码提供的幂等保证。

练习结束可保留有意义的记录。若要清理，只删除刚才记录的评论 ID，并在网页确认，不要按“最后一条评论”猜测目标：

```powershell
gh api --method DELETE "repos/$repo/issues/comments/$($comment.id)"
Remove-Item -LiteralPath $bodyPath
```

## 遇到错误时读哪一层

401 通常先查认证；403 可能是权限、策略或限流；404 可能是路径错误，也可能是无权查看的私有对象；422 通常需要检查参数与验证错误。保留状态码和响应错误正文，不要把 token 或完整认证头贴进 Issue。[官方排错说明](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api)

对限流，观察 `x-ratelimit-remaining`、`x-ratelimit-reset` 和 `retry-after`。未认证公开请求通常是每 IP 每小时 60 次，常见用户认证额度是每小时 5,000 次，但搜索、安装身份及次级限流另有规则。不能把 5,000 当成每个 API 的固定配额。遇到限流按服务端等待要求退避，不用密集重试验证它是否解除。[REST 限流](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)

完成本篇意味着你能解释目标、身份、请求体和返回对象，并对一条受控写入留下可读回的证据。需要监听变化时进入 [现代 GitHub：接收和验证 Webhook 事件](<现代 GitHub：接收和验证 Webhook 事件.md>)；需要独立机器人身份时进入 [GitHub 协作与自动化：08 GitHub App 注册与权限配置](<GitHub 协作与自动化：08 GitHub App 注册与权限配置.md>)。不做自建集成可直接返回 [GitHub 协作与自动化：01 学习路线](<GitHub 协作与自动化：01 学习路线.md>)，继续主线。
