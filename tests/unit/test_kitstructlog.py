import pytest
from hypothesis import given, strategies as st

from kitstructlog.main import (
    LoggerError,
    LoggerNotFoundError,
    LoggerReg,
    SetupLogger,
    InitLoggers,
)


def test_logger_error_inheritance():
    assert issubclass(LoggerNotFoundError, LoggerError)


@given(level=st.sampled_from(list(LoggerReg.Level)))
def test_logger_reg_levels(level):
    reg = LoggerReg(name="TEST", level=level)
    assert reg.name == "TEST"
    assert reg.level == level


def test_setup_logger_str_and_renderer(monkeypatch):
    reg = [LoggerReg(name="TEST", level=LoggerReg.Level.DEBUG)]

    s1 = SetupLogger(name_registration=reg, developer_mode=True)
    assert "registered" in str(s1)
    assert s1._renderer == s1.CONSOLE_HANDLER

    monkeypatch.setenv("MODE_DEV", "1")
    s2 = SetupLogger(name_registration=reg, developer_mode=False)
    assert s2._renderer == s2.CONSOLE_HANDLER

    monkeypatch.delenv("MODE_DEV", raising=False)
    s3 = SetupLogger(name_registration=reg, developer_mode=False)
    assert s3._renderer == s3.JSON_HANDLER


def test_timestamper_returns_callable():
    reg = [LoggerReg(name="TEST")]
    s = SetupLogger(name_registration=reg, developer_mode=True)
    ts = s._timestamper()
    assert callable(ts)


def test_preprocessors_extended_and_basic():
    reg = [LoggerReg(name="TEST")]
    s = SetupLogger(name_registration=reg, developer_mode=True)
    base = s._pre()
    ext = s._pre(extended=True)

    assert len(ext) > len(base)
    assert any(getattr(call, "__name__", "") == "merge_contextvars" for call in ext)


def test_init_loggers_no_loggers_defined():
    class Empty(InitLoggers):
        pass

    with pytest.raises(LoggerError):
        Empty()


def test_init_loggers_logger_not_found():
    class MyLoggers(InitLoggers):
        app = LoggerReg(name="APP")

    loggers = MyLoggers(developer_mode=True)
    with pytest.raises(LoggerNotFoundError):
        _ = loggers.not_exist
