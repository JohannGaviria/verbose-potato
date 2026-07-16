"""This module contains the structlog logger outbound adapter class."""

import structlog

from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class StructlogLoggerOutboundAdapter(LoggerOutboundPort):
    """Concrete logger adapter backed by structlog.

    Wraps a structlog bound-logger so every call is routed through the
    processors configured in ``StructlogConfigureLogging.configure()``,
    producing JSON-structured output in production and pretty-printed
    output in debug mode — with zero changes to call-sites.

    Usage::

        logger = StructlogLoggerOutboundAdapter(__name__)
        logger.info("user_created", user_id=str(user.id))
    """

    def __init__(self, name: str) -> None:
        """Initialize the StructlogLoggerOutboundAdapter.

        Args:
            name (str): Typically ``__name__`` of the calling module,
                used as the ``logger`` field in structured log output.
        """
        self._logger = structlog.get_logger(name)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log a debug-level message.

        Args:
            message (str): The log message (mapped to structlog's ``event`` field).
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        self._logger.debug(event=message, **kwargs)

    def info(self, message: str, **kwargs: object) -> None:
        """Log an info-level message.

        Args:
            message (str): The log message (mapped to structlog's ``event`` field).
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        self._logger.info(event=message, **kwargs)

    def warning(self, message: str, **kwargs: object) -> None:
        """Log a warning-level message.

        Args:
            message (str): The log message (mapped to structlog's ``event`` field).
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        self._logger.warning(event=message, **kwargs)

    def error(self, message: str, **kwargs: object) -> None:
        """Log an error-level message.

        Args:
            message (str): The log message (mapped to structlog's ``event`` field).
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        self._logger.error(event=message, **kwargs)

    def critical(self, message: str, **kwargs: object) -> None:
        """Log a critical-level message.

        Args:
            message (str): The log message (mapped to structlog's ``event`` field).
            **kwargs: Arbitrary key-value pairs added as structured fields.
        """
        self._logger.critical(event=message, **kwargs)
