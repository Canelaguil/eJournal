"""
test_timeline.py.

Test all about the timeline.
"""
import datetime

from django.test import TestCase

import VLE.factory as factory
import VLE.timeline as timeline
from VLE.models import Role, Template


class TimelineTests(TestCase):
    """Test the timeline."""

    def setUp(self):
        """Setup."""
        self.u_rick = factory.make_user("Rick", "pass", "r@r.com")
        self.u_lars = factory.make_user("Lars", "pass", "l@l.com")

        self.template = Template(name="some_template")
        self.template.save()

        f_colloq = factory.make_format()
        self.deadlineentry = factory.make_entrydeadline_node(f_colloq, datetime.date(2020, 1, 1), self.template)
        self.progressnode = factory.make_progress_node(f_colloq, datetime.date(2024, 1, 1), 10)
        f_log = factory.make_format()

        f_colloq.available_templates.add(self.template)

        course = factory.make_course("Some Course", "c")
        student_role = Role.objects.get(name='Student', course=course)
        factory.make_participation(self.u_rick, course, student_role)

        a_colloq = factory.make_assignment("Colloq", "In de opdracht...1",
                                           author=self.u_rick, format=f_colloq, courses=[course])
        a_log = factory.make_assignment("Logboek", "In de opdracht...2",
                                        author=self.u_rick, format=f_log, courses=[course])

        self.j_rick_colloq = factory.make_journal(a_colloq, self.u_rick)
        self.j_lars_colloq = factory.make_journal(a_colloq, self.u_lars)
        self.j_rick_log = factory.make_journal(a_log, self.u_rick)

    def test_deadline_format(self):
        """Test if the deadline is correctly formatted."""
        deadline = datetime.date.today()

        format = factory.make_format()
        format.save()
        preset = factory.make_entrydeadline_node(format, deadline, self.template)

        self.assertEquals(deadline, preset.deadline)

        assignment = factory.make_assignment("Portfolio", "Fixed deadlines", author=self.u_rick, format=format)
        journal = factory.make_journal(assignment, self.u_rick)

        self.assertTrue(journal.node_set.get(preset__deadline=deadline))

    def test_sorted(self):
        """Test is the sort function works."""
        entry = factory.make_entry(self.template, datetime.date(2022, 1, 1))
        node = factory.make_node(self.j_rick_colloq, entry)
        nodes = timeline.get_sorted_nodes(self.j_rick_colloq)

        self.assertEquals(nodes[0].preset, self.deadlineentry)
        self.assertEquals(nodes[1], node)
        self.assertEquals(nodes[2].preset, self.progressnode)

    def test_json(self):
        """Test is the to dict function works correctly."""
        entry = factory.make_entry(self.template, datetime.date(2022, 1, 1))
        factory.make_node(self.j_rick_colloq, entry)

        nodes = timeline.get_nodes(self.j_rick_colloq, self.u_rick)

        self.assertEquals(len(nodes), 4)

        self.assertEquals(nodes[0]['type'], 'd')
        self.assertEquals(nodes[0]['entry'], None)

        self.assertEquals(nodes[1]['type'], 'e')

        self.assertEquals(nodes[2]['type'], 'a')

        self.assertEquals(nodes[3]['type'], 'p')
        self.assertEquals(nodes[3]['target'], 10)
