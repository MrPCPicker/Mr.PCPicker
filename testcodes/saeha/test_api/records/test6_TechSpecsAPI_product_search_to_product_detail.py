import requests
from pprint import pprint

def get_product_search():
    '''
    API : GET / Product Search
    DOC : https://techspecs.readme.io/reference/search-products
    URL : https://api.techspecs.io/v5/products/search?query=&category=Desktops&brand=&keepCasing=True&machineId=&page=0&size=10
    '''

    url = "https://api.techspecs.io/v5/products/search"

    params = {
        "query": "",              # 제품명, 모델명, 버전, 머신ID, 주요 특징 (안 적으면 기본값 "iPhone 14"이 되므로 ""로 초기화)
        "category": "Desktops",   # 제품 카테고리 ("Smartphones", "Tablets", "Smartwatches", "Laptops", "Desktops" 중 하나만)
        "brand": "",              # 브랜드 ("Apple", "Samsung" 등)
        "keepCasing": True,       # 응답 속성 이름 대소문자 유지 (false 로 적으면 모든 속성 소문자로 나옴)
        "machineId": "",          # 특정 제품의 고유 Machine ID (특정 모델만 검색하는게 아니면 작성하지 않음)
        "page": 0,                # 페이지 번호
        "size": 10                # 한 페이지당 반환할 결과 개수 (최소 10 ~ 최대 50)
    }

    headers = {
        "accept": "application/json",   # 응답 포맷 지정 
        "x-api-id": "API-ID",           # TechSpecs 대시보드에서 발급받는 API ID
        "x-api-key": "API-KEY"          # TechSpecs 대시보드에서 발급받는 API KEY
    }

    # API 요청 보내기
    response = requests.get(url, params=params, headers=headers)
    print(response.url)     # 만들어진 URL 확인하기
    pprint(response.json()) # 만들어진 JSON 확인하기
    print("---------------------------------------------------")
    return response.json()

def get_product_detail(product_id):
    '''
    API : GET / Product Search
    DOC : https://techspecs.readme.io/reference/product-detail
    URL : https://api.techspecs.io/v5/products/6429bf4cd23cbd21e8687738?lang=en&keepCasing=True
    '''

    url = f"https://api.techspecs.io/v5/products/{product_id}"

    params = {
        "lang": "en",       # 언어 (기본 영어)
        "keepCasing": True  # 대소문자 유지 (false 면 모두 소문자)
    }

    headers = {
        "accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "x-api-id": "API-ID",
        "x-api-key": "API-KEY"
    }

    # API 요청 보내기
    response = requests.get(url, params=params, headers=headers)
    print(response.url)     # 만들어진 URL 확인하기
    pprint(response.json()) # 만들어진 JSON 확인하기
    print("---------------------------------------------------")
    return response.json()

if __name__ == '__main__':
    response_product_search = get_product_search()
    product_model_id = response_product_search["data"][0]["Product"]["id"]
    response_product_detail = get_product_detail(product_model_id)
