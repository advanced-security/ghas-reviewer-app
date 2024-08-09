from typing import Dict
import logging
import json

logger = logging.getLogger("CodeScanningAlert")


class CodeScanningAlert:
    payload: Dict = {}

    comment: str = (
        """Security Alerts discovered by "{tool}". Informing @{org_name}/{ghas_team} team members."""
    )

    _client: object = None

    ghas_team_name: str = ""

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def base_url(self):
        return self.client.getBaseUrl()

    @property
    def id(self) -> str:
        return self.payload.get("alert", {}).get("number", "")

    @property
    def ref(self) -> str:
        return self.payload.get("alert", {}).get("most_recent_instance", {}).get(
            "ref"
        ) or self.payload.get("ref", "")

    @property
    def tool(self) -> str:
        return self.payload.get("alert", {}).get("tool", {}).get("name", "")

    @property
    def severity(self) -> str:
        return self.payload.get("alert", {}).get("rule", {}).get("severity", "")

    @property
    def repository(self) -> str:
        return self.payload.get("repository", {}).get("name", "")

    @property
    def owner(self) -> str:
        return self.payload.get("repository", {}).get("owner", {}).get("login", "")

    @property
    def full_name(self) -> str:
        return self.payload.get("repository", {}).get("full_name", "")

    @property
    def date_updated(self) -> str:
        return self.payload.get("alert", {}).get("updated_at", "")

    def getUser(self):
        return self.payload.get("alert", {}).get("dismissed_by", {}).get("login")

    def storePayload(self):
        path = f"./samples/{self.repository.replace('/', '')}-{self.date_updated}.json"
        with open(path, "w") as handle:
            json.dump(self.payload, handle, indent=2)

        logger.info(f"Saving payload: {path}")

    def isPR(self) -> bool:
        return self.ref.startswith("refs/pull/")

    def pullRequest(self) -> int:
        # refs/pull/{id}/merge
        _, _, prid, *_ = self.ref.split("/")
        return int(prid)

    def createCommentOnPR(self) -> bool:
        comment = self.comment.format(
            tool=self.tool, org_name=self.owner, ghas_team=self.ghas_team_name
        )

        pr_comment_req = self.client.postComment(
            self.owner, self.repository, self.pullRequest(), comment
        )
        if pr_comment_req.status_code != 200 and pr_comment_req.status_code != 201:
            logger.warning(
                f"Failed to write comment to PR: {self.pullRequest()} :: {pr_comment_req.status_code}"
            )
            logger.debug(pr_comment_req.json())
            return False

        return True

    def createProjectBoard(self, board_name: str) -> bool:
        logger.warning(f"Creating Org level is currently not present")
        return False

    def getBotUsername(self) -> str:
        return self.client.getBotUsername()

    def hasCommentedInPR(self) -> bool:
        owner = self.owner
        repo = self.repository
        pull_number = self.pullRequest()

        bot_username = self.getBotUsername()
        if not bot_username:
            logger.warning("Bot username could not be determined.")
            return False

        pr_comments_req = self.client.getPRComments(owner, repo, pull_number)
        pr_comments = pr_comments_req.json()
        if pr_comments_req.status_code != 200:
            logger.warning(f"Error getting PR comments: {pr_comments_req.status_code}")
            return False

        for comment in pr_comments:
            if comment.get("user", {}).get("login") == bot_username:
                return True
        return False

    def addTeamToPullRequest(self) -> bool:
        org_name = self.owner
        repo_name = self.repository
        pull_number = self.pullRequest()
        team_name = self.ghas_team_name

        return self.client.addTeamToPullRequestReviewer(
            team_name, org_name, repo_name, pull_number
        )
