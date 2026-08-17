"""This module contains the books routers."""

from fastapi import APIRouter

from src.modules.books.presentation.api.routes import registration_new_book_router

router = APIRouter(
    prefix="/api/v1/books",
    tags=["Books"],
)


router.include_router(registration_new_book_router.router)
