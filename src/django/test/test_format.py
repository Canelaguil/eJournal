import test.factory as factory
from test.utils import api

from django.test import TestCase


class AssignmentAPITest(TestCase):
    def setUp(self):
        self.teacher = factory.Teacher()
        self.admin = factory.Admin()
        self.course = factory.Course(author=self.teacher)
        self.assignment = factory.Assignment(courses=[self.course])
        self.template = factory.Template()
        self.format = factory.Format(assignment=self.assignment)
        self.format.unused_templates.add(self.template)
        self.create_params = {'name': 'test', 'description': 'test_description', 'course_id': self.course.pk}

    def test_update(self):
        api.update(self, 'formats', params={'pk': self.assignment.pk, 's': 5},
                   user=factory.User(), status=403)
        api.update(self, 'formats', params={'pk': self.assignment.pk},
                   user=self.teacher)
        api.update(self, 'formats', params={'pk': self.assignment.pk},
                   user=factory.Admin())
