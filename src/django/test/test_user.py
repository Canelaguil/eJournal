from test.utils import api
from test.utils import generic_utils as utils
from django.test import TestCase


class UserAPITest(TestCase):
    def setUp(self):
        """Setup"""
        self.student = utils.setup_user('student')
        self.teacher = utils.setup_user('teacher', is_teacher=True)
        self.superuser = utils.setup_user('superuser', is_superuser=True)

    def test_rest(self):
        api.test_rest(self, 'users',
                      create_params={'username': 'test', 'password': 'Pa$$word!', 'email': 'test@123.nl'},
                      update_params={'username': 'test2'},
                      username=self.superuser['username'])
