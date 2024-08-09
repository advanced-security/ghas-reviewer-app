from typing import Dict, List
import logging

logger = logging.getLogger("DependabotAlert")


class DependabotAlert:
    payload: Dict = {}

    @property
    def id(self) -> int:
        return self.payload.get("alert", {}).get("number", 0)

    @property
    def state(self) -> str:
        return self.payload.get("alert", {}).get("state", "")

    @property
    def package_name(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("dependency", {})
            .get("package", {})
            .get("name", "")
        )

    @property
    def ecosystem(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("dependency", {})
            .get("package", {})
            .get("ecosystem", "")
        )

    @property
    def manifest_path(self) -> str:
        return (
            self.payload.get("alert", {}).get("dependency", {}).get("manifest_path", "")
        )

    @property
    def scope(self) -> str:
        return self.payload.get("alert", {}).get("dependency", {}).get("scope", "")

    @property
    def ghsa_id(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("ghsa_id", "")
        )

    @property
    def cve_id(self) -> str:
        return (
            self.payload.get("alert", {}).get("security_advisory", {}).get("cve_id", "")
        )

    @property
    def summary(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("summary", "")
        )

    @property
    def description(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("description", "")
        )

    @property
    def severity(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("severity", "")
        )

    @property
    def identifiers(self) -> List[Dict]:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("identifiers", [])
        )

    @property
    def references(self) -> List[Dict]:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("references", [])
        )

    @property
    def published_at(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("published_at", "")
        )

    @property
    def updated_at(self) -> str:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("updated_at", "")
        )

    @property
    def vulnerabilities(self) -> List[Dict]:
        return (
            self.payload.get("alert", {})
            .get("security_advisory", {})
            .get("vulnerabilities", [])
        )

    @property
    def cvss(self) -> Dict:
        return (
            self.payload.get("alert", {}).get("security_advisory", {}).get("cvss", {})
        )

    @property
    def cwes(self) -> List[Dict]:
        return (
            self.payload.get("alert", {}).get("security_advisory", {}).get("cwes", [])
        )

    @property
    def url(self) -> str:
        return self.payload.get("alert", {}).get("url", "")

    @property
    def html_url(self) -> str:
        return self.payload.get("alert", {}).get("html_url", "")

    @property
    def created_at(self) -> str:
        return self.payload.get("alert", {}).get("created_at", "")

    @property
    def updated_at(self) -> str:
        return self.payload.get("alert", {}).get("updated_at", "")

    @property
    def dismissed_at(self) -> str:
        return self.payload.get("alert", {}).get("dismissed_at", "")

    @property
    def dismissed_by(self) -> str:
        return self.payload.get("alert", {}).get("dismissed_by", {}).get("login", "")

    @property
    def dismissed_reason(self) -> str:
        return self.payload.get("alert", {}).get("dismissed_reason", "")

    @property
    def dismissed_comment(self) -> str:
        return self.payload.get("alert", {}).get("dismissed_comment", "")

    @property
    def fixed_at(self) -> str:
        return self.payload.get("alert", {}).get("fixed_at", "")

    @property
    def auto_dismissed_at(self) -> str:
        return self.payload.get("alert", {}).get("auto_dismissed_at", "")

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
        return self.dismissed_by
