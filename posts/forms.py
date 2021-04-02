from django import forms

from .models import Post, Comment, Follow


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widget = {'text': forms.Textarea(attrs={'cols': 80, 'rows': 20})}


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ('user', 'author')
