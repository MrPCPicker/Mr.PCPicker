# products/management/commands/fetch_product_data.py

import requests
import json
from urllib.parse import urlencode
from django.core.management.base import BaseCommand
from time import sleep
from products.models import ProductSearch, ProductDetailRaw
from django.conf import settings
from django.utils import timezone

# API URLs
BASE_API_URL = "https://api.techspecs.io/v5"
PRODUCT_SEARCH_API_URL = f"{BASE_API_URL}/products/search"
PRODUCT_DETAIL_API_URL = f"{BASE_API_URL}/products"

class Command(BaseCommand):
    help = "Fetches products from TechSpecs API and saves to the database"
    
    def handle(self, *args, **kwargs):
        all_products = []
        categories = ["Laptops", "Desktops"]  # 검색할 제품 카테고리 "Laptops", "Desktops"

        # API 키 확인
        if not all([hasattr(settings, 'API_KEY'), hasattr(settings, 'API_ID')]):
            self.stderr.write("Error: API_KEY or API_ID is not set in settings.")
            return

        headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "X-API-KEY": settings.API_KEY,
            "X-API-ID": settings.API_ID
        }

        # 제품 검색
        for category in categories:
            for page in range(20):  # page 0부터 19까지 반복, 20
                params = {
                    "query": category,
                    "page": page,
                    "size": 50,  # 한 번에 가져올 상품 수
                    "keepCasing": "true"
                }
                
                # 요청 정보 출력
                full_url = f"{PRODUCT_SEARCH_API_URL}?{urlencode(params)}"
                print(f"\n=== 검색 요청 ===")
                print(f"URL: {full_url}")
                print(f"Headers: {json.dumps(headers, indent=2)}")
                
                try:
                    # 검색 API 호출
                    response = requests.get(
                        PRODUCT_SEARCH_API_URL,
                        headers=headers,
                        params=params,
                        timeout=10
                    )
                    
                    # 응답 정보 출력
                    print(f"\n=== 검색 응답 ===")
                    print(f"상태 코드: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"응답 데이터: {json.dumps(data, indent=2)[:500]}...")

                            if 'data' in data and data['data']:
                                all_products.extend(data['data'])
                                print(f"'{category}' 카테고리에서 {len(data['data'])}개 제품을 찾았습니다.")
                                
                                # ProductSearch 모델에 데이터 저장
                                for product in data['data']:
                                    product_id = product['Product'].get('id')  # 'Product' 안의 'id' 접근
                                    if product_id:
                                        # ProductSearch에 저장
                                        ProductSearch.objects.update_or_create(
                                            product_id=product['Product'].get('id'),
                                            defaults={
                                                'brand': product['Product'].get('Brand'),
                                                'category': product['Product'].get('Category'),
                                                'model': product['Product'].get('Model'),
                                                'version': product['Product'].get('Version'),
                                                'thumbnail': product['Product'].get('Thumbnail'),
                                                'release_date': product.get('Release Date'),
                                                'image': product.get('Image'),
                                                'created_at': timezone.now()  # 현재 시간
                                            }
                                        )
                                        # 상세 정보 조회
                                        self.fetch_product_detail(product_id, headers)
                                    else:
                                        print(f"제품 ID가 없습니다: {product}")
                                    
                            else:
                                print(f"'{category}'에 대한 검색 결과가 없습니다.")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"JSON 파싱 실패. 응답: {response.text[:500]}...")

                            break
                            
                    else:
                        print(f"에러 {response.status_code}: {response.text[:500]}")
                        break
                        
                except requests.exceptions.RequestException as e:
                    print(f"요청 실패: {str(e)}")
                    break
                    
                sleep(1)  # API 호출 간격

    def fetch_product_detail(self, product_id, headers):
        """제품 상세 정보 조회"""
        detail_url = f"{PRODUCT_DETAIL_API_URL}/{product_id}"
        params = {
            "lang": "en"
        }
        
        print(f"\n상세 정보 조회 - 제품 ID: {product_id}")
        
        try:
            response = requests.get(
                detail_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    product_detail = response.json()
                    print(f"제품 상세 정보 조회 성공: {product_id}")
                    print(f"제품명: {product_detail.get('name', 'N/A')}")
                    
                    # 여기서 ProductDetailRaw 모델에 저장
                    ProductDetailRaw.objects.update_or_create(
                        product_id=product_id,
                        defaults={'raw_json': product_detail}
                    )
                    
                except json.JSONDecodeError:
                    print(f"상세 정보 JSON 파싱 실패: {response.text[:200]}...")
            else:
                print(f"상세 정보 조회 실패 ({response.status_code}): {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"상세 정보 요청 실패: {str(e)}")
            
        sleep(1)  # API 호출 간격
