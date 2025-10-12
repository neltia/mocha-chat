import yaml
from pathlib import Path
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_all_prompts(file_name: str) -> dict:
    """YAML 프롬프트 파일을 로드합니다."""
    try:
        path = Path(__file__).resolve().parent.parent / "config" / file_name
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"프롬프트 파일을 찾을 수 없습니다: {file_name}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"YAML 파싱 오류: {e}")
        raise


def get_prompt(file_name: str, section: str, merge_base: bool = True) -> Dict[str, Any]:
    """
    특정 섹션의 프롬프트를 반환하며, 필요 시 base_prompts.yaml의 context를 병합합니다.

    Args:
        file_name: 프롬프트 파일명
        section: 섹션명
        merge_base: base_prompts.yaml 병합 여부

    Returns:
        프롬프트 데이터 딕셔너리
    """
    # main prompt 파일 로드
    prompts = load_all_prompts(file_name=file_name)

    if section not in prompts:
        raise KeyError(f"프롬프트 섹션 '{section}'을 {file_name}에서 찾을 수 없습니다")

    prompt_data = prompts[section].copy()  # 원본 데이터 보호를 위해 복사

    # base 프롬프트 병합
    if merge_base:
        try:
            base_path = Path(__file__).resolve().parent.parent / "prompts" / "base_prompts.yaml"
            if base_path.exists():
                with open(base_path, "r", encoding="utf-8") as f:
                    base_prompts = yaml.safe_load(f)

                # base_context 병합
                base_context = base_prompts.get("base_context")
                if base_context and "system" in prompt_data:
                    prompt_data["system"] = base_context.strip() + "\n\n" + prompt_data.get("system", "")

        except Exception as e:
            logger.warning(f"베이스 프롬프트 병합 실패: {e}")

    return prompt_data


def render_prompt(template: str, variables: Dict[str, Any]) -> str:
    """
    템플릿 문자열에서 {{var}} 또는 {var} 형태의 표현식을 실제 값으로 치환합니다.

    Args:
        template: 템플릿 문자열
        variables: 치환할 변수들의 딕셔너리

    Returns:
        치환된 문자열
    """
    def replacer(match):
        # group(1): {{var}} / group(2): {var}
        key = (match.group(1) or match.group(2)).strip()
        value = variables.get(key)

        if value is not None:
            # 값이 문자열이 아닌 경우 문자열로 변환
            return str(value)
        else:
            # 값이 없으면 원본 그대로 반환
            logger.warning(f"템플릿 변수 '{key}'에 대한 값이 제공되지 않았습니다")
            return match.group(0)

    # 정규표현식 패턴: {{변수}} 또는 {변수} 형태 매칭
    pattern = re.compile(r"\{\{\s*(.*?)\s*\}\}|\{(\w+)\}")
    result = re.sub(pattern, replacer, template)

    return result


def validate_prompt_structure(prompt_data: Dict[str, Any], required_keys: Optional[list] = None) -> bool:
    """
    프롬프트 데이터 구조를 검증합니다.

    Args:
        prompt_data: 검증할 프롬프트 데이터
        required_keys: 필수 키 목록 (기본값: ['system', 'user'])

    Returns:
        구조가 유효한지 여부
    """
    if required_keys is None:
        required_keys = ['system', 'user']

    for key in required_keys:
        if key not in prompt_data:
            logger.error(f"필수 키 '{key}'가 프롬프트 데이터에 없습니다")
            return False

        if not isinstance(prompt_data[key], str) or not prompt_data[key].strip():
            logger.error(f"키 '{key}'의 값이 유효하지 않습니다")
            return False

    return True


def get_prompt_with_validation(file_name: str, section: str, variables: Dict[str, Any] = None) -> Dict[str, str]:
    """
    프롬프트를 가져오고 검증한 후 변수를 치환하여 반환합니다.

    Args:
        file_name: 프롬프트 파일명
        section: 섹션명
        variables: 템플릿 변수들

    Returns:
        system과 user 프롬프트가 포함된 딕셔너리
    """
    try:
        # 프롬프트 로드
        prompt_data = get_prompt(file_name, section)

        # 구조 검증
        if not validate_prompt_structure(prompt_data):
            raise ValueError(f"프롬프트 구조가 유효하지 않습니다: {section}")

        # 변수 치환
        if variables:
            system_prompt = render_prompt(prompt_data["system"], variables)
            user_prompt = render_prompt(prompt_data["user"], variables)
        else:
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"]

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    except Exception as e:
        logger.error(f"프롬프트 처리 중 오류 발생: {e}")
        raise
