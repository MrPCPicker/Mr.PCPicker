from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('notice', '공지'),
        ('tip', '개발팁'),
        ('qna', 'Q&A'),
        ('free', '자유게시판'),
        ('estimate', '견적 요청'),
    ]
    
    title = models.CharField('제목', max_length=100)
    content = models.TextField('내용')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    category = models.CharField('카테고리', max_length=10, choices=CATEGORY_CHOICES, default='free')
    
    def save(self, *args, **kwargs):
        # Convert category to lowercase before saving
        if self.category:
            self.category = self.category.lower()
        super().save(*args, **kwargs)
    
    # 노트북 ID 리스트 저장을 위한 필드
    laptops = models.JSONField('선택된 노트북 ID들', default=list, blank=True)
    
    views = models.PositiveIntegerField('조회수', default=0)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

# 이 부분이 누락되어 에러가 났었습니다. 다시 추가합니다.
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} - {self.content[:30]}"