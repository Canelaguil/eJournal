"""
test_get_apis.py.

Test the get apis.
"""
import test.test_utils as test

import django.utils.timezone as timezone
from django.test import TestCase
from rest_framework.settings import api_settings

import VLE.factory as factory
from VLE.models import Role


class GetApiTests(TestCase):
    """Get Api tests.

    Test the get apis.
    """

    def setUp(self):
        """Set up the test file."""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'testtt@te.com')
        self.rein_user, self.rein_pass, self.rein = test.set_up_user_and_auth("Rein", "123", 're@rein.com')
        self.no_perm_user, self.no_perm_pass, self.no_permission_user = test.set_up_user_and_auth("no_perm", "123",
                                                                                                  'sigh@sigh.com')
        self.course = factory.make_course("Beeldbewerken", "BB")
        self.lars = factory.make_user("Lars", "123", "l@l.com")
        self.not_found_pk = 9999

    def test_get_course_data(self):
        """Test get coursedata function."""
        test.set_up_participation(self.user, self.course, 'Teacher')
        login = test.logging_in(self, self.username, self.password)

        response = test.api_get_call(self, '/courses/' + str(self.course.pk) + '/', login)

        self.assertEquals(response.json()['course']['name'], 'Beeldbewerken')
        self.assertEquals(response.json()['course']['abbreviation'], 'BB')

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/courses/' + str(self.course.pk) + '/', login, status=403)
        test.api_get_call(self, '/courses/' + str(self.not_found_pk) + '/', login, status=404)
        test.test_unauthorized_api_get_call(self, '/courses/' + str(self.course.pk) + '/')

    def test_get_course_users(self):
        """Test the get course users function."""
        teacher_user, teacher_pass, teacher = test.set_up_user_and_auth('teacher', 'pass', 'teach@teach.com')
        test.set_up_participation(teacher, self.course, 'Teacher')
        test.set_up_participation(self.lars, self.course, 'Student')
        test.set_up_participation(self.rein, self.course, 'TA')

        login = test.logging_in(self, teacher_user, teacher_pass)

        response = test.api_get_call(self, '/participations/', login, params={'course_id': self.course.pk})

        self.assertEquals(len(response.json()['participants']), 3)

        response = test.api_get_call(self, '/participations/unenrolled/', login, params={'course_id': self.course.pk})

        self.assertEquals(len(response.json()['participants']), 2)
        self.assertEquals(response.json()['participants'][0]['username'], self.username)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/participations/', login, status=403, params={'course_id': self.course.pk})
        test.api_get_call(self, '/participations/', login, status=404, params={'course_id': self.not_found_pk})
        test.test_unauthorized_api_get_call(self, '/participations/', params={'course_id': self.not_found_pk})
        test.test_unauthorized_api_get_call(self,  '/courses/' + str(self.course.pk) + '/')
        test.test_unauthorized_api_get_call(self, '/participations/unenrolled/', params={'course_id': self.course.pk})

        test.set_up_participation(self.no_permission_user, self.course, 'Student')
        test.api_get_call(self, '/participations/', login, status=403, params={'course_id': self.course.pk})

    def test_get_unenrolled_users(self):
        """Test the get get_unenrolledusers."""
        teacher_user, teacher_pass, teacher = test.set_up_user_and_auth('teacher', 'pass', 'teach@teach.com')
        test.set_up_participation(teacher, self.course, 'Teacher')
        test.set_up_participation(self.lars, self.course, 'Student')
        test.set_up_participation(self.rein, self.course, 'TA')

        login = test.logging_in(self, teacher_user, teacher_pass)

        response = test.api_get_call(self, '/participations/unenrolled/', login, params={'course_id': self.course.pk})

        self.assertEquals(len(response.json()['participants']), 2)
        self.assertEquals(response.json()['participants'][0]['username'], self.username)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/participations/unenrolled/', login, status=403, params={'course_id': self.course.pk})
        test.test_unauthorized_api_get_call(self, '/participations/unenrolled/', params={'course_id': self.course.pk})

        test.set_up_participation(self.no_permission_user, self.course, 'Student')
        test.api_get_call(self, '/participations/unenrolled/', login, status=403, params={'course_id': self.course.pk})

    def test_GDPR(self):
        # Test normal user
        login = test.logging_in(self, self.username, self.password)
        _, _, other_user = test.set_up_user_and_auth('teacher', 'pass', 'teach@teach.com')

        # Other user
        test.api_get_call(self, '/users/{0}/GDPR/'.format(other_user.pk), login, status=403)

        # Multiple times its own
        for _ in range(int(api_settings.DEFAULT_THROTTLE_RATES['gdpr'].split('/')[0])):
            test.api_get_call(self, '/users/0/GDPR/', login)
        test.api_get_call(self, '/users/0/GDPR/', login, status=429)

        # Test super user
        self.user.is_superuser = True
        self.user.save()

        # Other user
        test.api_get_call(self, '/users/{0}/GDPR/'.format(other_user.pk), login, status=403)

        # Multiple times its own
        for _ in range(int(api_settings.DEFAULT_THROTTLE_RATES['gdpr'].split('/')[0])):
            test.api_get_call(self, '/users/0/GDPR/', login)
        test.api_get_call(self, '/users/0/GDPR/', login)

        self.user.is_superuser = False
        self.user.save()

    def test_get_user_courses(self):
        """Test the get user courses function."""
        for course in test.set_up_courses('course', 4):
            student_role = Role.objects.get(name='Student', course=course)
            factory.make_participation(self.user, course, student_role)

        login = test.logging_in(self, self.username, self.password)

        response = test.api_get_call(self, '/courses/', login)
        self.assertEquals(len(response.json()['courses']), 4)

        # permissions and authorization check for the api call.
        test.test_unauthorized_api_get_call(self, '/courses/')

    def test_get_linkable_courses(self):
        """Test the get linkable courses function."""
        self.user.is_teacher = True
        self.user.save()

        test.set_up_courses('course', 3, author=self.user)
        test.set_up_courses('course', 4, author=self.user, lti_id=True)

        login = test.logging_in(self, self.username, self.password)

        response = test.api_get_call(self, '/courses/linkable/', login)
        self.assertEquals(len(response.json()['courses']), 7)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/courses/linkable/', login, status=403)
        test.test_unauthorized_api_get_call(self, '/courses/linkable/')

    def test_get_course_assignments(self):
        """Test the get course assignment function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein, enddate=timezone.now())
        assigns = test.set_up_assignments('assign', 'desc', 2, course=course)
        test.set_up_participation(self.user, course, 'Student')
        factory.make_journal(assigns[0], self.user)
        factory.make_journal(assigns[1], self.user)

        login_user = test.logging_in(self, self.username, self.password)
        response = test.api_get_call(self, '/assignments/', login_user, params={'course_id': course.pk})
        self.assertEquals(len(response.json()['assignments']), 2)
        self.assertIn('journal', response.json()['assignments'][0])

        login_rein = test.logging_in(self, self.rein_user, self.rein_pass)
        response = test.api_get_call(self, '/assignments/', login_rein, params={'course_id': course.pk})
        self.assertEquals(len(response.json()['assignments']), 2)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/assignments/', login, status=403, params={'course_id': course.pk})
        test.api_get_call(self, '/assignments/', login, status=404, params={'course_id': self.not_found_pk})
        test.test_unauthorized_api_get_call(self, '/assignments/' + str(course.pk) + '/')

    def test_get_assignment_data(self):
        """Test the get assignment data function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format1 = factory.make_format([template])
        format2 = factory.make_format([template])
        assignment1 = factory.make_assignment('Colloq', 'description1', format=format1, courses=[course],
                                              is_published=True)
        assignment2 = factory.make_assignment('Portfolio', 'description2', format=format2, courses=[course],
                                              is_published=True)

        test.set_up_participation(self.user, course, 'Student')

        login_user = test.logging_in(self, self.username, self.password)
        resp = test.api_get_call(self, '/assignments/' + str(assignment1.pk) + '/', login_user)
        self.assertEquals(resp.json()['assignment']['name'], 'Colloq')
        self.assertIn('journal', resp.json()['assignment'])

        login_rein = test.logging_in(self, self.rein_user, self.rein_pass)
        resp = test.api_get_call(self, '/assignments/' + str(assignment2.pk) + '/',
                                 login_rein)
        self.assertEquals(resp.json()['assignment']['name'], 'Portfolio')

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/assignments/{}/'.format(assignment1.pk), login, status=403)
        test.api_get_call(self, '/assignments/{}/'.format(assignment2.pk), login, status=403)
        test.test_unauthorized_api_get_call(self, '/assignments/{}/'.format(assignment1.pk))

    def test_assignment_journals(self):
        """Test the get assignment journals function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course])
        students = test.set_up_users('student', 2)
        for student in students:
            test.set_up_participation(student, course, 'Student')
            test.set_up_journal(assignment, template, student, 4)

        login = test.logging_in(self, self.rein_user, self.rein_pass)
        response = test.api_get_call(self,
                                     '/journals/',
                                     login,
                                     params={'course_id': course.pk, 'assignment_id': assignment.pk})
        result = response.json()
        self.assertEquals(len(result['journals']), 2)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self,
                          '/journals/',
                          login,
                          status=403,
                          params={'course_id': course.pk, 'assignment_id': assignment.pk})
        test.api_get_call(self,
                          '/journals/',
                          login,
                          status=404,
                          params={'course_id': course.pk, 'assignment_id': self.not_found_pk})

        test.api_get_call(self,
                          '/journals/',
                          login,
                          status=400,
                          params={})
        test.test_unauthorized_api_get_call(self,
                                            '/journals/',
                                            params={'course_id': course.pk, 'assignment_id': self.not_found_pk})

    def test_get_nodes(self):
        """Test the get nodes function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course])
        student_user, student_pass, student = test.set_up_user_and_auth('student', 'pass', 'student@student.com')
        test.set_up_participation(student, course, 'Student')
        journal = test.set_up_journal(assignment, template, student, 4)

        login = test.logging_in(self, student_user, student_pass)
        response = test.api_get_call(self, '/nodes/', login, params={'journal_id': journal.pk})
        result = response.json()
        self.assertEquals(len(result['nodes']), 5)

        login = test.logging_in(self, self.rein_user, self.rein_pass)
        response = test.api_get_call(self, '/nodes/', login, params={'journal_id': journal.pk})
        result = response.json()
        self.assertEquals(len(result['nodes']), 4)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/nodes/', login, status=403, params={'journal_id': journal.pk})
        test.api_get_call(self, '/nodes/', login, status=404, params={'journal_id': self.not_found_pk})
        test.test_unauthorized_api_get_call(self, '/nodes/', params={'journal_id': journal.pk})

    def test_get_format(self):
        """Test get format."""
        course1 = factory.make_course('Portfolio2016', 'PAV', author=self.rein)
        course2 = factory.make_course('Portfolio2017', 'PAV', author=self.rein)
        course3 = factory.make_course('Portfolio2018', 'PAV')
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format,
                                             courses=[course1, course2, course3])
        login = test.logging_in(self, self.rein_user, self.rein_pass)
        response = test.api_get_call(self, '/formats/' + str(assignment.pk) + '/', login)
        self.assertEquals(response.json()['format']['templates'][0]['name'], 'template')

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/formats/' + str(assignment.pk) + '/', login, status=403)
        test.api_get_call(self, '/formats/' + str(self.not_found_pk) + '/', login, status=404)
        test.test_unauthorized_api_get_call(self, '/formats/' + str(assignment.pk) + '/')

    def test_get_course_roles(self):
        """Test the get delete assignment function."""
        teacher_user = 'Teacher'
        teacher_pass = 'pass'
        teacher = factory.make_user(teacher_user, teacher_pass, "teach@teach.com")
        factory.make_role_student("SD", self.course)
        factory.make_role_default_no_perms("HE", self.course)
        teacher_role = factory.make_role_teacher("TE", self.course)
        factory.make_participation(teacher, self.course, teacher_role)
        login = test.logging_in(self, teacher_user, teacher_pass)
        result = test.api_get_call(self, '/roles/', login, params={'course_id': 1})
        self.assertEquals(len(result.json()['roles']), 6)

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.test_unauthorized_api_get_call(self, '/roles/', params={'course_id': 1})
        test.api_get_call(self, '/roles/', login, params={'course_id': 1}, status=403)
        test.api_get_call(self, '/roles/', login, params={'course_id': self.not_found_pk}, status=404)

        test.set_up_participation(self.no_permission_user, self.course, 'Student')
        test.api_get_call(self, '/roles/', login, params={'course_id': 1}, status=403)

    def test_get_user_teacher_courses(self):
        """Test get user teacher course function."""
        factory.make_course('Portfolio2016', 'PAV', author=self.rein)
        factory.make_course('Portfolio2017', 'PAV', author=self.rein)
        factory.make_course('Portfolio2018', 'PAV')

        login = test.logging_in(self, self.rein_user, self.rein_pass)
        response = test.api_get_call(self, '/courses/', login)
        self.assertEquals(len(response.json()['courses']), 2)

        # permissions and authorization check for the api call.
        test.test_unauthorized_api_get_call(self, '/courses/')

    def test_get_names(self):
        """Test get names function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course],
                                             is_published=True)
        student_user, student_pass, student = test.set_up_user_and_auth('student', 'pass', 's@s.com', 'first', 'last')
        test.set_up_participation(student, course, 'Student')
        journal = test.set_up_journal(assignment, template, student, 4)

        login = test.logging_in(self, student_user, student_pass)
        url = '/names/{}/{}/{}/'.format(course.pk, assignment.pk, journal.pk)
        result = test.api_get_call(self, url, login).json()
        self.assertEquals(result['names']['course'], 'Portfolio')
        self.assertEquals(result['names']['journal'], 'first last')
        self.assertEquals(result['names']['assignment'], 'Colloq')

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, url, login, status=403)

    def test_get_comments(self):
        """Test get comments function."""
        course = factory.make_course('Portfolio', 'PAV', author=self.rein)
        template = factory.make_entry_template('template')
        format = factory.make_format([template])
        assignment = factory.make_assignment('Colloq', 'description1', format=format, courses=[course])
        student_user, student_pass, student = test.set_up_user_and_auth('student', 'pass', 's@s.com')
        test.set_up_participation(student, course, 'Student')
        journal = factory.make_journal(assignment, student)
        entry = factory.make_entry(template)
        factory.make_node(journal, entry)
        factory.make_comment(entry, self.rein, 'Excellent!', True)

        login = test.logging_in(self, student_user, student_pass)

        result = test.api_get_call(self, '/comments/', login, params={'entry_id': entry.pk}).json()
        self.assertEquals(result['comments'][0]['text'], 'Excellent!')

        # permissions and authorization check for the api call.
        login = test.logging_in(self, self.no_perm_user, self.no_perm_pass)
        test.api_get_call(self, '/comments/', login, status=403, params={'entry_id': entry.pk})
        test.api_get_call(self, '/comments/', login, status=404, params={'entry_id': self.not_found_pk})
        test.test_unauthorized_api_get_call(self, '/comments/', params={'entry_id': entry.pk})
