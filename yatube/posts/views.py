from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()

NUM_POSTS_NEED: int = 10


def paginator_page(request, list, num):
    pag = Paginator(list, num)
    page_num = request.GET.get('page')
    page_with_pag = pag.get_page(page_num)
    return page_with_pag


def index(request):
    '''Главная страница'''
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = paginator_page(request, posts, NUM_POSTS_NEED)
    follow_index = True
    context = {
        'page_obj': page_obj,
        'follow_index': follow_index,
    }
    return render(request, template, context)


def group_posts(request, slug):
    '''Вывод списка для определенной группы'''
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page(request, posts, NUM_POSTS_NEED)
    template = 'posts/group_list.html'
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_page(request, posts, NUM_POSTS_NEED)
    template = 'posts/profile.html'
    followers = (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author
        ).exists())
    context = {
        'page_obj': page_obj,
        'author': author,
        'followers': followers,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(None)
    comments = post.comments.all()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False
    }

    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/create_post.html'
    if request.user != post.author:
        return redirect('posts:post_detail',
                        post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'is_edit': True
    }

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_page(request, posts, NUM_POSTS_NEED)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=user, author=author)
    if user != author and not follower.exists():
        Follow.objects.get_or_create(
            user=user, author=author
        )
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    follower.delete()
    return redirect('posts:profile', author.username)
