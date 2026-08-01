from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import Post, Comment, Category
from .forms import NewCommentForm, PostSearchForm
from django.views.generic import ListView
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.core import serializers
from django.http import JsonResponse


def home(request):
    posts = list(Post.newmanager.all()[:6])
    featured_post = posts[0] if posts else None
    recent_posts = posts[1:] if len(posts) > 1 else []
    categories = Category.objects.exclude(name='default').order_by('name')
    popular_posts = Post.newmanager.order_by('-views', '-publish')[:3]

    return render(request, 'index.html', {
        'posts': recent_posts,
        'featured_post': featured_post,
        'categories': categories,
        'popular_posts': popular_posts,
    })


@login_required
def saved_posts(request):
    posts = Post.newmanager.filter(saved_by=request.user).order_by('-publish')
    return render(request, 'saved_posts.html', {'posts': posts})


def post_single(request, post):
    post = get_object_or_404(Post, slug=post, status='published')

    viewed_posts = request.session.get('viewed_posts', [])
    liked_posts = request.session.get('liked_posts', [])
    saved_posts = request.session.get('saved_posts', [])
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'like':
            if post.id in liked_posts:
                liked_posts.remove(post.id)
            else:
                liked_posts.append(post.id)
            request.session['liked_posts'] = liked_posts
        elif action == 'save':
            if request.user.is_authenticated:
                if post.saved_by.filter(pk=request.user.pk).exists():
                    post.saved_by.remove(request.user)
                else:
                    post.saved_by.add(request.user)
            if post.id in saved_posts:
                saved_posts.remove(post.id)
            else:
                saved_posts.append(post.id)
            request.session['saved_posts'] = saved_posts

    if post.id not in viewed_posts:
        Post.objects.filter(pk=post.pk).update(views=post.views + 1)
        post.views += 1
        viewed_posts.append(post.id)
        request.session['viewed_posts'] = viewed_posts

    allcomments = post.comments.filter(status=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(allcomments, 3)

    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.post = post
            user_comment.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        comment_form = NewCommentForm()

    related_posts = Post.newmanager.filter(category=post.category).exclude(id=post.id)[:3]

    return render(request, 'single.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'allcomments': allcomments,
        'related_posts': related_posts,
        'liked': post.id in liked_posts,
        'saved': post.id in saved_posts or (request.user.is_authenticated and post.saved_by.filter(pk=request.user.pk).exists()),
    })


class CatListView(ListView):
    template_name = 'category.html'
    context_object_name = 'catlist'

    def get_queryset(self):
        content = {
            'cat': self.kwargs['category'],
            'posts': Post.objects.filter(category__name=self.kwargs['category']).filter(status='published')
        }
        return content


def category_list(request):
    category_list = Category.objects.exclude(name='default')
    context = {
        "category_list": category_list,
    }
    return context


def post_search(request):
    form = PostSearchForm()
    q = ''
    c = ''
    results = []
    query = Q()

    if request.POST.get('action') == 'post':
        search_string = request.POST.get('ss', '').strip()
        if search_string:
            matches = Post.newmanager.filter(title__icontains=search_string)[:5]
            suggestions = [
                {
                    'id': post.id,
                    'title': post.title,
                    'slug': post.slug,
                    'url': post.get_absolute_url(),
                }
                for post in matches
            ]
            return JsonResponse({'search_string': suggestions}, safe=False)

    if 'q' in request.GET:
        form = PostSearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            c = form.cleaned_data['c']

        if c is not None:
            query &= Q(category=c)
        if q is not None:
            query &= Q(title__icontains=q)

        results = Post.newmanager.filter(query)

    return render(request, 'search.html', {
        'form': form,
        'q': q,
        'results': results,
    })
