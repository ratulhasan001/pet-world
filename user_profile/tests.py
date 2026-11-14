import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from category.models import Category
from posts.models import Post

from .models import Profile


class RegistrationTests(TestCase):
    def test_register_sends_activation_link(self):
        response = self.client.post(reverse('register'), {
            'username': 'newbie', 'first_name': 'New', 'last_name': 'Bie',
            'email': 'newbie@example.com', 'contact_number': '01700000000',
            'address': 'Dhaka', 'password1': 'pass-12345-word', 'password2': 'pass-12345-word',
        })
        self.assertRedirects(response, reverse('homepage'))
        user = User.objects.get(username='newbie')
        self.assertFalse(user.is_active)
        self.assertEqual(user.profile.contact_number, '01700000000')
        self.assertEqual(len(mail.outbox), 1)

        link = re.search(r'http://testserver(\S+)', mail.outbox[0].body).group(1)
        response = self.client.get(link)
        self.assertRedirects(response, reverse('homepage'))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_invalid_activation_link(self):
        response = self.client.get(reverse('activate', args=['bad', 'token']))
        self.assertRedirects(response, reverse('register'))


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')

    def test_login_and_post_only_logout(self):
        response = self.client.post(reverse('user_login'), {'username': 'sam', 'password': 'pass-12345-word'})
        self.assertRedirects(response, reverse('homepage'))
        self.assertEqual(self.client.get(reverse('user_logout')).status_code, 405)
        response = self.client.post(reverse('user_logout'))
        self.assertRedirects(response, reverse('homepage'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_pages_require_login(self):
        for name in ('profile', 'edit_profile', 'pass_change', 'add_post', 'deposit_money'):
            response = self.client.get(reverse(name))
            self.assertRedirects(response, f"{reverse('user_login')}?next={reverse(name)}",
                                 msg_prefix=name)

    def test_edit_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('edit_profile'), {
            'username': 'sam', 'first_name': 'Sam', 'last_name': 'Lee', 'email': 'sam@example.com',
            'contact_number': '0123', 'address': 'Chittagong',
        })
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(Profile.objects.get(user=self.user).address, 'Chittagong')


class PageSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sam', 'sam@example.com', 'pass-12345-word')
        Profile.objects.create(user=self.user, balance=100)
        category = Category.objects.create(name='Dogs', slug='dogs')
        # No image: pages must still render.
        self.pet = Post.objects.create(author=self.user, title='Rex', description='Dog', category=category, price=10)

    def test_public_pages(self):
        urls = [reverse('homepage'), reverse('cat_wise_post', args=['dogs']),
                reverse('post_details', args=[self.pet.id]), reverse('user_login'),
                reverse('register'), reverse('password_reset')]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get(reverse('cat_wise_post', args=['nope'])).status_code, 404)

    def test_logged_in_pages(self):
        self.client.force_login(self.user)
        urls = [reverse('homepage'), reverse('profile'), reverse('edit_profile'), reverse('pass_change'),
                reverse('add_post'), reverse('edit_post', args=[self.pet.id]), reverse('deposit_money'),
                reverse('post_details', args=[self.pet.id])]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
