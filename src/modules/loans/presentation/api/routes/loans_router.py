"""This module contains the loans routers."""

from fastapi import APIRouter

from src.modules.loans.presentation.api.routes import recording_loan_router

router = APIRouter(
    prefix="/api/v1/loans",
    tags=["Loans"],
)


router.include_router(recording_loan_router.router)
