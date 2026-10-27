########################
# Logger               #
########################

import logging


class Logger:
    """
    Central logging helper for the calculator.

    All parts of the application log through this class, so every message
    goes to the same log file (set by CALCULATOR_LOG_FILE in the configuration)
    with the right logging level.
    """

    @staticmethod
    def info(message: str) -> None:
        """Log normal events, like a completed calculation."""
        logging.info(message)

    @staticmethod
    def warning(message: str) -> None:
        """Log something unexpected that the app can recover from."""
        logging.warning(message)

    @staticmethod
    def error(message: str) -> None:
        """Log errors, like a failed calculation."""
        logging.error(message)