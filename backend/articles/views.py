from rest_framework import status, permissions, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from .models import Article, Comment
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CommentSerializer
)

#페이지네이션
class ArticlePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

#게시글 목록 + 생성
class ArticleListCreateView(ListCreateAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ArticlePagination

    #queryset 로직
    def get_queryset(self):
        queryset = Article.objects.annotate(
            comment_count=Count('comments', distinct=True),
            likes_count=Count('likes', distinct=True)
        ).select_related('author').prefetch_related('likes')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )

        sort = self.request.query_params.get('sort', 'created_at')
        if sort in ['views', 'created_at', 'like_count', 'comment_count']:
            queryset = queryset.order_by('-' + sort)

        return queryset

    #생성 시 작성자 자동 지정
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

#게시글 상세/ 수정/ 삭제
class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Article.objects.all()

    #조회수 증가
    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        article.increase_views()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    #작성자만 수정/삭제
    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise permissions.PermissionDenied("권한이 없습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise permissions.PermissionDenied("권한이 없습니다.")
        instance.delete()

#게시글 좋아요
class ArticleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)

        if article.likes.filter(id=request.user.id).exists():
            article.likes.remove(request.user)
            liked = False
        else:
            article.likes.add(request.user)
            liked = True

        return Response({
            'liked': liked,
            'count': article.likes.count()
        })

#댓글 목록 + 생성
class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ArticlePagination

    def get_queryset(self):
        article_pk = self.kwargs['article_pk']
        return Comment.objects.filter(
            article_id=article_pk
        ).select_related('author')

    def perform_create(self, serializer):
        article_pk = self.kwargs['article_pk']
        article = get_object_or_404(Article, pk=article_pk)
        serializer.save(
            article=article,
            author=self.request.user
        )

#댓글 상세/ 수정/ 삭제
class CommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise permissions.PermissionDenied("권한이 없습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise permissions.PermissionDenied("권한이 없습니다.")
        instance.delete()





