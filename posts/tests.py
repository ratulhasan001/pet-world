from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from category.models import Category
from user_profile.models import Profile

from .models import Comment, Post


def make_user(username, balance=0):
    user = User.objects.create_user(username, f'{username}@example.com', 'pass-12345-word')
    Profile.objects.create(user=user, balance=balance)
    return user


class AdoptionTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.adopter = make_user('adopter', balance=500)
        self.category = Category.objects.create(name='Dogs', slug='dogs')
        self.pet = Post.objects.create(
            author=self.owner, title='Rex', description='Friendly dog',
            category=self.category, price=300,
        )
        self.url = reverse('adopt_pet', args=[self.pet.id])

    def refresh(self):
        self.pet.refresh_from_db()
        self.adopter.profile.refresh_from_db()

    def test_adopt_success(self):
        self.client.force_login(self.adopter)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('post_details', args=[self.pet.id]))
        self.refresh()
        self.assertFalse(self.pet.is_available)
        self.assertIn(self.adopter, self.pet.buyers.all())
        self.assertEqual(self.adopter.profile.balance, Decimal('200'))

    def test_adopt_requires_login(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f"{reverse('user_login')}?next={self.url}")
        self.refresh()
        self.assertTrue(self.pet.is_available)

    def test_adopt_rejects_get(self):
        self.client.force_login(self.adopter)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.refresh()
        self.assertTrue(self.pet.is_available)

    def test_adopt_with_insufficient_balance(self):
        poor = make_user('poor', balance=100)
        self.client.force_login(poor)
        self.client.post(self.url)
        self.refresh()
        poor.profile.refresh_from_db()
        self.assertTrue(self.pet.is_available)
        self.assertEqual(poor.profile.balance, 100)

    def test_cannot_adopt_twice(self):
        self.client.force_login(self.adopter)
        self.client.post(self.url)
        self.client.post(self.url)
        self.refresh()
        self.assertEqual(self.adopter.profile.balance, Decimal('200'))

    def test_cannot_adopt_own_pet(self):
        self.owner.profile.balance = 1000
        self.owner.profile.save()
        self.client.force_login(self.owner)
        self.client.post(self.url)
        self.refresh()
        self.owner.profile.refresh_from_db()
        self.assertTrue(self.pet.is_available)
        self.assertEqual(self.owner.profile.balance, 1000)

    def test_missing_pet_returns_404(self):
        self.client.force_login(self.adopter)
        self.assertEqual(self.client.post(reverse('adopt_pet', args=[999])).status_code, 404)


class CommentTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.adopter = make_user('adopter', balance=500)
        category = Category.objects.create(name='Cats', slug='cats')
        self.pet = Post.objects.create(
            author=self.owner, title='Tom', description='Cat', category=category, price=100,
        )
        self.url = reverse('post_details', args=[self.pet.id])

    def test_adopter_can_comment(self):
        self.pet.buyers.add(self.adopter)
        self.client.force_login(self.adopter)
        response = self.client.post(self.url, {'body': 'Lovely cat'})
        self.assertRedirects(response, self.url)
        comment = Comment.objects.get()
        self.assertEqual(comment.name, 'adopter')
        self.assertEqual(comment.email, 'adopter@example.com')

    def test_non_adopter_is_redirected_back(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {'body': 'Spam'})
        self.assertRedirects(response, self.url)
        self.assertFalse(Comment.objects.exists())

    def test_anonymous_cannot_comment(self):
        response = self.client.post(self.url, {'body': 'Spam'})
        self.assertRedirects(response, reverse('user_login'))
        self.assertFalse(Comment.objects.exists())


class ListingOwnershipTests(TestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.category = Category.objects.create(name='Birds', slug='birds')
        self.pet = Post.objects.create(
            author=self.owner, title='Polly', description='Parrot', category=self.category, price=50,
        )

    def test_add_post(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('add_post'), {
            'title': 'Kiwi', 'description': 'Small bird', 'category': self.category.id, 'price': 20,
        })
        post = Post.objects.get(title='Kiwi')
        self.assertRedirects(response, reverse('post_details', args=[post.id]))
        self.assertEqual(post.author, self.owner)

    def test_negative_price_rejected(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('add_post'), {
            'title': 'Kiwi', 'description': 'Small bird', 'category': self.category.id, 'price': -5,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='Kiwi').exists())

    def test_only_owner_can_edit_or_delete(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('edit_post', args=[self.pet.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('delete_post', args=[self.pet.id])).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.pet.pk).exists())

    def test_owner_can_delete_with_post_only(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('delete_post', args=[self.pet.id])).status_code, 405)
        response = self.client.post(reverse('delete_post', args=[self.pet.id]))
        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Post.objects.filter(pk=self.pet.pk).exists())
