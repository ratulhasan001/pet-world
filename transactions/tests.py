from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from user_profile.models import Profile

from .models import Transaction


class DepositTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')
        Profile.objects.create(user=self.user, balance=10)

    def test_deposit_requires_login(self):
        response = self.client.post(reverse('deposit_money'), {'amount': 50})
        self.assertRedirects(response, f"{reverse('user_login')}?next={reverse('deposit_money')}")
        self.assertFalse(Transaction.objects.exists())

    def test_deposit_adds_to_balance(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('deposit_money'), {'amount': '40.50'})
        self.assertRedirects(response, reverse('profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, Decimal('50.50'))
        self.assertEqual(Transaction.objects.get().balance_after_transaction, Decimal('50.50'))

    def test_non_positive_deposit_rejected(self):
        self.client.force_login(self.user)
        for amount in (0, -20):
            response = self.client.post(reverse('deposit_money'), {'amount': amount})
            self.assertContains(response, 'Amount must be greater than zero')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, 10)

    def test_user_without_profile_can_deposit(self):
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin-pass-123')
        self.client.force_login(admin)
        self.client.post(reverse('deposit_money'), {'amount': 5})
        self.assertEqual(Profile.objects.get(user=admin).balance, 5)
