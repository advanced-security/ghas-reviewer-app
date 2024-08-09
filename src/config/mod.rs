use anyhow::Result;
use std::path::PathBuf;

pub mod v1;

#[derive(Debug, Clone, serde::Deserialize)]
#[serde(untagged)]
pub enum Config {
    V1(v1::ConfigV1),
}

impl Config {
    pub fn new() -> Self {
        Self::default()
    }

    /// Load the configuration from a file
    pub fn load(path: impl Into<PathBuf>) -> Result<Self> {
        let path = path.into();
        log::info!("Loading configuration from {:?}", path);

        let data = std::fs::read_to_string(&path)?;
        Self::load_str(&data)
    }
    /// Load the configuration from a string
    pub fn load_str(data: &str) -> Result<Self> {
        let mut config: Self = serde_yaml::from_str(data)?;

        Self::load_defaults(&mut config);

        Ok(config)
    }
    /// Load the configuration from the command line arguments
    pub fn load_arguments(arguments: &crate::cli::Arguments) -> Self {
        let mut config = Self::default();
        Self::load_defaults(&mut config);
        config
    }

    fn load_defaults(config: &mut Self) {
        match config {
            Self::V1(ref mut config) => {
                // Defaults for V1
                if config.teams.is_empty() {
                    config.teams.push(v1::Team {
                        name: "ghas-reviewers".to_string(),
                        default: Some(true),
                        ..Default::default()
                    });
                }
            }
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Self::V1(v1::ConfigV1::default())
    }
}
