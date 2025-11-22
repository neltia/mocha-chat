from pydantic import BaseModel, Field
from typing import Optional


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="검색할 질문")
    referer: bool = True
    test: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "query": "FastAPI에서 의존성 주입은 어떻게 하나요?"
            }
        }
