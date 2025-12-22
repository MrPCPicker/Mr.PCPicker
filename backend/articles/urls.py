from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'articles'

urlpatterns = [
    # 게시글 관련
    path('', views.ArticleListCreateView.as_view(), name='article-list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('<int:pk>/like/', views.ArticleLikeView.as_view(), name='article-like'),
    
    # 댓글 관련
    path('<int:article_pk>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
]
