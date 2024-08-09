use crate::{Action, Config};
use octoapp::prelude::*;

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
        client: &octocrab::Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError> {
        let config = match config {
            Config::V1(config_v1) => config_v1,
        };
        log::info!("Running Code Scanning Action");

        Ok(())
    }
}
