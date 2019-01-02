import test.factory as factory
from test.utils import api

from django.test import TestCase


class NodeAPITest(TestCase):
    def setUp(self):
        self.student = factory.User()
        self.admin = factory.Admin()
        self.journal = factory.Journal(user=self.student)
        self.teacher = self.journal.assignment.courses.first().author

    def test_get(self):
        assignment = self.journal.assignment
        course = assignment.courses.first()
        payload = {'assignment_id': assignment.pk, 'course_id': course.pk}
        # Test list
        api.get(self, 'journals', params=payload, user=self.student, status=403)
        api.get(self, 'journals', params=payload, user=self.teacher)

        # Test get
        api.get(self, 'journals', params={'pk': self.journal.pk}, user=self.student)
        api.get(self, 'journals', params={'pk': self.journal.pk}, user=self.teacher)
        api.get(self, 'journals', params={'pk': self.journal.pk}, user=factory.Teacher(), status=403)

    def test_update(self):
        # Check if students cannot update journals
        api.update(self, 'journals', params={'pk': self.journal.pk}, user=self.student, status=403)

        # Check if teacher can only update the published state
        api.update(self, 'journals', params={'pk': self.journal.pk}, user=self.teacher, status=403)
        # 400 is because its not coupled to LTI, and thus cannot really publish grades
        # this will be checked in the lti testing
        api.update(self, 'journals', params={'pk': self.journal.pk, 'published': True}, user=self.teacher, status=400)

        # Check if the admin can update the journal
        api.update(self, 'journals', params={'pk': self.journal.pk, 'user': factory.User().pk}, user=factory.Admin())
