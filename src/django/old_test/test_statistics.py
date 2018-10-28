"""
test_statisticspy.

Test the authentication calls.
"""

import test.test_utils as test

from django.test import TestCase

import VLE.factory as factory
import VLE.utils.generic_utils as utils
from VLE.models import Journal


class StatisticsTests(TestCase):
    """Test statistics functions."""
    def setUp(self):
        """Set up the test file."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'tt@tt.com')
        self.teacher = test.set_up_users('teacher', 1)[0]

    def test_journal_stats(self):
        """Test the journal stats functions in the serializer."""
        template = factory.make_entry_template('template_test')
        format = factory.make_format([template])
        assign = factory.make_assignment("Colloq", "In de opdracht...1", self.teacher, format=format)
        journal = factory.make_journal(assign, self.user)
        entries = test.set_up_entries(template, 4)

        for entry in entries:
            factory.make_node(journal, entry)

        journal = Journal.objects.get(user=self.user)
        entries = utils.get_journal_entries(journal)
        for i in range(len(entries)):
            if i > 0:
                entries[i].grade = 1
                entries[i].published = True
                entries[i].save()
        self.assertEquals(utils.get_acquired_points(entries), 3)
        self.assertEquals(utils.get_submitted_count(entries), 4)
        self.assertEquals(utils.get_graded_count(entries), 3)
