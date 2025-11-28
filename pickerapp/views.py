# from django.shortcuts import render
from .models import Post
from .serializers import PostListSerializer, PostSerializer
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
# @api_view(['GET'])
# def post_list(request):
#     if request.method == 'GET':
#         posts = Post.objects.all()
#         serializer = PostListSerializer(posts, many=True)
#         return Response(serializer.data)

# @api_view(['GET'])
# def post_detail(request, post_pk):
#     post = Post.objects.get(pk=post_pk)
#     if request.method == 'GET':
#         serializer = PostSerializer(post)
#         return Response(serializer.data)
    
@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET': # READ(index)
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True) # ArticleListSerializer
        return Response(serializer.data)

    elif request.method == 'POST': # CREATE
        serializer = PostSerializer(data=request.data) # ArticleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors
        
    elif request.method == 'POST': # CREATE
        serializer = PostSerializer(data=request.data) # ArticleSerializer
        if serializer.is_valid(raise_exception=True): # raise_exception=True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        


@api_view(['GET', 'DELETE', 'PUT', 'PATCH']) # PUT/PATCH 중 하나 선택
def post_detail(request, post_pk): # article_pk
    post = Post.objects.get(pk=post_pk)
    
    if request.method == 'GET': # READ(detail)
        serializer = PostSerializer(post) # ArticleSerializer
        return Response(serializer.data) 

    elif request.method == 'DELETE': # DELETE
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'DELETE': # DELETE
        pk = post.pk
        title = post.title
        post.delete()
        data = {
            'message': f'{pk}번 게시글 "{title}"이 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PUT': # UPDATE
        serializer = PostSerializer(post, data=request.data) # PostSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors

    elif request.method == 'PATCH': # UPDATE
        serializer = PostSerializer(post, data=request.data, partial=True) # PostSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # serializer.errors