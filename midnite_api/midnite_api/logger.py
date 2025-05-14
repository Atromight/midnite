import logging
from logging.config import dictConfig

from midnite_api.const import APP_NAME

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        APP_NAME: {
            "handlers": ["default"],
            "level": "DEBUG",
        },
    },
}


dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("your_app")  # Use this in your code
