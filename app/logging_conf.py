from logging.config import dictConfig
from app.config import DevConfig, config


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(name)s - %(lineno)d - %(message)s"
                },

                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)8s | %(name)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "formatter": "console",
                    "level": "DEBUG"
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024, 
                    "backupCount": 5,
                    "formatter": "file",
                    "level": "DEBUG",
                    "encoding": "utf8"
                }
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                    "propagate": False
                },
                
                "app": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False
                },

                "database": {
                    "handlers": ["default", "rotating_file"],
                    "level": "WARNING",
                    "propagate": False
                },

                "sqlalchemy": {
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": False
                },
            }
        }
    )