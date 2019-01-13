import test.factory as factory
from test.utils import api

from django.test import TestCase


class CommonAPITest(TestCase):
    def setUp(self):
        self.student = factory.Student()
        self.journal = factory.Journal(user=self.student)
        self.teacher = self.journal.assignment.courses.first().author

    def test_names(self):
        assignment = self.journal.assignment
        course = assignment.courses.first()
        url = 'names/{}/{}/{}'.format(course.id, assignment.id, self.journal.id)

        # Check if these users can view the names
        api.get(self, url, user=self.student)
        api.get(self, url, user=self.teacher)
        api.get(self, url, user=factory.Admin())

        # CHeck if a random student cannot view the names
        api.get(self, url, user=factory.Student(), status=403)
