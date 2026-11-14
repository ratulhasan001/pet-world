from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'image', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price


class EditPostForm(PostForm):

    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'image', 'price']


class CommentForm(forms.ModelForm):
    # The commenter's name and email are taken from their account.
    class Meta:
        model = Comment
        fields = ['body']
        labels = {'body': 'Comment'}
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}
