use super::Action;
use crate::config::Config;
use octoapp::{events::payloads::CodeScanningAlertEvent, OctoAppError};
use octocrab::Octocrab;

pub struct CodeScanningAction {}

impl Action for CodeScanningAction {
    type Event = CodeScanningAlertEvent;

    fn check(config: &Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError> {
        let config = match config {
            Config::V1(config_v1) => config_v1,
        };

        if !config.code_scanning.is_enabled() {
            log::info!("Code Scanning feature is disabled");
            return Ok(false);
        }

        Ok(true)
    }

    async fn run(
        config: &Config,
        client: &Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError> {
        let config = match config {
            Config::V1(config_v1) => config_v1,
        };
        log::info!("Running Code Scanning Action");

        let team = config.find_team_by_repository(event.repository.full_name)?;

        Ok(())
    }
}
