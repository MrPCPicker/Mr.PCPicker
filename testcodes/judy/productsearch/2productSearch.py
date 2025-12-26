import requests
import os
import json
from dotenv import load_dotenv

# API 요청 URL (노트북, 첫 페이지, 10개)
URL = "https://api.techspecs.io/v5/products/search?category=Laptops&keepCasing=true&page=1&size=10"

# API 인증 정보를 직접 입력해야 하는 부분입니다.
# ⚠️ 반드시 "따옴표 안에" 실제 API ID와 KEY 값을 넣어주세요.

load_dotenv()

# API 인증 정보 (API ID와 KEY가 .env 파일에 정확히 있어야 작동합니다.)
API_ID = os.getenv("TECHSPECS_API_ID")
API_KEY = os.getenv("TECHSPECS_API_KEY")

HEADERS = {
    "accept": "application/json",
    "x-api-id": API_ID,  # ⬅️ 여기에 실제 ID 값 입력
    "x-api-key": API_KEY # ⬅️ 여기에 실제 KEY 값 입력
}

# 파일 이름 설정
FILE_NAME = "2techspecs_laptops_result.json"

try:
    print("🔎 Techspecs API에 데이터 요청 중...")
    
    # 1. API 호출 (크레딧 1 소모)
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status() # HTTP 오류 발생 시 예외 발생

    # 2. 응답 데이터를 JSON 객체로 변환
    data = response.json()
    
    # 3. 콘솔에 결과 텍스트 출력
    print("\n[API 응답 텍스트]")
    print(response.text)
    
    # 4. JSON 파일로 저장
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        # 받은 데이터를 예쁘게 포매팅(indent=2)하여 파일에 저장
        json.dump(data, f, ensure_ascii=False, indent=2)

    current_dir = os.getcwd() # 현재 작업 경로 확인

    print("\n=======================================================")
    print("✅ 작업 완료: JSON 파일이 성공적으로 생성되었습니다.")
    print(f"📍 파일 이름: {FILE_NAME}")
    print(f"📂 저장된 경로: {os.path.join(current_dir, FILE_NAME)}")
    print("=======================================================")

except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP 오류 발생: {e}")
    print("💡 API ID와 KEY가 정확한지 또는 유효한 크레딧이 있는지 확인해주세요.")
except requests.exceptions.RequestException as e:
    print(f"\n❌ 요청 처리 중 오류 발생: {e}")
except Exception as e:
    print(f"\n❌ 알 수 없는 오류 발생: {e}")