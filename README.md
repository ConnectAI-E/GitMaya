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

[![][github-contributors-shield]][github-contributors-link]
[![][github-forks-shield]][github-forks-link]
[![][github-stars-shield]][github-stars-link]
[![][github-issues-shield]][github-issues-link]
[![][github-license-shield]][github-license-link]<br>

</div>

<p align="center">
    <a href="https://gitmaya.com">🖥 Use Now </a>
</p>

## 📃 Prerequisites
Before deploying GitMaya, you need to create a Feishu bot application and obtain authorization for your GitHub application. 

### 1. Feishu Bot Application
The Feishu bot application can be set up with the help of **[botops](https://github.com/ConnectAI-E/botops). (recommended)**
```fish
# gitmaya.botops.example.json provided in the project
npx botops deploy gitmaya.botops.example.json
```
or by referring to the official [Feishu app documentation](https://open.feishu.cn/document/home/introduction-to-custom-app-development/self-built-application-development-process); 


### 2. GitHub Application
For the GitHub app, please refer to [GitHub Application](#reference).


## 🛳 Self Hosting

GitMaya provides Self-Hosted Version with Severless and [Docker Image][docker-release-link]. This allows you to deploy your own chatbot within a few minutes without any prior knowledge.

<!-- ### `A` Deploying with Zeabur or Sealos

If you want to deploy this service yourself on either Zeabur or Sealos, you can follow these steps:

- Prepare GitHub App
- todo
<div align="center">

|                     Deploy with Zeabur                      |                     Deploy with Sealos                      |
| :---------------------------------------------------------: | :---------------------------------------------------------: |
| [![][deploy-on-zeabur-button-image]][deploy-on-zeabur-link] | [![][deploy-on-sealos-button-image]][deploy-on-sealos-link] |

</div>

> \[!TIP]
>
> We suggest you redeploy using the following steps, [📘 Maintaining Updates with GitMaya Self-Deployment](https://github.com/connectai-e/gitmaya/wiki/Upstream-Sync). -->

### Deploying with Docker-Compose

[![][docker-release-shield]][docker-release-link]
[![][docker-size-shield]][docker-size-link]
[![][docker-pulls-shield]][docker-pulls-link]

We provide a Docker image for deploying the GitMaya service on your own private device. Use the following command to start the GitMaya service:

```fish
$ docker run -d -p 3210:3210 \
  -e OPENAI_API_KEY=sk-xxxx \
  --name gitmaya \
  connectai-e/gitmaya
```

> \[!NOTE]
>
> For detailed instructions on deploying with Docker, please refer to the [📘 Docker Deployment Guide](https://github.com/connectai-e/gitmaya/wiki/Docker-Deployment)

<details><summary><h4>🫙 Docker-Compose Environment Variable</h4></summary>

This project provides some additional configuration items set with environment variables:

| Environment Variable | Required | Description                                              | Example              |
| -------------------- | -------- | -------------------------------------------------------- | -------------------- |
| `OPENAI_API_KEY`     | Yes      | This is the API key you apply on the OpenAI account page | `sk-xxxxxx...xxxxxx` |

> \[!NOTE]
>
> The complete list of environment variables can be found in the [📘 Environment Variables](https://github.com/connectai-e/gitmaya/wiki/Environment-Variable)

</details>
<div align="right">

[![][back-to-top]](#readme-top)

</div>

## ⌨️ Local Development

### Prerequisites

Ensure you have the following installed:

- MySQL
- Celery
- Redis
<!-- You can use GitHub Codespaces for online development:

[![][codespaces-shield]][codespaces-link]

Or clone it for local development: -->

### 1. Clone the Repository

Clone the repository to your local machine or server:

```fish
$ git clone https://github.com/ConnectAI-E/GitMaya.git
$ cd GitMaya
```

### 2. Installing Dependencies

#### Using pip

If you are using `pip`

```fish
pip -r requirements.txt
```

#### Using pdm(Recommended)

If you are using `pdm`

```fish
pdm install
```

Activate the virtual environment:

```fish
$ eval $(pdm venv activate)
```

### 3. Configuration Files

Before starting, ensure you have the following configuration files in place:

- `.env`: **Configure Feishu, GitHub, and various middleware variables.**

Configure Feishu Application, for details refer to: [Feishu Application](#reference)

```fish
# Feishu App Settings
APP_ID='cli_xxxx'
APP_SECRET='xxx'
ENCRYPT_KEY='xxx'
VERIFICATION_TOKEN='xxx'

# For Feishu Bot Testing
TEST_BOT_HOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxxx
```

Configure database by replacing [root], [passwd] and [db_name] with your own username, password and database name

```fish
# Database Settings
FLASK_SQLALCHEMY_DATABASE_URI="mysql+pymysql://[root]:[passwd]@mysql:3306/[db_name]?charset=utf8mb4&binary_prefix=true"
```

Configure Celery, using Redis as Broker

```fish
# Celery Settings
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Configure GitHub App, for details refer to: [GitHub App](#reference)

```fish
# GitHub Settings
GITHUB_APP_NAME=test
GITHUB_APP_ID=1024
GITHUB_APP_PRIVATE_KEY_PATH=/server/pem.pem
GITHUB_CLIENT_ID=test
GITHUB_CLIENT_SECRET=test
GITHUB_WEBHOOK_SECRET=secret
```

Configure server address

```fish
HOST=0.0.0.0
PORT=8888
DOMAIN=http://localhost:8888
```

(Optional) Configure Flask
```fish
# Flask Settings
SECRET_KEY="test"
FLASK_PERMANENT_SESSION_LIFETIME=86400
```

### 4. Running the Server

Before running the server, ensure you have the following services running:

- MySQL
- Celery
- Redis

Then, run the following command to start the server:

```fish
$ python server/server.py
```


## 📕 Reference
- Feishu Application Doc
- GitHub App Doc

<div align="right">

[![][back-to-top]](#readme-top)

</div>

## 📦 Ecosystem

There are four repositories for gitmaya, and this is one of them:

|     | Repository                                                          | Language   | Purpose                            |
| --- | ------------------------------------------------------------------- | ---------- | ---------------------------------- |
| 👉   | [GitMaya](https://github.com/ConnectAI-E/GitMaya)                   | Python     | Server-side code                   |
|     | [GitMaya-Frontend](https://github.com/ConnectAI-E/GitMaya-Frontend) | TypeScript | Frontend code                      |
|     | [GitMaya-WebSite](https://github.com/ConnectAI-E/GitMaya-Website)   | TypeScript | Official website and documentation |
|     | [GitMaya-Cli](https://github.com/ConnectAI-E/GitMaya-Cli)           | Python     | Super Git management tool          |

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
[docker-pulls-link]: https://hub.docker.com/r/connectai-e/gitmaya
[docker-pulls-shield]: https://img.shields.io/docker/pulls/connectai-e/gitmaya?color=45cc11&labelColor=black&style=flat-square
[docker-release-link]: https://hub.docker.com/r/connectai-e/gitmaya
[docker-release-shield]: https://img.shields.io/docker/v/connectai-e/gitmaya?color=369eff&label=docker&labelColor=black&logo=docker&logoColor=white&style=flat-square
[docker-size-link]: https://hub.docker.com/r/connectai-e/gitmaya
[docker-size-shield]: https://img.shields.io/docker/image-size/connectai-e/gitmaya?color=369eff&labelColor=black&style=flat-square
[deploy-on-sealos-button-image]: https://raw.githubusercontent.com/labring-actions/templates/main/Deploy-on-Sealos.svg
[deploy-on-sealos-link]: https://cloud.sealos.io/?xxx
[deploy-on-zeabur-button-image]: https://zeabur.com/button.svg
[deploy-on-zeabur-link]: https://zeabur.com/templates/xxx
