import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():
    log_format = "%(levelname)s:    %(asctime)s - %(name)s - %(message)s"
    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # логи в файл
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers = []

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
