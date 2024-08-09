//! Project board configuration

#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct ProjectBoard {
    /// Disabled by default
    pub enabled: bool,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub description: String,

    /// TODO: This is a placeholder for future features
    pub fields: Vec<ProjectBoardField>,
}

impl Default for ProjectBoard {
    fn default() -> Self {
        Self {
            enabled: false,
            title: "GHAS Reviewer Board".to_string(),
            description: "A project board for managing GHAS alerts".to_string(),
            fields: vec![],
        }
    }
}

#[derive(Debug, Clone, serde::Deserialize, serde::Serialize)]
pub struct ProjectBoardField {
    pub name: String,
    #[serde(default)]
    pub r#type: String,
}

impl Default for ProjectBoardField {
    fn default() -> Self {
        Self {
            name: "Severity".to_string(),
            r#type: "text".to_string(),
        }
    }
}
