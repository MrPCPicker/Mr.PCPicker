# products/admin.py
from django.contrib import admin
from .models import ProductSearch, ProductDetailRaw, ProductDetailSpec

# admin.site.register(ProductSearch)
# admin.site.register(ProductDetailRaw)
# admin.site.register(ProductDetailSpec)

@admin.register(ProductSearch)
class ProductSearchAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "brand",
        "model",
        "category",
        "release_date",
    )
    search_fields = ("product_id", "brand", "model")


@admin.register(ProductDetailRaw)
class ProductDetailRawAdmin(admin.ModelAdmin):
    list_display = ("product_id", "fetched_at")
    search_fields = ("product_id",)


@admin.register(ProductDetailSpec)
class ProductDetailSpecAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "product_type",
        "brand",
        "model",
        "os",
        "ram_gb",
        "storage_gb",
        "weight_kg",
        "display_inch",
    )
    list_filter = ("product_type", "os")
    search_fields = ("product_id", "brand", "model")

