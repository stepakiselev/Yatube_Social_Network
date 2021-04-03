from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Post, Group, User, Comment


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Andr')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Фантастика',
            slug='Test',
            description='Что то о группе'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    def test_page_not_found_url_exists_at_desired_location(self):
        """Страница /pppp/ вызывает ошибку."""
        response = self.guest_client.get('/pppp/')
        self.assertEqual(response.status_code, 404)

    def test_about_author_url_exists_at_desired_location(self):
        """Страница "/about/author/" доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница "/about/tech/" доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('group_posts', args=[self.group.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location_authorized(self):
        """Страница /new/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location_authorized(self):
        """Страница /username/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(
            reverse('profile', args=[self.post.author])
        )
        self.assertEqual(response.status_code, 200)

    def test_post_url_exists_at_desired_location_authorized(self):
        """Страница "<str:username>/<int:post_id>/"
         доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    }
                    )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница "<str:username>/<int:post_id>/edit/"
         доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    }
                    )
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_not_author(self):
        """Страница "<str:username>/<int:post_id>/edit/"
         перенаправляет не автора поста."""
        self.not_author = User.objects.create_user(username='not_author')
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
        response = self.not_author_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    }
                    ))
        self.assertEqual(response.status_code, 302)

    def test_not_author_authorized_edit_post(self):
        """Страница "<str:username>/<int:post_id>/edit/"
        не редактируется для не автора поста."""
        self.user = User.objects.create_user(username='not_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        form_data = {
            'text': 'Обновляем',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': self.post.author,
                                         'post_id': self.post.id
                                         }
                    ),
            data=form_data,
            follow=True)
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.post.author,
                                         'post_id': self.post.id
                                     }
                                     )
                             )
        # Если False, то запись не обновилась
        self.assertFalse(
            Post.objects.filter(
                text='Обновляем',
            ).exists()
        )

    def test_authorized_add_follow(self):
        """Только авторизированный пользователь
           может комментировать посты"""
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={'username': self.post.author,
                                           'post_id': self.post.id
                                           }
                    ),
            data=form_data,
            follow=True)
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.post.author,
                                         'post_id': self.post.id
                                     }
                                     )
                             )
        # Если False, то запись не обновилась
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент',
            ).exists()
        )

    def test_post_edit_url_exists_at_desired_anonymous(self):
        """Страница "<str:username>/<int:post_id>/edit/"
         перенаправляет анонимного пользователя."""
        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': self.post.author,
                        'post_id': self.post.id
                    }), follow=True)
        self.assertRedirects(
            response,
            '/auth/login/?next=' + reverse('post_edit',
                                           kwargs={
                                               'username': self.post.author,
                                               'post_id': self.post.id
                                           }
                                           )
        )

    def test_new_list_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
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
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
