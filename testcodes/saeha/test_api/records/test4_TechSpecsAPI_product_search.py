import requests
from pprint import pprint

def get_product_search():
    '''
    API : GET / Product Search
    DOC : https://techspecs.readme.io/reference/search-products
    URL : https://api.techspecs.io/v5/products/search?query=&category=Desktops&brand=&keepCasing=True&machineId=&page=0&size=50
    '''

    url = "https://api.techspecs.io/v5/products/search"

    params = {
        "query": "",              # 제품명, 모델명, 버전, 머신ID, 주요 특징 (안 적으면 기본값 "iPhone 14"이 되므로 ""로 초기화)
        "category": "Desktops",   # 제품 카테고리 ("Smartphones", "Tablets", "Smartwatches", "Laptops", "Desktops" 중 하나만)
        "brand": "",              # 브랜드 ("Apple", "Samsung" 등)
        "keepCasing": True,       # 응답 속성 이름 대소문자 유지 (false 로 적으면 모든 속성 소문자로 나옴)
        "machineId": "",          # 특정 제품의 고유 Machine ID (특정 모델만 검색하는게 아니면 작성하지 않음)
        "page": 0,                # 페이지 번호
        "size": 50                # 한 페이지당 반환할 결과 개수 (기본 10, 최대 50)
    }

    headers = {
        "accept": "application/json",   # 응답 포맷 지정 
        "x-api-id": "693e43668ea1b71b83af047e",           # TechSpecs 대시보드에서 발급받는 API ID
        "x-api-key": "d3106dda-3123-4e93-a254-7435e3a2a5d7"          # TechSpecs 대시보드에서 발급받는 API KEY
    }

    # API 요청 보내기
    response = requests.get(url, params=params, headers=headers)
    print(response.url)     # 실제로 만들어진 URL 확인 가능
    pprint(response.json())
    return response.json()

if __name__ == '__main__':
    result = get_product_search()   # json 형태의 데이터 반환
    # pprint(result)                  # prrint(): json 을 보기 좋은 형식으로 출력

