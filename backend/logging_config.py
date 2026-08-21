import logging
from logging.handlers import RotatingFileHandler

from paths import LOG_DIR


class IgnoreClientDisconnect(logging.Filter):
    """クライアント切断によるConnectionResetErrorをログに残さない。"""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name != "asyncio":
            return True

        if not record.exc_info:
            return True

        return not isinstance(
            record.exc_info[1],
            ConnectionResetError,
        )


def setup_logging() -> None:
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    disconnect_filter = IgnoreClientDisconnect()
    file_handler.addFilter(disconnect_filter)
    console_handler.addFilter(disconnect_filter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            console_handler,
            file_handler,
        ],
        force=True,
    )