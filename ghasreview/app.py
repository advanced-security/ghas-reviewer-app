import logging
from typing import Dict

from flask import Flask
from flask_githubapp import GitHubApp

from ghasreview.process import CodeScanningAlert


logger = logging.getLogger("app")

app = Flask("GHAS Review")

githubapp = GitHubApp()

# https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert


@githubapp.on("code_scanning_alert.created")
@githubapp.on("code_scanning_alert.appeared_in_branch")
@githubapp.on("code_scanning_alert.reopened")
def onCodeScanningAlertCreation():
    """Code Scanning Alert event
    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert
    """
    alert = CodeScanningAlert()
    alert.payload = githubapp.payload

    # Check if in a PR
    if not alert.isPR():
        logger.debug(f"Alert is not in a Pull Request, ignoring")
        return

    logger.debug(f"Alert Opened :: {alert.id} ({alert.ref})")

    client = githubapp.installation_client

    org_name, repo_name = alert.repository.split("/", 2)

    team_name = "ghas-reviewers"
    pull_number = alert.pullRequest()

    # Check tool and severity
    if alert.tool != "CodeQL":
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return
    if alert.severity not in ["critical", "high", "error", "errors"]:
        logger.debug(
            f"Severity is not high enough to get security involved: {alert.severity}"
        )
        return

    # https://docs.github.com/en/rest/reference/pulls#list-requested-reviewers-for-a-pull-request
    pr_reviewers_req = client.session.get(
        f"{client.session.base_url}/repos/{org_name}/{repo_name}/pulls/{pull_number}/requested_reviewers"
    )
    pr_reviewers = pr_reviewers_req.json()
    # If the team is already attached to the PR
    if team_name in pr_reviewers.get("teams"):
        logger.info(f"Team is already a reviewer")
        return

    # Add team to PR for review
    # https://docs.github.com/en/rest/reference/pulls#request-reviewers-for-a-pull-request
    pr_add_reviewer = client.session.put(
        f"{client.session.base_url}/repos/{org_name}/{repo_name}/pulls/{pull_number}/requested_reviewers",
        json={"team_reviewers": [team_name]},
    )
    if pr_add_reviewer.status_code != 200:
        logger.warning(f"Failed to add to PR: {pull_number}")

    return


@githubapp.on("code_scanning_alert.closed_by_user")
def onCodeScanningAlertClose():
    """Code Scanning Alert Close Event"""
    alert = CodeScanningAlert()
    alert.payload = githubapp.payload

    logger.debug(f"Alert Opened :: {alert.id} ({alert.ref})")

    client = githubapp.installation_client

    # get user
    user = alert.getUser()
    org_name, repo_name = alert.repository.split("/", 2)

    # Check tool and severity
    if alert.tool != "CodeQL":
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return
    if alert.severity not in ["critical", "high", "error", "errors"]:
        logger.debug(
            f"Severity is not high enough to get security involved: {alert.severity}"
        )
        return

    # Check if an org account
    try:
        # TODO: Is this needed this org check?
        client.organization(org_name)
    except Exception:
        logger.debug(f"Non-organization account is using the App, lets do nothing...")
        return

    team_name = "ghas-reviewers"
    team_req = client.session.get(
        f"{client.session.base_url}/orgs/{org_name}/teams/{team_name}"
    )
    team = team_req.json()

    if team_req.status_code != 200:
        logger.debug(f"Team does not exist :: {team_name}")
        # https://docs.github.com/en/rest/reference/teams#create-a-team
        team_request = {
            "name": "GHAS Security",
            "description": "GitHub Advanced Security Reviewers",
        }
        team_creation = client.session.post(
            f"{client.session.base_url}/orgs/{org_name}/teams", json=team_request
        )
        if team_creation.status_code != 200:
            logger.warning(f"Failed to create team :: {team_name} in {org_name}")
            logger.debug(f"{team_creation.json()}")
            return
        logging.debug(f"Created team for org :: {org_name}")

    # https://docs.github.com/en/rest/reference/teams#get-team-membership-for-a-user
    membership_res = client.session.get(
        f"{client.session.base_url}/orgs/{org_name}/teams/{team_name}/memberships/{user}"
    )
    membership = membership_res.json()
    # check if the users is a member of the security team
    if membership_res.status_code == 200:
        logger.debug(f"User is part of security team, no action taken.")
        logger.debug(f"User({user}, {membership.get('role')})")
        return

    logger.debug(f"User does not have permission to close alerts: {user}")

    # Open Alert back up
    open_alert = client.session.patch(
        f"{client.session.base_url}/repos/{org_name}/{repo_name}/code-scanning/alerts/{alert.id}",
        json={"state": "open"},
    )
    if open_alert.status_code != 200:
        logger.warning(f"Unable to re-open alert")
        return

    # If in a PR, add team to
    if alert.pullRequest:
        logger.debug(f"In PR request")

    # https://github3py.readthedocs.io/en/master/api-reference/pulls.html#github3.pulls.ShortPullRequest.create_review
    return


def run(config: Dict, debug: bool = False):
    app.config.update(**config)

    githubapp.init_app(app)

    app.run("0.0.0.0", debug=debug)
