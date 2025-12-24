# products/serializers.py
from rest_framework import serializers
from .models import ProductSearch, ProductDetailSpec

class ProductSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSearch
        fields = '__all__'

class ProductDetailSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetailSpec
        fields = '__all__'
