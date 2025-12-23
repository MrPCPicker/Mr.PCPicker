# 3️⃣ Management Command (Detail → Raw → Spec)
# products/management/commands/import_product_detail.py
from django.core.management.base import BaseCommand
from products.models import ProductDetailRaw, ProductDetailSpec
from products.services.detail_parser import extract_spec


class Command(BaseCommand):
    help = "Parse ProductDetailRaw into ProductDetailSpec"

    def handle(self, *args, **kwargs):
        raws = ProductDetailRaw.objects.all()
        self.stdout.write(f"Processing {raws.count()} raw products")

        for raw in raws:
            spec_data = extract_spec(raw.raw_json)

            ProductDetailSpec.objects.update_or_create(
                product_id=raw.product_id,
                defaults=spec_data,
            )

        self.stdout.write(self.style.SUCCESS("ProductDetailSpec updated"))
