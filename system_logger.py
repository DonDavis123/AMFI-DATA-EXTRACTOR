import logging
import os


class SystemLogger:
    _logger = None

    @classmethod
    def get_logger(cls):
        if cls._logger:
            return cls._logger

        os.makedirs("logs", exist_ok=True)

        logger = logging.getLogger("system")

        if not logger.handlers:
            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                "logs/system.log",
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s : %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            handler.setFormatter(formatter)
            logger.addHandler(handler)

        cls._logger = logger
        return logger