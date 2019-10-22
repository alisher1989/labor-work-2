from django import forms
from django.core.exceptions import ValidationError

from webapp.models import Article, Comment, Tag


class ArticleForm(forms.ModelForm):
    tags = forms.CharField(max_length=31, required=False, label='Tag')

    class Meta:
        model = Article
        fields = ['title', 'text', 'author', 'category']

    def clean_title(self):
        title = self.cleaned_data['title']
        length = 10
        if len(title) <= length:
            raise ValidationError('This field should be at least %(length)s symbols length!',
                                  code='too_short', params={'length': 11})
        return title.capitalize()

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if cleaned_data['text'] == cleaned_data['title']:
    #         raise ValidationError("Text of the article should not duplicate it's title!")
    #     return cleaned_data

    def clean(self):
        super().clean()
        title = self.cleaned_data.get('title', '')
        text = self.cleaned_data.get('text', '')
        if title.lower() == text.lower():
            raise ValidationError('Text should not duplicate title')
        return self.cleaned_data


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


class FullSearchForm(forms.Form):
    text = forms.CharField(max_length=100, required=False, label='Текст')
    in_title = forms.BooleanField(initial=True, required=False, label='В заголовках')
    in_text = forms.BooleanField(initial=True, required=False, label='В тексте')
    in_tags = forms.BooleanField(initial=True, required=False, label='В тегах')
    in_comment_text = forms.BooleanField(initial=False, required=False, label='В тексте комментариев')


    # test = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=())


    author = forms.CharField(max_length=100, required=False, label='Автор')
    in_articles = forms.BooleanField(initial=True, required=False, label='Статей')
    in_comments = forms.BooleanField(initial=False, required=False, label='Комментариев')

    def clean(self):
        super().clean()
        text = self.cleaned_data.get('text')
        author = self.cleaned_data.get('author')
        in_title = self.cleaned_data.get('in_title')
        in_text = self.cleaned_data.get('in_text')
        in_tags = self.cleaned_data.get('in_tags')
        in_comment_text = self.cleaned_data.get('in_comment_text')
        in_articles = self.cleaned_data.get('in_articles')
        in_comments = self.cleaned_data.get('in_comments')

        try:
            if text:
                if not (in_title or in_text or in_tags or in_comment_text):
                    raise ValidationError(
                        'One of the checkboxes: In Title, In Text, In Tags, In Comment text should be checked.',
                        code='no_text_search_destination'
                                          )
            return self.cleaned_data
        except:
            if author:
                if not (in_articles or in_comments):
                    raise ValidationError(
                        'One of the checkboxes: In Articles, In Comments text should be checked.',
                        code='no_author_search_destination'
                    )
            return self.cleaned_data


