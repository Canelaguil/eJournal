"""
test_apis.py.

Test API calls.
"""
import test.test_utils as test

import django.utils.timezone as timezone
from django.test import TestCase

import VLE.factory as factory
from VLE.models import Content, Entry, Group, Lti_ids


class CreateApiTests(TestCase):
    def setUp(self):
        """Setup."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'test@test.com')

    def test_create_user(self):
        user = {
            'username': 'Student',
            'password': 'Pa$$word!',
            'first_name': 'Student',
            'last_name': 'Testing',
        }
        # No email
        test.api_post_call(self, '/users/', params=user, status=400)

        user['email'] = 'student@ejourn.al'
        test.api_post_call(self, '/users/', params=user, status=201)

    def test_create_new_course(self):
        """Test create new course."""
        username, password, user = test.set_up_user_and_auth('test2', 'test1233', 'test@ttaest.com', is_teacher=True)
        lti_id = '12AB'
        login = test.logging_in(self, username, password)
        create_course_dict = {'name': 'Beeldbewerken', 'abbreviation': 'BB', 'lti_id': lti_id}

        test.api_post_call(self, '/courses/', params=create_course_dict, login=login, status=201)
        self.assertEquals(Lti_ids.objects.get(lti_id=lti_id).course.name, 'Beeldbewerken')

    def test_create_new_assignment(self):
        """test create new assignment."""
        lti_id = '12AB'
        course = factory.make_course("BeeldBewerken", "BB", enddate=timezone.now())

        role = factory.make_role_default_no_perms("teacher", course, can_add_assignment=True)
        factory.make_participation(user=self.user, course=course, role=role)

        login = test.logging_in(self, self.username, self.password)
        create_assign_dict = {
            'name': 'SIFT',
            'description': 'In this assign...',
            'course_id': course.pk,
            'lti_id': lti_id
        }

        test.api_post_call(self, '/assignments/', params=create_assign_dict, login=login, status=201)
        self.assertEquals(Lti_ids.objects.get(lti_id=lti_id).assignment.name, 'SIFT')

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
