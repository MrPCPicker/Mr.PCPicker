from rest_framework import serializers
from .models import Article, Comment

class ArticleListSerializer(serializers.ModelSerializer): # READ(index)
    class Meta:
        model = Article
        fields = ('id', 'title', 'content',)

class ArticleSerializer(serializers.ModelSerializer): # READ(detail), CREATE, UPDATE(detail)
    class Meta:
        model = Article
        fields = '__all__'

class CommentListSerializer(serializers.ModelSerializer): # READ(index)
    class Meta:
        model = Comment
        fields = ('content',)

class CommentSerializer(serializers.ModelSerializer): # READ(detail), CREATE, UPDATE
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('article',) # CREATE 충돌 방지
