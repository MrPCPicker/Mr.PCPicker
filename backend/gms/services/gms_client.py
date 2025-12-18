import requests
import os

GMS_OPENAI_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/responses"

def call_gms_openai(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GMS_API_KEY')}",
    }

    data = {
        "model": "gpt-4.1",
        "input": prompt
    }

    response = requests.post(GMS_OPENAI_URL, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()

    # OpenAI responses 표준 출력 경로
    return result["output"][0]["content"][0]["text"]
