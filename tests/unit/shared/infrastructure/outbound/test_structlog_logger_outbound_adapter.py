from typing import Any

import structlog
from structlog.testing import capture_logs

from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort
from src.shared.infrastructure.outbound.structlog_logger_outbound_adapter import (
    StructlogLoggerOutboundAdapter,
)


class TestStructlogLoggerOutboundAdapter:
    def test_should_implement_logger_outbound_port_when_created(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        assert isinstance(logger, LoggerOutboundPort)

    def test_should_log_debug_event_when_debug_is_called(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        with capture_logs() as logs:
            logger.debug("something happened", user_id="123")

        assert len(logs) == 1
        assert logs[0]["event"] == "something happened"
        assert logs[0]["user_id"] == "123"
        assert logs[0]["log_level"] == "debug"

    def test_should_log_info_event_when_info_is_called(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        with capture_logs() as logs:
            logger.info("user created", user_id="123")

        assert len(logs) == 1
        assert logs[0]["event"] == "user created"
        assert logs[0]["user_id"] == "123"
        assert logs[0]["log_level"] == "info"

    def test_should_log_warning_event_when_warning_is_called(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        with capture_logs() as logs:
            logger.warning("low disk space", disk="c:")

        assert len(logs) == 1
        assert logs[0]["event"] == "low disk space"
        assert logs[0]["disk"] == "c:"
        assert logs[0]["log_level"] == "warning"

    def test_should_log_error_event_when_error_is_called(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        with capture_logs() as logs:
            logger.error("operation failed", reason="timeout")

        assert len(logs) == 1
        assert logs[0]["event"] == "operation failed"
        assert logs[0]["reason"] == "timeout"
        assert logs[0]["log_level"] == "error"

    def test_should_log_critical_event_when_critical_is_called(self) -> None:
        logger = StructlogLoggerOutboundAdapter("test.module")

        with capture_logs() as logs:
            logger.critical("service down", service="cache")

        assert len(logs) == 1
        assert logs[0]["event"] == "service down"
        assert logs[0]["service"] == "cache"
        assert logs[0]["log_level"] == "critical"

    def test_should_bind_module_name_when_created(self) -> None:
        logger = StructlogLoggerOutboundAdapter("my.module.name")

        assert logger._logger is not None

    def test_should_use_structlog_get_logger_when_created(
        self, monkeypatch: Any
    ) -> None:
        captured_names = []
        original_get_logger = structlog.get_logger

        def fake_get_logger(name: str) -> Any:
            captured_names.append(name)
            return original_get_logger(name)

        monkeypatch.setattr(structlog, "get_logger", fake_get_logger)

        StructlogLoggerOutboundAdapter("my.module.name")

        assert captured_names == ["my.module.name"]
