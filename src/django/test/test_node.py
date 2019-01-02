import test.factory as factory
from test.utils import api

from django.test import TestCase


class NodeAPITest(TestCase):
    def setUp(self):
        self.teacher = factory.Teacher()
        self.student = factory.User()
        self.admin = factory.Admin()
        self.journal = factory.Journal(user=self.student)

    def test_get(self):
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=self.student)
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=factory.Admin())
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=self.teacher, status=403)
        api.get(self, 'nodes', params={'journal_id': self.journal.pk},
                user=self.journal.assignment.courses.first().author)
