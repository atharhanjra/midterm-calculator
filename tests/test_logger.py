"""Tests for the Logger class (app/logger.py)."""

import logging

import pytest

from app.logger import Logger


@pytest.mark.parametrize("log_method, expected_level", [
    (Logger.info, logging.INFO),
    (Logger.warning, logging.WARNING),
    (Logger.error, logging.ERROR),
])
def test_logger_levels(caplog, log_method, expected_level):
    """Each Logger method records the message at the right level."""
    with caplog.at_level(logging.INFO):
        log_method("test message")
    assert caplog.records[-1].levelno == expected_level
    assert caplog.records[-1].getMessage() == "test message"