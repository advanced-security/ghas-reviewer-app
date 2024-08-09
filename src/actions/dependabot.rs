use crate::{Action, Config};
use octoapp::prelude::*;

pub struct DependabotAction {}

impl Action for DependabotAction {
    type Event = DependabotAlertEvent;

    fn check(config: &Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError> {
        let config = match config {
            crate::config::Config::V1(config_v1) => config_v1,
        };

        if !config.dependabot.is_enabled() {
            log::info!("Dependabot feature is disabled");
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
            crate::config::Config::V1(config_v1) => config_v1,
        };

        log::info!("Running Dependabot Action");

        Ok(())
    }
}
