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
