from test.utils import api
from test.utils import generic_utils as utils

from django.test import TestCase

import VLE.factory as factory


class GroupAPITest(TestCase):
    def setUp(self):
        """Setup"""
        self.student = utils.setup_user('student')
        self.teacher = utils.setup_user('teacher', is_teacher=True)
        self.superuser = utils.setup_user('superuser', is_superuser=True)

        self.course = factory.make_course('test_course', 'tc', author=self.teacher['user'])

        self.create_params = {'name': 'test', 'course_id': self.course.pk}

    def test_rest(self):
        # Test the basic rest functionallity as a superuser
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=self.superuser)

        # Test the basic rest functionallity as a teacher
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=self.teacher)

        # Test the basic rest functionallity as a student
        api.test_rest(self, 'groups',
                      create_params=self.create_params, get_status=405, get_is_create=False,
                      create_status=403,
                      user=self.student)
