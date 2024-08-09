use serde::{Deserialize, Serialize};

pub mod project_board;

#[derive(Debug, Default, Clone, Deserialize, Serialize)]
pub struct ConfigV1 {
    #[serde(default, rename = "code-scanning")]
    pub code_scanning: Feature,
    #[serde(default)]
    pub dependabot: Feature,
    #[serde(default, rename = "secret-scanning")]
    pub secret_scanning: Feature,

    #[serde(default, rename = "project-board")]
    pub project_board: project_board::ProjectBoard,

    pub teams: Teams,
}

impl ConfigV1 {
    pub fn new() -> Self {
        Self::default()
    }

    /// Find the default team
    pub fn find_default_team(&self) -> Option<&Team> {
        self.teams.iter().find(|team| team.default.unwrap_or(false))
    }

    /// Find a team by the repository name
    ///
    /// - Match the repository name
    /// - If no match, return the default team
    pub fn find_team_by_repository(&self, repository: impl Into<String>) -> Team {
        let repository = repository.into();
        self.teams
            .iter()
            .find(|team| team.repositories.contains(&repository))
            .unwrap_or_else(|| self.find_default_team().unwrap())
            .clone()
    }
}

pub type Teams = Vec<Team>;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Team {
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub default: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub severity: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub repositories: Vec<String>,
}

impl Team {
    pub fn new(name: String) -> Self {
        Self {
            name,
            default: None,
            severity: None,
            repositories: vec![],
        }
    }
}

impl Default for Team {
    fn default() -> Self {
        Self {
            name: "ghas-reviewers".to_string(),
            default: Some(true),
            severity: None,
            repositories: vec![],
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Feature {
    pub enabled: Option<bool>,
}

impl Feature {
    /// Is the feature enabled?
    pub fn is_enabled(&self) -> bool {
        self.enabled.unwrap_or(true)
    }
}

impl Default for Feature {
    fn default() -> Self {
        Self {
            enabled: Some(true),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_defaults() {
        let config = ConfigV1::new();
        assert_eq!(config.code_scanning.enabled, Some(true));
        assert_eq!(config.dependabot.enabled, Some(true));
        assert_eq!(config.secret_scanning.enabled, Some(true));
        assert_eq!(config.project_board.enabled, false);
    }

    #[test]
    fn test_config_teams() {
        let data = include_str!("../../../tests/resources/v1/config-teams.yml");
        let config: ConfigV1 = serde_yaml::from_str(data).unwrap();

        // Validate the configuration
        assert_eq!(config.teams.len(), 3);

        let team = &config.teams[0];
        assert_eq!(team.name, "ghas-reviewers");
        assert_eq!(team.default, Some(true));

        let team = &config.teams[1];
        assert_eq!(team.name, "octo-reviewers");
        assert_eq!(
            team.repositories,
            vec![
                "octocat/hello-world".to_string(),
                "octocat/earth".to_string()
            ]
        );
    }

    #[test]
    fn test_find_team() {
        let data = include_str!("../../../tests/resources/v1/config-teams.yml");
        let config: ConfigV1 = serde_yaml::from_str(data).unwrap();

        let team = config.find_team_by_repository("octocat/hello-world");
        assert_eq!(team.name, "octo-reviewers");

        // Default team
        let team = config.find_team_by_repository("octocat/random-name");
        assert_eq!(team.name, "ghas-reviewers");
    }
}
