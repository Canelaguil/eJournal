import test.factory as factory
from datetime import date, timedelta
from test.utils import api

from django.test import TestCase

from VLE.models import Field


class EntryAPITest(TestCase):
    def setUp(self):
        self.student = factory.Student()
        self.admin = factory.Admin()
        self.journal = factory.Journal(user=self.student)
        self.teacher = self.journal.assignment.courses.first().author
        self.journal_teacher = factory.Journal(user=self.teacher, assignment=self.journal.assignment)
        self.format = self.journal.assignment.format
        self.format.available_templates.add(factory.Template())
        self.format.available_templates.add(factory.Template())
        self.format.unused_templates.add(factory.Template())

        self.valid_create_params = {
            'journal_id': self.journal.pk,
            'template_id': self.format.available_templates.first().pk,
            'content': []
        }
        fields = Field.objects.filter(template=self.format.available_templates.first())
        self.valid_create_params['content'] = [{'data': 'test data', 'id': field.id} for field in fields]

    def test_create(self):
        # Check valid entry creation
        api.create(self, 'entries', params=self.valid_create_params, user=self.student)

        # Check if students cannot update journals without required parts filled in
        create_params = self.valid_create_params.copy()
        create_params['content'] = [{'data': 'test title', 'id': 1}]
        api.create(self, 'entries', params=create_params, user=self.student, status=400)

        # Check for assignment locked
        self.journal.assignment.lock_date = date.today() - timedelta(1)
        self.journal.assignment.save()
        api.create(self, 'entries', params=create_params, user=self.student, status=403)
        self.journal.assignment.lock_date = date.today() + timedelta(1)
        self.journal.assignment.save()

        # Check if not connected templates wont work
        create_params = self.valid_create_params.copy()
        create_params['template_id'] = factory.Template().pk
        api.create(self, 'entries', params=create_params, user=self.student, status=403)

        # Teachers shouldn't be able to make entries on their own journal
        teacher_params = self.valid_create_params.copy()
        teacher_params['journal_id'] = self.journal_teacher.pk
        api.create(self, 'entries', params=teacher_params, user=self.teacher, status=403)

        # TODO: Test for entry bound to entrydeadline
        # TODO: Test with file upload
        # TODO: Test added index

    def test_update(self):
        entry = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']

        params = {
            'pk': entry['id'],
            'content': [{
                'id': field['field'],
                'contentID': field['id'],
                'data': field['data']
            } for field in entry['content']]
        }
        entry2 = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']
        params2 = {
            'pk': entry2['id'],
            'content': [{
                'id': field['field'],
                'contentID': field['id'],
                'data': ''
            } for field in entry2['content']]
        }
        api.update(self, 'entries', params=params.copy(), user=self.student)
        # Student should always provide required parameters
        api.update(self, 'entries', params=params2.copy(), user=self.student)
        # Other users shouldn't be able to update an entry
        api.update(self, 'entries', params=params.copy(), user=self.teacher, status=403)

        # Check for assignment locked
        self.journal.assignment.lock_date = date.today() - timedelta(1)
        self.journal.assignment.save()
        api.update(self, 'entries', params=params.copy(), user=self.student, status=403)
        self.journal.assignment.lock_date = date.today() + timedelta(1)
        self.journal.assignment.save()

        # Grade and publish an entry
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5}, user=self.student, status=403)
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5}, user=self.teacher)

        # Shouldn't be able to edit entries after grade
        api.update(self, 'entries', params=params.copy(), user=self.student, status=400)

        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5, 'published': False}, user=self.teacher)
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5, 'published': True}, user=self.teacher)
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5, 'published': True},
                   user=factory.Teacher(), status=403)

        # Check if a published entry cannot be unpublished
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'published': False}, user=self.teacher, status=400)

    def test_destroy(self):
        # Only a student can delete their own entry
        entry = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']
        api.delete(self, 'entries', params={'pk': entry['id']}, user=factory.Student(), status=403)
        api.delete(self, 'entries', params={'pk': entry['id']}, user=self.teacher, status=403)
        api.delete(self, 'entries', params={'pk': entry['id']}, user=self.student)

        # Superusers can delete all entries
        entry = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']
        api.delete(self, 'entries', params={'pk': entry['id']}, user=factory.Admin())

        # Only superusers should be allowed to delete graded entries
        entry = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']
        api.update(self, 'entries/grade', params={'pk': entry['id'], 'grade': 5, 'published': True}, user=self.teacher)
        api.delete(self, 'entries', params={'pk': entry['id']}, user=self.student, status=403)
        api.delete(self, 'entries', params={'pk': entry['id']}, user=factory.Admin())

        # Only superusers should be allowed to delete locked entries
        entry = api.create(self, 'entries', params=self.valid_create_params, user=self.student)['entry']
        self.journal.assignment.lock_date = date.today() - timedelta(1)
        self.journal.assignment.save()
        api.delete(self, 'entries', params={'pk': entry['id']}, user=self.student, status=403)
        api.delete(self, 'entries', params={'pk': entry['id']}, user=factory.Admin())
