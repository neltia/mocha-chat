# app.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Mocha Chat API", version="0.0.1",
    docs_url=None, redoc_url=None
)


@app.get("/")
async def redirect_to_vercel():
    """
    루트 경로 접근 시 Vercel로 리다이렉트, /api/v1/* 엔드포인트는 별도 처리
    mochachat.app:443 -> mochachat.vercel.app
    """
    return RedirectResponse(
        url=os.getenv("REDIRECT_URL"),
        status_code=301  # Permanent Redirect
    )
