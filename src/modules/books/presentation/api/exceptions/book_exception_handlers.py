"""This module contains the book exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.books.domain.exceptions.book_exception import (
    BookRepositoryException,
    ISBNAlreadyRegisteredException,
    InvalidAuthorException,
    InvalidBookCatalogQueryException,
    InvalidIsbnException,
    InvalidPublishedYearException,
    InvalidTitleException,
    InvalidTotalCopiesException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def book_exception_handlers(app: FastAPI) -> None:
    """Register the book exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidTitleException)
    async def invalid_title_exception_handler(
        request: Request, exc: InvalidTitleException
    ) -> JSONResponse:
        """Invalid title exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidTitleException): The InvalidTitleException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid title exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            title=exc.title,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"title": exc.title},
                ),
            ),
        )

    @app.exception_handler(InvalidAuthorException)
    async def invalid_author_exception_handler(
        request: Request, exc: InvalidAuthorException
    ) -> JSONResponse:
        """Invalid author exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidAuthorException): The InvalidAuthorException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid author exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            author=exc.author,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"author": exc.author},
                ),
            ),
        )

    @app.exception_handler(InvalidPublishedYearException)
    async def invalid_published_year_exception_handler(
        request: Request, exc: InvalidPublishedYearException
    ) -> JSONResponse:
        """Invalid published year exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidPublishedYearException): The InvalidPublishedYearException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid published year exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            published_year=exc.published_year,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"published_year": exc.published_year},
                ),
            ),
        )

    @app.exception_handler(InvalidTotalCopiesException)
    async def invalid_total_copies_exception_handler(
        request: Request, exc: InvalidTotalCopiesException
    ) -> JSONResponse:
        """Invalid total copies exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidTotalCopiesException): The InvalidTotalCopiesException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid total copies exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            total_copies=exc.total_copies,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"total_copies": exc.total_copies},
                ),
            ),
        )

    @app.exception_handler(InvalidIsbnException)
    async def invalid_isbn_exception_handler(
        request: Request, exc: InvalidIsbnException
    ) -> JSONResponse:
        """Invalid isbn exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidIsbnException): The InvalidIsbnException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid isbn exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            isbn=exc.isbn,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"isbn": exc.isbn},
                ),
            ),
        )

    @app.exception_handler(ISBNAlreadyRegisteredException)
    async def isbn_already_registered_exception_handler(
        request: Request, exc: ISBNAlreadyRegisteredException
    ) -> JSONResponse:
        """ISBN already registered exception handler.

        Args:
            request (Request): The request object.
            exc (ISBNAlreadyRegisteredException): The ISBNAlreadyRegisteredException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "ISBN already registered exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(BookRepositoryException)
    async def book_repository_exception_handler(
        request: Request, exc: BookRepositoryException
    ) -> JSONResponse:
        """Book repository exception handler.

        Args:
            request (Request): The request object.
            exc (BookRepositoryException): The BookRepositoryException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Book repository exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidBookCatalogQueryException)
    async def invalid_book_catalog_exception_handler(
        request: Request, exc: InvalidBookCatalogQueryException
    ) -> JSONResponse:
        """Invalid book catalog exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidBookCatalogQueryException): The InvalidBookCatalogQueryException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid book catalog exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
            query=exc.query,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"query": exc.query},
                )
            ),
        )
