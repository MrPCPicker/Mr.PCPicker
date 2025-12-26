from django.contrib import admin
from .models import ProductSearchItem, ProductDetail

@admin.register(ProductSearchItem)
class ProductSearchItemAdmin(admin.ModelAdmin):
    list_display = ("techspecs_id", "brand", "category", "model_name", "version", "updated_at")
    search_fields = ("techspecs_id", "brand", "model_name", "version")
    list_filter = ("brand", "category")

@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ("techspecs_id", "brand", "category", "model_name", "ram_gb", "storage_gb_min", "weight_g", "updated_at")
    search_fields = ("techspecs_id", "brand", "model_name", "cpu", "gpu")
    list_filter = ("brand", "category")
