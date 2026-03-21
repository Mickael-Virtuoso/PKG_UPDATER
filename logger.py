import logging
import colorlog
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config import BASE_DIR
from log_config import LOG_LEVELS

LOG_FILE = Path(BASE_DIR) / "logs" / "pkg-updater.log"
LOG_FILE.parent.mkdir(exist_ok=True)

# ─── Nível TRACE customizado (abaixo do DEBUG) ────────────────────────────────
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def _build_active_level() -> int:
    """Retorna o nível mínimo ativo baseado no log_config."""
    order = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    for level_name in order:
        if LOG_LEVELS.get(level_name, False):
            return logging.getLevelName(level_name) if level_name != "TRACE" else TRACE_LEVEL
    return logging.CRITICAL


class LevelFilterHandler(logging.Handler):
    """Handler que filtra mensagens baseado nos booleanos do log_config."""

    def __init__(self, inner_handler: logging.Handler):
        super().__init__()
        self.inner_handler = inner_handler

    def emit(self, record: logging.LogRecord):
        level_name = record.levelname
        if LOG_LEVELS.get(level_name, False):
            self.inner_handler.emit(record)


class PkgLogger(logging.Logger):
    """Logger customizado com método .trace()."""

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, msg, args, **kwargs)


def setup_logger(name: str = "pkg-updater") -> PkgLogger:
    logging.setLoggerClass(PkgLogger)
    logger = logging.getLogger(name)
    logger.setLevel(TRACE_LEVEL)  # captura tudo — o filtro decide o que exibir

    # ─── Terminal — colorido ──────────────────────────────────────────────────
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "TRACE":    "white",
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
        }
    ))

    # ─── Arquivo — sem cores, com rotação ────────────────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    logger.addHandler(LevelFilterHandler(console_handler))
    logger.addHandler(LevelFilterHandler(file_handler))

    return logger


logger = setup_logger()