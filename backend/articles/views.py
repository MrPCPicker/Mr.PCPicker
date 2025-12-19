# from django.shortcuts import render
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleSerializer, CommentListSerializer, CommentSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth.decorators import login_required


# Create your views here.
@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == 'GET': # READ(index)
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True) # ArticleListSerializer
        return Response(serializer.data)

    elif request.method == 'POST': # CREATE
        serializer = ArticleSerializer(data=request.data) # ArticleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors
        
    elif request.method == 'POST': # CREATE
        serializer = ArticleSerializer(data=request.data) # ArticleSerializer
        if serializer.is_valid(raise_exception=True): # raise_exception=True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # 생략가능

@api_view(['GET', 'DELETE', 'PUT', 'PATCH']) # PUT/PATCH 중 하나 선택
def article_detail(request, article_pk): # article_pk
    article = Article.objects.get(pk=article_pk)
    
    if request.method == 'GET': # READ(detail)
        serializer = ArticleSerializer(article) # ArticleSerializer
        return Response(serializer.data) 

    elif request.method == 'DELETE': # DELETE
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'DELETE': # DELETE
        pk = article.pk
        title = article.title
        article.delete()
        data = {
            'message': f'{pk}번 게시글 "{title}"이 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PUT': # UPDATE
        serializer = ArticleSerializer(article, data=request.data) # ArticleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors

    elif request.method == 'PATCH': # UPDATE
        serializer = ArticleSerializer(article, data=request.data, partial=True) # ArticleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors

@api_view(['GET'])
def comment_list(request):
    if request.method == 'GET': # READ(index)
        comments = Comment.objects.all()
        serializer = CommentListSerializer(comments, many=True) # CommentListSerializer
        return Response(serializer.data)

@api_view(['POST'])
def comment_create(request, article_pk): # article_pk
    article = Article.objects.get(pk=article_pk)
    if request.method == 'POST':
        serializer = CommentSerializer(datat=request.data)
        if serializer.is_valid(raise_exception=True): # 404 Error -> read_only_field
            serializer.save(article=article) # form 일때는 commit=False        
            return Response(serializer.errors, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # 생략가능

@api_view(['GET', 'PUT', 'DELETE'])
def comment_detail(request, comment_pk): # comment_pk
    comment = Comment.objects.get(pk=comment_pk)

    if request.method == 'GET': # READ(detail)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'DELETE': # DELETE
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    elif request.method == 'DELETE': # DELETE
        pk = comment.pk
        comment.delete()
        data = {
            'message': f'{pk}번째 댓글'
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PUT': # UPDATE
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True): # 404 Error -> read_only_field
            serializer.save()
            return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # 생략가능
        
    elif request.method == 'PATCH': # UPDATE
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True): # 404 Error -> read_only_field
            serializer.save()
            return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # 생략가능
