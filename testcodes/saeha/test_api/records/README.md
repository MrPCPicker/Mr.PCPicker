# 1️⃣ OpenWeatherMap API

- `requests` 모듈을 설치해야한다
- `.py` 파일을 실행하면 JSON 형태로 pprint 할 수 있다

```bash
$ python -m venv venv
$ source venv/Scripts/activate
$ pip install requests
```

# 2️⃣ 관통프로젝트 1회차에서 진행한 '금융' API 

# 3️⃣ TECHSPECS API 테스트

## 🔆 1. 데이터 형식 확인하기 

### Product Search 데이터 형식

- 전체
    - status : 요청 성공/실패
    - total_results : 총 제품 개수
    - total_results_per_page : 한 페이지당 제품 개수 (지정)
    - total_pages : 전체 페이지 수
    - page : 현재 페이지 번호
    - data : 제품들 정보
- 제품
    - Product
        - id : 모델 번호 (Product Detail 에서 활용)
        - brand : 회사명
        - Category : 분류
        - Model : 모델 이름
        - Version : 버전
        - Thumbnail : 제품 썸네일
    - Release Date : 출시일
    - Image : 제품 이미지

### Product Detail 데이터 형식

- product_id 를 필수로 넣어야 호출할 수 있다

### 불필요한 API

- GET ALL PRODUCTS BY RELEASE DATE (불필요)
- GET ALL BRANDS (불필요)
- GET ALL CATEGORIES (불필요)
- GET ALL BRAND LOGOS (불필요)
- GET LOGO FOR A BRAND (불필요)
- GET PRODUCT SCHEMA (불필요)
- GET PRODUCT IMAGES (불필요)

---

## 🔆 2. 요청 릴레이 설계하기

- Product Search API 로 모든 Desktops, Laptops 데이터를 요청
    - response['data'][i] 에 있는 딕셔너리 내용 전부를 제품별로 DB로 저장한다
        - ['Image']
        - ['Product']['Brand']
        - ['Product']['Category']
        - ['Product']['Model']
        - ['Product']['Thumbnail']
        - ['Product']['Version']
        - ['Product']['id']
        - ['Release Date']
- 그 중 response['data'][i]['Product']['id'] 에 해당하는 문자열을 활용해서
- Product Detail API 받은 데이터를 칼럼으로 추가한다
    - response['data']['Camera']['Additional Features']
    - ...
    - (이하 생략)

---

## 🔆 3. 요청 형식 확인하기

### Product Search 요청 형식

- size `100000000000` 로 요청했을때의 에러메세지를 통해 최대 `50`임을 확인할 수 있었다

```python
{
  "status": "fail",
  "error": {
    "message": "The server cannot process the request due to invalid syntax or parameters.",
    "errors": [
      {
        "code": "too_big",
        "path": [
          "query",
          "size"
        ],
        "message": "Number must be less than or equal to 50"
      }
    ]
  }
}
```

- size `50` , category `Desktops` 로 요청했을때, 총 제품이 `1000`개이므로 페이지는 `0~19`로 검색하면 된다
    - url : https://api.techspecs.io/v5/products/search?query=&category=Desktops&brand=&keepCasing=True&machineId=&page=0&size=50
    - total_results : 1000
    - total_results_per_page : 50
    - total_pages : 20
    - page : 0

- size `50` , category `Laptops` 로 요청했을때, 총 제품이 `1000`개이므로 페이지는 `0~19`로 검색하면 된다
    - url : https://api.techspecs.io/v5/products/search?query=&category=Laptops&brand=&keepCasing=True&machineId=&page=0&size=50
    - total_results : 1000
    - total_results_per_page : 50
    - total_pages : 20
    - page : 0

- 문제점
    - category 여러개를 한번에 요청할 수 없으므로, 모든 모델명을 가져오려면 총 40번의 요청을 보내야 한다
    - 모델별로 상세 스펙을 가져오려면 총 2000번의 요청을 추가로 보내야한다
    - 하지만 각 계정당 요청 제한 최대 10회이고, 추가시 1회당 $0.02(30원)
    - 전체 제품으로 DB를 만들려면 (실수가 없다는 전제하에) 최소 6만원 소요

---

### 🔆 4. 요청 코드 작성해보기

- Product Search 요청 코드는 무난하게 성공
- Product Detail 요청 코드도 무난하게 성공
- response 자체는 JSON 이 아니기 때문에 `.json()` 을 붙인 후에 `pprint()` 를 해줘야한다

