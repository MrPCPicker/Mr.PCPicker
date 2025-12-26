from django.urls import path
from .views import (
    ImportProductSearchResponseAPIView,
    ImportProductDetailResponseAPIView,
    ProductSearchItemListAPIView,
    ProductDetailListAPIView,
    ProductDetailRetrieveAPIView,
)

urlpatterns = [
    # import endpoints (수집/적재)
    path("import-search/", ImportProductSearchResponseAPIView.as_view()),
    path("import-detail/", ImportProductDetailResponseAPIView.as_view()),

    # 조회 endpoints
    path("search-items/", ProductSearchItemListAPIView.as_view()),
    path("details/", ProductDetailListAPIView.as_view()),
    path("details/<str:techspecs_id>/", ProductDetailRetrieveAPIView.as_view()),
]
