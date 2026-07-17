from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_outbound_adapter import (
    StructlogLoggerOutboundAdapter,
)


class TestStructlogLoggerFactoryOutboundAdapter:
    def test_should_implement_logger_factory_outbound_port_when_created(self) -> None:
        factory = StructlogLoggerFactoryOutboundAdapter()

        assert isinstance(factory, LoggerFactoryOutboundPort)

    def test_should_return_logger_outbound_port_when_get_logger_is_called(
        self,
    ) -> None:
        factory = StructlogLoggerFactoryOutboundAdapter()

        logger = factory.get_logger("my.module")

        assert isinstance(logger, LoggerOutboundPort)

    def test_should_return_structlog_logger_outbound_adapter_when_get_logger_is_called(
        self,
    ) -> None:
        factory = StructlogLoggerFactoryOutboundAdapter()

        logger = factory.get_logger("my.module")

        assert isinstance(logger, StructlogLoggerOutboundAdapter)

    def test_should_return_new_logger_instance_when_get_logger_is_called_twice(
        self,
    ) -> None:
        factory = StructlogLoggerFactoryOutboundAdapter()

        first_logger = factory.get_logger("my.module")
        second_logger = factory.get_logger("my.module")

        assert first_logger is not second_logger
