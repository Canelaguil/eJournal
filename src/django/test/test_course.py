import test.factory.user as userfactory
from test.utils import api

from django.test import TestCase


class CourseAPITest(TestCase):
    def setUp(self):
        self.create_params = {'name': 'test_course', 'abbreviation': 'TC'}

    def test_rest(self):
        # Test the basic rest functionallity as a superuser
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=userfactory.AdminFactory())

        # Test the basic rest functionallity as a teacher
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=userfactory.TeacherFactory())

        # Test the basic rest functionallity as a student
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      create_status=403,
                      user=userfactory.UserFactory())
