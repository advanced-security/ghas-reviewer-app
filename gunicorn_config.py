# gunicorn_config.py

loglevel = "debug"
bind = "0.0.0.0:9000"
workers = 4
accesslog = "-"
errorlog = "-"
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "gunicorn.access": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "app": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "GitHubClient": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "CodeScanningAlert": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "DependabotAlert": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "SecretScanningAlert": {
            "level": loglevel.upper(),
            "handlers": ["console"],
            "propagate": False,
        },
        "": {
            "level": loglevel.upper(),
            "handlers": ["console"],
        },
    },
}
