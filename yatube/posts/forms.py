from django import forms
from django.forms.widgets import Textarea
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea,
        }


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        widgets = {
            'text: TextArea',
        }
