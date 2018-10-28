"""
test_jwt.py.

Test if the JWT token system works.
"""
import test.test_utils as test

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from VLE.models import User


class JWTTests(TestCase):
    """Test JWT.

    Test if the JWT token system works.
    """

    def setUp(self):
        """Setup."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'tt@tt.com')

    def test_get_auth(self):
        """Test simple authentication with JWT keys."""
        result = self.client.post(reverse('token_obtain_pair'),
                                  {'username': self.username,
                                   'password': self.password}, format='json')

        self.assertEquals(result.status_code, 200)
        self.assertTrue(result.json()['access'])
        self.assertTrue(result.json()['refresh'])

    def test_anonymous(self):
        """Test simple anonymous access."""
        result = self.client.get('/courses/', {}, format='json')

        self.assertEquals(result.status_code, 401)

    def test_user(self):
        """Test authenticated access."""
        result = self.client.post(reverse('token_obtain_pair'),
                                  {'username': self.username,
                                   'password': self.password}, format='json')

        result = self.client.get('/courses/', {},
                                 HTTP_AUTHORIZATION='Bearer {0}'.format(result.json()['access']))

        self.assertEquals(result.status_code, 200)
        self.assertEquals(result.json()['description'], '')
        self.assertEquals(result.json()['courses'], [])

    def test_auth_without_password(self):
        """Test authentication without password."""
        user = User(username='john')
        user.save()

        authenticated = auth.authenticate(username='john', password='')
        self.assertEquals(authenticated, None)
