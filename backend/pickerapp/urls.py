from django.urls import path
from . import views


urlpatterns = [
    path('', views.post_list), # READ(index), CREATE
    path('<int:post_pk>/', views.post_detail), # READ(detail), UPDATE, DELETE
]
