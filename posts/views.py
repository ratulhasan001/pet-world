from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from user_profile.models import Profile

from . import forms
from .models import Post


@login_required
def add_post(request):
    if request.method == 'POST':
        post_form = forms.PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            post_form.save_m2m()
            messages.success(request, 'Your pet has been listed for adoption.')
            return redirect('post_details', id=post.id)
    else:
        post_form = forms.PostForm()
    return render(request, 'add_post.html', {'form': post_form, 'title': 'List a Pet'})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    if post.author != request.user:
        return HttpResponseForbidden('You can only edit your own listings.')
    if request.method == 'POST':
        post_form = forms.EditPostForm(request.POST, request.FILES, instance=post)
        if post_form.is_valid():
            post_form.save()
            messages.success(request, 'Listing updated.')
            return redirect('post_details', id=post.id)
    else:
        post_form = forms.EditPostForm(instance=post)
    return render(request, 'add_post.html', {'form': post_form, 'title': 'Edit Listing'})


@login_required
@require_POST
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)
    if post.author != request.user:
        return HttpResponseForbidden('You can only delete your own listings.')
    post.delete()
    messages.success(request, 'Listing deleted.')
    return redirect('profile')


class DetailPostView(DetailView):
    model = Post
    pk_url_kwarg = 'id'
    template_name = 'post_details.html'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if not request.user.is_authenticated:
            return redirect('user_login')
        if not post.buyers.filter(pk=request.user.pk).exists():
            messages.error(request, 'Only the adopter of this pet can comment on it.')
            return redirect('post_details', id=post.id)

        comment_form = forms.CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.name = request.user.get_full_name() or request.user.username
            new_comment.email = request.user.email
            new_comment.save()
            messages.success(request, 'Your comment has been added.')
            return redirect('post_details', id=post.id)

        self.object = post
        context = self.get_context_data(object=post)
        context['comment_form'] = comment_form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user
        context['comments'] = post.comments.order_by('-created_on')
        context['comment_form'] = forms.CommentForm()
        context['can_comment'] = user.is_authenticated and post.buyers.filter(pk=user.pk).exists()
        return context


@login_required
@require_POST
def update_pet(request, id):
    """Adopt a pet: pay its price from the user's balance."""
    post = get_object_or_404(Post, pk=id)

    if post.author == request.user:
        messages.error(request, 'You cannot adopt your own pet.')
        return redirect('post_details', id=post.id)

    with transaction.atomic():
        post = Post.objects.select_for_update().get(pk=post.pk)
        profile, _ = Profile.objects.select_for_update().get_or_create(user=request.user)

        if not post.is_available:
            messages.error(request, 'This pet has already been adopted.')
            return redirect('post_details', id=post.id)
        if profile.balance < post.price:
            messages.error(
                request,
                f'Insufficient balance. {post.title} costs {post.price}$ and you have {profile.balance}$.'
            )
            return redirect('post_details', id=post.id)

        profile.balance -= post.price
        profile.save(update_fields=['balance'])
        post.is_available = False
        post.save(update_fields=['is_available'])
        post.buyers.add(request.user)

    messages.success(request, f'You adopted {post.title}!')
    return redirect('post_details', id=post.id)
