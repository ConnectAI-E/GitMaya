<a name="readme-top"></a>

<div align="center">
<a href="https://gitmaya.com" target="_blank" style="display: block" align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/ConnectAI-E/GitMaya/assets/50035229/45cfd4f3-9c17-44d2-b6b7-3aa97c08006b" width="655" height="auto">
    <img alt="GitMaya - make git flow in chat " src="https://github.com/ConnectAI-E/GitMaya/assets/50035229/1c28f0ca-d6e6-4ebd-b858-c4be3eff845e" width="655" height="auto">
  </picture>
</a>
<p align='center'>
  <samp>An open-source, high-performance GitOps for boosting developer-teams productivity</samp>
<br/>
 <samp>Supports lark, discord, slack, and so on <sup><em>(FULL OPENSOURCE)</em></sup></samp>
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
    <a href="https://gitmaya.com">🖥 Try GitMaya Now </a>
</p>

<strong align="center">
<samp>

[**English**](./README.md) · [**简体中文**](./README_zh.md)

</samp>
</strong>

https://github.com/ConnectAI-E/GitMaya/assets/50035229/490b87d3-47f7-4a89-a4c7-737df359d67d

## 🔥 Feature List

### 🧑🏻‍💻 For Developers, By Developers

Embrace the power of collaboration with our developer-centric, fully open-source product designed by developers, for developers.

### 🌐 Cross-Platform Bliss

Enjoy seamless communication across various platforms including **Feishu, Discord, Slack, Microsoft Teams, and Telegram**. Our commitment is to serve developers wherever they feel at home!

### 🔄 One Repo = One ChatGroup

Experience the perfection of a 2-way sync with the mantra "One Repo = One ChatGroup". let the collaboration flow effortlessly!

### 💬 GitHub Msg Interaction, Simplified:

Manage all your GitHub interactions right from your favorite chat platform. No more context-switching, just pure efficiency.

### 🚀 Instant Issue Reminders

Say goodbye to delays! Receive instant issue reminders that make feedback and interaction a breeze. Stay in sync with your team effortlessly.

### 🔄 Pull Request Recap Magic

Efficient stand-ups made easy! Get a quick recap of pull requests, ensuring that your team stays on the same page and moves forward with confidence.

### 🛠 CI/CD and GitHub Actions Integration

Elevate your development workflow with seamless integration of CI/CD and GitHub Actions directly within your ChatPlatform. Boost productivity and streamline your processes effortlessly.

### 🚚 Stay in the Code Review Flow

Maximize productivity with dedicated code review time slots. Stay focused, collaborate effectively, and ensure your codebase is always in its best shape!

## 📃 Deployment Workflow

Deploying GitMaya requires a total of 3 steps.

<details>
<summary>

### Step 1. Install GitHub Application

</summary>

You need to create a GitHub app at first, for details refer to [Deploy GitHub App From Scratch][Deploy GitHub App From Scratch].

</details>

<details>
<summary>

### Step 2. Deploy GitMaya

</summary>

