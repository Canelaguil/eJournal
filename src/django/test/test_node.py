import test.factory as factory
from test.utils import api

from django.test import TestCase


class NodeAPITest(TestCase):
    def setUp(self):
        self.student = factory.Student()
        self.journal = factory.Journal(user=self.student)
        self.teacher = self.journal.assignment.courses.first().author

    def test_get(self):
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=self.student)
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=factory.Admin())
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=factory.Teacher(), status=403)
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=self.teacher)
