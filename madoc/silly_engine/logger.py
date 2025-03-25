"""
This modules provides a quick and easy way to use Logger class.
example:

logger = Logger("My Application", level="DEBUG")

logger.debug("that works")

"""


import logging

levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

class CustomFormatter(logging.Formatter):
    blue = "\033[34m"
    green = "\033[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    prefix = "[%(asctime)s][%(name)s][%(levelname)s] "
    message = "%(message)s"

    FORMATS = {
        logging.DEBUG: green + prefix + reset + message,
        logging.INFO: blue + prefix + reset + message,
        logging.WARNING: yellow + prefix + reset + message,
        logging.ERROR: red + prefix + reset + message,
        logging.CRITICAL: bold_red + prefix + reset + message
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class Logger(logging.Logger):
    def __init__(self, name :str=__name__, level: str="INFO"):
        super().__init__(name)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(CustomFormatter())
        self.addHandler(self.console_handler)

    def setLevel(self, level):
        super().setLevel(levels[level])
