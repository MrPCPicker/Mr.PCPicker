# products/management/commands/import_product_detail.py

from django.core.management.base import BaseCommand
from products.models import ProductDetailRaw, ProductDetailSpec
from products.services.detail_parser import extract_spec


class Command(BaseCommand):
    help = "Parse ProductDetailRaw into ProductDetailSpec"

    def handle(self, *args, **kwargs):
        # 모든 원본 데이터 가져오기
        raws = ProductDetailRaw.objects.all()
        self.stdout.write(f"Processing {raws.count()} raw products")

        for raw in raws:
            # 원본 데이터를 파싱하여 제품 세부 정보 추출
            spec_data = extract_spec(raw.raw_json)

            # 'model' 필드가 없으면 기본값 'Unknown' 설정
            if 'model' not in spec_data or not spec_data['model']:
                spec_data['model'] = 'Unknown'

            # ProductDetailSpec 모델에 데이터 저장 (또는 업데이트)
            ProductDetailSpec.objects.update_or_create(
                product_id=raw.product_id,
                defaults=spec_data,
            )

        self.stdout.write(self.style.SUCCESS("ProductDetailSpec updated"))
