import logging
from typing import Dict

from flask import Flask, redirect, current_app, jsonify
from flask_githubapp import GitHubApp

from ghasreview import __url__
from ghasreview.process import CodeScanningAlert, Processes


PR_COMMENT = """\
Security Alerts discovered by "{tool}". Informing @{org_name}/ghas-reviewers team members.
"""

logger = logging.getLogger("app")

app = Flask("GHAS Review")

githubapp = GitHubApp()


# https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert

@githubapp.on("code_scanning_alert.created")
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

    owner_name, repo_name = alert.repository.split("/", 2)

    team_name = current_app.config.get("GHAS_TEAM")
    pull_number = alert.pullRequest()

    process = Processes(
        client,
        alert=alert,
        team_name=team_name,
        org_name=owner_name,
        repo_name=repo_name,
        pull_number=pull_number
    )

    # Check tool and severity
    tool = current_app.config.get("GHAS_TOOL")
    if tool and alert.tool != tool:
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return
    severities = current_app.config.get("GHAS_SEVERITIES")
    if severities and alert.severity not in severities:
        logger.debug(
            f"Severity is not high enough to get security involved: {alert.severity}"
        )
        return

    # Currently, comment creating a very easy versus adding team to PR
    if not process.hasCommentedInPR(pull_number, team_name):
        process.createCommentOnPR(PR_COMMENT.format(
            tool=alert.tool, org_name=owner_name 
        ))
    # process.addTeamToPullRequest(team_name)
    return


@githubapp.on("code_scanning_alert.closed_by_user")
def onCodeScanningAlertClose():
    """Code Scanning Alert Close Event"""
    alert = CodeScanningAlert()
    alert.payload = githubapp.payload

    client = githubapp.installation_client
    team_name = current_app.config.get("GHAS_TEAM")
    # get user
    user = alert.getUser()
    owner_name, repo_name = alert.repository.split("/", 2)

    logger.info(f"Processing Alert :: {owner_name}/{repo_name} => {alert.id} ({alert.ref})")
    process = Processes(
        client,
        alert=alert,
        team_name=team_name,
        org_name=owner_name,
        repo_name=repo_name,
    )

    # Check tool and severity
    tool = current_app.config.get("GHAS_TOOL")
    if tool and alert.tool != tool:
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return
    severities = current_app.config.get("GHAS_SEVERITIES")
    if severities and alert.severity not in severities:
        logger.debug(
            f"Severity is not high enough to get security involved: {alert.severity}"
        )
        return

    # Check if an org account
    try:
        # TODO: Is this needed this org check?
        client.organization(owner_name)
    except Exception:
        logger.debug(f"Non-organization account is using the App, lets do nothing...")
        return

    # Check team
    team_req = client.session.get(
        f"{client.session.base_url}/orgs/{owner_name}/teams/{team_name}"
    )

    if team_req.status_code != 200:
        process.createTeam(team_name)

    # TODO: Check and Create Project Board
    # process.createProjectBoard()

    # https://docs.github.com/en/rest/reference/teams#get-team-membership-for-a-user
    membership_res = client.session.get(
        f"{client.session.base_url}/orgs/{owner_name}/teams/{team_name}/memberships/{user}"
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
        f"{client.session.base_url}/repos/{owner_name}/{repo_name}/code-scanning/alerts/{alert.id}",
        json={"state": "open"},
    )
    if open_alert.status_code != 200:
        logger.warning(f"Unable to re-open alert")
        return

    if alert.isPR():
        logger.debug(f"In PR request")

    return


@app.route("/", methods=["GET"])
def index():
    logger.info(f"Redirecting user to url...")
    return redirect(__url__)


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify({"status": "healthy"})


def run(config: Dict, debug: bool = False):
    app.config.update(**config)
    githubapp.init_app(app)

    app.run("0.0.0.0", debug=debug, port=80)

