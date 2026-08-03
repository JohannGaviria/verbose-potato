"""This module contains the auth routers."""

from fastapi import APIRouter

from src.modules.auth.presentation.api.routes import new_user_registration_router

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


router.include_router(new_user_registration_router.router)
