from fastapi import APIRouter
import logging

from app.schemas.blog import SearchQuery
from app.schemas.ret_result import ResponseResult
from app.services.rag_service import rag_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search")
async def search_blog(query: SearchQuery):
    """
    Search blog posts using RAG.
    """
    try:
        if query.test:
            answer = rag_service.query_test(query.query)
        elif query.referer:
            answer = rag_service.query_with_sources(query.query)
        else:
            answer = rag_service.query(query.query)
        return await ResponseResult.success(
            result_code=200,
            result_msg="Blog search successful",
            data={"answer": answer}
        )
    except Exception as e:
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"Blog search error: {str(e)}"
        )


@router.post("/index")
async def index_blog_posts():
    """
    Trigger re-indexing of blog posts.
    """
    try:
        rag_service.load_and_index()
        return await ResponseResult.success(
            result_code=200,
            result_msg="Blog posts indexed successfully"
        )
    except Exception as e:
        logger.exception(f"Error indexing blog posts: {e}", exc_info=True)
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"Blog indexing error: {str(e)}"
        )
