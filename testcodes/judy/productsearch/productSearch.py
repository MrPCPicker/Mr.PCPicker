import requests
import os
import json
from dotenv import load_dotenv

# ====================================================================
# 1. 환경 설정 및 API 키 로드
# ====================================================================
# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# API 인증 정보 (API ID와 KEY가 .env 파일에 정확히 있어야 작동합니다.)
API_ID = os.getenv("TECHSPECS_API_ID")
API_KEY = os.getenv("TECHSPECS_API_KEY")

# API 엔드포인트
URL = "https://api.techspecs.io/v5/products/search"

# 공통 헤더
HEADERS = {
    "accept": "application/json",
    # .env 파일에서 불러온 인증 정보를 헤더에 포함합니다.
    "x-api-id": API_ID,
    "x-api-key": API_KEY
}

# ====================================================================
# 2. 데이터 가져오기 함수 (크레딧 1 소모)
# ====================================================================
def fetch_laptops_data():
    """
    Laptop 카테고리에서 최대 100개의 제품 데이터를 가져와 딕셔너리로 반환합니다.
    """
    
    # API 키나 ID가 비어 있으면 즉시 종료
    if not API_ID or not API_KEY:
        raise ValueError(".env 파일에 TECHSPECS_API_ID 또는 TECHSPECS_API_KEY가 설정되어 있지 않습니다.")

    # 검색 파라미터 설정
    params = {
        "category": "Laptops",  # 'Laptops' (대문자 L)가 더 안전합니다.
        "keepCasing": "true",
        "page": 0, # 첫 페이지
        "size": 100, # 페이지당 최대 개수 (100개)
    }

    print("🔎 Techspecs API에 데이터 요청 중...")
    
    # API 호출 (여기서 크레딧 1 소모)
    response = requests.get(URL, headers=HEADERS, params=params)
    response.raise_for_status() # HTTP 오류 발생 시 예외 발생 (4xx, 5xx)

    # 이 부분이 주석 해제되어야 합니다.
    data = response.json()

    # 필요한 정보만 추출하여 리스트 정리
    results = []
    for item in data.get("data", []):
        product = item.get("Product", {})

        results.append({
            "id": product.get("id"),
            "brand": product.get("Brand"),
            "category": product.get("Category"),
            "model": product.get("Model"),
            "version": product.get("Version")
        })

    # 이 부분이 주석 해제되어야 하며, 결과를 반환해야 합니다.
    return {
        "meta": {
            "status": data.get("status"),
            "total_results": data.get("total_results"),
            "page": data.get("page"),
            "size_requested": data.get("size"),
            "size_received": len(results)
        },
        "products": results
    }

# ====================================================================
# 3. 메인 실행 블록
# ====================================================================
if __name__ == "__main__":
    
    FILE_NAME = "techspecs_laptops_data.json"
    
    try:
        # 1. API에서 데이터 가져오기
        # 함수가 이제 데이터를 반환하므로 정상 작동합니다.
        laptop_data = fetch_laptops_data()
        
        # 2. 파일로 저장
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(laptop_data, f, ensure_ascii=False, indent=2)

        current_dir = os.getcwd() # 현재 작업 경로 확인
        
        print("\n=======================================================")
        print("✅ 작업 완료: JSON 파일이 성공적으로 생성되었습니다.")
        print(f"📍 파일 이름: {FILE_NAME}")
        print(f"📂 저장된 경로: {os.path.join(current_dir, FILE_NAME)}")
        print(f"📊 총 저장된 Laptop 제품 수: {len(laptop_data['products'])}")
        print("=======================================================")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 오류 (API 인증 문제 가능성): {e}")
        print("💡 API ID와 KEY가 정확한지 다시 한 번 확인해주세요.")
    except ValueError as e:
        print(f"\n❌ 설정 오류: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ 연결 오류: 네트워크 상태를 확인해주세요.")
    except Exception as e:
        print(f"\n❌ 알 수 없는 오류 발생: {e}")