# backend/gms/services/gms_client.py
import requests
import os
import uuid
import json
import re

GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses"


def _extract_json_safely(text: str) -> dict:
    """
    GMS 응답에서 JSON만 안전하게 추출
    """
    if not text:
        raise ValueError("Empty GMS response")

    text = text.strip()

    # ```json ``` 코드블록 제거
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text).strip()

    # 전체가 JSON이면 바로 파싱
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # 텍스트 + JSON 섞인 경우 JSON 부분만 추출
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))

    raise ValueError("JSON not found in GMS response")


def call_gms_openai(prompt: str) -> dict:
    """
    ✅ 항상 dict(JSON)만 반환
    ❌ 문자열 반환 없음
    """
    call_id = uuid.uuid4().hex[:8]
    print(f"[GMS CALL START] id={call_id}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GMS_API_KEY')}",
    }

    system_prompt = """
너는 컴퓨터 추천 API다.
반드시 JSON만 출력한다.
설명 문장, 코드블록, 주석, 마크다운을 절대 출력하지 마라.

출력 형식:
{
  "needs": ["..."],
  "recommends": ["..."],
  "filters": {
    "min_ram_gb": number | null,
    "min_storage_gb": number | null,
    "preferred_types": ["laptop","desktop","aio"]
  }
}
"""

    data = {
        "model": "gpt-4.1-nano",
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_output_tokens": 300,  # ❗ 요청 조건 유지
    }

    resp = requests.post(
        GMS_OPENAI_URL,
        headers=headers,
        json=data,
        timeout=15,
    )

    print(f"[GMS CALL DONE] id={call_id}, status={resp.status_code}")

    if not resp.ok:
        print("[GMS ERROR BODY]", resp.text)
        resp.raise_for_status()

    result = resp.json()

    outputs = result.get("output") or []
    if not outputs:
        raise ValueError("GMS output empty")

    contents = outputs[0].get("content") or []
    for c in contents:
        if c.get("type") in ("output_text", "text"):
            raw_text = c.get("text")
            print(f"[GMS RAW TEXT] {raw_text[:300]}")
            return _extract_json_safely(raw_text)

    raise ValueError("No usable text in GMS response")
