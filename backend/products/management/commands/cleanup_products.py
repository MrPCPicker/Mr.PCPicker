# products/management/commands/cleanup_products.py
from django.core.management.base import BaseCommand
from products.models import ProductSearch, ProductDetailRaw
class Command(BaseCommand):
    help = 'Clean up product data by removing specific ranges of records'
    def handle(self, *args, **options):
        # Delete ProductSearch records with IDs 451-500
        deleted_search = ProductSearch.objects.filter(id__range=(1601, 2000)).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_search[0]} ProductSearch records (IDs 1601-2000)'))
        # Delete ProductDetailRaw records with IDs 451-490
        deleted_detail = ProductDetailRaw.objects.filter(id__range=(1601, 2000)).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_detail[0]} ProductDetailRaw records (IDs 1601-2000)'))
