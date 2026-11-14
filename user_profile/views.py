from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import FormView
from django.contrib.auth.views import LoginView

from posts.models import Post
from user_profile.models import Profile

from .forms import ChangeUserForm, RegistrationForm


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('homepage')


@require_POST
def user_logout(request):
    # Logout is POST-only (as required by Django 5's LogoutView).
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('homepage')


class UserRegistrationView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('homepage')

    def form_valid(self, form):
        user = form.save()
        # The account stays inactive until the emailed link is opened.
        user.is_active = False
        user.save(update_fields=['is_active'])

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'protocol': self.request.scheme,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        email = EmailMessage(mail_subject, message, to=[form.cleaned_data.get('email')])
        email.send()

        messages.success(self.request, 'Please confirm your email address to complete the registration')
        return super().form_valid(form)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully')
        return redirect('homepage')
    else:
        messages.warning(request, 'Activation link is invalid!')
        return redirect('register')


class UserProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'edit_profile.html'

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ChangeUserForm(instance=request.user, initial={
            'address': profile.address,
            'contact_number': profile.contact_number,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    data = Post.objects.filter(buyers=request.user)
    data2 = Post.objects.filter(author=request.user)
    return render(request, "profile.html", {'data': data, 'data2': data2})


@login_required
def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Updated Successfully')
            update_session_auth_hash(request, form.user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'pass_change.html', {'form': form})
