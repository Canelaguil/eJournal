import test.test_utils as test

from django.test import TestCase

import VLE.factory as factory


class AuthenticationTests(TestCase):
    def setUp(self):
        """Set up the test file."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'test@test.com')

    def test_login(self):
        """Test if the login is successful."""
        login = test.logging_in(self, self.username, self.password)
        factory.make_course('test', 'TTTT')
        test.api_get_call(self, '/courses/', login)

    def test_not_logged_in(self):
        """Test error for api request call for non-authenticated user."""
        result = self.client.get('/courses/', {}, format='json')
        self.assertEquals(result.status_code, 401)
