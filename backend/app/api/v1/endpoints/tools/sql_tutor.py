from fastapi import APIRouter
import logging

from app.core.groq_client import call_groq_with_yaml
from app.utils.prompt_loader import get_prompt, render_prompt
from app.schemas.sql_tutor import TextInput, SQLInput, ScenarioInput
from app.utils.json_utils import parse_json_response, validate_json_structure, remove_emojis
from app.schemas.ret_result import ResponseResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/result")
async def get_sql_result(data: SQLInput):
    """SQL 쿼리 실행 결과를 시뮬레이션합니다."""
    try:
        prompt_data = get_prompt("sql_tutor_prompts.yaml", "sql_execute")
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        user_prompt = render_prompt(user_template, {
            "query": data.query,
            "database_type": data.database_type,
            "context": data.context
        })

        result = call_groq_with_yaml(system_prompt, user_prompt)
        parsed_result = parse_json_response(result)

        return await ResponseResult.success(
            result_code=200,
            result_msg="SQL simulation successful",
            data={
                "query": data.query,
                "database_type": data.database_type,
                "execution_result": parsed_result
            }
        )

    except Exception as e:
        logger.exception(f"SQL 실행 시뮬레이션 오류: {e}")
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"SQL simulation error: {str(e)}",
            data={
                "query": data.query,
                "database_type": data.database_type
            }
        )


@router.post("/convert")
async def convert_nl_to_sql(data: TextInput):
    """자연어를 SQL 쿼리로 변환합니다."""
    try:
        prompt_data = get_prompt("sql_tutor_prompts.yaml", "sql_convert")
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        user_prompt = render_prompt(user_template, {
            "natural_language_query": data.description,
            "database_type": data.database_type,
            "context": data.context
        })

        # LLM 호출
        result = call_groq_with_yaml(system_prompt, user_prompt)
        logger.info(f"LLM 원본 응답 타입: {type(result)}")
        logger.info(f"LLM 원본 응답 내용: {str(result)[:200]}...")

        # JSON 파싱
        parsed_result = parse_json_response(result)
        logger.info(f"파싱된 결과 타입: {type(parsed_result)}")

        # 필수 필드 검증
        required_fields = ["sql_query", "explanation", "complexity", "estimated_performance", "key_concepts", "security_notes"]
        validated_result = validate_json_structure(parsed_result, required_fields)
        # 응답 구조 표준화
        response = {"input": data.description, "database_type": data.database_type, "context": data.context}
        response.update(validated_result)

        return await ResponseResult.success(
            result_code=200,
            result_msg="Natural language to SQL conversion successful",
            data={
                "query": response.get("input"),
                "database_type": response.get("database_type"),
                "execution_result": {
                    "sql_query": response.get("sql_query"),
                    "explanation": response.get("explanation"),
                    "complexity": response.get("complexity"),
                    "estimated_performance": response.get("estimated_performance"),
                    "key_concepts": response.get("key_concepts"),
                    "security_notes": response.get("security_notes")
                }
            }
        )

    except Exception as e:
        logger.exception(f"natural lang to SQL convert Error: {e}", exc_info=True)
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"Error converting natural language to SQL: {str(e)}",
            data={
                "description": data.description,
                "database_type": data.database_type
            }
        )


@router.post("/optimize")
async def optimize_sql(data: SQLInput):
    """SQL 쿼리를 최적화합니다."""
    try:
        prompt_data = get_prompt("sql_tutor_prompts.yaml", "sql_optimize")
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        user_prompt = render_prompt(user_template, {
            "query": data.query,
            "database_type": data.database_type,
            "data_scale": "1k,10k,100k,1m",
            "performance_requirements": "balanced"
        })

        result = call_groq_with_yaml(system_prompt, user_prompt)
        parsed_result = parse_json_response(result)

        return await ResponseResult.success(
            result_code=200,
            result_msg="Natural language to SQL conversion successful",
            data={
                "query": data.query,
                "database_type": data.database_type,
                "data_scale": "1k,10k,100k,1m",
                "performance_requirements": "balanced",
                "execution_result": {
                    "optimized_query": parsed_result.get("optimized_query"),
                    "optimization_explanation": parsed_result.get("optimization_explanation"),
                    "expected_improvements": parsed_result.get("expected_improvements"),
                    "additional_recommendations": parsed_result.get("additional_recommendations")
                }
            }
        )

    except Exception as e:
        logger.exception(f"SQL 최적화 오류: {e}", exc_info=True)
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"Error converting natural language to SQL: {str(e)}",
            data={
                "query": data.query,
                "database_type": data.database_type
            }
        )


@router.post("/schema")
async def design_schema(data: ScenarioInput):
    """비즈니스 요구사항에 따라 데이터베이스 스키마를 설계합니다."""
    try:
        prompt_data = get_prompt("sql_tutor_prompts.yaml", "schema_design")
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        user_prompt = render_prompt(user_template, {
            "business_requirements": data.scenario,
            "database_type": data.database_type,
            "expected_scale": data.expected_scale,
            "performance_requirements": data.performance_requirements
        })

        result = call_groq_with_yaml(system_prompt, user_prompt)

        # 스키마 설계는 DBML 형식이므로 JSON 파싱하지 않음
        cleaned_result = remove_emojis(str(result))

        return await ResponseResult.success(
            result_code=200,
            result_msg="Natural language to SQL conversion successful",
            data={
                "business_requirements": data.scenario,
                "database_type": data.database_type,
                "expected_scale": data.expected_scale,
                "scenario": data.scenario,
                "performance_requirements": data.performance_requirements,
                "execution_result": {
                    "schema_design": cleaned_result,
                }
            }
        )

    except Exception as e:
        logger.exception(f"스키마 설계 오류: {e}", exc_info=True)
        return await ResponseResult.error(
            result_code=500,
            result_msg=f"Shema design error: {str(e)}",
            data={
                "business_requirements": data.scenario,
                "database_type": data.database_type
            }
        )
