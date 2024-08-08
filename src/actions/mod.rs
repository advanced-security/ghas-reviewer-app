use codescanning::CodeScanningAction;
use octoapp::{events::payloads::CodeScanningAlertEvent, OctoAppError};

use crate::config::Config;

pub mod codescanning;
pub mod projectboard;

pub trait Action {
    type Event;
    /// Setup the feature if it is needed
    async fn setup(config: &Config, client: &octocrab::Octocrab) -> Result<(), OctoAppError> {
        Ok(())
    }

    /// Check if the feature is enabled
    fn check(config: &Config, client: &octocrab::Octocrab) -> Result<bool, OctoAppError>;

    async fn run(
        config: &Config,
        client: &octocrab::Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError>;
}
