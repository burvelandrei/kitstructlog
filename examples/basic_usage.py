import structlog
from kitstructlog import InitLoggers, LoggerReg


class Loggers(InitLoggers):
    app = LoggerReg(name="APP", level=LoggerReg.Level.INFO)
    db = LoggerReg(name="DATABASE", level=LoggerReg.Level.DEBUG)


# Initialize the logging system
loggers = Loggers(developer_mode=True)

# Use a logger
logger = structlog.getLogger(Loggers.app.name)
logger.info("Application started", version="1.0.0")
