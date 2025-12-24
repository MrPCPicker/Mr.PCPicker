# backend/gms/services/gms_client.py
import requests
import os
import uuid


GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses"


def call_gms_openai(prompt: str) -> str:
    """
    GMS를 통해 OpenAI Responses API를 호출하는 헬퍼 함수.
    - 모델: gpt-4.1 (응답 구조 안정적, JSON 출력 잘 지킴)
    - max_output_tokens 를 제한해서 크레딧/토큰 사용을 조절.
    """
    call_id = uuid.uuid4().hex[:8]
    print(f"[GMS CALL START] id={call_id}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GMS_API_KEY')}",
    }

    data = {
        "model": "gpt-4.1-nano",
        "input": prompt,
        "max_output_tokens": 250,  # 🔻 400 → 250으로 줄여서 출력 토큰 다이어트
    }

    response = requests.post(GMS_OPENAI_URL, headers=headers, json=data)
    print(f"[GMS CALL DONE] id={call_id}, status={response.status_code}")

    # 4xx, 5xx 이면 에러 내용 한 번 찍어보고 예외 발생
    if not response.ok:
        print("[GMS ERROR BODY]", response.text)
        response.raise_for_status()

    result = response.json()

    # ---- Responses API 표준 경로에서 텍스트 추출 ----
    # 보통:
    # result["output"][0]["content"][0] == {"type": "output_text", "text": "..."}

    outputs = result.get("output", []) or []
    if not outputs:
        raise ValueError("No 'output' field in GMS response")

    first_output = outputs[0]
    contents = first_output.get("content", []) or []

    for c in contents:
        c_type = c.get("type")
        if c_type in ("output_text", "text", "input_text"):
            text = c.get("text")
            if text:
                return text

    # 혹시 다른 형태일 때 대비한 fallback (디버깅용)
    print("[WARN] Unable to extract text from GMS response:", result)
    raise ValueError("No text content found in GMS response")
