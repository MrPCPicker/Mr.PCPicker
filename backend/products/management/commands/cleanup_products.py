# products/management/commands/cleanup_products.py
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import ProductDetailSpec


class Command(BaseCommand):
    help = "Delete first N ProductDetailSpec records safely"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=2000,
            help="How many ProductDetailSpec records to delete (default: 2000)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        limit = options["limit"]

        # ✅ id 기준으로 '처음 N개' 정확히 선택
        spec_ids = list(
            ProductDetailSpec.objects
            .order_by("id")
            .values_list("id", flat=True)[:limit]
        )

        if not spec_ids:
            self.stdout.write(self.style.WARNING("⚠️ 삭제할 ProductDetailSpec 데이터가 없습니다."))
            return

        deleted_count, _ = ProductDetailSpec.objects.filter(id__in=spec_ids).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Deleted {deleted_count} ProductDetailSpec records (first {limit} by id)"
            )
        )
