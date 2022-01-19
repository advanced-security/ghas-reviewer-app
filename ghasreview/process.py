import json
import logging
import requests
from typing import Dict, List
from dataclasses import dataclass, asdict

# from ghapi.core import GhApi

logger = logging.getLogger("CodeScanningAlert")


class CodeScanningAlert:
    payload: Dict = {}

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


class Processes:
    def __init__(self, client, **metadata) -> None:
        self.client = client
        self.metadata = metadata

    @property
    def base_url(self):
        return self.client.session.base_url

    def get(self, key: str):
        if hasattr(self, key):
            return getattr(self, key)
        if self.metadata.get(key):
            return self.metadata.get(key)

        raise Exception(f"Unknown key: {key}")

    def createCommentOnPR(self, comment: str) -> bool:
        comment = comment.format(**self.metadata)
    
        owner = self.get("org_name") 
        repo = self.get("repo_name")
        pull_number = self.get("pull_number")

        pr_comment_req = self.client.session.post(
            f"{self.base_url}/repos/{owner}/{repo}/issues/{pull_number}/comments",
            json={
                "body": comment
            }
        )
        if pr_comment_req.status_code != 200:
            logger.warning(f"Failed to write comment to PR: {pull_number}")
            logger.debug(pr_comment_req.json())
            return False
        
        return True

    def createTeam(self, team_name: str) -> bool:
        logger.debug(f"Team does not exist :: {team_name}")
        owner = self.get("org_name")

        # https://docs.github.com/en/rest/reference/teams#create-a-team
        team_request = {
            "name": team_name,
            "description": "GitHub Advanced Security Reviewers",
        }
        team_creation = self.client.session.post(
            f"{self.base_url}/orgs/{owner}/teams", json=team_request
        )
        if team_creation.status_code != 200:
            logger.warning(f"Failed to create team :: {team_name} in {owner}")
            logger.debug(f"{team_creation.json()}")
            return False
        logging.debug(f"Created team for org :: {owner}")
        return True 

    def createProjectBoard(self, board_name: str) -> bool:
        logger.warning(f"Creating Org level is currently not present")
        return False
    
    def hasCommentedInPR(self, pull_number: int, commenter: str = "ghas-reviewers") -> bool:
        owner = self.get("org_name")
        repo = self.get("repo_name")
        pull_number = self.get("pull_number")

        pr_comments_req = self.client.session.get(
            f"{self.base_url}/repos/{owner}/{repo}/issues/{pull_number}/comments"
        )
        pr_comments = pr_comments_req.json()
        if pr_comments_req.status_code != 200:
            logger.warning(f"Error getting PR comments: {pr_comments_req.status_code}")
            return False

        for comment in pr_comments:
            if comment.get("user", {}).get("login") == commenter:
                return True
        return False

    def addTeamToPullRequest(self, team_name: str) -> bool:
        org_name = self.get("org_name")
        repo_name = self.get("repo_name")
        pull_number = self.get("pull_number")

        # https://docs.github.com/en/rest/reference/pulls#list-requested-reviewers-for-a-pull-request
        pr_reviewers_req = self.client.session.get(
            f"{self.get('base_url')}/repos/{org_name}/{repo_name}/pulls/{pull_number}/requested_reviewers"
        )
        pr_reviewers = pr_reviewers_req.json()
        # If the team is already attached to the PR
        if team_name in pr_reviewers.get("teams"):
            logger.info(f"Team is already a reviewer")
            return False

        # Add team to PR for review
        # https://docs.github.com/en/rest/reference/pulls#request-reviewers-for-a-pull-request
        pr_add_reviewer = self.client.session.put(
            f"{self.get('base_url')}/repos/{org_name}/{repo_name}/pulls/{pull_number}/requested_reviewers",
            json={"team_reviewers": [team_name]},
        )
        if pr_add_reviewer.status_code != 200:
            logger.warning(f"Failed to add to PR: {pull_number}") 

        return True

