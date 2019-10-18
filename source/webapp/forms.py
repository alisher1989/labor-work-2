from django import forms

from webapp.models import Article, Comment, Tag


class ArticleForm(forms.ModelForm):
    tags = forms.CharField(max_length=31, required=False, label='Tag')

    class Meta:
        model = Article
        fields = ['title', 'text', 'author', 'category']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label='Search')


