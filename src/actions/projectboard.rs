use octoapp::OctoAppError;
use octocrab::Octocrab;

use crate::config::{v1::ConfigV1, Config};

use super::Action;

pub struct ProjectBoardAction {}

impl Action for ProjectBoardAction {
    type Event = ();

    async fn setup(config: &Config, client: &octocrab::Octocrab) -> Result<(), OctoAppError> {
        let configv1 = match config {
            Config::V1(config_v1) => config_v1,
        };

        if ProjectBoardAction::check_board(&configv1, client).await? {
            ProjectBoardAction::create(&configv1, client).await?;
        }

        Ok(())
    }

    fn check(config: &Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError> {
        let configv1 = match config {
            Config::V1(config_v1) => config_v1,
        };

        if !configv1.project_board.enabled {
            log::info!("GHAS Project Board feature is disabled");
            return Ok(false);
        }

        Ok(true)
    }

    async fn run(
        config: &Config,
        client: &octocrab::Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError> {
        todo!()
    }
}

impl ProjectBoardAction {
    async fn check_board(
        config: &ConfigV1,
        client: &octocrab::Octocrab,
    ) -> Result<bool, OctoAppError> {
        let query = include_str!("./graphql/CheckProjectBoard.graphql");

        let response = client
            .graphql(&serde_json::json!({
                "query": query,
            }))
            .await
            .map_err(|err| OctoAppError::UnknownError)?;

        Ok(false)
    }

    async fn create(config: &ConfigV1, client: &octocrab::Octocrab) -> Result<(), OctoAppError> {
        let query = include_str!("./graphql/CreateProjectBoard.graphql");

        let response = client
            .graphql(&serde_json::json!({
                "query": query,
                "variables": {
                    "title": &config.project_board.title,
                    "shortDescription": &config.project_board.description,
                }
            }))
            .await
            .map_err(|err| OctoAppError::UnknownError)?;

        log::info!("Project Board created: {:?}", response);

        Ok(())
    }

    pub async fn add(
        config: &Config,
        client: &Octocrab,
        event: &octoapp::events::Event,
    ) -> Result<(), OctoAppError> {
        Ok(())
    }
}
