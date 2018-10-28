import test.test_utils as test

import django.utils.timezone as timezone
from django.test import TestCase

import VLE.factory as factory
import VLE.serializers as serialize
from VLE.models import Assignment, Comment, Course, Participation, Role, User


class UpdateApiTests(TestCase):
    def setUp(self):
        """Setup"""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'tt@tt.com')
        self.rein_user, self.rein_pass, self.rein = test.set_up_user_and_auth("Rein", "123", 'rr@rr.com')
        self.no_perm_user, self.no_perm_pass, self.no_permission_user = test.set_up_user_and_auth("no_perm", "123",
                                                                                                  'sigh@sigh.com')
        self.course = factory.make_course("Beeldbewerken", "BB", enddate=timezone.now())

    def test_update_course(self):
        """Test update_course"""
        login = test.logging_in(self, self.username, self.password)

        course = factory.make_course("Portfolio Academische Vaardigheden", "PAV", author=self.user)

        test.api_patch_call(self, '/courses/' + str(course.pk) + '/', {
            'name': 'Beeldbewerken',
            'abbreviation': 'BB',
            'startdate': course.startdate,
            'enddate': course.enddate
            },
            login
        )

        course = Course.objects.get(pk=course.pk)
        self.assertEquals(course.name, 'Beeldbewerken')
        self.assertEquals(course.abbreviation, 'BB')

    def test_update_course_roles(self):
        """Test update course roles"""
        teacher_user, teacher_pass, teacher = test.set_up_user_and_auth('Teacher', 'pass', 'teach@teach.com')
        teacher_role = factory.make_role_teacher("TE", self.course)

        factory.make_role_ta('TA2', self.course)
        factory.make_participation(teacher, self.course, teacher_role)

        login = test.logging_in(self, teacher_user, teacher_pass)
        result = test.api_get_call(self, '/roles/', login, params={'course_id': 1})

        roles = result.json()['roles']
        for role in roles:
            if role['name'] == 'TA2':
                role['can_grade'] = 1

        roles.append(serialize.RoleSerializer(factory.make_role_default_no_perms('test_role', self.course)).data)
        test.api_patch_call(self, '/roles/1/', {'roles': roles}, login)

        role_test = Role.objects.get(name='TA2', course=self.course)
        self.assertTrue(role_test.can_grade)
        self.assertEquals(Role.objects.filter(name='test_role', course=self.course).count(), 1)

    def test_update_course_with_student(self):
        """Test update_course_with_student"""
        login = test.logging_in(self, self.username, self.password)

        course = factory.make_course("Portfolio Academische Vaardigheden", "PAV")
        teacher_role = Role.objects.get(name='Teacher', course=course)

        factory.make_participation(self.user, course, teacher_role)
        student = factory.make_user("Rick", "pass", "r@r.com")

        test.api_post_call(
            self,
            '/participations/',
            {'user_id': student.pk, 'course_id': course.pk},
            login
        )

        course = Course.objects.get(pk=course.pk)
        self.assertEquals(len(course.users.all()), 2)
        self.assertTrue(User.objects.filter(participation__course=course, username='Rick').exists())

    def test_update_assignment(self):
        """Test update assignment"""
        teacher_user, teacher_pass, teacher = test.set_up_user_and_auth('Teacher', 'pass', 'teach@teach.com')
        teacher_role = factory.make_role_teacher("TE", self.course)

        factory.make_participation(teacher, self.course, teacher_role)
        assign = test.set_up_assignments('Assign', '', 1, self.course)[0]

        login = test.logging_in(self, teacher_user, teacher_pass)

        test.api_patch_call(self,
                            '/assignments/' + str(assign.pk) + '/',
                            {'name': 'Assign2',
                             'description': 'summary',
                             'is_published': True},
                            login)

        assign = Assignment.objects.get(pk=assign.pk)
        self.assertEquals(assign.name, 'Assign2')
        self.assertEquals(assign.description, 'summary')

    def test_update_format(self):
        """Test update format function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course])

        login = test.logging_in(self, self.rein_user, self.rein_pass)

        update_dict = {
            'assignment_details': {
                'name': 'Colloq',
                'description': 'description1',
                'is_published': True
            },
            'templates': [serialize.TemplateSerializer(template).data
                          for template in format.available_templates.all()],
            'removed_presets': [],
            'removed_templates': [],
            'presets': [],
            'unused_templates': []
        }

        test.api_patch_call(self, '/formats/' + str(assignment.pk) + '/', update_dict, login)

    def test_update_user_role_course(self):
        """Test user role update in a course."""
        login = test.logging_in(self, self.rein_user, self.rein_pass)
        course = factory.make_course("Portfolio Academische Vaardigheden", "PAV", author=self.rein)

        ta_role = Role.objects.get(name='TA', course=course)
        student_role = factory.make_role_student(name='SD', course=course)

        self.user_role = factory.make_user("test123", "test", "testq@test.com")
        factory.make_participation(self.user_role, course, ta_role)
        factory.make_participation(self.user, course, student_role)

        user_role = Participation.objects.get(user=self.user_role, course=2).role.name
        self.assertEquals(user_role, 'TA')

        test.api_patch_call(
            self,
            '/participations/' + str(course.pk) + '/',
            {'user_id': self.user_role.pk, 'role': 'SD'},
            login
        )
        user_role = Participation.objects.get(user=self.user_role, course=course.pk).role.name
        self.assertEquals(user_role, 'SD')

    def test_update_password(self):
        """Test update password."""
        login = test.logging_in(self, self.username, self.password)

        test.api_patch_call(self,
                            '/users/password/',
                            {'new_password': 'Pass123!',
                             'old_password': self.password},
                            login)

        test.logging_in(self, self.username, 'Pass123!')

        test.api_patch_call(self,
                            '/users/password/',
                            {'new_password': 'Pass321!',
                             'old_password': 'Pass123!'},
                            login)

    def test_get_comments(self):
        """Test update comment function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course])
        student_user, student_pass, student = test.set_up_user_and_auth('student', 'pass', 'student@student.com')
        test.set_up_participation(student, course, 'Student')
        journal = factory.make_journal(assignment, student)
        entry = factory.make_entry(template)
        factory.make_node(journal, entry)
        comment = factory.make_comment(entry, self.rein, 'Excellent!', True)

        login = test.logging_in(self, self.rein_user, self.rein_pass)

        update_dict = {'text': 'Bad!'}
        test.api_patch_call(self, '/comments/' + str(comment.pk) + '/', update_dict, login)

        q_comment = Comment.objects.get(pk=comment.pk)
        self.assertEquals(q_comment.text, 'Bad!')
