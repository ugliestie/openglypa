"""
https://pythonbynight.com/blog/sharpen-your-code
"""
import logging
from functools import lru_cache

from pydantic import BaseModel


class LoggerConfig(BaseModel):
    handlers: list
    format: str | None
    date_format: str | None = None
    level: int = logging.INFO

@lru_cache
def get_logger_config():
	from rich.logging import RichHandler

	return LoggerConfig(
		handlers=[
			RichHandler(
				rich_tracebacks=True,
				tracebacks_show_locals=True,
				show_time=False
			)
		],
		format=None,
		date_format="%d %b %Y | %H:%M:%S",
	)
   
def setup_rich_logger():
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger_config = get_logger_config()  # get Rich logging config

    logging.basicConfig(
        level=logger_config.level,
        format=logger_config.format,
        datefmt=logger_config.date_format,
        handlers=logger_config.handlers,
    )