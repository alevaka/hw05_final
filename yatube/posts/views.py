from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    posts = Paginator(post_list, POSTS_PER_PAGE)
    template = 'posts/index.html'
    page_number = request.GET.get('page')
    page_obj = posts.get_page(page_number)
    context = {'page_obj': page_obj,
               }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {'group': group,
               'page_obj': page_obj,
               }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(
            author=User.objects.get(username=author)).count()
    context = {'author': author,
               'page_obj': page_obj,
               'posts_count': post_list.count,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = Post.objects.filter(author=post.author)
    comments_list = Comment.objects.filter(post=post)
    form = CommentForm()
    context = {'post': post,
               'posts_count': post_list.count,
               'comments': comments_list,
               'form': form
               }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {'form': form,
               }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', username=request.user)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = request.user
    if username == post.author:
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post
                        )
        context = {'form': form,
                   'is_edit': True,
                   }
        if not form.is_valid():
            return render(request, 'posts/create_post.html', context)
        form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    user = request.user
    author_pk_list = user.follower.all().values_list('author', flat=True)
    post_list = Post.objects.filter(author__in=author_pk_list)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'username': user,
               'page_obj': page_obj,
               }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_to_delete = get_object_or_404(
        Follow,
        user=user,
        author=author
    )
    follow_to_delete.delete()
    return redirect('posts:profile', username=username)
