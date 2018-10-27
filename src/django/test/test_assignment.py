from test.utils import api
from test.utils import generic_utils as utils
from django.test import TestCase
import VLE.factory as factory


class AssignmentAPITest(TestCase):
    def setUp(self):
        """Setup"""
        self.student = utils.setup_user('student')
        self.teacher = utils.setup_user('teacher', is_teacher=True)
        self.superuser = utils.setup_user('superuser', is_superuser=True)

        self.course = factory.make_course('test_course', 'tc', author=self.teacher['user'])

        self.create_params = {'name': 'test', 'description': 'test_description', 'course_id': self.course.pk}

    def test_rest(self):
        # Test the basic rest functionallity as a superuser
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk},
                      update_params={'description': 'test_description2'},
                      delete_params={'course_id': self.course.pk},
                      user=self.superuser)

        # Test the basic rest functionallity as a teacher
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk},
                      update_params={'description': 'test_description2'},
                      delete_params={'course_id': self.course.pk},
                      user=self.teacher)

        # Test the basic rest functionallity as a student
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      create_status=403,
                      user=self.student)

    def test_update(self):
        assignment = api.create(self, 'assignments', params=self.create_params, user=self.teacher)['assignment']

        # Try to publish the assignment
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True},
                   user=self.student, status=403)
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True}, user=self.teacher)
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True}, user=self.superuser)
