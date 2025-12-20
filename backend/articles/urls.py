from django.urls import path
from articles import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list), # READ(index), CREATE
    path('<int:article_pk>/', views.article_detail), # READ(detail), UPDATE, DELETE

    path('comments/', views.comment_list), # READ(index)
    path('comments/<int:comment_pk>/', views.comment_detail), # READ(detail), UPDATE, DELETE
    path('<int:article_pk>/comments/', views.comment_create), # CREATE
]
