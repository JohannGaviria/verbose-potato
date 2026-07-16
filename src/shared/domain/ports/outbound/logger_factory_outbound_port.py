"""This module contains the logger factory outbound port class."""

from abc import ABC, abstractmethod

from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class LoggerFactoryOutboundPort(ABC):
    """Interface for a logger factory.

    Decouples every application layer from the concrete logging backend.
    Consumers call ``get_logger(__name__)`` so the resulting logger is
    always tagged with the module that owns the log call, regardless of
    where the factory instance was created.

    Usage::

        class MyUseCase:
            def __init__(self, logger_factory: LoggerFactoryPort) -> None:
                self._logger = logger_factory.get_logger(__name__)
    """

    @abstractmethod
    def get_logger(self, name: str) -> LoggerOutboundPort:
        """Create and return a logger bound to the given module name.

        Args:
            name (str): Typically ``__name__`` of the calling module.

        Returns:
            LoggerOutboundPort: A logger instance tagged with name.
        """
        pass
