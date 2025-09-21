import dataclasses
import logging.config
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import structlog
from structlog.typing import EventDict

__all__ = [
    "InitLoggers",
    "LoggerError",
    "LoggerNotFoundError",
    "LoggerReg",
    "SetupLogger",
]


class LoggerError(Exception):
    """Общая ошибка системы логирования."""


class LoggerNotFoundError(LoggerError):
    """Запрошенный логгер не зарегистрирован."""


def add_caller_details(_: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
    filename = event_dict.pop("filename", "?")
    func_name = event_dict.pop("func_name", "?")
    lineno = event_dict.pop("lineno", 0)
    event_dict["logger"] = f"{filename}:{func_name}:{lineno}"
    return event_dict


@dataclasses.dataclass(slots=True)
class LoggerReg:
    """Параметры отдельного логгера."""

    name: str

    class Level(Enum):
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"
        NONE = None

    level: "LoggerReg.Level" = Level.DEBUG
    propagate: bool = False


class SetupLogger:
    """Настройка стандартного `logging` + `structlog`."""

    CONSOLE_HANDLER = "console"
    JSON_HANDLER = "json"

    def __init__(
        self,
        name_registration: list[LoggerReg] | None,
        *,
        developer_mode: bool = False,
    ) -> None:
        self._regs: list[LoggerReg] = name_registration or [LoggerReg("")]
        self._regs.append(LoggerReg("confhub", LoggerReg.Level.INFO))
        self._developer_mode = developer_mode
        self._module_name = Path(sys.argv[0]).stem
        self._init_structlog()

    def __str__(self) -> str:
        """Return short debug representation."""
        registered = len(self._regs)
        dev = sys.stderr.isatty()
        return f"<{self.__class__.__name__} dev:{dev}; registered:{registered}>"

    # ---------------------------------------------------------------- private
    @property
    def _renderer(self) -> str:
        if sys.stderr.isatty() or os.environ.get("MODE_DEV") or self._developer_mode:
            return self.CONSOLE_HANDLER
        return self.JSON_HANDLER

    @staticmethod
    def _timestamper() -> structlog.processors.TimeStamper:
        return structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    def _pre(self, *, extended: bool = False) -> list[Any]:
        base = [
            self._timestamper(),
            structlog.processors.EventRenamer("event" if self._developer_mode else "_msg"),
            structlog.stdlib.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                },
            ),
            add_caller_details,
        ]
        if not extended:
            return base

        return [
            *[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.filter_by_level,
            ],
            *base,
            *[
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
        ]

    def _init_structlog(self) -> None:
        handlers_cfg = {
            self.CONSOLE_HANDLER: {
                "class": "logging.StreamHandler",
                "formatter": self.CONSOLE_HANDLER,
            },
            self.JSON_HANDLER: {
                "class": "logging.StreamHandler",
                "formatter": self.JSON_HANDLER,
            },
        }

        formatters = {
            self.JSON_HANDLER: {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": self._pre(),
            },
            self.CONSOLE_HANDLER: {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
                "foreign_pre_chain": self._pre(),
            },
        }

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": formatters,
                "handlers": handlers_cfg,
                "loggers": {
                    reg.name: {
                        "handlers": [self._renderer],
                        "level": reg.level.value,
                        "propagate": reg.propagate,
                    }
                    for reg in self._regs
                },
            },
        )

        structlog.configure(
            processors=self._pre(extended=True),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


class InitLoggers:
    """Контейнер проектных логгеров."""

    def __init__(self, *, developer_mode: bool = False) -> None:
        self._loggers = {name: getattr(self, name) for name in dir(self) if isinstance(getattr(self, name), LoggerReg)}
        if not self._loggers:
            _msg_no_loggers = "Ни одного логгера не определено в дочернем классе"
            raise LoggerError(_msg_no_loggers)

        self._setup = SetupLogger(list(self._loggers.values()), developer_mode=developer_mode)
        self._instances = {reg.name: structlog.get_logger(reg.name) for reg in self._loggers.values()}

    def __getattr__(self, name: str):
        """Вернуть ранее созданный логгер по имени."""
        try:
            return self._instances[name]
        except KeyError as exc:  # pragma: no cover — должно ловиться тестами
            registered = ", ".join(self._instances)
            _msg = f"Logger '{name}' not found. Available: {registered}"
            raise LoggerNotFoundError(_msg) from exc
