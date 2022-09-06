from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст сообщения",
            "group": "Сообщество",
            "image": "Картинки поста",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Текст комментария"}
