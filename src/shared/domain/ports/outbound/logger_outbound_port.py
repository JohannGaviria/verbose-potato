"""This module contains the logger outbound port class."""

from abc import ABC, abstractmethod


class LoggerOutboundPort(ABC):
    """Interface for structured logging across all application layers.

    Implementations must delegate to the configured logging backend
    so that all layers remain decoupled from the concrete logging library.
    """

    @abstractmethod
    def debug(self, message: str, **kwargs: object) -> None:
        """Log a debug-level message.

        Args:
            message (str): The log message.
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        pass

    @abstractmethod
    def info(self, message: str, **kwargs: object) -> None:
        """Log an info-level message.

        Args:
            message (str): The log message.
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: object) -> None:
        """Log a warning-level message.

        Args:
            message (str): The log message.
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        pass

    @abstractmethod
    def error(self, message: str, **kwargs: object) -> None:
        """Log an error-level message.

        Args:
            message (str): The log message.
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs: object) -> None:
        """Log a critical-level message.

        Args:
            message (str): The log message.
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        pass
