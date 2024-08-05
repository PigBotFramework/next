import logging
import os
from datetime import datetime
import pytz

try:
    from ..config import logs_level, logs_format, logs_directory
    from ..utils import Path
except ImportError:
    from pbf.config import logs_level, logs_format, logs_directory
    from pbf.utils import Path


class Logger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logs_level)
        self.formatter = logging.Formatter(logs_format)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logs_level)
        self.console_handler.setFormatter(self.formatter)

        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        file_name = now.strftime("%Y-%m-%d.log")
        self.file_handler = logging.FileHandler(os.path.join(Path.replace(logs_directory), file_name))
        self.file_handler.setLevel(logs_level)
        self.file_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: str) -> None:
        self.logger.setLevel(level)
        self.console_handler.setLevel(level)
        self.file_handler.setLevel(level)

    def set_format(self, format: str) -> None:
        self.formatter = logging.Formatter(format)
        self.console_handler.setFormatter(self.formatter)
        self.file_handler.setFormatter(self.formatter)

    def set_file(self, file: str) -> None:
        self.file_handler = logging.FileHandler(file)
        self.file_handler.setLevel(self.logger.level)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)


if __name__ == "__main__":
    logger = Logger("test")
    logger.info("info")
    logger.debug("debug")
    logger.warning("warning")
    logger.error("error")
