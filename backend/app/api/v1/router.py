# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints.tools import sql_tutor
from app.api.v1.endpoints.blog import blog

api_router = APIRouter()

# tools router
api_router.include_router(sql_tutor.router, prefix="/tools/sql", tags=["SQL Tutor"])

# blog router
api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
