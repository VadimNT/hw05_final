from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from posts.utils import get_paginator


def index(request):
    posts = Post.objects.prefetch_related("author", "group")
    page_obj = get_paginator(request, posts)
    return render(request, "posts/index.html", {"page_obj": page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author")
    page_obj = get_paginator(request, posts)
    return render(
        request,
        "posts/group_list.html",
        {"group": group, "page_obj": page_obj},
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.prefetch_related("group")
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    page_obj = get_paginator(request, posts)
    return render(
        request,
        "posts/profile.html",
        {"page_obj": page_obj, "author": author, "following": following},
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    form_comment = CommentForm(request.POST or None)
    if form_comment.is_valid():
        form_comment.save()
        return redirect("posts:post_detail", post.id)
    return render(
        request,
        "posts/post_detail.html",
        {
            "count": count,
            "post": post,
            "comments": comments,
            "form_comment": form_comment,
        },
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post.id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.id)
    return render(
        request, "posts/create_post.html", {"post": post, "form": form}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, posts)
    return render(request, "posts/follow.html", {"page_obj": page_obj})


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    if request.user != author and not following:
        Follow.objects.create(user=request.user, author=author).save()
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
