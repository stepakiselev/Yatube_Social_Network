import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from posts.models import Post, Group, User, Follow
from django import forms


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
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
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='Andr')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='Test',
            description='Что то о группе'
        )
        cls.group_two = Group.objects.create(
            title='Заголовок2',
            slug='Test2',
            description='группа2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('index'): 'index.html',
            reverse('new_post'): 'new.html',
            reverse('group_posts', args=[self.group.slug]): 'group.html',
            reverse('profile', args=[self.post.author]): 'profile.html',
            reverse(
                'post',
                kwargs={
                    'username': self.post.author,
                    'post_id': self.post.id
                }
            ): 'post.html',
            reverse(
                'post_edit',
                kwargs={
                    'username': self.post.author,
                    'post_id': self.post.id
                }
            ): 'new.html',
            reverse('follow_index'): 'follow.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        post = PostPagesTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)
        post_text_0 = response_post.text
        post_group_0 = response_post.group
        post_author_0 = response_post.author
        post_image_0 = response_post.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_show_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        post = PostPagesTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)
        post_text_0 = response_post.text
        post_group_0 = response_post.group
        post_author_0 = response_post.author
        post_image_0 = response_post.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.post.author})
        )
        post = PostPagesTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)
        post_text_0 = response_post.text
        post_group_0 = response_post.group
        post_author_0 = response_post.author
        post_image_0 = response_post.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_view_show_correct_context(self):
        """Шаблон post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    })
        )
        post = PostPagesTests.post
        response_post = response.context['post']
        self.assertEqual(post, response_post)
        post_text_0 = response_post.text
        post_group_0 = response_post.group
        post_author_0 = response_post.author
        post_image_0 = response_post.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        group = self.group
        response_group = response.context['group']
        self.assertEqual(group, response_group)

    def test_new_post_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.post.author})
        )
        post = self.post
        response_post = response.context['posts'][0]
        self.assertEqual(post, response_post)

    def test_post_shows_correct_context(self):
        """Шаблон post_view сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    }
                    )
        )
        post = self.post
        response_post = response.context['post']
        self.assertEqual(post, response_post)

    def test_post_edit_post_show_correct_context(self):
        """Шаблон new для post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.post.author, 'post_id': self.post.id})
        )
        fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected)

    def test_index_with_group_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом,
        пост с группой появляется на главной странице сайта."""
        form_two = {'text': self.post.text, 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_two,
            follow=True
        )
        self.assertRedirects(response, '/')
        self.assertTrue(Post.objects.filter(
            text=self.post.text,
            group=self.group.id
        ).exists())
        self.assertFalse(Post.objects.filter(
            text=self.post.text,
            group=self.group_two.id
        ).exists())

    def test_group_show_new_post(self):
        """Пост попадает на страницу с группой поста."""
        response = self.authorized_client.get(
            reverse('group_posts',
                    kwargs={'slug': self.group.slug}
                    )
        )
        post = self.post
        response_post = response.context['posts'][0]
        self.assertEqual(post, response_post)

    def test_group_new_post_not_exists_in_any_group(self):
        """Пост не попадает на страницу другой группы."""
        response = self.authorized_client.get(
            reverse('group_posts',
                    kwargs={'slug': self.group_two.slug}
                    )
        )
        post = self.post
        response_post = response.context['posts']
        self.assertNotEqual(post, response_post)

    def test_follow_show_post(self):
        """Пост попадает на страницу с подписками ."""
        any_user = User.objects.create_user(username='Any')
        self.authorized_client = Client()
        self.authorized_client.force_login(any_user)
        Follow.objects.create(user=any_user, author=self.user)
        response = self.authorized_client.get(reverse('follow_index'))
        post = self.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)

    def test_follow_not_show_post(self):
        """Пост не попадает на страницу с подписками
         для user не подписаного на автора."""
        any_user = User.objects.create_user(username='Any')
        self.authorized_client = Client()
        self.authorized_client.force_login(any_user)
        response = self.authorized_client.get(reverse('follow_index'))
        post = self.post
        response_post = response.context['page']
        self.assertNotEqual(post, response_post)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model()
        cls.user = user.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создадим запись в БД
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Post.objects.create(text='Текст %s' % author_num)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Andr')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='Test',
            description='Что то о группе'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def test_cache_index_page(self):
        """Посты страницы Index хранятся в cash и
        обновляются каждые 20 сек"""
        response = self.authorized_client.get(reverse('index'))
        content_one = response.content
        Post.objects.create(
            text='Тестовый текст 2',
            author=self.user
        )
        response = self.authorized_client.get(reverse('index'))
        content_plus = response.content
        self.assertEqual(content_one, content_plus, 'Caching is working.')

        cache.clear()

        response = self.authorized_client.get(reverse('index'))
        content_two = response.content
        self.assertNotEqual(content_plus, content_two, 'Caching is clear.')
