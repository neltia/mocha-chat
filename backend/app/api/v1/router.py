# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints.tools import sql_tutor

api_router = APIRouter()

# tools router
api_router.include_router(sql_tutor.router, prefix="/tools/sql", tags=["SQL Tutor"])
