"""This module contains the structlog logger factory outbound adapter class."""

from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort
from src.shared.infrastructure.outbound.structlog_logger_outbound_adapter import (
    StructlogLoggerOutboundAdapter,
)


class StructlogLoggerFactoryOutboundAdapter(LoggerFactoryOutboundPort):
    """Concrete logger factory backed by structlog.

    Returns a :class:`StructlogLoggerAdapter` instance bound to the
    supplied module name, inheriting all processors configured in
    ``StructlogConfigureLogging.configure()``.

    Usage::

        factory = StructlogLoggerFactory()
        use_case = CreateFirstAdminUseCase(..., logger_factory=factory)
    """

    def get_logger(self, name: str) -> LoggerOutboundPort:
        """Create a structlog-backed logger for the given module name.

        Args:
            name (str): Typically ``__name__`` of the calling module.

        Returns:
            LoggerPort: A :class:`StructlogLoggerAdapter` tagged with ``name``.
        """
        return StructlogLoggerOutboundAdapter(name)
