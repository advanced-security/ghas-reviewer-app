from typing import Dict
import logging

logger = logging.getLogger("GitHubClient")


class Client:
    installation_client: object = None
    app_client: object = None
    installation_id: int = 0

    def __init__(
        self, installation_client, app_client: object = None, installation_id: int = 0
    ):
        self.installation_client = installation_client
        self.app_client = app_client
        self.installation_id = installation_id

    def getInstallationId(self) -> int:
        return self.installation_id

    def isUserPartOfTeam(self, owner_name: str, team_name: str, user: str) -> bool:

        team = self.callApi(
            "GET",
            f"{self.installation_client.session.base_url}/orgs/{owner_name}/teams/{team_name}",
        )
        if team.status_code != 200:
            logger.error(f"Team does not exist :: {team_name} - {team.json()}")
            return False

        membership_res = self.callApi(
            "GET",
            f"{self.installation_client.session.base_url}/orgs/{owner_name}/teams/{team_name}/memberships/{user}",
        )

        if membership_res.status_code == 200:
            logger.debug(f"User is part of the security team, no action taken.")
            return True
        return False

    def callApi(self, method: str, url: str, json: Dict = {}) -> Dict:
        response = self.installation_client.session.request(method, url, json=json)
        return response

    def reOpenAlert(self, owner: str, repo: str, type: str, alert_id: int) -> Dict:
        return self.callApi(
            "PATCH",
            f"{self.installation_client.session.base_url}/repos/{owner}/{repo}/{type}/alerts/{alert_id}",
            {"state": "open"},
        )

    def reOpenSecretScanningAlert(self, owner: str, repo: str, alert_id: int) -> Dict:
        return self.reOpenAlert(owner, repo, "secret-scanning", alert_id)

    def reOpenDependabotAlert(self, owner: str, repo: str, alert_id: int) -> Dict:
        return self.reOpenAlert(owner, repo, "dependabot", alert_id)

    def reOpenCodeScanningAlert(self, owner: str, repo: str, alert_id: int) -> Dict:
        return self.reOpenAlert(owner, repo, "code-scanning", alert_id)

    def checkIfTeamExists(self, owner: str, team_name: str) -> bool:
        team = self.installation_client.session.get(
            f"{self.installation_client.session.base_url}/orgs/{owner}/teams/{team_name}"
        )
        if team.status_code != 200:
            logger.debug(f"Team does not exist :: {team_name} - {team.json()}")
            return False
        return True

    def createTeam(self, owner: str, team_name: str) -> bool:
        # https://docs.github.com/en/rest/reference/teams#create-a-team
        team_request = {
            "name": team_name,
            "description": "GitHub Advanced Security Reviewers",
        }
        team_creation = self.installation_client.session.post(
            f"{self.installation_client.session.base_url}/orgs/{owner}/teams", json=team_request
        )
        if team_creation.status_code != 200:
            logger.warning(f"Failed to create team :: {team_name} in {owner}")
            logger.debug(f"{team_creation.json()}")
            return False
        logging.debug(f"Created team for org :: {owner}")
        return True

    def postComment(
        self, owner: str, repo: str, issue_number: int, comment: str
    ) -> Dict:
        return self.callApi(
            "POST",
            f"{self.installation_client.session.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments",
            {"body": comment},
        )

    def getPRComments(self, owner: str, repo: str, pull_number: int) -> Dict:
        return self.callApi(
            "GET",
            f"{self.getBaseUrl()}/repos/{owner}/{repo}/issues/{pull_number}/comments",
        )

    def getBaseUrl(self) -> str:
        return self.installation_client.session.base_url

    def getBotUsername(self) -> str:

        app_req = self.app_client.session.get(
            f"{self.app_client.session.base_url}/app",
        )
        if app_req.status_code != 200:
            logger.warning(f"Error getting app details: {app_req.status_code}")
            return None

        app_details = app_req.json()
        app_name = app_details.get("slug")
        if not app_name:
            logger.warning("Bot username could not be determined.")
            return None

        return app_name + "[bot]"

    def getPRReviewers(self, owner: str, repo: str, pull_number: int) -> Dict:
        # https://docs.github.com/en/rest/reference/pulls#list-requested-reviewers-for-a-pull-request
        return self.callApi(
            "GET",
            f"{self.getBaseUrl()}/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
        )

    def addTeamToPullRequestReviewer(
        self, team_name: str, owner: str, repo: str, pull_number: int
    ) -> bool:
        pr_reviewers = self.getPRReviewers(owner, repo, pull_number).json()
        team_names = [team["name"] for team in pr_reviewers.get("teams", [])]
        # If the team is already attached to the PR
        if team_name in team_names:
            logger.debug(f"Team is already a reviewer. Skipping")
        else:
            logger.debug(f"Team is not a reviewer. Adding")
            # https://docs.github.com/en/rest/reference/pulls#request-reviewers-for-a-pull-request
            pr_add_reviewer = self.callApi(
                "POST",
                f"{self.getBaseUrl()}/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
                {"team_reviewers": [team_name]},
            )
            if pr_add_reviewer.status_code != 201:
                logger.warning(f"Failed to add to PR: {pull_number}")
                logger.debug(
                    f"Response: {pr_add_reviewer.status_code} - {pr_add_reviewer.text}"
                )
                return False
        return True
