import logging
from typing import Dict

from flask import Flask, redirect, current_app, jsonify
from ghasreview.flask_githubapp import GitHubApp
from ghasreview.setup import setup_app
from ghasreview import __url__
from ghasreview.client import Client
from ghasreview.models import (
    DependabotAlert,
    CodeScanningAlert,
    SecretScanningAlert,
)

logger = logging.getLogger("app")
app = Flask("GHAS Review")
githubapp = GitHubApp()


def create_app(config: Dict):
    app.config.update(**config)
    githubapp.init_app(app)
    return app


config = setup_app()
app = create_app(config)


# Secret Scanning
@githubapp.on("secret_scanning_alert.resolved")
def onSecretScanningAlertClose():
    """Secret Scanning Alert Resolved Event"""
    logger.debug("Secret Scanning Alert Resolved by User")
    client = Client(
        githubapp.installation_client, githubapp.payload["installation"]["id"]
    )
    alert = SecretScanningAlert()
    alert.payload = githubapp.payload

    # Check if the user is part of the security team
    if client.isUserPartOfTeam(alert.owner, config.get("GHAS_TEAM"), alert.getUser()):
        return {"message": "User is part of the security team"}

    # Open Alert back up
    open_alert = client.reOpenSecretScanningAlert(
        alert.owner, alert.repository, alert.id
    )

    if open_alert.status_code != 200:
        logger.warning(f"Unable to re-open alert")
        return
    return {"message": "Secret Scanning Alert Reopened"}


# Dependabot
@githubapp.on("dependabot_alert.dismissed")
def onDependabotAlertDismiss():
    """Dependabot Alert Dismissed Event"""
    logger.debug("Dependabot Alert Dismissed by User")
    client = Client(
        githubapp.installation_client, githubapp.payload["installation"]["id"]
    )
    alert = DependabotAlert()
    alert.payload = githubapp.payload

    # Check if the user is part of the security team
    if client.isUserPartOfTeam(alert.owner, config.get("GHAS_TEAM"), alert.getUser()):
        return {"message": "User is part of the security team"}

    # Open Alert back up
    open_alert = client.reOpenDependabotAlert(alert.owner, alert.repository, alert.id)
    if open_alert.status_code != 200:
        logger.warning(f"Unable to re-open alert")
        return
    return {"message": "Dependabot Alert Reopened"}


# Code Scanning
# https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert
@githubapp.on("code_scanning_alert.created")
def onCodeScanningAlertCreation():
    """Code Scanning Alert event
    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#code_scanning_alert
    """
    alert = CodeScanningAlert()
    alert.payload = githubapp.payload
    alert.client = Client(
        githubapp.installation_client,
        githubapp.app_client,
        githubapp.payload["installation"]["id"],
    )
    alert.ghas_team_name = config.get("GHAS_TEAM")

    # Check if in a PR
    if not alert.isPR():
        logger.debug(f"Alert is not in a Pull Request, ignoring")
        return {"message": "Alert is not in a Pull Request. Not doing anything."}

    logger.debug(f"Alert Opened :: {alert.id} ({alert.ref})")

    # Check tool and severity
    tool = config.get("GHAS_TOOL")
    if tool and alert.tool != tool:
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return {"message": "Tool is not in the list of approved tools"}

    severities = config.get("GHAS_SEVERITIES")
    if severities and alert.severity not in severities:
        logger.debug(
            f"Severity is not high enough to get security involved: {alert.severity}"
        )
        return {"message": "Severity is not high enough to get security involved"}

    # Currently, comment creating a very easy versus adding team to PR
    if not alert.hasCommentedInPR():
        alert.createCommentOnPR()
        alert.addTeamToPullRequest()
    return {"message": "Code Scanning create alert in PR handled"}


@githubapp.on("code_scanning_alert.closed_by_user")
def onCodeScanningAlertClose():
    """Code Scanning Alert Close Event"""
    alert = CodeScanningAlert()
    alert.payload = githubapp.payload
    alert.client = Client(
        githubapp.installation_client, githubapp.payload["installation"]["id"]
    )

    logger.info(
        f"Processing Alert :: {alert.owner}/{alert.repository} => {alert.id} ({alert.ref})"
    )

    # Check if comment in alert
    if current_app.config.get("GHAS_COMMENT_REQUIRED") and not alert.hasDismissedComment():
        logger.debug(f"Comment required, reopeneing alert: {alert.id}")

        open_alert = alert.client.reOpenCodeScanningAlert(
            alert.owner, alert.repository, alert.id,
        )
        if open_alert.status_code != 200:
            logger.error(f"Unable to re-open alert :: {alert.id}")
            logger.error("This might be a permissions issue, please check the documentation for more details")
            return {"message": "Unable to re-open alert"}
        return {
            "message": "Comment required, re-opening alert"
        }

    # Check tool and severity
    tool = current_app.config.get("GHAS_TOOL")
    if tool and alert.tool != tool:
        logger.debug(f"Tool is not in the list of approved tools: {alert.tool}")
        return {"message": "Tool is not in the list of approved tools"}

    # Severity check, if not high enough, do not involve security team
    severities = current_app.config.get("GHAS_SEVERITIES")
    if severities:
        if alert.severity not in severities:
            logger.debug(
                f"Severity is not high enough to get security involved: {alert.severity}"
            )
            return {"message": "Severity is not high enough to get security involved, doing nothing."}
        if alert.payload.get("alert", {}).get("rule", {}).get("security_severity_level", "") not in severities:
            logger.debug(
                f"Security severity level is not high enough to get security involved: {alert.payload.get('alert', {}).get('rule', {}).get('security_severity_level', '')}"
            )
            return {"message": "Security severity level is not high enough to get security involved, doing nothing."}
    else:
        logger.debug("No severities provided, reopening all findings")

    # Check team exists
    if not alert.client.checkIfTeamExists(alert.owner, config.get("GHAS_TEAM")):
        logger.info(f"GHAS Reviewer Team `{config.get('GHAS_TEAM')}` does not exist, creating team.")
        alert.client.createTeam(alert.owner, config.get("GHAS_TEAM"))

    # check if the user is part of the security team
    if alert.client.isUserPartOfTeam(alert.owner, config.get("GHAS_TEAM"), alert.getUser()):
        logger.debug(f"User is part of security team, no action taken.")
        return {"message": "User is part of the security team"}

    logger.info(f"User is not allowed to close alerts: {alert.getUser()} ({alert.owner}/{alert.repository} => {alert.id})")

    # Open Alert back up
    open_alert = alert.client.reOpenCodeScanningAlert(
        alert.owner, alert.repository, alert.id,
    )

    if open_alert.status_code != 200:
        logger.error(f"Unable to re-open alert :: {alert.id}")
        logger.error("This might be a permissions issue, please check the documentation for more details")
        return {"message": "Unable to re-open alert"}

    if alert.isPR():
        logger.debug(f"In PR request")

    return {"message": "Code Scanning Alert Reopened"}


@app.errorhandler(500)
def page_not_found(error):
    data = {"error": 500, "msg": "Internal Server Error"}
    if app.debug:
        data["msg"] = str(error)
    resp = jsonify(**data)
    return resp


@app.route("/", methods=["GET"])
def index():
    logger.info(f"Redirecting user to url...")
    return redirect(__url__)


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    logger.debug("Healthcheck status")
    return jsonify({"status": "healthy"})
