from django.shortcuts import render, get_object_or_404, redirect
from webapp.forms import CommentForm, CommentArticleForm
from webapp.models import Comment
from django.views import View
from django.views.generic import TemplateView

class CommentsView(TemplateView):
    template_name = 'comments/comments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = Comment.objects.all().order_by('-created_at')
        print(Comment.objects.all().order_by('-created_at'))
        return context


class CommentCreateView(View):
    def get(self, request, *args, **kwargs):
        form = CommentForm()
        return render(request, 'comments/create.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                author=form.cleaned_data['author'],
                text=form.cleaned_data['text'],
                article=form.cleaned_data['article']
            )
            return redirect('article_view', pk=comment.article.pk)
        else:
            return render(request, 'comments/create.html', context={'form': form})


class NewCommentCreateView(View):

    def post(self, request, *args, **kwargs):
        form = CommentArticleForm(data=request.POST)
        if form.is_valid():
            comment = Comment.objects.create(
                author=form.cleaned_data['author'],
                text=form.cleaned_data['text'],
                article_id=kwargs.get('pk')
            )
            return redirect('article_view', pk=comment.article.pk)
        else:
            return render(request, 'comments/create.html', context={'form': form})


class CommentUpdateView(View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        form = CommentForm(data={
            'author': comment.author,
            'text': comment.text,
            'article': comment.article_id
        })
        return render(request, 'comments/update.html', context={'form': form, 'comment': comment})

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment.author = form.cleaned_data['author']
            comment.text = form.cleaned_data['text']
            comment.article = form.cleaned_data['article']
            comment.save()
            return redirect('article_view', pk=comment.article.pk)
        else:
            return render(request, 'comments/update.html', context={'form': form, 'comment': comment})



class CommentDeleteView(View):
    def get(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk)
        return render(request, 'comments/delete.html', context={'comment': comment})


    def post(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk)
        try:
            comment.delete()
            return redirect('comment_view')
        except:
            return render(request, 'comments/comments.html')