import test.factory as factory
from test.utils import api

from django.test import TestCase


class EntryAPITest(TestCase):
    def setUp(self):
        self.student = factory.Student()
        self.admin = factory.Admin()
        self.journal = factory.Journal(user=self.student)
        self.teacher = self.journal.assignment.courses.first().author
        self.format = self.journal.assignment.format
        self.format.available_templates.add(factory.Template())
        self.format.available_templates.add(factory.Template())
        self.format.unused_templates.add(factory.Template())

    def test_create(self):
        # Check if students cannot update journals
        create_params = {
            'journal_id': self.journal.pk,
            'template_id': self.format.available_templates.first().pk,
            'content': []
        }

        resp = api.create(self, 'entries', params=create_params, user=self.student)
        print(resp)

        assert 1 == 2
