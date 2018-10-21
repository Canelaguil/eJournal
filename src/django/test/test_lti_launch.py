"""
test_lti_launch.py.

Test lti launch.
"""

import datetime
import test.test_utils as test
import time

import jwt
import oauth2
from django.conf import settings
from django.test import RequestFactory, TestCase

import VLE.factory as factory
import VLE.lti_launch as lti
import VLE.views.lti as lti_view
from VLE.models import Lti_ids, Role, User


class canEnterThroughLTI(TestCase):
    """Lti launch test.

    Test if the gradepassback XML can be created.
    """

    def setUp(self):
        """Setup."""
        self.factory = RequestFactory()

        self.request = {"oauth_consumer_key": settings.LTI_KEY,
                        "oauth_signature_method": "HMAC-SHA1",
                        "oauth_version": "1.0",
                        "custom_assignment_due": "2018-11-10 23:59:00 +0100",
                        "custom_assignment_id": "bughh",
                        "custom_assignment_lock": "2018-12-15 23:59:59 +0100",
                        "custom_assignment_title": "TestAss",
                        "custom_assignment_unlock": "2018-08-16 00:00:00 +0200",
                        "custom_assignment_points": "10",
                        "custom_course_id": "asdf",
                        "custom_course_name": "TestCourse",
                        "custom_course_start": "2018-06-15 14:41:00 +0200",
                        "context_label": "aaaa",
                        "lti_message_type": "basic-lti-launch-request",
                        "lti_version": "LTI-1p0",
                        'custom_username': 'Test',
                        "roles": "Instructor",
                        "custom_user_image": "https://uvadlo-tes.instructure.com/images/thumbnails/11601/\
6ivT7povCYWoXPCVOSnfPqWADsLktcGXTXkAUYDv",
                        "user_id": "0000"}

        self.oauth_consumer = oauth2.Consumer(
            settings.LTI_KEY, settings.LTI_SECRET
        )

        self.username, self.password, self.user = test.set_up_user_and_auth('TestUser', 'Pass', 'ltiTest@test.com')
        self.user.lti_id = 'awefd'
        self.user.verified_email = True
        self.user.save()

        self.created_assignment = factory.make_assignment("TestAss", "TestDescr")
        self.created_journal = factory.make_journal(self.created_assignment, self.user)

    def test_select_user(self):
        """Hopefully select a user."""
        selected_user = lti.check_user_lti({
            'user_id': self.user.lti_id,
        })
        self.assertEquals(selected_user, self.user)

    def test_lti_launch_no_user_no_info(self):
        """Hopefully gives redirect with state = NO_USER."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.NO_USER), response.url)

    def test_lti_launch_no_user(self):
        """Hopefully gives redirect with state = NO_USER."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        self.request["custom_user_full_name"] = "testpersoon voor Science"
        self.request["custom_username"] = "TestUser"
        self.request["custom_user_email"] = "ltiTest@test.com"
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.NO_USER), response.url)

    def test_lti_launch_user(self):
        """Hopefully gives redirect with state = LOGGED_IN."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        self.request["user_id"] = "awefd"
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.LOGGED_IN), response.url)

    def test_lti_launch_multiple_roles(self):
        """Hopefully gives redirect with state = LOGGED_IN."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        self.request["user_id"] = "awefd"
        self.request["roles"] = 'Learner,Instructor'
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.LOGGED_IN), response.url)
        self.assertTrue(User.objects.filter(lti_id='awefd')[0].is_teacher)

    def test_lti_launch_unknown_role(self):
        """Hopefully gives redirect with state = LOGGED_IN."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        self.request["user_id"] = "awefd"
        self.request["roles"] = 'urn:lti:instrole:ims/lis/Administrator'
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.LOGGED_IN), response.url)

    def test_lti_launch_wrong_signature(self):
        """Hopefully gives redirect with state = BAD_AUTH."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        self.request["user_id"] = "awefd"
        self.request["oauth_signature"] = "1a2f3r"
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.BAD_AUTH), response.url)

    def test_lti_launch_key_error(self):
        """Hopefully gives redirect with state = KEY_ERR."""
        self.request["oauth_timestamp"] = str(int(time.time()))
        self.request["oauth_nonce"] = oauth2.generate_nonce()
        del self.request['custom_username']
        oauth_request = oauth2.Request.from_request(
            'POST', 'http://testserver/lti/launch', parameters=self.request
        )
        signature = oauth2.SignatureMethod_HMAC_SHA1().sign(oauth_request, self.oauth_consumer, {}).decode('utf-8')
        self.request['oauth_signature'] = signature
        request = self.factory.post('http://127.0.0.1:8000/lti/launch', self.request)
        response = lti_view.lti_launch(request)
        self.assertEquals(response.status_code, 302)
        self.assertIn('state={0}'.format(lti_view.KEY_ERR), response.url)

    def test_get_lti_params_from_jwt_invalid(self):
        """Hopefully returns the lti course and assignment data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        jwt_params = jwt.encode(self.request, 'fa12f4', algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=401)
        self.assertIn('Invalid', response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_unauthorized(self):
        """Hopefully returns the lti course and assignment data."""
        self.request["user_id"] = "awefd"
        jwt_params = jwt.encode(self.request, 'fa12f4', algorithm='HS256').decode('utf-8')
        request = self.factory.get('/get_lti_params_from_jwt/{0}/'.format(jwt_params))
        response = lti_view.get_lti_params_from_jwt(request, jwt_params)
        self.assertEquals(response.status_code, 401)

    def test_get_lti_params_from_jwt_expired(self):
        """Hopefully returns the lti course and assignment data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request['exp'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=403)
        self.assertIn('expired', response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_course_teacher(self):
        """Hopefully returns the lti course and assignment data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.NEW_COURSE), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_course_student(self):
        """Hopefully returns the lti course and assignment data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request["roles"] = settings.ROLES["Student"]
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=404)
        self.assertIn('course', response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_assignment_teacher(self):
        """Hopefully returns the lti assignment data."""
        factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.NEW_ASSIGN), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_no_context_label(self):
        """Hopefully returns the lti course data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        del self.request['context_label']
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.NEW_COURSE), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_assignment_student(self):
        """Hopefully returns the lti assignment data."""
        factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request["roles"] = settings.ROLES["Student"]
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=404)
        self.assertIn('assignment', response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_journal_teacher(self):
        """Hopefully returns the LTI assignment and course."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        factory.make_assignment("TestAss", "TestDescr", lti_id='bughh', courses=[course])
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.FINISH_T), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_journal_student(self):
        """Hopefully returns the lti journal data."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        factory.make_assignment("TestAss", "TestDescr", lti_id='bughh', courses=[course])
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request["roles"] = settings.ROLES["Student"]
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.FINISH_S), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_multiple_roles(self):
        """Test case for when multible roles are given ."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        factory.make_assignment("TestAss", "TestDescr", lti_id='bughh', courses=[course])
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request["roles"] = 'Learner,Instructor'
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.FINISH_T), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_unknown_role(self):
        """Test case for when a unknown role is given ."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        factory.make_assignment("TestAss", "TestDescr", lti_id='bughh', courses=[course])
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        self.request["roles"] = 'urn:lti:instrole:ims/lis/Administrator'
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=200)
        self.assertIn('"state": "{0}"'.format(lti_view.FINISH_S), response.content.decode('utf-8'))

    def test_get_lti_params_from_jwt_key_Error(self):
        """Hopefully returns the lti course data."""
        login = test.logging_in(self, self.username, self.password)
        self.request["user_id"] = "awefd"
        del self.request['custom_course_id']
        jwt_params = jwt.encode(self.request, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
        response = test.api_get_call(self, '/get_lti_params_from_jwt/{0}/'.format(jwt_params), login=login, status=400)
        self.assertIn('KeyError', response.content.decode('utf-8'))

    def test_select_course_with_participation(self):
        """Hopefully select a course."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        factory.make_participation(self.user, course, Role.objects.create(name='role', course=course))
        selected_course = lti.check_course_lti({
            'custom_course_id': Lti_ids.objects.filter(course=course)[0].lti_id,
        },
            user=self.user,
            role=settings.ROLES['Teacher']
        )
        self.assertEquals(selected_course, course)

    def test_select_journal(self):
        """Hopefully select a journal."""
        selected_journal = lti.select_create_journal({
            'roles': settings.ROLES['Student'],
            'lis_result_sourcedid': "267-686-2694-585-0afc8c37342732c97b011855389af1f2c2f6d552",
            'lis_outcome_service_url': "https://uvadlo-tes.instructure.com/api/lti/v1/tools/267/grade_passback"
        },
            user=self.user,
            assignment=self.created_assignment
        )
        self.assertEquals(selected_journal, self.created_journal)

    def test_select_journal_no_assign(self):
        """Hopefully select None."""
        selected_journal = lti.select_create_journal({
            'roles': settings.ROLES['Student'],
            'lis_result_sourcedid': "267-686-2694-585-0afc8c37342732c97b011855389af1f2c2f6d552",
            'lis_outcome_service_url': "https://uvadlo-tes.instructure.com/api/lti/v1/tools/267/grade_passback"
        },
            user=self.user,
            assignment=None
        )
        self.assertEquals(selected_journal, None)
