import test.factory.user as userfactory
from test.utils import api

from django.test import TestCase


class UserAPITest(TestCase):
    def test_rest(self):
        api.test_rest(self, 'users',
                      create_params={'username': 'test', 'password': 'Pa$$word!', 'email': 'test@123.nl'},
                      update_params={'username': 'test2'},
                      user=userfactory.AdminFactory())
