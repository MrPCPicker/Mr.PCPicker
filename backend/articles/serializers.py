from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'updated_at')
        read_only_fields = ('article', 'author')

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = (
            'id', 'title', 'content', 'category', 'author',
            'views', 'created_at', 'updated_at',
            'comment_count', 'like_count'
        )
        read_only_fields = ('author', 'views', 'likes', 'comment_count', 'like_count')
    
    def get_like_count(self, obj):
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.likes.count()

class ArticleDetailSerializer(ArticleListSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ('content', 'comments', 'is_liked')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
