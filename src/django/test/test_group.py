import test.factory.course as coursefactory
import test.factory.user as userfactory
from test.utils import api

from django.test import TestCase


class GroupAPITest(TestCase):
    def setUp(self):
        self.teacher = userfactory.TeacherFactory()
        self.course = coursefactory.CourseFactory(author=self.teacher)
        self.create_params = {'name': 'test', 'course_id': self.course.pk}

    def test_rest(self):
        # Test the basic rest functionality as a superuser
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=userfactory.AdminFactory())

        # Test the basic rest functionality as a teacher
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=self.teacher)

        # Test the basic rest functionality as a student
        api.test_rest(self, 'groups',
                      create_params=self.create_params, get_status=405, get_is_create=False,
                      create_status=403,
                      user=userfactory.UserFactory())
