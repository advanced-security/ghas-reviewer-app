import sys
from argparse import ArgumentParser

from ghasreview.app import create_app, config

if __name__ == "__main__":
    parser = ArgumentParser("GHAS Review", add_help=False)
    parser.add_argument("--test-mode", action="store_true")
    args, _ = parser.parse_known_args()

    app = create_app(config)

    if args.test_mode:
        app.config["TESTING"] = True
        with app.test_client() as client:
            response = client.get("/healthcheck")
            data = response.get_json()
            healthy = response.status_code == 200 and data.get("status") == "healthy"
            sys.exit(0 if healthy else 1)
    else:
        app.run("0.0.0.0", port=9000, debug=config.get("GHAS_DEBUG", False))
