from test.utils import api

from django.test import TestCase

import test.factory.user as userfactory
import test.factory.course as coursefactory


class AssignmentAPITest(TestCase):
    def setUp(self):
        self.teacher = userfactory.TeacherFactory()
        self.course = coursefactory.CourseFactory(author=self.teacher)
        self.create_params = {'name': 'test', 'description': 'test_description', 'course_id': self.course.pk}

    def test_rest(self):
        # Test the basic rest functionality as a superuser
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk},
                      update_params={'description': 'test_description2'},
                      delete_params={'course_id': self.course.pk},
                      user=userfactory.AdminFactory())

        # Test the basic rest functionality as a teacher
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk},
                      update_params={'description': 'test_description2'},
                      delete_params={'course_id': self.course.pk},
                      user=self.teacher)

        # Test the basic rest functionality as a student
        api.test_rest(self, 'assignments',
                      create_params=self.create_params,
                      create_status=403,
                      user=userfactory.UserFactory())

    def test_update(self):
        assignment = api.create(self, 'assignments', params=self.create_params,
                                user=self.teacher)['assignment']

        # Try to publish the assignment
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True},
                   user=userfactory.UserFactory(), status=403)
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True},
                   user=self.teacher)
        api.update(self, 'assignments', params={'pk': assignment['id'], 'published': True},
                   user=userfactory.AdminFactory())
