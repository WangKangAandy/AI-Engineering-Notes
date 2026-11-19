---
title: 现代 GitHub：附录 D Actions 工程化选择
summary: 围绕真实维护问题选择 matrix、缓存、复用、并发、权限、OIDC、attestation 和 runner groups，避免为了展示功能增加复杂度。
tags:
  - github
  - actions
  - engineering
created: 2026-11-18
status: ready
---

# 现代 GitHub：附录 D Actions 工程化选择

> 本文收录于 [AI-Engineering-Notes](https://github.com/xallor-ai/AI-Engineering-Notes)，分享 AI 技术研究、工程实践与应用探索。欢迎 Star 关注后续更新。欢迎通过 Issue 交流和纠错。

工程化不是把所有 Actions 功能都加进一个 workflow，而是先确认当前问题，再选择最小工具。

## matrix：确实有多个维度时才用

适用场景是同一测试需要在多个 Python 版本或操作系统上运行：

~~~yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
~~~

matrix 会增加运行次数和费用。resource-nav 只有一个标准库程序，主线使用单版本即可；只有当兼容性成为真实需求，才把矩阵加入 Issue、验收和费用估算。

## 缓存：确认瓶颈再启用

setup-python 可以缓存 pip 目录，但本项目没有第三方依赖，加入缓存不会带来可观察收益。缓存键变化、命中失败和陈旧依赖会增加排错面。

先记录不使用缓存的运行时间，再用一个独立 PR 比较；没有测量差异就不要为了“更专业”添加缓存。

## 复用 workflow：输入和权限要显式

多个仓库需要同一套检查时，可以使用 reusable workflow：

~~~yaml
jobs:
  call-check:
    uses: YOUR_ORG/.github/.github/workflows/python-check.yml@main
    with:
      python-version: '3.12'
    secrets: inherit
~~~

复用 workflow 的权限、输入、Secrets 和版本都必须在调用点可见。不要把仓库特有的路径和发布权限隐藏到“通用” workflow 中。

## concurrency：取消没有价值的旧运行

同一分支连续 push 时，旧的 PR 检查可能已经没有价值：

~~~yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
~~~

发布 workflow 要更谨慎；取消一个已经进入部署阶段的 run 可能留下不完整结果。先为 CI 和 deploy 使用不同的并发组。

## 权限：从只读开始

顶层使用：

~~~yaml
permissions:
  contents: read
~~~

只在具体 job 增加 pages: write、id-token: write 或 pull-requests: write。权限写在 job 上能缩小影响面，也方便审查。

Fork PR、pull_request_target、脚本注入和第三方 action 都需要单独评估。不要因为 action 名称看起来官方就授予全部写权限。

## OIDC、attestation 和可信来源

OIDC 适合让云服务验证 workflow 身份，避免把长期云密钥放在 Secrets；它需要云服务端的信任配置和 job 的 id-token: write。

Artifact attestations 用来证明 artifact 与构建来源之间的关系。它不是简单的 provenance.json；两者都要按实际生成和验证步骤分别说明。没有签发和验证证据，就不能把“配置了 attestation”写成“供应链已证明”。

## runner groups 和 Self-hosted Runner

当多个自托管 Runner 承担不同风险和工具链时，用 runner groups 限制哪些仓库可以调度哪些机器。普通 CI 仍优先使用 GitHub-hosted runner；自托管细节转到附录 A。

不要把不可信 Fork PR 路由到个人电脑或带秘密的 Runner。

## 做选择而不是堆功能

| 真实问题 | 可能选择 | 先验证什么 |
| --- | --- | --- |
| 多版本兼容 | matrix | 版本数量、费用和失败定位 |
| 安装依赖很慢 | cache | 未使用缓存的基线和命中率 |
| 多仓库重复检查 | reusable workflow | 输入、权限、版本和失败反馈 |
| 旧 PR 运行没有价值 | concurrency | 是否会取消正在发布的任务 |
| 需要云端短期身份 | OIDC | 云服务信任关系和 job 权限 |
| 要证明构建来源 | attestation | 实际签发和验证路径 |
| 工具链或内网只在本机 | self-hosted + groups | 可信来源、隔离和退出成本 |

本附录的结束标准不是 workflow 更长，而是你能解释每个工程化选项解决的真实问题、增加的风险和可以撤销的方式。

