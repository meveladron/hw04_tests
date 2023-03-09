from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_authorized_client = Client()
        cls.author = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )

    def test_urls_no_authorized_client(self):
        """Тестирование страниц для всех пользователей"""
        url_list = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.author.username}/': 200,
            f'/posts/{self.post.id}/': 200,
            'unexisting_page/': 404
        }
        for url, status_code in url_list.items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.no_authorized_client.get(url).status_code,
                    status_code
                )

    def test_urls_authorized_client(self):
        """Тестирование доступов для неавторизованного пользователя"""
        url_list = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author.username}/',
            f'/posts/{self.post.id}/'
        )
        for url in url_list:
            response = self.no_authorized_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_urls_guest_client(self):
        """Тестирование доступов для авторизованного пользователя"""
        urls = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author.username}/',
            f'/posts/{self.post.id}/'
        )
        for url in urls:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.authorized_client.get(adress),
                    template
                )
