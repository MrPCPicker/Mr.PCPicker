import requests
import os

GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses"


def call_gms_openai(prompt: str) -> str:
    """
    GMS를 통해 OpenAI Responses API를 호출하는 헬퍼 함수.
    - 현재 모델: gpt-5-nano (저비용/경량)
    - 한 번 호출에 max_output_tokens 를 제한해서 크레딧 사용을 줄임.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GMS_API_KEY')}",
    }

    data = {
        "model": "gpt-5-nano",   # ✅ gpt-4.1  → gpt-5-nano 로 변경
        "input": prompt,
        "max_output_tokens": 400,  # ✅ 출력 토큰 상한 (필요시 더 줄여도 됨)
    }

    response = requests.post(GMS_OPENAI_URL, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()

    # OpenAI responses 표준 출력 경로
    return result["output"][0]["content"][0]["text"]
