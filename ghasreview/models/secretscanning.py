from typing import Dict
import logging

logger = logging.getLogger("SecretScanningAlert")


class SecretScanningAlert:
    payload: Dict = {}

    @property
    def id(self) -> int:
        return self.payload.get("alert", {}).get("number", 0)

    @property
    def secret_type(self) -> str:
        return self.payload.get("alert", {}).get("secret_type", "")

    @property
    def secret_type_display_name(self) -> str:
        return self.payload.get("alert", {}).get("secret_type_display_name", "")

    @property
    def url(self) -> str:
        return self.payload.get("alert", {}).get("url", "")

    @property
    def html_url(self) -> str:
        return self.payload.get("alert", {}).get("html_url", "")

    @property
    def locations_url(self) -> str:
        return self.payload.get("alert", {}).get("locations_url", "")

    @property
    def created_at(self) -> str:
        return self.payload.get("alert", {}).get("created_at", "")

    @property
    def updated_at(self) -> str:
        return self.payload.get("alert", {}).get("updated_at", "")

    @property
    def validity(self) -> str:
        return self.payload.get("alert", {}).get("validity", "")

    @property
    def resolution(self) -> str:
        return self.payload.get("alert", {}).get("resolution", "")

    @property
    def resolved_by(self) -> str:
        return self.payload.get("alert", {}).get("resolved_by", {}).get("login", "")

    @property
    def resolved_at(self) -> str:
        return self.payload.get("alert", {}).get("resolved_at", "")

    @property
    def repository(self) -> str:
        return self.payload.get("repository", {}).get("name", "")

    @property
    def owner(self) -> str:
        return self.payload.get("repository", {}).get("owner", {}).get("login", "")

    @property
    def full_name(self) -> str:
        return self.payload.get("repository", {}).get("full_name", "")

    def getUser(self):
        return self.resolved_by

    def isResolved(self) -> bool:
        return self.resolution != ""

    def isPushProtectionBypassed(self) -> bool:
        return self.payload.get("alert", {}).get("push_protection_bypassed", False)
