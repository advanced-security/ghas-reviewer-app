# ghas-reviewer-app

GHAS (GitHub Advanced Security) Reviewer GitHub App allows security teams to enforces a reviewer to appove and dismiss alerts.
This allows security experts to provide 4-eyes principal over all security alerts generated in GitHub.

> :warning: **The public GitHub App will be sent security data and shouldn't be used from production**

[Public GitHub App](https://github.com/apps/ghas-reviewer)

<!-- TODO: Video -->

## Setup

GHAS Reviewer is a Python based web application which uses Docker to deploy.
Any solution which supports Docker containers will work.

### Docker

**Pull / Download image:**

```bash
# Pull latest (or a release)
docker pull ghcr.io/geekmasher/ghas-reviewer-app:main
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
    -p 5000:5000 \ 
    ghcr.io/geekmasher/ghas-reviewer-app:main
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


**Limitations**

- Pull Request require team approval
- No Dependabot or Secret Scanning support



