from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestAuthor')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug-group',
            description='test-description'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_create_post(self):
        posts_count = Post.objects.count()

        post_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username':
                                                       self.user.username}))

        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=self.user,
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        post_test1 = Post.objects.filter(id=1)

        post_data = {
            'text': 'Исправленный текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=post_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}))

        edit_post = Post.objects.filter(id=1)
        self.assertNotEqual(post_test1, edit_post)
