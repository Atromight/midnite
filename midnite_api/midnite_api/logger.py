import logging
from logging.config import dictConfig

from midnite_api.const import APP_NAME
from midnite_api.context import get_request_id


class RequestIDLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": RequestIDLogFilter,
        },
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s][%(request_id)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
        },
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
