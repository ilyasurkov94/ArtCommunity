from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.core.cache import cache

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """
    Тесты внутри класса:
      1.URL использует правильный шаблон
      2.Шаблон index с правильным контекстом
      3.Шаблон group_list с правильным контентом
      4.Шаблон profile с правильным контентом
      5.Шаблон post_detail с правильным контентом
      6.Шаблон post_edit с правильной формой
      7.Шаблон post_create с правильной формой
      8.Пост с картинкой попадает в БД
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestAuthor')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug-group',
            description='test-description'
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={
                    'slug': 'test-slug-group'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                    'username': 'TestAuthor'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                    'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                    'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_content(self):
        response = self.authorized_client.get(reverse('posts:index'))

        first_post = response.context['page_obj'][0]

        post_data_expected = {
            first_post.text: 'Тестовый заголовок',
            first_post.author.username: 'TestAuthor',
            first_post.group.title: 'Тестовый заголовок группы',
            first_post.image: self.post.image
        }

        for data, expected in post_data_expected.items():
            with self.subTest(data=data):
                self.assertEqual(data, expected)

    def test_group_list_content(self):
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug': 'test-slug-group'
                                                      }
                                                      ))

        first_post = response.context['page_obj'][0]
        group_object = response.context['group']

        group_data_expected = {
            first_post.text: 'Тестовый заголовок',
            first_post.author.username: 'TestAuthor',
            first_post.group.title: 'Тестовый заголовок группы',
            group_object.title: 'Тестовый заголовок группы',
            first_post.image: self.post.image
        }

        for data, expected in group_data_expected.items():
            with self.subTest(data=data):
                self.assertEqual(data, expected)

    def test_profile_content(self):
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              'TestAuthor'}))

        first_post = response.context['page_obj'][0]
        author_object = response.context['author']
        posts_count_object = response.context['posts_count']

        profile_data_expected = {
            first_post.text: 'Тестовый заголовок',
            first_post.author.username: 'TestAuthor',
            first_post.group.title: 'Тестовый заголовок группы',
            author_object.username: 'TestAuthor',
            posts_count_object: 1,
            first_post.image: self.post.image
        }

        for data, expected in profile_data_expected.items():
            with self.subTest(data=data):
                self.assertEqual(data, expected)

    def test_post_detail_content(self):

        response = self.authorized_client.get(reverse(
                                              'posts:post_detail',
                                              kwargs={'post_id': '1'}))

        first_post = response.context['post']
        posts_count_object = response.context['author_posts_count']

        post_detail_data_expected = {
            first_post.text: 'Тестовый заголовок',
            first_post.author.username: 'TestAuthor',
            first_post.group.title: 'Тестовый заголовок группы',
            posts_count_object: 1,
            first_post.image: self.post.image
        }

        for data, expected in post_detail_data_expected.items():
            with self.subTest(data=data):
                self.assertEqual(data, expected)

    def test_post_edit_form(self):

        response = self.authorized_client.get(reverse(
                                              'posts:post_edit',
                                              kwargs={'post_id': '1'}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_form(self):
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """
    Тесты внутри класса:
      1.На первой странице index 10 постов
      2.На второй странице index три поста
      3.На первой странице group_list 10 постов
      4.На второй странице group_list три поста
      5.На первой странице profile 10 постов
      6.На второй странице profile три поста
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestAuthor')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug-group',
            description='test-description')

        NEEDED_POSTS = 13

        for number in range(NEEDED_POSTS):
            Post.objects.create(text='Тестовый заголовок{number}',
                                author=cls.user,
                                group=cls.group
                                )

    def setUp(self):

        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)

    def test_first_page_10_index(self):

        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_3_index(self):

        response = self.authorized_client.get(reverse(
                                              'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_10_group_list(self):

        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_3_group_list(self):

        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_10_profile(self):

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestAuthor'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_3_profile(self):

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestAuthor'
                                             }) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class Post_adds_correct(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestAuthor')

        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug-group',
            description='test-description'
        )

        cls.second_group = Group.objects.create(
            title='Тестовый заголовок группы2',
            slug='second-test-slug-group',
            description='second-test-description'
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

    def test_post_add_homepage(self):
        response = self.authorized_client.get(reverse('posts:index'))
        all_objects_one = response.context['page_obj']
        objects_count = len(all_objects_one)

        post_data = {
            'text': 'Второй текст',
            'group': self.second_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        second_response = self.authorized_client.get(reverse('posts:index'))
        all_objects_two = second_response.context['page_obj']
        another_objects_count = len(all_objects_two)

        self.assertEqual(objects_count + 1, another_objects_count)

    def test_post_add_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }))
        all_objects_one = response.context['page_obj']
        objects_count = len(all_objects_one)

        post_data = {
            'text': 'Второй текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        second_response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }))

        all_objects_two = second_response.context['page_obj']
        another_objects_count = len(all_objects_two)
        self.assertEqual(objects_count + 1, another_objects_count)

    def test_post_add_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username
                                             }))

        all_objects_one = response.context['page_obj']
        objects_count = len(all_objects_one)

        post_data = {
            'text': 'Второй текст',
            'group': self.second_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        second_response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username
                                             }))

        all_objects_two = second_response.context['page_obj']
        another_objects_count = len(all_objects_two)
        self.assertEqual(objects_count + 1, another_objects_count)

    def test_post_add_correct_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }))
        all_objects_one = response.context['page_obj']
        objects_count = len(all_objects_one)

        post_data = {
            'text': 'Второй текст',
            'group': self.second_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        second_response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug-group'
                                                 }))
        all_objects_two = second_response.context['page_obj']
        another_objects_count = len(all_objects_two)

        self.assertEqual(objects_count, another_objects_count)

    def test_second_post_with_image(self):
        first_post_count = Post.objects.all().count()

        middle_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x31\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        second_uploaded = SimpleUploadedFile(
            name='middle.gif',
            content=middle_gif,
            content_type='image/gif'
        )

        post_data = {
            'text': 'Второй текст',
            'group': self.second_group.id,
            'image': second_uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username':
                                                       self.user.username}))

        second_post_count = Post.objects.all().count()
        self.assertEqual(second_post_count, first_post_count + 1)


