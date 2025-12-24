# backend/gms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("gms-test/", views.gms_test, name="gms-test"),
    path("recommend-computers/", views.recommend_computers, name="gms-recommend-computers"),  # 경로 변경
]
