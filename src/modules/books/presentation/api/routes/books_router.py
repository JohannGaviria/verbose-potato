"""This module contains the books routers."""

from fastapi import APIRouter

from src.modules.books.presentation.api.routes import (
    delete_book_router,
    get_book_catalog_router,
    registration_new_book_router,
    update_book_router,
)

router = APIRouter(
    prefix="/api/v1/books",
    tags=["Books"],
)


router.include_router(registration_new_book_router.router)
router.include_router(update_book_router.router)
router.include_router(delete_book_router.router)
router.include_router(get_book_catalog_router.router)
