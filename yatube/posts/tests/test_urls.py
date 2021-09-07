from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()


class PostsURLTests(TestCase):
    """
    Тесты внутри класса:
      1.Проверка подключения шаблонов
      2.Проверка доступа неавторизованного пользоватяли
      3.Проверка доступа авторизованного автора поста
      4.Проверка доступа авторизованного не автора
      5.Проверка редиректа гостя на страницу авторизации
        при создании и редактировании поста
      6.Проверка редиректа не автора поста
        из редактирования поста на просмотр
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')

        cls.not_author = User.objects.create_user(username='NotAuthor')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug-group',
            description='test-description'
        )
        # Создаем тестовый объект Post
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.not_author)

        cache.clear()

    def test_urls_uses_corrent_template(self):
        template_url_name = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for adress, template in template_url_name.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_quest_client(self):
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug-group/': 200,
            '/profile/TestAuthor/': 200,
            '/create/': 302,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/unexisting_page/': 404,
            '/follow/': 302,  # Ок!!!
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_client_with_post(self):
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug-group/': 200,
            '/profile/TestAuthor/': 200,
            '/create/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 200,
            '/unexisting_page/': 404,
            '/follow/': 200,
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_client_no_post(self):
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug-group/': 200,
            '/profile/TestAuthor/': 200,
            '/create/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/unexisting_page/': 404,
            '/follow/': 200,
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.another_authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_redirect_quest_client(self):
        url_and_redirect_way = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/follow/': '/auth/login/?next=/follow/'
        }
        for url, redirect_way in url_and_redirect_way.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_way)

    def test_redirect_authorized_client_no_post(self):
        url_and_redirect_way = {
            '/posts/1/edit/': '/posts/1/',
        }
        for url, redirect_way in url_and_redirect_way.items():
            with self.subTest(url=url):
                response = self.another_authorized_client.get(url, follow=True)
                self.assertRedirects(response, redirect_way)

    def test_urls_comment(self):
        comment_data = {
            'text': 'Первый коммент',
        }

        comment_response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_data,
            follow=True
        )

        self.assertRedirects(
            comment_response, reverse('posts:post_detail',
                                      kwargs={'post_id': self.post.id}))

    def test_urls_follow_unfollow(self):
        follow_response = self.another_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.not_author.username}))

        self.assertRedirects(
            follow_response, reverse(
                'posts:profile',
                kwargs={'username': self.not_author.username}))

        unfollow_response = self.another_authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.not_author.username}))

        self.assertRedirects(
            unfollow_response, reverse(
                'posts:profile',
                kwargs={'username': self.not_author.username}))
