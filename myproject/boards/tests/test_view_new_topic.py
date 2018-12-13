from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from boards.views import new_topic
from boards.models import Board, Topic, Post
from boards.forms import NewTopicForm


class NewTopicTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django borad.')
        self.user = User.objects.create_user(username='john', email='john@demo.com', password='123456')
        self.client.login(username='john', password='123456')

    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEqual(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_valid_form(self):
        topic = Topic.objects.create(
            subject='foo',
            board=self.board,
            starter=self.user
        )
        post = Post.objects.create(
            message='bar',
            topic=topic,
            created_by=self.user
        )
        data = {
            # 'subject': topic.subject,
            # 'message': post.message,
            'subject': 'foo',
            'message': 'bar',
        }
        form = NewTopicForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        topic = Topic.objects.create(
            subject='foo',
            board=self.board,
            starter=self.user
        )
        post = Post.objects.create(
            message='',
            topic=topic,
            created_by=self.user
        )
        data = {
            'subject': topic.subject,
            'message': post.message,
        }
        form = NewTopicForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }

        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertEqual(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

