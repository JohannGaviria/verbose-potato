"""This module contains the loans routers."""

from fastapi import APIRouter

from src.modules.loans.presentation.api.routes import (
    get_loan_catalog_router,
    get_my_loans_router,
    recording_loan_router,
    returning_loan_router,
)

router = APIRouter(
    prefix="/api/v1/loans",
    tags=["Loans"],
)


router.include_router(recording_loan_router.router)
router.include_router(returning_loan_router.router)
router.include_router(get_my_loans_router.router)
router.include_router(get_loan_catalog_router.router)
