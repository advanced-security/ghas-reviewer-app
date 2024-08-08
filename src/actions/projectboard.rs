use octoapp::OctoAppError;

use crate::config::v1::ConfigV1 as Config;

pub struct ProjectBoardAction {}

impl ProjectBoardAction {
    /// Setup the Project Board
    pub async fn setup(config: &Config, client: &octocrab::Octocrab) -> Result<(), OctoAppError> {
        if !config.project_board.enabled {
            log::info!("GHAS Project Board feature is disabled");
            return Ok(());
        }
        todo!("Project Board setup");
    }

    async fn check(config: &Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError> {
        let query = include_str!("./graphql/CheckProjectBoard.graphql");

        let response = client
            .graphql(&serde_json::json!({
                "query": query,
            }))
            .await?;

        Ok(false)
    }

    async fn create(config: &Config, client: &octocrab::Octocrab) -> Result<(), OctoAppError> {
        let query = include_str!("./graphql/CreateProjectBoard.graphql");

        let response = client
            .graphql(&serde_json::json!({
                "query": query,
                "variables": {
                    "title": &config.project_board.title,
                    "shortDescription": &config.project_board.description,
                }
            }))
            .await?;

        log::info!("Project Board created: {:?}", response);

        Ok(())
    }
}
