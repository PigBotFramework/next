import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

try:
    from ..config import logs_level, logs_format, logs_directory
    from ..utils import Path
except ImportError:
    from pbf.config import logs_level, logs_format, logs_directory
    from pbf.utils import Path


class Logger:
    def __init__(self, name: str) -> None:
        """
        Initialize the Logger.
        :param name: str Logger name
        """
        self.file_handler = None
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logs_level)
        self.formatter = logging.Formatter(logs_format)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logs_level)
        self.console_handler.setFormatter(self.formatter)

        self.set_file(logs_directory)

        self.logger.addHandler(self.console_handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the logger.
        :return: logging.Logger
        """
        return self.logger

    def set_level(self, level: str) -> None:
        """
        Set the logger level.
        :param level: str level
        :return: None
        """
        self.logger.setLevel(level)
        self.console_handler.setLevel(level)
        self.file_handler.setLevel(level)

    def set_format(self, format: str) -> None:
        """
        Set the logger format.
        :param format: str format
        :return: None
        """
        self.formatter = logging.Formatter(format)
        self.console_handler.setFormatter(self.formatter)
        self.file_handler.setFormatter(self.formatter)

    def set_file(self, file: str) -> None:
        """
        Set the logger file.
        :param file: str file path
        :return: None
        """
        self.file_handler = TimedRotatingFileHandler(
            filename=os.path.join(Path.replace(file), "log"), when="MIDNIGHT", interval=1, backupCount=20
        )
        self.file_handler.suffix = "%Y-%m-%d.log"
        self.file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def info(self, message: str, *args, **kwargs) -> None:
        """
        Log the info message.
        :param message: str message
        :param args: *list
        :param kwargs: **dict
        :return: None
        """
        self.logger.info(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        """
        Log the debug message.
        :param message: str message
        :param args: *list
        :param kwargs: **dict
        :return: None
        """
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """
        Log the warning message.
        :param message: str message
        :param args: *list
        :param kwargs: **dict
        :return: None
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """
        Log the error message.
        :param message: str message
        :param args: *list
        :param kwargs: **dict
        :return: None
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """
        Log the critical message.
        :param message: str message
        :param args: *list
        :param kwargs: **dict
        :return: None
        """
        self.logger.critical(message, *args, **kwargs)


if __name__ == "__main__":
    logger = Logger("test")
    logger.info("info")
    logger.debug("debug")
    logger.warning("warning")
    logger.error("error")
