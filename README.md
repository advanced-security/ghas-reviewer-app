<!-- markdownlint-disable -->
<div align="center">
<h1>GHAS Reviewer App</h1>

[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/advanced-security/ghas-reviewer-app)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/advanced-security/ghas-reviewer-app/build.yml?style=for-the-badge)](https://github.com/advanced-security/ghas-reviewer-app/actions/workflows/build.yml?query=branch%3Amain)
[![GitHub Issues](https://img.shields.io/github/issues/advanced-security/ghas-reviewer-app?style=for-the-badge)](https://github.com/advanced-security/ghas-reviewer-app/issues)
[![GitHub Stars](https://img.shields.io/github/stars/advanced-security/ghas-reviewer-app?style=for-the-badge)](https://github.com/advanced-security/ghas-reviewer-app)
[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)

</div>
<!-- markdownlint-restore -->

## Overview

GitHub Advanced Security (GHAS) Reviewer App allows security teams to enforces a reviewer to approve and dismiss alerts.
This allows security experts to provide 4-eyes principle over all security alerts generated in GitHub.

> [!TIP]
> GitHub Advanced Security (GHAS) has now Alert Dismissal feature built directly into the product.
> This app is not required for that functionality.

## ✨ Features

- Re-open closed alerts if an unapproved users changes the alert
- Notifies Security Team for vulneraiblities found in PR and assigns them as reviewers. **Requires security team to be repository collaborators.**
- GitHub Advanced Security Features
  - [x] [Code Scanning][github-codescanning] alerts
  - [x] [Secret Scanning][github-secretscanning] alerts
  - [x] [Dependabot][github-supplychain] alerts

## ⚡️ Requirements

- Python `+3.9`
- GitHub Application Setup
  - [Permissions][permissions]
- [optional] Docker / Docker Compose

## Usage

GHAS Reviewer is a Python based web application which primarily uses Docker for easy deployment.

### GitHub Application Configuration

[Checkout how to setup a GitHub App here](https://docs.github.com/en/developers/apps/building-github-apps/creating-a-github-app).

Store the App key so the service can read it from the path provided along with the other environment variables or cli arguments.

**Environment Variable:**

Create a `.env` file in the root of the project with the following environment variables.

```env
# Application ID
GITHUB_APP_ID=123456
# Path to the App private key
GITHUB_APP_KEY_PATH=./config/key.pem
# or use the private key directly
GITHUB_APP_KEY=-----BEGIN PRIVATE KEY-----\n...
# Webhook Secret
GITHUB_APP_SECRET=123456789012345678901234567890
GITHUB_APP_ENDPOINT=/
GITHUB_GHAS_TEAM="sec_team"
# GHAS Severities
GITHUB_GHAS_SEVERITIES="critical,high,error,errors"
```

You can also use the following CLI arguments to pass the configuration.

If you choose to pass the private key via a file just store the key in a file and pass the path to the file. In our case, we store the key in `./config/key.pem`. You will later mount this file into the container.

#### Permissions

The GitHub App requires the following permissions:

- Repository

  - [x] Code scanning alerts: Read & Write
  - [x] Dependabot alerts: Read & Write
  - [x] Secrets scanning alerts: Read & Write
  - [x] Issues: Read & Write
  - [x] Pull requests: Read & Write

- Webhook events
  - [x] Code scanning alerts
  - [x] Dependabot alerts
  - [x] Secret scanning alerts

### Container / Docker

The application is designed to be run in a container, this allows for easy deployment and scaling.

**Pull / Download image:**

```bash
# Pull latest or a release
docker pull ghcr.io/advanced-security/ghas-reviewer-app:latest

or

docker pull ghcr.io/advanced-security/ghas-reviewer-app:v0.6.2
```

**Or Build From Source:**

```bash
docker build -t advanced-security/ghas-reviewer-app .
```

or build locally

```bash
docker build -t advanced-security/ghas-reviewer-app .
```

**Run Docker Image:**

```bash
docker run \
    --env-file=.env \
    -v ./config:/ghasreview/config \
    -p 9000:9000 \
    ghcr.io/advanced-security/ghas-reviewer-app:latest # or use release tag, example v0.6.0
```

or run it locally

```bash
docker run \
    --env-file=.env \
    -v ./config:/ghasreview/config \
    -p 9000:9000 \
    advanced-security/ghas-reviewer-app
```

\*\*Run

### Docker Compose

If you are testing the GitHub App you can quickly use Docker Compose to spin-up the container.

```bash
docker-compose build
docker-compose up -d
```

## Local Development

If you want to run the application locally you can use the following the same steps as abouve meaning you need to create an GitHub App, store the private key and set the environment variables.

After you have set the environment variables you can run the application using the following commands.

```bash
# We are using Pipenv for dependency management
pip install pipenv

# Install dependencies
pipenv install --dev

# Run the application
pipenv run develop
```

## Limitations

- Pull Request require team approval. The security team needs to be repository collaborator.

## Maintainers / Contributors

- [@GeekMasher](https://github.com/GeekMasher) - Author / Core Maintainer
- [@theztefan](https://github.com/theztefan) - Contributor

## Support

Please create [GitHub Issues][github-issues] if there are bugs or feature requests.

This project uses [Sematic Versioning (v2)](https://semver.org/) and with major releases, breaking changes will occur.

## License

This project is licensed under the terms of the MIT open source license.
Please refer to [MIT][license] for the full terms.

<!-- Resources -->

[license]: ./LICENSE
[github-issues]: https://github.com/advanced-security/ghas-reviewer-app/issues
[github-codescanning]: https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning
[github-secretscanning]: https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning
[github-supplychain]: https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-supply-chain-security
[permissions]: https://github.com/advanced-security/ghas-reviewer-app#permissions
