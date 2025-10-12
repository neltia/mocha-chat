import json
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def _parse_json_safe(text: str):
    """
    Groq 응답이 문자열 내부 JSON 형태로 들어올 경우 2단계 파싱 수행
    """
    try:
        data = json.loads(text)
        # 내부에 문자열 형태의 JSON이 있으면 재파싱
        for key, value in list(data.items()):
            if isinstance(value, str) and value.strip().startswith("{"):
                try:
                    data[key] = json.loads(value)
                except Exception:
                    pass
        return data
    except Exception:
        # JSON 변환이 불가능한 경우 그대로 반환
        return text


def call_groq_with_yaml(system_prompt: str, user_prompt: str):
    # Using synchronous call per groq SDK example in the environment.
    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        reasoning_effort="medium",
        stream=False
    )

    try:
        content = completion.choices[0].message.content
    except Exception:
        try:
            content = completion.choices[0].text
        except Exception:
            content = str(completion)

    # JSON 파싱 보정
    return _parse_json_safe(content)
