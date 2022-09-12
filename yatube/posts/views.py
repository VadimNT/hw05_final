from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post, User


class IndexView(ListView):
    template_name = "posts/index.html"
    paginate_by = settings.NUMS_OF_POSTS_ON_PAGE
    model = Post

    def get_queryset(self):
        return self.model.objects.prefetch_related("author", "group")


class GroupPostsView(ListView):
    model = Group
    paginate_by = settings.NUMS_OF_POSTS_ON_PAGE
    template_name = "posts/group_list.html"

    def get_queryset(self):
        return get_object_or_404(
            self.model,
            slug=self.kwargs.get('slug')
        ).posts.select_related("author")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(
            self.model,
            slug=self.kwargs.get('slug')
        )
        return context


class ProfileView(ListView):
    model = Post
    paginate_by = settings.NUMS_OF_POSTS_ON_PAGE
    template_name = "posts/profile.html"
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, **kwargs)

    def get_queryset(self):
        return get_object_or_404(
            User, username=self.kwargs.get('username')
        ).posts.prefetch_related("group")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        context["author"] = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        context["following"] = Follow.objects.filter(
            user=self.user,
            author=author
        ).exists()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = 'post'
    pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data()
        context["count"] = self.model.objects.filter(
            author=context["post"].author
        ).count()
        context["comments"] = Comment.objects.filter(
            post=context['post']
        ).all()
        context["form_comment"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "posts/create_post.html"
    context_object_name = "form"
    form_class = PostForm
    context = {}

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST or None,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", request.user)
        self.context["form"] = form
        return render(request, self.template_name, self.context)


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_id"
    template_name = "posts/create_post.html"
    context_object_name = "post"
    context = {}

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if request.user != obj.author:
            return redirect(
                "posts:post_edit",
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "posts:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    pk_url_kwarg = "post_id"
    template_name = "posts/post_detail.html"
    form_class = CommentForm
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["count"] = self.model.objects.filter(
            author=context["post"].author
        ).count()
        context["comments"] = Comment.objects.filter(
            post=context['post']
        ).all()
        context["form_comment"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        comment.save()
        return redirect("posts:post_detail", post_id=self.kwargs["post_id"])


class FollowIndexView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = settings.NUMS_OF_POSTS_ON_PAGE
    user = None
    template_name = "posts/follow.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(author__following__user=self.user)


class ProfileFollowView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        author = get_object_or_404(User, username=self.kwargs["username"])
        if request.user != author:
            Follow.objects.get_or_create(user=request.user, author=author)
        return redirect("posts:profile", username=self.kwargs["username"])


class ProfileUnfollowView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        author = get_object_or_404(User, username=self.kwargs["username"])
        if request.user != author:
            Follow.objects.filter(user=request.user, author=author).delete()
        return redirect("posts:profile", username=self.kwargs["username"])