You can choose to use [Self Hosting](#self-hosting) or [Local Deployment](#local-development) to deploy the front-end and back-end of GitMaya.

</details>

<details>
<summary>

### Step 3. Deploy Feishu App Bot

</summary>

The steps for deploying the Feishu (Lark) bot application are already integrated into the onboarding process of GitMaya. Completing the onboarding will automatically complete the Feishu-related configuration. For more details, please refer to [Deploy Feishu App Bot From Scratch][Deploy Feishu App Bot From Scratch].

</details>

<h2 id="self-hosting">🛳 Self Hosting</h2>

GitMaya provides Self-Hosted Version with Severless and [Docker Image][docker-release-link]. This allows you to deploy your own chatbot within a few minutes without any prior knowledge.

<details>
<summary>

### `A` Deploying with Docker-Compose

[![][docker-release-shield]][docker-release-link]
[![][docker-size-shield]][docker-size-link]
[![][docker-pulls-shield]][docker-pulls-link]

</summary>

We provide a Docker image for deploying the GitMaya service on your own private device. Use the following command to start the GitMaya service:

<details>
<summary>

### 1. Download the `docker-compose.yml` and `.env` File

</summary>

First, download the `docker-compose.yml` and `.env` file; they contain the configuration for the GitMaya services, including MySQL, Celery, and Redis.

```fish
$ wget https://raw.githubusercontent.com/ConnectAI-E/GitMaya/main/deploy/docker-compose.yml
$ wget https://raw.githubusercontent.com/ConnectAI-E/GitMaya/main/deploy/.env.example -O .env
```
</details>

<details>
<summary>

### 2. Configure the Environment Variables

</summary>

Then, you need to configure the .env file. You should replace the variables with your own GitHub App information, which created in [Step 1](#step-1-install-github-application).

```fish
$ vim .env
```

**Replacing `GITHUB_APP_NAME`, `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_WEBHOOK_SECRET` into .env file**

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

> \[!NOTE]
> `.env` **file supports multi-line string, so the .pem file could be pasted into .env file directly**

</details>

<details>
<summary>

### 3. Run the Images

</summary>

It will init database in first time, thus it may contain a few error messages in logs.

```fish
$ docker-compose up -d
```
</details>

<!-- > \[!NOTE]
>
> For detailed instructions on deploying with Docker, please refer to the [📘 Docker Deployment Guide](https://github.com/connectai-e/gitmaya/wiki/Docker-Deployment) -->

<!-- <details><summary><h4>🫙 Docker-Compose Environment Variable</h4></summary>

This project provides some additional configuration items set with environment variables:

| Environment Variable | Required | Description                                              | Example              |
| -------------------- | -------- | -------------------------------------------------------- | -------------------- |
| `OPENAI_API_KEY`     | Yes      | This is the API key you apply on the OpenAI account page | `sk-xxxxxx...xxxxxx` | -->
<!--
> \[!NOTE]
>
> The complete list of environment variables can be found in the [📘 Environment Variables](https://github.com/connectai-e/gitmaya/wiki/Environment-Variable) -->

</details>

### `B` Deploying with Zeabur or Sealos (Coming soon!)

We will soon support one-click deployment for Zeabur.

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

<h2 id="local-development">⌨️ Local Development</h2>

<!-- You can use GitHub Codespaces for online development:

[![][codespaces-shield]][codespaces-link]

Or clone it for local development: -->

<details>
<summary>

### 1. Clone the Repository

</summary>

Clone the repository to your local machine or server:

```fish
$ git clone https://github.com/ConnectAI-E/GitMaya.git
$ cd GitMaya
```

</details>

<details>
<summary>

### 2. Installing Dependencies

</summary>

#### Using pip

If you are using `pip`

```fish
$ pip install -r requirements.txt
```

#### Using pdm(Recommended)

If you are using `pdm`

```fish
$ pdm install
```

Activate the virtual environment:

```fish
$ eval $(pdm venv activate)
```

</details>

<details>
<summary>

### 3. Configuration Files

</summary>

Before starting, ensure you have the following configuration files in place:

- `.env`: **Configure Feishu, GitHub, and various middleware variables. We provide an example [.env.example](https://github.com/ConnectAI-E/GitMaya/blob/main/deploy/.env.example) for referring**

Configure database by replacing relevant variables

```fish
# Database Settings
FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:gitmaya2023@mysql:3306/gitmaya?charset=utf8mb4&binary_prefix=true"
```

Configure Celery, using Redis as Broker

```fish
# Celery Settings
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Configure GitHub App, for details refer to: [Deploy GitHub App From Scratch][Deploy GitHub App From Scratch]

```fish
# GitHub Settings
GITHUB_APP_NAME=test
GITHUB_APP_ID=1024
GITHUB_CLIENT_ID=test
GITHUB_CLIENT_SECRET=test
GITHUB_WEBHOOK_SECRET=secret
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
<replace you private key>
-----END RSA PRIVATE KEY-----"
```

Configure server address

```fish
DOMAIN=127.0.0.1
```

(Optional) Configure Flask

```fish
# Flask Settings
SECRET_KEY="test"
FLASK_PERMANENT_SESSION_LIFETIME=86400
```

</details>

<details>
<summary>

### 4. Running the Server

</summary>

Start Redis：

```fish
$ docker run -d -p 6379:6379 redis:alpine
```

Start Celery, using Redis as Broker：

```fish
$ cd server
$ celery -A tasks.celery worker -l INFO -c 2
```

Start MySQL：

```fish
$ docker run --name mysql -e MYSQL_ROOT_PASSWORD=gitmaya2023 -e MYSQL_DATABASE=gitmaya -e TZ=Asia/Shanghai -p 3306:3306 -v /path/to/your/mysql/data:/var/lib/mysql -v /path/to/your/mysql/conf.d:/etc/mysql/conf.d -d mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
```

Create database and tables **(needed only once)**:

```fish
$ flask --app server/server:app create
```

Run the GitMaya server by using `gunicorn`:

```fish
$ gunicorn --worker-class=gevent --workers 1 --bind 0.0.0.0:8888 -t 600 --keep-alive 60 --log-level=info server:app
```

</details>

</details>

## 📕 Reference

- [Deploy Feishu App Bot From Scratch][Deploy Feishu App Bot From Scratch]
- [Deploy GitHub App From Scratch][Deploy GitHub App From Scratch]
- [Feishu App Official Doc][Feishu App Official Doc]
- [GitHub App Official Doc][GitHub App Official Doc]

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 📦 Ecosystem

There is a series of gitmaya repositories, and this is one of them:

|     | Repository                                                | Language | Purpose                   |
| --- | --------------------------------------------------------- | -------- | ------------------------- |
| 👉  | [GitMaya](https://github.com/ConnectAI-E/GitMaya)         | Python   | Server-side code          |
|     | [GitMaya-Cli](https://github.com/ConnectAI-E/GitMaya-Cli) | Python   | Super Git management tool |

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 🤝 Contributing Now

Gitmaya is an open-source platform, freely available and crafted by developers, just like yourself. Feel free to proudly present your envisioned features and bring them to life through code.

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

## 👻 Alternatives

`gitmaya` is inspired by the following tools.

- [pullpo](https://pullpo.io/)
- [graphite](https://graphite.dev/)
- [typoapp](https://typoapp.io/)

They work well but have different focuses and feature sets, try them out as well :)

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
