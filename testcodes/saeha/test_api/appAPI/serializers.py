from rest_framework import serializers
from .models import ProductSearchItem, ProductDetail


class ProductSearchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSearchItem
        fields = [
            "id",
            "techspecs_id",
            "brand",
            "category",
            "model_name",
            "version",
            "thumbnail_url",
            "release_date",
            "image_note",
            "created_at",
            "updated_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    # search item을 같이 보고 싶으면 nested로 포함
    search_item = ProductSearchItemSerializer(read_only=True)

    class Meta:
        model = ProductDetail
        fields = [
            "id",
            "techspecs_id",
            "brand",
            "category",
            "model_name",
            "version",
            "os",
            "os_version",
            "cpu",
            "gpu",
            "ram_gb",
            "storage_gb_min",
            "weight_g",
            "display_size_in",
            "refresh_rate_hz",
            "msrp_text",
            "raw_json",
            "added_on",
            "search_item",
            "created_at",
            "updated_at",
        ]
