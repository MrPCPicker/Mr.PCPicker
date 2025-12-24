# products/urls.py
from django.urls import path
from .views import ProductSearchList, ProductDetailSpecList

urlpatterns = [
    path('products/', ProductSearchList.as_view(), name='product_search_list'),
    path('product_specs/', ProductDetailSpecList.as_view(), name='product_spec_list'),
]
