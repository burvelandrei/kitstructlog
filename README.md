# kitstructlog

[![PyPI version](https://badge.fury.io/py/kitstructlog.svg)](https://pypi.org/project/kitstructlog/)
[![Python Versions](https://img.shields.io/pypi/pyversions/kitstructlog.svg)](https://pypi.org/project/kitstructlog/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A superstructure over [structlog](https://www.structlog.org/en/stable/) that simplifies the configuration and use of structured logging in Python.

---

## ✨ Features

- Simple declaration of project loggers via `dataclass`-like syntax
- Automatic setup of `logging` + `structlog`
- Developer-friendly **console output** or **JSON structured logs** (depending on mode)
- Extensible processors chain (timestamps, stack info, caller details, etc.)
- Support for multiple named loggers in one place

---

## 📦 Installation

```bash
pip install kitstructlog
```

---

## 🚀 Quick Start

### Basic usage

```python
import structlog
from kitstructlog import InitLoggers, LoggerReg

class Loggers(InitLoggers):
    app = LoggerReg(name="APP", level=LoggerReg.Level.INFO)
    db = LoggerReg(name="DATABASE", level=LoggerReg.Level.DEBUG)

# Initialize
loggers = Loggers(developer_mode=True)

# Use logger
logger = structlog.getLogger(Loggers.app.name)
logger.info("Application started", version="1.0.0")
```

---

### JSON logging

```python
import structlog
from kitstructlog import InitLoggers, LoggerReg

class Loggers(InitLoggers):
    app = LoggerReg(name="APP", level=LoggerReg.Level.INFO)
    access = LoggerReg(name="ACCESS", level=LoggerReg.Level.INFO)

# developer_mode=False => JSON output
loggers = Loggers(developer_mode=False)

logger = structlog.getLogger(Loggers.access.name)
logger.info("Request handled", status=200, path="/login")
```

Example JSON output:

```json
{
  "timestamp": "2025-09-21 03:09:46",
  "level": "info",
  "logger": "json_logging:logger:14",
  "_msg": "Request handled",
  "status": 200,
  "path": "/login"
}
```

---

### Multiple loggers

```python
import structlog
from kitstructlog import InitLoggers, LoggerReg

class Loggers(InitLoggers):
    auth = LoggerReg(name="AUTH", level=LoggerReg.Level.DEBUG)
    router = LoggerReg(name="ROUTER", level=LoggerReg.Level.INFO)
    utils = LoggerReg(name="UTILS", level=LoggerReg.Level.DEBUG)

loggers = Loggers(developer_mode=True)

auth_logger = structlog.getLogger(Loggers.auth.name)
auth_logger.debug("Checking token", token="abc123")

router_logger = structlog.getLogger(Loggers.router.name)
router_logger.info("New request", path="/api/v1/resource")
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.