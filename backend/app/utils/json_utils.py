from typing import Any, Dict, Union
import json
import re
import logging


logger = logging.getLogger(__name__)


def remove_emojis(text: str) -> str:
    """
    텍스트에서 모든 이모지와 특수 유니코드 문자를 제거합니다.
    """
    # 이모지 및 특수 유니코드 문자 패턴
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F170-\U0001F251"  # enclosed alphanumeric supplement
        "]+",
        flags=re.UNICODE
    )

    # 숫자 이모지 패턴 (1️⃣, 2️⃣ 등)
    number_emoji_pattern = re.compile(r'[\u0031-\u0039]\uFE0F?\u20E3')

    # 기타 특수 문자들
    special_chars_pattern = re.compile(r'[⚡🔥💡📊🎯✅❌⭐🚀📈📉💰🔧⚙️🛠️🎨🔍📝💻🖥️📱⌨️🖱️💾🗄️📂📁🔒🔓🔑🛡️⚠️❗❓💬💭🗨️💡🔔📢📣]')

    # 모든 패턴 적용
    text = emoji_pattern.sub('', text)
    text = number_emoji_pattern.sub('', text)
    text = special_chars_pattern.sub('', text)

    return text


def clean_json_string(text: str) -> str:
    """
    JSON 문자열에서 문제가 될 수 있는 문자들을 정리합니다.
    """
    # 이모지 제거
    text = remove_emojis(text)

    # 불필요한 백슬래시와 newline 제거
    text = re.sub(r'\\n', ' ', text)
    text = re.sub(r'\\\\', '\\', text)

    # 연속된 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)

    # 앞뒤 공백 제거
    text = text.strip()

    return text


def safe_json_loads(text: str) -> Union[Dict[str, Any], str]:
    """
    안전한 JSON 파싱을 시도합니다. 실패 시 원본 텍스트를 반환합니다.
    """
    try:
        # 입력이 이미 딕셔너리인 경우 그대로 반환
        if isinstance(text, dict):
            return text

        # 문자열이 아닌 경우 문자열로 변환
        if not isinstance(text, str):
            text = str(text)

        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON 파싱 실패: {e}")
        return text


def parse_json_response(result: Union[str, dict]) -> Dict[str, Any]:
    """
    LLM 응답에서 JSON을 추출하고 파싱합니다.
    마크다운 코드 블록이나 여분의 텍스트, 이모지를 제거합니다.
    """
    try:
        # 입력이 이미 딕셔너리인 경우
        if isinstance(result, dict):
            return clean_dict_values(result)

        # 문자열이 아닌 경우 문자열로 변환
        if not isinstance(result, str):
            result = str(result)

        # 먼저 이모지와 특수 문자 제거
        result = remove_emojis(result)

        # 마크다운 코드 블록 제거
        if "```json" in result:
            start = result.find("```json") + 7
            end = result.find("```", start)
            if end != -1:
                result = result[start:end].strip()
        elif "```" in result:
            # 일반 코드 블록도 처리
            start = result.find("```") + 3
            end = result.find("```", start)
            if end != -1:
                result = result[start:end].strip()

        # JSON 부분만 추출 (중괄호 기준)
        json_start = result.find('{')
        json_end = result.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            result = result[json_start:json_end + 1]

        # JSON 문자열 정리
        result = clean_json_string(result)

        # JSON 파싱 시도
        parsed_data = safe_json_loads(result)

        # 파싱이 성공하고 딕셔너리인 경우 값들 정리
        if isinstance(parsed_data, dict):
            return clean_dict_values(parsed_data)
        else:
            # 파싱 실패 시 원본 텍스트와 함께 오류 정보 반환
            return {
                "success": False,
                "raw_response": remove_emojis(str(parsed_data)),
                "parse_error": "JSON 파싱에 실패했습니다",
                "error_message": "LLM 응답을 JSON으로 파싱할 수 없습니다"
            }

    except Exception as e:
        logger.error(f"응답 처리 중 예상치 못한 오류: {e}")
        return {
            "success": False,
            "error_message": f"응답 처리 중 오류가 발생했습니다: {str(e)}",
            "raw_response": remove_emojis(str(result)) if isinstance(result, str) else str(result)
        }


def validate_json_structure(data: Dict[str, Any], required_fields: list) -> Dict[str, Any]:
    """
    JSON 응답의 필수 필드를 검증하고 누락된 필드가 있으면 기본값을 추가합니다.
    """
    if not isinstance(data, dict):
        return {
            "success": False,
            "error_message": "응답이 올바른 JSON 형식이 아닙니다"
        }

    # 필수 필드 확인 및 기본값 설정
    for field in required_fields:
        if field not in data:
            if field == "sql_query":
                data[field] = "-- 쿼리를 생성할 수 없습니다"
            elif field == "explanation":
                data[field] = "설명을 제공할 수 없습니다"
            elif field == "complexity":
                data[field] = "UNKNOWN"
            elif field == "estimated_performance":
                data[field] = "성능 정보를 제공할 수 없습니다"
            elif field == "key_concepts":
                data[field] = []
            elif field == "security_notes":
                data[field] = "보안 권장사항이 제공되지 않았습니다"
            else:
                data[field] = ""

    return data


def clean_dict_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    딕셔너리의 모든 문자열 값에서 이모지를 제거합니다.
    """
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_data[key] = remove_emojis(value)
        elif isinstance(value, list):
            cleaned_data[key] = [
                remove_emojis(item) if isinstance(item, str) else item
                for item in value
            ]
        elif isinstance(value, dict):
            # 중첩된 딕셔너리도 재귀적으로 처리
            cleaned_data[key] = clean_dict_values(value)
        else:
            cleaned_data[key] = value
    return cleaned_data
