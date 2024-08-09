use clap::Parser;
use console::style;
use std::path::PathBuf;

pub const VERSION_NUMBER: &str = env!("CARGO_PKG_VERSION");
pub const AUTHOR: &str = env!("CARGO_PKG_AUTHORS");

pub const BANNER: &str = r#"  ________  ___ ___    _____    _________ __________            .__                                _____
 /  _____/ /   |   \  /  _  \  /   _____/ \______   \ _______  _|__| ______  _  __ ___________    /  _  \ ______ ______
/   \  ___/    ~    \/  /_\  \ \_____  \   |       _// __ \  \/ /  |/ __ \ \/ \/ // __ \_  __ \  /  /_\  \\____ \\____ \
\    \_\  \    Y    /    |    \/        \  |    |   \  ___/\   /|  \  ___/\     /\  ___/|  | \/ /    |    \  |_> >  |_> >
 \______  /\___|_  /\____|__  /_______  /  |____|_  /\___  >\_/ |__|\___  >\/\_/  \___  >__|    \____|__  /   __/|   __/
        \/       \/         \/        \/          \/     \/             \/            \/                \/|__|   |__|
"#;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
pub struct Arguments {
    /// Enable Debugging
    #[clap(long, env, default_value_t = false)]
    pub debug: bool,

    /// Disable Banner
    #[clap(long, default_value_t = false)]
    pub disable_banner: bool,

    /// Test Mode
    #[clap(long, default_value_t = false)]
    pub test_mode: bool,

    /// Configuration file path
    #[clap(short, long, env, default_value = "./config.yml")]
    pub config: PathBuf,

    /// GitHub Review App Team Name
    #[clap(long)]
    pub ghas_team_name: Option<String>,

    /// GitHub Review App Tool Name
    #[clap(long)]
    pub ghas_tool_name: Option<String>,

    /// GitHub App Endpoint
    #[clap(long, env, default_value = "/github")]
    pub github_app_endpoint: String,

    /// GitHub App ID
    #[clap(long, env = "APP_ID")]
    pub github_app_id: Option<u32>,

    /// GitHub App Private Key
    #[clap(long, env = "PRIVATE_KEY")]
    pub github_app_private_key: Option<String>,

    /// GitHub App Key Path
    #[clap(long, env = "PRIVATE_KEY_PATH")]
    pub github_app_key_path: Option<PathBuf>,

    /// GitHub App Client Secret
    #[clap(long, env = "CLIENT_SECRET")]
    pub github_app_client_secret: Option<String>,

    /// GitHub App Webhook Secret
    #[clap(long, env = "WEBHOOK_SECRET")]
    pub github_app_webhook_secret: Option<String>,
}

pub fn init() -> Arguments {
    dotenvy::dotenv().ok();

    let arguments = Arguments::parse();

    let log_level = match &arguments.debug {
        false => log::LevelFilter::Info,
        true => log::LevelFilter::Debug,
    };

    env_logger::builder()
        .parse_default_env()
        .filter_level(log_level)
        .init();

    if !arguments.disable_banner {
        println!(
            "{}\n                      {} - v{}",
            style(BANNER).green(),
            style(AUTHOR).red(),
            style(VERSION_NUMBER).blue()
        );
    }

    arguments
}
