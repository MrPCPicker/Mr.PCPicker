from django import forms
from .models import Post, Article,Comment

class PostForm(forms.ModelForm):
    class Meta :
        model = Post
        fields = '__all__'

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
