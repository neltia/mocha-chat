# /app/schemas/ret_result.py
from typing import Optional, Any, Dict
from enum import Enum
import logging
from pydantic import BaseModel, Field
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.responses import ORJSONResponse


logger = logging.getLogger(__name__)


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ResultMessageEnum(str, Enum):
    """API 응답 메시지 정의 (공통 구간)"""
    # 200
    SUCCESS = "요청이 처리되었습니다."
    FILE_UPLOAD_SUCCESS = "파일이 업로드되었습니다."

    # 202
    NOW_ANALYZING = "분석 중입니다."

    # 400
    BAD_REQUEST = "잘못된 요청입니다."
    FILE_NOT_FOUND = "파일이 첨부되지 않았습니다."
    FILE_NOT_PERMIT = "허용되지 않는 파일 형식입니다."
    FILE_TOO_LARGE = "파일의 크기가 허용량을 초과합니다."

    # 401
    AUTHENTICATION_REQUIRE = "인증 정보가 누락되었거나 유효하지 않습니다."
    # 403
    NO_PERMISSION = "요청에 대한 권한이 없습니다."

    # 404
    NOT_FOUND = "해당하는 결과가 없습니다."

    # 500
    INTERNAL_ERROR = "요청 처리 중 서버 오류가 발생했습니다."


# API 공통 응답 규격 정의
class ResponseResult(BaseModel):
    status: ResponseStatus
    result_code: int
    result_msg: Optional[str] = Field(default=None)
    data: Optional[Dict[str, Any]] = None

    @classmethod
    async def success(
        cls,
        result_code: int = HTTP_200_OK,
        result_msg: str = ResultMessageEnum.SUCCESS,
        data: Optional[Dict[str, Any]] = None,
    ) -> ORJSONResponse:
        return retResponseResult(
            cls(status=ResponseStatus.SUCCESS, result_code=result_code, result_msg=result_msg, data=data)
        )

    @classmethod
    async def error(
        cls,
        result_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        result_msg: str = ResultMessageEnum.INTERNAL_ERROR,
        data: Optional[Dict[str, Any]] = None,
    ) -> ORJSONResponse:
        return retResponseResult(
            cls(status=ResponseStatus.ERROR, result_code=result_code, result_msg=result_msg, data=data)
        )


# result_code와 status를 일치시키고, None Exclude 설정을 적용한 return
def retResponseResult(result: ResponseResult) -> ORJSONResponse:
    status_code = result.result_code

    return ORJSONResponse(
        status_code=status_code,
        content=result.model_dump(exclude_unset=True, exclude_none=True)
    )
