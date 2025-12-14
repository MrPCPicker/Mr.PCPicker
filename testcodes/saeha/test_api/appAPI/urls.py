from django.urls import path
from . import views

urlpatterns = [
    path("sync/", views.sync_products, name="sync_products"),  # POST
    path("products/", views.product_list, name="product_list"),  # GET
    path("products/<str:techspecs_id>/", views.product_detail, name="product_detail"),  # GET
]
