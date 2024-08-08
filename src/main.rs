#![allow(unused_variables)]

#[macro_use]
extern crate rocket;

use actions::{codescanning::CodeScanningAction, Action};
use anyhow::Result;
use octoapp::prelude::*;
use rocket::{http::Status, State};

mod actions;
mod cli;
mod config;

use config::Config;

pub struct AppState {
    pub config: Config,
}

#[post("/", data = "<event>")]
async fn webhook(
    state: &State<AppState>,
    app: &State<OctoAppState>,
    event: WebHook<Event>,
) -> (Status, String) {
    let octo = event.octocrab(app).await.unwrap();

    match event.into_inner() {
        Event::Installation(installation) => {
            log::info!("Received an Installation event: {:?}", installation);
        }
        Event::CodeScanningAlert(alert) => {
            log::info!("Received a CodeScanningAlert event: {:?}", alert);

            if CodeScanningAction::check(&state.config, &octo).unwrap() {
                CodeScanningAction::run(&state.config, &octo, &alert)
                    .await
                    .unwrap();
            }
        }
        Event::DependabotAlert(alert) => {
            log::info!("Received a DependabotAlert event: {:?}", alert);
        }
        Event::SecretScanningAlert(alert) => {
            log::info!("Received a SecretScanningAlert event: {:?}", alert);
        }
        _ => {
            log::warn!("Received an unknown event");
        }
    }
    (Status::Ok, "Received Event".to_string())
}

#[rocket::main]
async fn main() -> Result<()> {
    let arguments = cli::init();

    let mut app = OctoAppConfig::init()
        .app_id(arguments.github_app_id.expect("GitHub App ID is required") as usize)
        .build()?;
    app.install().await?;

    let config = match Config::load(&arguments.config) {
        Ok(config) => config,
        Err(_) => Config::load_arguments(&arguments),
    };

    let rocket = rocket::build()
        .manage(OctoAppState::new(app))
        .manage(AppState { config })
        .mount(arguments.github_app_endpoint.as_str(), routes![webhook]);

    rocket.launch().await?;

    Ok(())
}
