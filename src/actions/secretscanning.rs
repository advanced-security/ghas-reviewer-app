use crate::Action;
use octoapp::prelude::*;

pub struct SecretScanningAction {}

impl Action for SecretScanningAction {
    type Event = SecretScanningAlertEvent;

    fn check(config: &crate::Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError> {
        let config = match config {
            crate::Config::V1(config_v1) => config_v1,
        };

        if !config.secret_scanning.is_enabled() {
            log::info!("Secret Scanning feature is disabled");
            return Ok(false);
        }

        Ok(true)
    }

    async fn run(
        config: &crate::Config,
        client: &octocrab::Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError> {
        let config = match config {
            crate::Config::V1(config_v1) => config_v1,
        };
        log::info!("Running Secret Scanning Action");

        Ok(())
    }
}
