import structlog
from kitstructlog import InitLoggers, LoggerReg


class Loggers(InitLoggers):
    app = LoggerReg(name="APP", level=LoggerReg.Level.INFO)
    db = LoggerReg(name="DATABASE", level=LoggerReg.Level.DEBUG)


# Инициализируем систему логирования
loggers = Loggers(developer_mode=True)

# Используем логгер
logger = structlog.getLogger(Loggers.app.name)
logger.info("Приложение запущено", version="1.0.0")