class CommentTest(TestCase):
    """"
    Тесты внутри класса:
    1.Комментарий добавляется в post_detail
    2.Коментировать может только авторизованный(для других форма не появляется)
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.quest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_in_post_detail(self):
        comment_data = {
            'post': self.post.id,
            'author': self.user.username,
            'text': 'Тестовый комментарий',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}))
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        first_comment = response.context['comments'][0]

        self.assertEqual(first_comment.text, 'Тестовый комментарий')


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestAuthor')

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts_list_homepage = response.context['page_obj'].object_list
        self.assertIn(self.post, posts_list_homepage)

        self.post.delete()

        self.assertIn(str.encode(f'{self.post}'), response.content)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(str.encode(f'{self.post}'), response.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.who_follow = User.objects.create_user(username='WhoFollow')
        cls.author = User.objects.create_user(username='Author')
        cls.not_follower = User.objects.create_user(username='NotFollower')

        cls.author_first_post = Post.objects.create(
            text='Первый текст',
            author=cls.author
        )

    def setUp(self):
        self.client_who_follow = Client()
        self.client_who_follow.force_login(self.who_follow)

        self.client_author = Client()
        self.client_author.force_login(self.author)

        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

        cache.clear()

    def test_follow_to_author(self):
        """
        Проверка просмотра поста автора в follow_index
        Проверка просмотра постов в follow_index после добавления нового поста
        Проверка отсутсвтия постов автора у неподписанного юзера
        """
        to_follow_response = self.client_who_follow.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))

        self.assertRedirects(to_follow_response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             self.author.username}))

        posts_follow = self.client_who_follow.get(
            reverse('posts:follow_index'))

        objects_in_follow_index = posts_follow.context['page_obj'].object_list

        self.assertIn(self.author_first_post, objects_in_follow_index)

        not_follower_response = self.not_follower_client.get(
            reverse('posts:follow_index'))

        self.assertNotIn(str.encode(f'{self.author_first_post}'),
                         not_follower_response.content)

    def test_follow_unfollow(self):
        to_follow_response = self.client_who_follow.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))

        self.assertRedirects(to_follow_response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             self.author.username}))

        posts_follow = self.client_who_follow.get(
            reverse('posts:follow_index'))
        objects_in_follow_index = posts_follow.context['page_obj'].object_list
        self.assertIn(self.author_first_post, objects_in_follow_index)

    def test_unfollow(self):
        to_follow_response = self.client_who_follow.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))

        self.assertRedirects(to_follow_response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             self.author.username}))

        posts_follow = self.client_who_follow.get(
            reverse('posts:follow_index'))
        objects_in_follow_index = posts_follow.context['page_obj'].object_list
        self.assertIn(self.author_first_post, objects_in_follow_index)

        to_unfollow_response = self.client_who_follow.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}))
        self.assertRedirects(to_unfollow_response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             self.author.username}))

        unfollowed_client_response = self.client_who_follow.get(
            reverse('posts:follow_index'))

        self.assertNotIn(str.encode(f'{self.author_first_post}'),
                         unfollowed_client_response.content)
