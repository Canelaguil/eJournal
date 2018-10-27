from test.utils import api
from test.utils import generic_utils as utils
from django.test import TestCase
import VLE.factory as factory


class UserAPITest(TestCase):
    def setUp(self):
        """Setup"""
        self.maxDiff = None
        self.student = utils.setup_user('student')
        self.teacher = utils.setup_user('teacher', is_teacher=True)
        self.superuser = utils.setup_user('superuser', is_superuser=True)

    def test_rest(self):
        course = factory.make_course('test_course', 'tc', author=self.teacher['user'])

        api.test_rest(self, 'assignments',
                      create_params={'name': 'test', 'description': 'test_description', 'course_id': course.pk},
                      get_params={'course_id': course.pk},
                      update_params={'description': 'test_description2'},
                      delete_params={'course_id': course.pk},
                      username=self.teacher['username'])
