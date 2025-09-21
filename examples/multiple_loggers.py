import structlog
from kitstructlog import InitLoggers, LoggerReg


class Loggers(InitLoggers):
    auth = LoggerReg(name="AUTH", level=LoggerReg.Level.DEBUG)
    router = LoggerReg(name="ROUTER", level=LoggerReg.Level.INFO)
    utils = LoggerReg(name="UTILS", level=LoggerReg.Level.DEBUG)


loggers = Loggers(developer_mode=True)

# В коде используем конкретный логгер
auth_logger = structlog.getLogger(Loggers.auth.name)
auth_logger.debug("Проверка токена", token="abc123")

router_logger = structlog.getLogger(Loggers.router.name)
router_logger.info("Новый запрос", path="/api/v1/resource")

# В режиме разработки это не заметно, но в JSON типе с `developer_mode=False` там указывается Logger Name
