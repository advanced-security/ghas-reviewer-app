import os
import logging
from argparse import ArgumentParser

from ghasreview.app import run

parser = ArgumentParser("GHAS Review")
parser.add_argument(
    "--debug", action="store_true", default=bool(os.environ.get("DEBUG"))
)

parser_github = parser.add_argument_group("GitHub")
parser_github.add_argument("--github-app-id", default=os.environ.get("GITHUB_APP_ID"))
parser_github.add_argument(
    "--github-app-key", default=os.environ.get("GITHUB_APP_KEY_PATH")
)
parser_github.add_argument(
    "--github-app-secret", default=os.environ.get("GITHUB_APP_SECRET")
)


if __name__ == "__main__":
    arguments = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if arguments.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.info(f"GitHub App ID :: {arguments.github_app_id}")
    logging.info(f"GitHub Key Path :: {arguments.github_app_key}")
    logging.debug(f"GitHub App Secret :: {arguments.github_app_secret}")

    if not arguments.github_app_id:
        raise Exception(f"GitHub App ID not set")
    if not arguments.github_app_secret:
        raise Exception(f"GitHub App Secret not set")
    if not arguments.github_app_key and not os.path.exists(arguments.github_app_key):
        raise Exception(f"GitHub App Key not set")

    with open(arguments.github_app_key, "r") as handle:
        app_key = handle.read()

    config = {
        "GITHUBAPP_ID": arguments.github_app_id,
        "GITHUBAPP_KEY": app_key,
        "GITHUBAPP_SECRET": arguments.github_app_secret,
    }

    run(config)
