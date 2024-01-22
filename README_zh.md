<a name="readme-top"></a>

<div align="center">
<a href="https://gitmaya.com" target="_blank" style="display: block" align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ConnectAI-E/GitMaya/assets/50035229/45cfd4f3-9c17-44d2-b6b7-3aa97c08006b" width="655" height="auto">
    <img alt="GitMaya - 在聊天中进行Git流程" src="https://github.com/ConnectAI-E/GitMaya/assets/50035229/1c28f0ca-d6e6-4ebd-b858-c4be3eff845e" width="655" height="auto">
  </picture>
</a>
<p align='center'>
  <samp>一个开源的、高性能的GitOps工具 one chat = one repo 从此告别双边协同</samp>
<br/>
 <samp>支持飞书、discord、slack 等 <sup><em>(完全开源)</em></sup></samp>
</p>

<!-- SHIELD GROUP -->
[![][github-logo-shield]][github-logo-link]
[![][github-contributors-shield]][github-contributors-link]
[![][github-forks-shield]][github-forks-link]
[![][github-stars-shield]][github-stars-link]
[![][github-issues-shield]][github-issues-link]
[![][github-license-shield]][github-license-link]<br>

</div>

<p align="center">
    <a href="https://gitmaya.com"> 🖥 立即尝试 GitMaya </a>
</p>

<strong align="center">
<samp>

[**English**](./README.md) · [**简体中文**](./README_zh.md)

</samp>
</strong>

https://github.com/ConnectAI-E/GitMaya/assets/50035229/490b87d3-47f7-4a89-a4c7-737df359d67d

## 🔥 功能列表

### 🧑🏻‍💻 所有代码完全开源

以开发者为中心，由开发者设计，为开发者打造。

### 🌐 跨平台的愉悦体验

享受在不同平台上的无缝沟通，IM计划支持 **Feishu, Discord, Slack, Microsoft Teams, 和 Telegram**。

Git计划支持**GIthub, GitLab, SourceForge 和 Bitbucket**。

开发者在哪里，GitMaya就在哪里。

### 🔄 One Repo = One Chat
体验 "One Repo = One Chat" 的完美同步，让协作流畅无阻！

### 💬 简化 GitHub 消息互动：
从您喜爱的聊天平台直接管理所有 GitHub 互动，不再需要切换上下文。

### 🚀 Issue 全集成
即时处理Issue，随时同步处理进度。

### 🔄 Pr 全集成
高效的PR处理流程，code-diff、comment、merge，一应俱全。

### 🛠 CI/CD 和 GitHub Actions 全集成
通过在您的聊天平台中直接集成 CI/CD 和 GitHub Actions。

### 🚚 保持在代码审查流程中
最大化生产力，有效协作保持注意力。

## 📃 部署流程

部署 GitMaya 需要共计 3 个步骤。

<details>
<summary>

### 步骤 1. 安装 GitHub 应用

</summary>

您首先需要创建一个 GitHub 应用，详细信息请参考 [从零开始部署 GitHub 应用][Deploy GitHub App From Scratch]。

</details>

<details>
<summary>

### 步骤 2. 部署 GitMaya

</summary>

