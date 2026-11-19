---
title: 现代 GitHub：附录 B GitHub CLI、API 和 GitHub App
summary: 从 gh 的日常命令走到 gh api 和 GitHub App，理解个人登录、token、安装身份与服务端权限的边界。
tags:
  - github
  - gh
  - api
  - github-app
created: 2026-11-18
status: ready
---

# 现代 GitHub：附录 B GitHub CLI、API 和 GitHub App

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新。欢迎通过 Issue 交流和纠错。

主线只需要 gh 的少量命令。只有当网页和现有命令无法表达需求时，才进入 API；只有当程序需要自己的安装身份、权限和生命周期时，才注册 GitHub App。三者不是从易到难的同一条命令列表。

## gh 的日常命令

先检查登录：

~~~bash
gh auth status
gh repo view YOUR_LOGIN/resource-nav
gh issue list --repo YOUR_LOGIN/resource-nav
gh pr list --repo YOUR_LOGIN/resource-nav
gh run list --repo YOUR_LOGIN/resource-nav
~~~

查看具体对象：

~~~bash
gh issue view ISSUE_NUMBER --repo YOUR_LOGIN/resource-nav
gh pr view PR_NUMBER --repo YOUR_LOGIN/resource-nav
gh run view RUN_ID --repo YOUR_LOGIN/resource-nav --log-failed
~~~

创建 PR：

~~~bash
gh pr create --repo YOUR_LOGIN/resource-nav --base main --head BRANCH_NAME --title "..." --body-file pr-body.md
~~~

gh 调用的是 GitHub API，但它会把常见对象格式化成适合人的输出。命令成功只代表请求被接受；仍要回到网页或用 read-back 命令核对状态。

## 用 gh api 读回仓库对象

先做只读请求：

~~~bash
gh api repos/YOUR_LOGIN/resource-nav
gh api repos/YOUR_LOGIN/resource-nav/issues --paginate
gh api repos/YOUR_LOGIN/resource-nav/pulls
~~~

使用 jq 只取字段：

~~~bash
gh api repos/YOUR_LOGIN/resource-nav/issues --jq '.[] | [.number, .state, .title] | @tsv'
~~~

列表接口可能分页；不加 --paginate 不能把“当前响应没有对象”解释成“仓库没有对象”。

## 一次受控写入

对自己的练习 Issue 添加一条评论：

~~~bash
gh api repos/YOUR_LOGIN/resource-nav/issues/ISSUE_NUMBER/comments \
  --method POST \
  --field body='API 写入测试：评论已由 gh api 创建。'
~~~

读回评论并核对：

~~~bash
gh api repos/YOUR_LOGIN/resource-nav/issues/ISSUE_NUMBER/comments \
  --jq '.[-1] | {id, body, user: .user.login}'
~~~

写入前确认仓库、Issue 编号和当前账号。不要把从网页复制的任意编号直接放进脚本；先用 GET 读回，再决定 POST。

## 什么时候需要 GitHub App

个人 token 适合一次性的个人操作。GitHub App 适合：

- 服务有自己的身份，而不是冒充某个用户；
- 只需要特定仓库和权限；
- 需要安装、撤销、轮换和审计；
- 需要用 installation token 短期访问 API。

注册 App、安装 App、生成私钥和服务端签名是不同阶段：

1. 在 Settings → Developer settings → GitHub Apps 注册；
2. 只申请本例需要的 repository permissions；
3. 生成并安全保存私钥；
4. 将 App 安装到目标仓库；
5. 使用 App ID、私钥和 installation ID 生成短期 token；
6. 用 token 做一次只读 API 请求；
7. 最后撤销安装或删除密钥。

App 安装成功不等于服务端已经能工作；服务端读回一个仓库对象才是另一层证据。

## 运行随书的最小 App 实验

随书的 [app_practice.py](<_assets/modern-github/integration/app_practice.py>) 将上面的阶段串成一个只针对 `resource-nav` 的实验。它使用 PyJWT 生成短期 App JWT，换取 installation token，读取一个 PR；`comment` 模式才申请 Pull requests write，并在写入后读回评论，最后撤销 installation token。

先在 Git Bash 创建临时虚拟环境并安装依赖：

~~~bash
python -m venv .venv-app
source .venv-app/Scripts/activate
python -m pip install PyJWT
~~~

在 GitHub App 的 Credentials 页面复制 App 的 Client ID，在本机保存刚下载的 PEM 私钥，然后只在当前 Git Bash 会话设置环境变量：

~~~bash
export APP_CLIENT_ID='YOUR_APP_CLIENT_ID'
export APP_PRIVATE_KEY_PATH="$PWD/app-private-key.pem"
~~~

不要把 PEM 文件、Client ID 或环境变量值加入 Git。确认 App 已安装到自己的 `resource-nav`，并且有 Pull requests read 权限。先运行只读实验：

~~~bash
python _assets/modern-github/integration/app_practice.py read \
  --repo YOUR_LOGIN/resource-nav \
  --pr PR_NUMBER
~~~

成功时应看到 App、installation、目标仓库、短期 token 到期时间和 PR 读回结果，随后看到 Installation token revoked。这里的 PR_NUMBER 换成自己的开放 PR 编号。

只有在确认只读实验成功后才运行受控评论。为评论准备一个不含密钥的文本文件：

~~~bash
cat > app-comment.md <<'EOF'
App 实验评论：已完成一次受控读回。
EOF
python _assets/modern-github/integration/app_practice.py comment \
  --repo YOUR_LOGIN/resource-nav \
  --pr PR_NUMBER \
  --body-file app-comment.md \
  --confirm YOUR_LOGIN/resource-nav#PR_NUMBER
~~~

`comment` 模式需要 App 的 Pull requests write 权限；脚本会打印写入回执，再按评论 ID 读回正文和机器人身份。若读回失败，不要立即重试，先使用回执检查评论是否已经写入。实验结束后删除 PEM、临时 body 文件和虚拟环境，或撤销 App 安装。

本实验未验证云端部署，也不要求把 App 私钥放进仓库或 Actions Secret；它只证明本机服务可以用最小 installation token 读回和可选评论。

## 权限最小化

如果程序只读 Issue，选择 Issues read；如果要发表评论，才授予 Issues write。不要因为未来可能使用 Pull Request 就提前给 administration 或 contents write。

把私钥放入凭据系统，不放入仓库、Issue、workflow 日志或命令历史。更换密钥时先验证新密钥，再撤销旧密钥。

## 结束实践

完成读回后：

- 删除本地临时 token；
- 撤销不再需要的 App 安装；
- 删除无用私钥；
- 在 Issue 中记录实际权限和撤销结果。

API 和 App 的失败必须区分为认证失败、权限不足、对象不存在和请求格式错误。不要把所有 404 都解释成 GitHub 没有这个对象。

