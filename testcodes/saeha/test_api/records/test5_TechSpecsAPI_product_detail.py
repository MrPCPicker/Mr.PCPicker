import requests
from pprint import pprint

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
        "x-api-id": "693e43668ea1b71b83af047e",
        "x-api-key": "d3106dda-3123-4e93-a254-7435e3a2a5d7"
    }

    # API 요청 보내기
    response = requests.get(url, params=params, headers=headers)
    print(response.url)   # 실제로 만들어진 URL 확인 가능
    pprint(response.json())
    return response.json()

if __name__ == '__main__':
    result = get_product_detail('6429bf4cd23cbd21e8687738')   # json 형태의 데이터 반환
    # pprint(result)                  # prrint(): json 을 보기 좋은 형식으로 출력