---

### 🔆 5. 코드 합쳐보기

- Product Search API 에서 page `0`, size `10`(최소 10) 로 해서 데이터를 저장한 후
- Product Detail API 로 id를 보내 추가 데이터를 저장한다

```python
if __name__ == '__main__':
    response_product_search = get_product_search()
    product_model_id = response_product_search["data"][0]["Product"]["id"]
    response_product_detail = get_product_detail(product_model_id)
    pprint(response_product_detail)
```

### 🔆 6. Django ORM 을 사용해서 DB 저장하기


1. Django 프로젝트 + 앱 을 만들어준다

```bash
$ python -m venv venv
$ touch .gitignore
$ source venv/Scripts/activate
$ pip install -r requirements.txt
$ django-admin startproject testAPI .
$ python manage.py startapp appAPI
```
```python
# setting.py
INSTALLED_APPS = [
    'appAPI',
```

2. 일단 제품 3개만 뽑아서, 데이터 형식 확인하고 <br>Model 속성을 임의로 설정해서 만들어본다

```python
# 테스트 코드로 3개 추출해보고
if __name__ == '__main__':
    response_product_search = get_product_search()

    for i in range(3):
        product_model_id = response_product_search["data"][i]["Product"]["id"]
        response_product_detail = get_product_detail(product_model_id)
```
```python
# models.py
# ChatGPT 의 도움을 받아, 데이터의 공통된 요소를 필드로 설정
```

3. 만들어둔 테스트코드를 Views 함수 만든다

```python
# views.py
# ChatGPT 의 도움을 받아, DB화를 도와주도록 수정한다
```

4. 모델을 마이그레이트 하면 빈 DB 가 생성된다

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

5. 서버를 돌려서 Postman 으로 확인해야 DB가 채워진다

``` bash
$ python manage.py runserver
```

```
POST
    http://localhost:8000/api/sync/

Header
    Key : Content-Type
    Value : application/json

Body
    {
    "limit": 3
    }

Result

    # 실패 : API ID 와 KEY 를 까먹음
    {
        "ok": false,
        "stage": "search",
        "response": {
            "status": "fail",
            "error": {
                "message": "Invalid API key or ID",
                "errors": []
            }
        }
    }

    # 성공
    {
        "ok": true,
        "requested": 3,
        "saved": 3,
        "failed": []
    }
```
![alt text](image.png)

6. 등록된 DB 확인하기

```
GET
    http://localhost:8000/api/products/?category=Desktops&brand=Lenovo&limit=20

Query Params
    category : Desktops
    brand : Lenovo
    limit : 20

Result
    {
        "ok": true,
        "count": 2,
        "results": [
            {
                "techspecs_id": "6429bf4cd23cbd21e868773f",
                "brand": "Lenovo",
                "category": "Desktops",
                "model_name": "Lenovo V30a",
                "version": "11LC000ETX",
                "product_type": "All-in-One PC",
                "cpu_model": "i5-1035G1",
                "cpu_cores": 4,
                "ram_size": "8 GB",
                "storage_type": "HDD",
                "ssd_capacity": null,
                "hdd_capacity": "1 TB",
                "igpu": "Intel® UHD Graphics",
                "dgpu": null,
                "wifi_standard": "Wi-Fi 5 (802.11ac)",
                "msrp": null,
                "thumbnail_1": "https://thumbnail-techspecs-io.s3.amazonaws.com/thumbnail_1_6429bf4cd23cbd21e868773f.jpg",
                "fetched_at": "2025-12-14T07:51:28.227Z"
            },
            {
                "techspecs_id": "6429bf4cd23cbd21e8687738",
                "brand": "Lenovo",
                "category": "Desktops",
                "model_name": "Lenovo V30a",
                "version": "11LA000BTX",
                "product_type": "All-in-One PC",
                "cpu_model": "i5-1035G1",
                "cpu_cores": 4,
                "ram_size": "8 GB",
                "storage_type": "HDD",
                "ssd_capacity": null,
                "hdd_capacity": "1 TB",
                "igpu": "Intel® UHD Graphics",
                "dgpu": null,
                "wifi_standard": "Wi-Fi 5 (802.11ac)",
                "msrp": null,
                "thumbnail_1": "https://thumbnail-techspecs-io.s3.amazonaws.com/thumbnail_1_6429bf4cd23cbd21e8687738.jpg",
                "fetched_at": "2025-12-14T07:51:26.298Z"
            }
        ]
    }
```