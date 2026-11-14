from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView

from user_profile.models import Profile

from .forms import DepositForm
from .models import Transaction


class DepositView(LoginRequiredMixin, CreateView):
    template_name = 'deposit.html'
    model = Transaction
    form_class = DepositForm
    success_url = reverse_lazy('profile')

    def get_profile(self):
        # Users created outside the sign-up form (e.g. createsuperuser) get a
        # profile on first use.
        if not hasattr(self, '_profile'):
            self._profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return self._profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.get_profile()
        })
        return kwargs

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.get_profile()
        with transaction.atomic():
            account.balance += amount
            account.save(update_fields=['balance'])
            response = super().form_valid(form)
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        return response
