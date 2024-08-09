use octoapp::OctoAppError;
use octocrab::Octocrab;

use crate::config::Config;

pub mod codescanning;
pub mod dependabot;
pub mod projectboard;
pub mod secretscanning;

pub use codescanning::CodeScanningAction;
pub use dependabot::DependabotAction;
pub use projectboard::ProjectBoardAction;
pub use secretscanning::SecretScanningAction;

pub trait Action {
    /// Webhook event type
    type Event;

    #[allow(async_fn_in_trait)]
    /// Setup the feature if it is needed
    async fn setup(config: &Config, client: &Octocrab) -> Result<(), OctoAppError> {
        Ok(())
    }

    /// Check if the feature is enabled
    fn check(config: &Config, client: &Octocrab) -> Result<bool, OctoAppError> {
        Ok(false)
    }

    /// Run the main logic of the feature
    #[allow(async_fn_in_trait)]
    async fn run(
        config: &Config,
        client: &Octocrab,
        event: &Self::Event,
    ) -> Result<(), OctoAppError>;
}
