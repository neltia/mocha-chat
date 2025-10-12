from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.schemas.ret_result import ResponseResult
from app.schemas.ret_result import retResponseResult


def setup_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """ Pydantic 요청 유효성 검사 실패 시 처리하는 핸들러 """
        # 에러 리스트 중 첫 번째만 사용
        first_err = exc.errors()[0]
        field = first_err.get("loc", [])[-1]
        message = first_err.get("msg", "")
        combined = f"{field}: {message}"

        # result_code는 400, result_msg에 조합된 메시지
        resp = await ResponseResult.error(
            result_code=400,
            result_msg=combined,
            data=None
        )
        if isinstance(resp, ORJSONResponse):
            return resp
        return retResponseResult(resp)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """ FastAPI HTTPException 처리 핸들러 """
        # exc.status_code 를 그대로 쓰고, 기본 메시지는 exc.detail
        resp = await ResponseResult.error(
            result_code=exc.status_code,
            result_msg=str(exc.detail),
            data=None
        )
        if isinstance(resp, ORJSONResponse):
            return resp
        return retResponseResult(resp)

    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc):
        """ 404 Not Found 처리 핸들러 """
        resp = await ResponseResult.error(
            result_code=404,
            result_msg="Resource not found",
            data=None
        )
        if isinstance(resp, ORJSONResponse):
            return resp
        return retResponseResult(resp)
