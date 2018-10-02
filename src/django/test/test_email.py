from django.test import TestCase

import test.test_utils as test


class EmailApiTests(TestCase):
    def setUp(self):
        """Setup"""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'tt@tt.com')

    def test_forgot_password(self):
        login = test.logging_in(self, self.username, self.password)
        test.api_post_call(self, '/forgot_password/', login=login, params={'email': '', 'username': self.username})
