import logging
from ghasreview.app import app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app.run(host="0.0.0.0", port=9000)

