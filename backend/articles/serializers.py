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
            'comment_count', 'like_count',
            'laptops'  # <-- 여기에 laptops 필드를 추가합니다.
        )
        # read_only_fields에는 추가하지 않습니다 (프론트에서 값을 보내야 하므로)
        read_only_fields = ('author', 'views', 'likes', 'comment_count', 'like_count')
    
    def get_like_count(self, obj):
        if hasattr(obj, 'likes_count'):
            return obj.likes_count
        return obj.likes.count()

class ArticleDetailSerializer(ArticleListSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    laptops = serializers.JSONField(required=False, allow_null=True)

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ('comments', 'is_liked', 'laptops')
        read_only_fields = ('laptops',) + ArticleListSerializer.Meta.read_only_fields
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False