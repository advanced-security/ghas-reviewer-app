# ghas-reviewer-app

GHAS (GitHub Advanced Security) Reviewer GitHub App allows security teams to enforces a reviewer to approve and dismiss alerts.
This allows security experts to provide 4-eyes principle over all security alerts generated in GitHub.

> :warning: **The public GitHub App will be sent security data and shouldn't be used from production**

[Public GitHub App](https://github.com/apps/ghas-reviewer)

<!-- TODO: Video -->

## Setup

GHAS Reviewer is a Python based web application which uses Docker to deploy.
Any solution which supports Docker containers will work.

### Configuration

[Checkout how to setup a GitHub App here](https://docs.github.com/en/developers/apps/building-github-apps/creating-a-github-app).

Store the App key so the service can read it from the path provided along with the other enviroment variables or cli arguments.

**Enviroment Variable:**

```env
GITHUB_APP_ID=123456
GITHUB_APP_KEY_PATH=./config/key.pem
GITHUB_APP_SECRET=123456789012345678901234567890
```

### Docker

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

## Features & Limitations

Here are a list of feature built into the app and limitations 

- Code Scanning alert Reviewer requirement 
- Adds comment in Pull Request to notify security reviewer team


## Limitations

- Pull Request require team approval
- No Dependabot or Secret Scanning support



