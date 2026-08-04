"""This module contains the auth routers."""

from fastapi import APIRouter

from src.modules.auth.presentation.api.routes import (
    login_router,
    new_user_registration_router,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)


router.include_router(new_user_registration_router.router)
router.include_router(login_router.router)
