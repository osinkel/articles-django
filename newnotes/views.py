from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from .models import Article, Category, ArticleCategoryRelation
from django.utils import timezone
from .forms import UserRegistrationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import View
from django.views.generic import ListView
import json
from django.http import JsonResponse
from django.template.loader import render_to_string

items_on_page = 3


def index(request):
    article_list = Article.objects.all()[:items_on_page]
    categories = Category.objects.all()
    return render(request, 'articles/main.html', {'all_articles': article_list,
                                                  'categories': categories,
                                                  'is_admin': request.user.is_staff, })


class ArticleListView(ListView):

    def get(self, request, **kwargs):
        user = request.user
        if user.groups.filter(name='admin').count():
            is_admin = True
        article_list = Article.objects.all()
        current_page = Paginator(article_list, items_on_page)
        page = request.GET.get('page')
        try:
            page_articles = current_page.page(page)
        except:
            page_articles = current_page.page(1)

        data = json.dumps(list(Article.objects.values_list('id', 'title')))
        categories = Category.objects.all()
        return render(request, 'articles/list.html',
                      {'all_articles': page_articles, 'is_admin': request.user.is_staff, 'qs_json': data,
                       'categories': categories, })


def create_article(request):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')

    if request.method == 'POST':
        try:
            category_choices = [x for x in request.POST.getlist('category')]
            category_list = [Category.objects.get(id=category_id) for category_id in category_choices]
        except:
            raise Http404('Категория не найдена!')
        request.user.article_set.create(title=request.POST['title'], text=request.POST['text'], date=timezone.now())
        current_article = Article.objects.all()[0]
        for category in category_list:
            category.includes_article.add(current_article)
        return redirect('/')
    category_list = Category.objects.all()
    return render(request, 'articles/create.html', {'category_list': category_list})


def update_article(request, article_id):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')

    current_article = Article.objects.get(id=article_id)
    if not current_article:
        raise Http404('Статья не найдена!')

    if request.method == 'POST':

        # try:
        #     category_choices = [x for x in request.POST.getlist('category')]
        #     category_list = [Category.objects.get(id=category_id) for category_id in category_choices]
        # except:
        #     raise Http404('Категория не найдена!')

        current_article.title=request.POST['title']
        current_article.text=request.POST['text']
        current_article.save()
        # ArticleCategoryRelation.objects.filter(article=current_article).delete()
        #
        # for category in category_list:
        #     category.includes_article.add(current_article)

        return redirect('/')

    category_list = Category.objects.all()
    category_of_article = ArticleCategoryRelation.objects.filter(article=current_article)

    return render(request, 'articles/update.html', {'category_list': category_list,
                                                    'article': current_article,
                                                    'article_category': category_of_article})


def leave_comment(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
    except:
        raise Http404('Статья не найдена!')
    article.comment_set.create(author=request.user, text=request.POST['text'], date=timezone.now())
    return HttpResponseRedirect(reverse('newnotes:view_article', args=(article.id,)))


def profile(request):
    if request.user.is_anonymous:
        raise Http404('Доступ запрещен!')

    categories = Category.objects.all()
    return render(request, 'account/profile.html', {'categories': categories, })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
        else:
            print(form.errors.as_data())
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def delete_article(request, article_id):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')
    try:
        article = Article.objects.get(id=article_id)
    except:
        raise Http404('Статья не найдена!')
    if request.method == "POST":
        article.delete()
        return redirect('/')
    return render(request, 'articles/delete.html', {'article': article})


def create_category(request):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')
    if request.method == 'POST':
        Category.objects.create(name=request.POST['name'])
        return redirect('/')
    category_list = Category.objects.all()
    return render(request, 'categories/create.html', {'category_list': category_list, })


def delete_category(request, category_id):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')
    try:
        category = Category.objects.get(id=category_id)
    except:
        raise Http404('Категория не найдена!')
    if request.method == "POST":
        category.delete()
        return redirect('/')
    category_list = Category.objects.all()
    return render(request, 'categories/delete.html', {'category': category, 'category_list': category_list, })


def update_category(request, category_id):
    if not request.user.is_staff:
        raise Http404('Доступ запрещен!')
    try:
        category = Category.objects.get(id=category_id)
    except:
        raise Http404('Категория не найдена!')

    if request.method == 'POST':
        Category.objects.filter(id=category_id).update(name=request.POST['name'])
        return redirect('/')
    category_list = Category.objects.all()
    return render(request, 'categories/update.html', {'category': category, 'category_list': category_list, })


class ListCategoryArticles(ListView):

    def get(self, request, category_id, **kwargs):
        rel_category_article = ArticleCategoryRelation.objects.filter(category=category_id).order_by('-id')
        category = Category.objects.all().get(id=category_id)
        article_list = [Article.objects.get(id=x.article.id) for x in rel_category_article]
        current_page = Paginator(article_list, items_on_page)
        page = request.GET.get('page')
        try:
            context = current_page.page(page)
        except:
            context = current_page.page(1)

        data = json.dumps(list(Article.objects.values_list('id', 'title')))
        categories = Category.objects.all()
        return render(request, 'categories/list.html',
                      {'all_articles': context, 'is_admin': request.user.is_staff, 'qs_json': data,
                       'categories': categories,
                       'category': category, })


def get_paginated_page(request, objects, number=items_on_page):
    current_page = Paginator(objects, number)
    page = request.GET.get('page') if request.method == 'GET' else request.POST.get('page')
    try:
        return current_page.page(page)
    except PageNotAnInteger:
        return current_page.page(1)
    except EmptyPage:
        return current_page.page(current_page.num_pages)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class ViewArticle(View):

    def get(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except:
            raise Http404('Статья не найдена!')
        list_comments = article.comment_set.order_by('-id')
        if not request.user.is_anonymous:
            article.readers.add(request.user)
        watched = article.readers.count()
        categories = Category.objects.all()
        return render(request, 'articles/view.html',
                      {'article': article, 'list_comments': get_paginated_page(request, list_comments),
                       'watched': watched, 'categories': categories, })

    def post(self, request, article_id):
        if is_ajax(request):
            try:
                article = Article.objects.get(id=article_id)
            except:
                raise Http404('Статья не найдена!')
            return JsonResponse({
                "result": True,
                "comms": render_to_string(
                    request=request,
                    template_name='articles/comms.html',
                    context={'list_comments': get_paginated_page(request, article.comment_set.order_by('-id'))}
                )
            })
        else:
            raise Http404()
