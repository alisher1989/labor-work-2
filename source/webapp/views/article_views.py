from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect

from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, \
    UpdateView, DeleteView, FormView

from webapp.forms import ArticleForm, ArticleCommentForm, SimpleSearchForm, FullSearchForm
from webapp.models import Article, Tag
from django.core.paginator import Paginator



class IndexView(ListView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 3
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if 'tag' in self.request.GET:
            context[self.context_object_name] = Article.objects.filter(tags__name=self.request.GET.get('tag'))
        if self.search_value:
            context['query'] = urlencode({'search': self.search_value})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_value:
            query = Q(title__icontains=self.search_value) | Q(author__icontains=self.search_value)\
                    | Q(tags__name__iexact=self.search_value)
            queryset = queryset.filter(query)
        return queryset

    def get_search_form(self):
        return SimpleSearchForm(self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']
        return None


class ArticleView(DetailView):
    template_name = 'article/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['form'] = ArticleCommentForm()
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


class ArticleCreateView(CreateView):
    form_class = ArticleForm
    model = Article
    template_name = 'article/create.html'
    key_kwarg = 'pk'
    redirect_url = 'article_view'


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('webapp:article_view', kwargs={self.key_kwarg: self.object.pk})

    def form_valid(self, form):
        self.object = form.save()
        self.add_tags()
        return redirect(self.get_success_url())

    def add_tags(self):
        tags = self.request.POST.get('tags').split(',')
        for tag in tags:
            tag, _ = Tag.objects.get_or_create(name=tag)
            self.object.tags.add(tag)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'article/update.html'
    form_class = ArticleForm
    context_object_name = 'article'

    def get_success_url(self):
        return reverse('webapp:article_view', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save()
        self.get_form()
        self.tag_clear()
        return redirect(self.get_success_url())

    def add_tags(self):
        tags = self.request.POST.get('tags').split(',')
        for tag in tags:
            tag, _ = Tag.objects.get_or_create(name=tag)
            self.object.tags.add(tag)

    def tag_clear(self):
        clear = self.object.tags.clear()
        self.add_tags()
        return clear

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        tags = list(self.object.tags.all().values('name'))
        tags_str = ''
        for tag in tags:
            tags_str += tag['name'] + ','
        form.fields['tags'].initial = tags_str[:-1]
        return form


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('webapp:index')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class ArticleSearchView(FormView):
    template_name = 'article/search.html'
    form_class = FullSearchForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        print(text)
        author = form.cleaned_data.get('author')
        a = Q(Article.objects.filter(author__exact=author))
        print(a)
        query = self.get_text_search_query(form, text)
        query_author = self.get_author_search_query(form, author)
        context = self.get_context_data(form=form)
        context['articles'] = Article.objects.filter(query, query_author).distinct()
        return self.render_to_response(context=context)


    def get_text_search_query(self, form, text):
        query = Q()
        if text:
            in_title = form.cleaned_data.get('in_title')
            if in_title:
                query = query | Q(title__icontains=text)
            in_text = form.cleaned_data.get('in_text')
            if in_text:
                query = query | Q(text__icontains=text)
            in_tags = form.cleaned_data.get('in_tags')
            if in_tags:
                query = query | Q(tags__name__iexact=text)
            in_comment_text = form.cleaned_data.get('in_comment_text')
            if in_comment_text:
                query = query | Q(comments__text__icontains=text)
        return query

    def get_author_search_query(self, form, author):
        query_author = Q()
        if author:
            in_articles = form.cleaned_data.get('in_articles')
            if in_articles:
                query_author = query_author | Q(Article.objects.filter(author__exact=author))
            in_comments = form.cleaned_data.get('in_comments')
            if in_comments:
                query_author = query_author | Q(comments__author__icontains=author)
        return query_author