import structlog
from kitstructlog import InitLoggers, LoggerReg


class Loggers(InitLoggers):
    app = LoggerReg(name="APP", level=LoggerReg.Level.INFO)
    access = LoggerReg(name="ACCESS", level=LoggerReg.Level.INFO)


# developer_mode=False => включаем JSON формат
loggers = Loggers(developer_mode=False)

logger = structlog.getLogger(Loggers.access.name)
logger.info("Запрос обработан", status=200, path="/login")

# Если вы видете:
# "_msg": "\u0417\u0430\u043f\u0440\u043e\u0441 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d"
# Это нормально
