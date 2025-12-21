# backend/gms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("gms-test/", views.gms_test, name="gms-test"),
    path("recommend-laptops/", views.recommend_laptops, name="gms-recommend-laptops"),
]
