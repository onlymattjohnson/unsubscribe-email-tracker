import logging.config
import sys


def setup_logging():
    """Sets up structured JSON logging."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(request_id)s",
                },
            },
            "filters": {
                "request_id_filter": {
                    "()": "app.core.logging_config.RequestIdFilter",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "json",
                    "filters": ["request_id_filter"],
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"],
            },
        }
    )


class RequestIdFilter(logging.Filter):
    """A logging filter that adds the request_id to the log record."""

    def filter(self, record):
        from app.core.request_context import request_id_cv

        record.request_id = request_id_cv.get()
        return True
