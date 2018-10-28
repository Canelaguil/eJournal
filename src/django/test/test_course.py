from test.utils import api
from test.utils import generic_utils as utils

from django.test import TestCase


class CourseAPITest(TestCase):
    def setUp(self):
        """Setup"""
        self.student = utils.setup_user('student')
        self.teacher = utils.setup_user('teacher', is_teacher=True)
        self.superuser = utils.setup_user('superuser', is_superuser=True)

        self.create_params = {'name': 'test_course', 'abbreviation': 'TC'}

    def test_rest(self):
        # Test the basic rest functionallity as a superuser
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=self.superuser)

        # Test the basic rest functionallity as a teacher
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=self.teacher)

        # Test the basic rest functionallity as a student
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      create_status=403,
                      user=self.student)