您可以选择使用 [自托管](#self-hosting) 或 [本地部署](#local-development) 来部署 GitMaya 的前端和后端。

</details>

<details>
<summary>

### 步骤 3. 部署飞书 App 机器人

</summary>

部署飞书（Lark）机器人应用的步骤已经集成到 GitMaya 的入门流程中。完成入门流程将自动完成与飞书相关的配置。更多详细信息，请参考 [从零开始部署飞书 App 机器人][Deploy Feishu App Bot From Scratch]。

</details>


<h2 id="self-hosting">🛳 自托管</h2>

GitMaya 提供支持无服务器和 [Docker 镜像][docker-release-link] 的自托管版本。这使您能够在几分钟内部署自己的聊天机器人，无需任何先前的知识。

<details>
<summary>

### `A` 使用 Docker-Compose 部署

[![][docker-release-shield]][docker-release-link]
[![][docker-size-shield]][docker-size-link]
[![][docker-pulls-shield]][docker-pulls-link]

</summary>

我们提供了一个 Docker 镜像，用于在您自己的私人设备上部署 GitMaya 服务。使用以下命令启动 GitMaya 服务：

<details>
<summary>

### 1. 下载 `docker-compose.yml` 和 `.env` 文件

</summary>

首先，下载 `docker-compose.yml` 和 `.env` 文件；它们包含 GitMaya 服务的配置，包括 MySQL、Celery 和 Redis。

```fish
$ wget https://raw.githubusercontent.com/ConnectAI-E/GitMaya/main/deploy/docker-compose.yml
$ wget https://raw.githubusercontent.com/ConnectAI-E/GitMaya/main/deploy/.env.example -O .env
```
</details>

<details>
<summary>

### 2. 配置环境变量

</summary>

接下来，您需要配置 `.env` 文件。您应该用您在 [步骤 1](#步骤-1-安装-github-应用) 中创建的 GitHub App 信息替换这些变量。

```fish
$ vim .env
```
**将 `GITHUB_APP_NAME`、`GITHUB_APP_ID`、`GITHUB_APP_PRIVATE_KEY`、`GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET`、`GITHUB_WEBHOOK_SECRET` 替换到 .env 文件中**

```fish
SECRET_KEY="<REPLACE>"
FLASK_PERMANENT_SESSION_LIFETIME=86400*30
FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:gitmaya2023@mysql:3306/gitmaya?charset=utf8mb4&binary_prefix=true"

GITHUB_APP_NAME=your-deploy-name
GITHUB_APP_ID=114514
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
<replace you private key>
-----END RSA PRIVATE KEY-----"

GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret

GITHUB_WEBHOOK_SECRET=secret
DOMAIN=127.0.0.1
```

> **NOTE**: **文件支持多行字符串，因此.pem 文件可以直接粘贴到 `.env` 文件中**

</details>

<details>
<summary>

### 3. 运行镜像

</summary>

第一次运行时，它将初始化数据库，因此日志中可能包含一些错误消息。

```fish
$ docker-compose up -d
```
</details>

<!-- > \[!NOTE]
>
> 有关使用 Docker 部署的详细说明，请参阅 [📘 Docker 部署指南](https://github.com/connectai-e/gitmaya/wiki/Docker-Deployment) -->

<!-- <details><summary><h4>🫙 Docker-Compose 环境变量</h4></summary>

该项目提供了一些使用环境变量设置的额外配置项：

| 环境变量            | 是否必需 | 描述                                                     | 示例                 |
| -------------------- | -------- | -------------------------------------------------------- | -------------------- |
| `OPENAI_API_KEY`     | 是       | 这是您在 OpenAI 帐户页面上申请的 API 密钥               | `sk-xxxxxx...xxxxxx` |

<!--
> \[!NOTE]
>
> 完整的环境变量列表可以在 [📘 Environment Variables](https://github.com/connectai-e/gitmaya/wiki/Environment-Variable) -->

</details>

### `B` 使用 Zeabur 或 Sealos 部署（即将推出！）

我们即将支持 Zeabur 的一键部署。

<div align="left">

|                     Deploy with Zeabur                      |
| :---------------------------------------------------------: |
| [![][deploy-on-zeabur-button-image]][deploy-on-zeabur-link] |

</div>

<div align="right">

[![][back-to-top]](#readme-top)

</div>
</details>

</details>

<h2 id="local-development">⌨️ 本地部署</h2>

<!-- 您可以使用 GitHub Codespaces 进行在线开发：

[![][codespaces-shield]][codespaces-link]

或者将其克隆到本地进行开发： -->

<details>
<summary>

### 1. 克隆仓库

</summary>

将仓库克隆到您的本地机器或服务器：

```fish
$ git clone https://github.com/ConnectAI-E/GitMaya.git
$ cd GitMaya
```

</details>

<details>
<summary>

### 2. 安装依赖

</summary>

#### 使用 pip

如果您使用 `pip`

```fish
$ pip install -r requirements.txt
```

#### 使用 pdm（推荐）

如果您使用 `pdm`

```fish
$ pdm install
```

激活虚拟环境：

```fish
$ eval $(pdm venv activate)
```

</details>

<details>
<summary>

### 3. 配置文件

</summary>

在开始之前，请确保您具备以下配置文件：

- `.env`: **配置飞书、GitHub 和各种中间件变量。我们提供了一个 [.env.example](https://github.com/ConnectAI-E/GitMaya/blob/main/deploy/.env.example) 作为参考**

通过替换相关变量配置数据库

```fish
# 数据库设置
FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:gitmaya2023@mysql:3306/gitmaya?charset=utf8mb4&binary_prefix=true"
```

配置 Celery，使用 Redis 作为 Broker

```fish
# Celery 设置
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

配置 GitHub App，详细信息请参考: [从零开始部署 GitHub App][Deploy GitHub App From Scratch]

```fish
# GitHub 设置
GITHUB_APP_NAME=test
GITHUB_APP_ID=1024
GITHUB_CLIENT_ID=test
GITHUB_CLIENT_SECRET=test
GITHUB_WEBHOOK_SECRET=secret
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
<replace you private key>
-----END RSA PRIVATE KEY-----"
```

配置服务器地址

```fish
DOMAIN=127.0.0.1
```

（可选）配置 Flask

```fish
# Flask 设置
SECRET_KEY="test"
FLASK_PERMANENT_SESSION_LIFETIME=86400
```

</details>

<details>
<summary>

### 4. 运行服务器

</summary>

启动 Redis：

```fish
$ docker run -d -p 6379:6379 redis:alpine
```

启动 Celery，使用 Redis 作为 Broker：

```fish
$ cd server
$ celery -A tasks.celery worker -l INFO -c 2
```

启动 MySQL：

```fish
$ docker run --name mysql -e MYSQL_ROOT_PASSWORD=gitmaya2023 -e MYSQL_DATABASE=gitmaya -e TZ=Asia/Shanghai -p 3306:3306 -v /path/to/your/mysql/data:/var/lib/mysql -v /path/to/your/mysql/conf.d:/etc/mysql/conf.d -d mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
```

创建数据库和表 （仅需要一次）：

```fish
$ flask --app server/server:app create
```

使用 `gunicorn` 运行 GitMaya 服务器：

```fish
$ gunicorn --worker-class=gevent --workers 1 --bind 0.0.0.0:8888 -t 600 --keep-alive 60 --log-level=info server:app
```

</details>

</details>

## 📕 参考

- [从零开始部署飞书 App 机器人][Deploy Feishu App Bot From Scratch]
- [从零开始部署 GitHub App][Deploy GitHub App From Scratch]
- [飞书 App 官方文档][Feishu App Official Doc]
- [GitHub App 官方文档][GitHub App Official Doc]

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 📦 生态系统

GitMaya 系列有多个仓库，这是其中之一：

|     | 仓库                                                    | 语言    | 用途                       |
| --- | -------------------------------------------------------- | ------- | ------------------------- |
| 👉  | [GitMaya](https://github.com/ConnectAI-E/GitMaya)         | Python  | 服务器端代码              |
|     | [GitMaya-Cli](https://github.com/ConnectAI-E/GitMaya-Cli) | Python  | 超级 Git 管理工具         |

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 🤝 立即参与贡献

Gitmaya 是完全开源的，由开发者们共同打造。请随时通过代码将你想要的功能变为现实。

[![][pr-welcome-shield]][pr-welcome-link]

<a href="https://github.com/connectai-e/gitmaya/graphs/contributors" target="_blank">
  <table>
    <tr>
      <th colspan="2">
        <br>
        <img src="https://contrib.rocks/image?repo=connectai-e/gitmaya">
        <br><br>
      </th>
    </tr>
    <tr>
      <td>
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://next.ossinsight.io/widgets/official/compose-recent-top-contributors/thumbnail.png?repo_id=734566084&image_size=auto&color_scheme=dark" width="373" height="auto">
          <img alt="Top Contributors of ConnectAI-E/GitMaya - Last 28 days" src="https://next.ossinsight.io/widgets/official/compose-recent-top-contributors/thumbnail.png?repo_id=734566084&image_size=auto&color_scheme=light" width="373" height="auto">
        </picture>
      </td>
    </tr>
  </table>
</a>

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 👻 替代方案

`gitmaya` 受到以下工具的启发。

- [pullpo](https://pullpo.io/)
- [graphite](https://graphite.dev/)
- [typoapp](https://typoapp.io/)

它们都很棒，但关注的重点和功能集合不同，有兴趣也可以试试 :)

<details><summary><h4>📝 License</h4></summary>


[![][fossa-license-shield]][fossa-license-link]

</details>

Copyright © 2024 [ConnectAI-E][profile-link]. <br />
This project is [MIT](./LICENSE) licensed.

<!-- LINK GROUP -->

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

[fossa-license-link]: [https://app.fossa.com/projects/git%2Bgithub.com%2Fconnectai-e%2Fgitmaya](https://app.fossa.com/projects/git%2Bgithub.com%2FConnectAI-E%2FGitMaya?ref=badge_large)
[fossa-license-shield]: https://app.fossa.com/api/projects/git%2Bgithub.com%2FConnectAI-E%2FGitMaya.svg?type=large
[profile-link]: https://github.com/connectai-e
[pr-welcome-link]: https://github.com/connectai-e/gitmaya/pulls
[pr-welcome-shield]: https://img.shields.io/badge/🤯_pr_welcome-%E2%86%92-ffcb47?labelColor=black&style=for-the-badge
[codespaces-link]: https://codespaces.new/connectai-e/gitmaya
[codespaces-shield]: https://github.com/codespaces/badge.svg
[github-logo-shield]: https://img.shields.io/badge/gitmaya-enabled?style=flat-square&logo=github&color=F9DC4E&logoColor=D9E0EE&labelColor=302D41
[github-logo-link]: https://github.com/connectai-e/gitmaya
[github-contributors-link]: https://github.com/connectai-e/gitmaya/graphs/contributors
[github-contributors-shield]: https://img.shields.io/github/contributors/connectai-e/gitmaya?color=c4f042&labelColor=black&style=flat-square
[github-forks-link]: https://github.com/connectai-e/gitmaya/network/members
[github-forks-shield]: https://img.shields.io/github/forks/connectai-e/gitmaya?color=8ae8ff&labelColor=black&style=flat-square
[github-issues-link]: https://github.com/connectai-e/gitmaya/issues
[github-issues-shield]: https://img.shields.io/github/issues/connectai-e/gitmaya?color=ff80eb&labelColor=black&style=flat-square
[github-license-link]: https://github.com/connectai-e/gitmaya/blob/main/LICENSE
[github-license-shield]: https://img.shields.io/github/license/connectai-e/gitmaya?color=white&labelColor=black&style=flat-square
[github-project-link]: https://github.com/connectai-e/gitmaya/projects
[github-release-link]: https://github.com/connectai-e/gitmaya/releases
[github-releasedate-link]: https://github.com/connectai-e/gitmaya/releases
[github-releasedate-shield]: https://img.shields.io/github/release-date/connectai-e/gitmaya?labelColor=black&style=flat-square
[github-stars-link]: https://github.com/connectai-e/gitmaya/network/stargazers
[github-stars-shield]: https://img.shields.io/github/stars/connectai-e/gitmaya?color=ffcb47&labelColor=black&style=flat-square
[docker-pulls-link]: https://hub.docker.com/r/connectai/gitmaya
[docker-pulls-shield]: https://img.shields.io/docker/pulls/connectai/gitmaya?color=45cc11&labelColor=black&style=flat-square
[docker-release-link]: https://hub.docker.com/r/connectai/gitmaya
[docker-release-shield]: https://img.shields.io/docker/v/connectai/gitmaya?color=369eff&label=docker&labelColor=black&logo=docker&logoColor=white&style=flat-square
[docker-size-link]: https://hub.docker.com/r/connectai/gitmaya
[docker-size-shield]: https://img.shields.io/docker/image-size/connectai/gitmaya?color=369eff&labelColor=black&style=flat-square
[deploy-on-sealos-button-image]: https://raw.githubusercontent.com/labring-actions/templates/main/Deploy-on-Sealos.svg
[deploy-on-sealos-link]: https://cloud.sealos.io/?xxx
[deploy-on-zeabur-button-image]: https://zeabur.com/button.svg
[deploy-on-zeabur-link]: https://zeabur.com/
[Deploy GitHub App From Scratch]: https://connect-ai.feishu.cn/wiki/OnVNwqZlhi5yM4keBWAcUF3ynFf?from=from_copylink
[Deploy GitHub App From Scratch]: https://connect-ai.feishu.cn/wiki/Qwq0wmamFiFTaXk1hfocwfpNnqf?from=from_copylink
[Deploy Feishu App Bot From Scratch]: https://connect-ai.feishu.cn/wiki/NQXywcS3Siqw60kYX8IcknDfn1e?from=from_copylink
[Feishu App Official Doc]: https://open.feishu.cn/document/home/develop-a-bot-in-5-minutes/step-1-create-app-and-enable-robot-capabilities
[GitHub App Official Doc]: https://docs.github.com/en/developers/apps/creating-a-github-app
