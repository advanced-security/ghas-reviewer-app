import os
import logging
from argparse import ArgumentParser

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def parse_arguments():
    parser = ArgumentParser("GHAS Review")
    parser.add_argument(
        "--debug", action="store_true", default=bool(os.environ.get("DEBUG"))
    )
    parser.add_argument(
        "--test-mode", action="store_true", default=bool(os.environ.get("TEST_MODE", 0))
    )

    parser_github = parser.add_argument_group("GHAS Reviewer")
    parser_github.add_argument(
        "--ghas-team-name",
        default=os.environ.get("GITHUB_GHAS_TEAM") or "ghas-reviewers",
    )
    parser_github.add_argument(
        "--ghas-tool-name", default=os.environ.get("GITHUB_TOOL_NAME") or "CodeQL"
    )

    parser_github = parser.add_argument_group("GitHub")
    parser_github.add_argument(
        "--github-app-endpoint", default=os.environ.get("GITHUB_APP_ENDPOINT")
    )
    parser_github.add_argument(
        "--github-app-id", default=os.environ.get("GITHUB_APP_ID")
    )
    parser_github.add_argument(
        "--github-app-key-path", default=os.environ.get("GITHUB_APP_KEY_PATH")
    )
    parser_github.add_argument(
        "--github-app-key", default=os.environ.get("GITHUB_APP_KEY")
    )
    parser_github.add_argument(
        "--github-app-secret", default=os.environ.get("GITHUB_APP_SECRET")
    )
    args, _ = parser.parse_known_args()
    return args


def setup_logging(arguments):
    logging.basicConfig(
        level=logging.DEBUG if arguments.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.debug("Debug mode enabled")

    logging.debug(f"GHAS Endpoint :: {arguments.github_app_endpoint}")
    logging.info(f"GitHub App ID :: {arguments.github_app_id}")
    logging.debug(f"GitHub Key :: {arguments.github_app_key}")
    logging.info(f"GitHub Key Path :: {arguments.github_app_key_path}")
    logging.debug(f"GitHub App Secret :: {arguments.github_app_secret}")
    logging.debug(f"GHAS Tool Name :: {arguments.ghas_tool_name}")


def validate_arguments(arguments):
    if arguments.test_mode:
        logging.info(f"Testing mode enabled, exiting...")
        exit(0)
    if not arguments.github_app_id:
        raise Exception(f"GitHub App ID not set")
    if not arguments.github_app_secret:
        raise Exception(f"GitHub App Secret not set")
    if not arguments.github_app_key:
        # Try and load from file
        if not arguments.github_app_key_path and not os.path.exists(
            arguments.github_app_key_path
        ):
            raise Exception(f"GitHub App Key not set")

        with open(arguments.github_app_key_path, "r") as handle:
            app_key = handle.read()
    else:
        logging.info(f"Loading in Key mode")
        app_key = arguments.github_app_key.replace("\\n", "\n")
    return app_key


def setup_app():
    arguments = parse_arguments()
    setup_logging(arguments)
    app_key = validate_arguments(arguments)
    config = {
        "GHAS_DEBUG": arguments.debug,
        # Set the route
        "GITHUBAPP_ROUTE": arguments.github_app_endpoint,
        # Team name
        "GHAS_TEAM": arguments.ghas_team_name,
        "GHAS_BOARD_NAME": "GHAS Reviewers Audit Board",
        # Tool and severities to check
        "GHAS_TOOL": arguments.ghas_tool_name,
        "GHAS_SEVERITIES": ["critical", "high", "error", "errors"],
        # GitHub App
        "GITHUBAPP_ID": arguments.github_app_id,
        "GITHUBAPP_KEY": app_key,
        "GITHUBAPP_SECRET": arguments.github_app_secret,
    }
    return config
