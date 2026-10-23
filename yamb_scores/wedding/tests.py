import json
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from .decorators import SESSION_FLAG
from .models import BoardColumn, Card


class WeddingAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        self.client.defaults['wsgi.url_scheme'] = 'https'
        self.client.get(reverse('wedding:login'))
        self.csrf_token = self.client.cookies['csrftoken'].value

    def test_login_page_is_public_and_noindex(self):
        response = self.client.get(reverse('wedding:login'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    def test_board_pages_and_api_require_the_wedding_session(self):
        protected = [
            ('get', reverse('wedding:board')),
            ('post', reverse('wedding:logout')),
            ('get', reverse('wedding:api_board')),
            ('post', reverse('wedding:api_cards')),
            ('put', reverse('wedding:api_card', args=[1])),
            ('delete', reverse('wedding:api_card', args=[1])),
            ('post', reverse('wedding:api_move_card', args=[1])),
        ]
        for method, url in protected:
            with self.subTest(method=method, url=url):
                if method == 'get':
                    response = self.client.get(url, HTTP_X_CSRFTOKEN=self.csrf_token)
                else:
                    response = getattr(self.client, method)(
                        url,
                        data='{}',
                        content_type='application/json',
                        HTTP_X_CSRFTOKEN=self.csrf_token,
                    )
                expected = 401 if '/api/' in url else 302
                self.assertEqual(response.status_code, expected)
                self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    @patch.dict('os.environ', {'WEDDING_PASSPHRASE_HASH': make_password('correct horse')})
    def test_successful_login_sets_scoped_secure_session_cookie(self):
        response = self.client.post(
            reverse('wedding:login'),
            {'passphrase': 'correct horse', 'csrfmiddlewaretoken': self.csrf_token},
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )
        self.assertEqual(response.status_code, 302)
        cookie = response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie['secure'])
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(int(cookie['max-age']), 90 * 24 * 60 * 60)
        self.assertTrue(self.client.session.get(SESSION_FLAG))

    @patch.dict('os.environ', {'WEDDING_PASSPHRASE_HASH': make_password('correct horse')})
    def test_repeated_failures_temporarily_lock_login(self):
        for _ in range(5):
            response = self.client.post(
                reverse('wedding:login'),
                {'passphrase': 'wrong', 'csrfmiddlewaretoken': self.csrf_token},
                HTTP_X_CSRFTOKEN=self.csrf_token,
            )
            self.assertEqual(response.status_code, 401)
        response = self.client.post(
            reverse('wedding:login'),
            {'passphrase': 'correct horse', 'csrfmiddlewaretoken': self.csrf_token},
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )
        self.assertEqual(response.status_code, 429)


class WeddingSeedTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command('seed_wedding')
        call_command('seed_wedding')
        self.assertEqual(Card.objects.count(), 29)
        gift = Card.objects.get(title='wedding gift')
        self.assertEqual(list(gift.subtasks.values_list('title', flat=True)), ['voor ons', 'voor gasten'])


class WeddingCardApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        self.client.defaults['wsgi.url_scheme'] = 'https'
        self.client.get(reverse('wedding:login'))
        self.csrf_token = self.client.cookies['csrftoken'].value
        session = self.client.session
        session[SESSION_FLAG] = True
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        self.todo = BoardColumn.objects.get(name='Te doen')
        self.busy = BoardColumn.objects.get(name='Bezig')

    def api_request(self, method, url, payload=None):
        body = json.dumps(payload) if payload is not None else ''
        return getattr(self.client, method)(
            url,
            data=body,
            content_type='application/json',
            HTTP_X_CSRFTOKEN=self.csrf_token,
        )

    def test_create_move_and_delete_card(self):
        created = self.api_request('post', reverse('wedding:api_cards'), {
            'title': 'Locatie bevestigen',
            'owner': 'S',
            'column_id': self.todo.pk,
            'subtasks': [{'title': 'Bel de locatie', 'done': False}],
        })
        self.assertEqual(created.status_code, 201, created.content)
        card_id = created.json()['id']
        self.assertEqual(created.json()['subtasks'][0]['title'], 'Bel de locatie')

        moved = self.api_request(
            'post',
            reverse('wedding:api_move_card', args=[card_id]),
            {'column_id': self.busy.pk, 'position': 0},
        )
        self.assertEqual(moved.status_code, 200, moved.content)
        self.assertEqual(moved.json()['column_id'], self.busy.pk)
        self.assertEqual(Card.objects.get(pk=card_id).position, 0)

        deleted = self.api_request('delete', reverse('wedding:api_card', args=[card_id]))
        self.assertEqual(deleted.status_code, 200, deleted.content)
        self.assertFalse(Card.objects.filter(pk=card_id).exists())
