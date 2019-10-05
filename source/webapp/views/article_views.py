from django.shortcuts import render, get_object_or_404, redirect
from webapp.forms import ArticleForm, CommentArticleForm
from webapp.models import Article, Comment
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator



class IndexView(ListView):
    template_name = 'article/index.html'
    model = Article
    context_object_name = 'articles'
    ordering = ['-created_at']
    paginate_by = 3
    paginate_orphans = 1




    # def get_queryset(self):
    #     return super().get_queryset().order_by('-created_at')


class ArticleView(DetailView):
    template_name = 'article/article.html'
    pk_url_kwarg = 'article_pk'
    model = Article

    class ArticleView(TemplateView):
        template_name = 'article/article.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            pk = kwargs.get('pk')
            article = get_object_or_404(Article, pk=pk)
            context['article'] = article
            context['form'] = CommentArticleForm()
            comments = article.comments.order_by('-created_at')
            self.paginate_comments_to_context(comments, context)
            return context

        def paginate_comments_to_context(self, comments, context):
            paginator = Paginator(comments, 3, 0)
            page_number = self.request.GET.get('page', 1)
            page = paginator.get_page(page_number)
            context['paginator'] = paginator
            context['page_obj'] = page
            context['comments'] = page.object_list
            context['is_paginated'] = page.has_other_pages()
            return context



class ArticleCreateView(View):
    def get(self, request, *args, **kwargs):
        form = ArticleForm()
        return render(request, 'article/create.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        form = ArticleForm(data=request.POST)
        if form.is_valid():
            article = Article.objects.create(
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author'],
                text=form.cleaned_data['text'],
                category=form.cleaned_data['category']
            )
            return redirect('article_view', pk=article.pk)
        else:
            return render(request, 'article/create.html', context={'form': form})


class ArticleUpdateView(View):
    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs.get('pk'))
        form = ArticleForm(data={
            'title': article.title,
            'author': article.author,
            'text': article.text,
            'category': article.category_id
        })
        return render(request, 'article/update.html', context={'form': form, 'article': article})

    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs.get('pk'))
        form = ArticleForm(data=request.POST)
        if form.is_valid():
            article.title = form.cleaned_data['title']
            article.author = form.cleaned_data['author']
            article.text = form.cleaned_data['text']
            article.category = form.cleaned_data['category']
            article.save()
            return redirect('article_view', pk=article.pk)
        else:
            return render(request, 'article/update.html', context={'form': form, 'article': article})



class ArticleDeleteView(View):
    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs.get('pk'))
        return render(request, 'article/delete.html', context={'article': article})

    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs.get('pk'))
        article.delete()
        return redirect('index')