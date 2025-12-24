# products/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductSearch, ProductDetailSpec
from .serializers import ProductSearchSerializer, ProductDetailSpecSerializer

class ProductSearchList(APIView):
    """
    API View to get all products from ProductSearch
    """
    def get(self, request, format=None):
        products = ProductSearch.objects.all()
        serializer = ProductSearchSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailSpecList(APIView):
    """
    API View to get all product specs from ProductDetailSpec
    """
    def get(self, request, format=None):
        specs = ProductDetailSpec.objects.all()
        serializer = ProductDetailSpecSerializer(specs, many=True)
        return Response(serializer.data)
