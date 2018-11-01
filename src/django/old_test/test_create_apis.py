"""
test_apis.py.

Test API calls.
"""
import test.test_utils as test

from django.test import TestCase

import VLE.factory as factory
from VLE.models import Content, Entry, Group


class CreateApiTests(TestCase):
    def setUp(self):
        """Setup."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'test@test.com')

    def test_create_group(self):
        """test create group."""
        login = test.logging_in(self, self.username, self.password)
        course = factory.make_course("Portfolio Academische Vaardigheden", "PAV")
        create_group_dict = {'name': 'TestGroup', 'course_id': course.pk}

        role = factory.make_role_default_no_perms("teacher", course, can_add_course_user_group=True)
        factory.make_participation(user=self.user, course=course, role=role)

        test.api_post_call(self, '/groups/', params=create_group_dict, login=login, status=201)
        self.assertTrue(Group.objects.filter(name='TestGroup', course=course).exists())

    def test_create_entry(self):
        """"Test create entry."""
        _, _, user2 = test.set_up_user_and_auth('testh', 'test123h', 'testh@test.com')

        course = factory.make_course('Portfolio', 'PAV', author=user2)
        template = factory.make_entry_template("some_template")
        format = factory.make_format([template])
        assignment = factory.make_assignment("Assignment", "Your favorite assignment", format=format, courses=[course])
        journal = factory.make_journal(assignment, self.user)
        field = factory.make_field(template, 'Some field', 0)
        login = test.logging_in(self, self.username, self.password)
        format.available_templates.add(template)

        role = factory.make_role_default_no_perms("student", course, can_have_journal=True)
        factory.make_participation(user=self.user, course=course, role=role)

        create_entry_dict = {
            'journal_id': journal.id,
            'template_id': template.id,
            'content': [{
                'id': field.pk,
                'data': "This is some data"
                }]
            }

        test.api_post_call(self, '/entries/', create_entry_dict, login, 201)
        self.assertTrue(Entry.objects.filter(node__journal=journal).exists())
        self.assertEquals(Content.objects.get(entry=1).data, "This is some data")
