from django.urls import path
from . import views


urlpatterns = [
    path('', views.post_list), # READ(index), CREATE
    path('<int:post_pk>/', views.post_detail), # READ(detail), UPDATE, DELETE
]

#gms연결
from django.urls import path
from .views import gms_test

urlpatterns = [
    path("gms-test/", gms_test),
]
