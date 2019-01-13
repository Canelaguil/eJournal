import test.factory as factory
from datetime import date, timedelta
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
        valid_create_params = {
            'journal_id': self.journal.pk,
            'template_id': self.format.available_templates.first().pk,
            'content': [{'data': 'test title', 'id': 1}, {'data': 'test summary', 'id': 2}]
        }
        api.create(self, 'entries', params=valid_create_params, user=self.student)

        # Check if students cannot update journals without required parts filled in
        create_params = valid_create_params
        create_params['content'] = [{'data': 'test title', 'id': 1}]
        api.create(self, 'entries', params=create_params, user=self.student, status=400)

        # Check for assignment locked
        self.journal.assignment.lock_date = date.today() - timedelta(1)
        self.journal.assignment.save()
        api.create(self, 'entries', params=create_params, user=self.student, status=400)
        self.journal.assignment.lock_date = date.today() + timedelta(1)
        self.journal.assignment.save()
