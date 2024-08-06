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

> [!CAUTION]
> The public GitHub App will be sent security data and is only used for testing purposes.
> It is recommended to deploy your own instance of the app for production use.

[Public GitHub App](https://github.com/apps/ghas-reviewer)

## ✨ Features

- Re-open closed alerts if an unapproved users changes the alert
- GitHub Advanced Security Features
  - [x] [Code Scanning][github-codescanning] alerts
  - [ ] [Secret Scanning][github-secretscanning] alerts
  - [ ] [Dependabot][github-supplychain] alerts

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

```env
# Application ID
GITHUB_APP_ID=123456
# Path to the App private key
GITHUB_APP_KEY_PATH=./config/key.pem
# or use the private key directly
GITHUB_APP_KEY=-----BEGIN PRIVATE KEY-----\n...
# Webhook Secret
GITHUB_APP_SECRET=123456789012345678901234567890
```

#### Permissions

The GitHub App requires the following permissions:

- Repository
  - [x] Security Events: Read & Write

### Container / Docker

The application is designed to be run in a container, this allows for easy deployment and scaling.

**Pull / Download image:**

```bash
# Pull latest (or a release)
docker pull ghcr.io/advanced-security/ghas-reviewer-app:main
```

**Or Build From Source:**

```bash
docker build -t {org}/ghas-reviewer-app .
```

**Run Docker Image:**

```bash
docker run \
    --env-file=.env \
    -v ./config:/ghasreview/config \
    -p 8000:8000 \ 
    ghcr.io/advanced-security/ghas-reviewer-app:main
```

### Docker Compose

If you are testing the GitHub App you can quickly use Docker Compose to spin-up the container.

```bash
docker-compose build
docker-compose up -d
```

## Limitations

- Pull Request require team approval
- No Dependabot or Secret Scanning support

## Maintainers / Contributors

- [@GeekMasher](https://github.com/GeekMasher) - Author / Core Maintainer

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
