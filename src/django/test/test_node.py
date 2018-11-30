import test.factory as factory
from test.utils import api

from django.test import TestCase


class NodeAPITest(TestCase):
    def setUp(self):
        self.teacher = factory.Teacher()
        self.student = factory.User()
        self.admin = factory.Admin()
        self.journal = factory.Journal(author=self.student)

    def test_get(self):
        # TODO: Improve template testing
        print(self.journal.assignment.courses.values('users'))
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=self.student)
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=factory.Admin())
        api.get(self, 'nodes', params={'journal_id': self.journal.pk}, user=factory.Teacher(), status=403)
