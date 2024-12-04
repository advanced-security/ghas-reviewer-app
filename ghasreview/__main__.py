from ghasreview.app import create_app, config

if __name__ == "__main__":
    app = create_app(config)
    app.run("0.0.0.0", port=9000, debug=config.get("GHAS_DEBUG", False))
