import test.factory as factory
from test.utils import api
from test.utils.response import is_response

from django.test import TestCase


class CourseAPITest(TestCase):
    def setUp(self):
        self.create_params = {'name': 'test_course', 'abbreviation': 'TC'}
        self.student = factory.User()
        self.teacher1 = factory.Teacher()
        self.teacher2 = factory.Teacher()
        self.admin = factory.Admin()

        self.course1 = factory.Course(author=self.teacher1)
        self.course2 = factory.Course(author=self.teacher1)
        self.course3 = factory.Course(author=self.teacher2)

    def test_rest(self):
        # Test the basic rest functionality as a superuser
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=factory.Admin())

        # Test the basic rest functionality as a teacher
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      update_params={'abbreviation': 'TC2'},
                      user=factory.Teacher())

        # Test the basic rest functionality as a student
        api.test_rest(self, 'courses',
                      create_params=self.create_params,
                      create_status=403,
                      user=factory.User())

    def test_get(self):
        factory.Participation(user=self.teacher2, course=self.course2)

        # Get all courses
        get_resp = api.get(self, 'courses', user=self.teacher1)['courses']
        assert len(get_resp) == 2, 'The teacher did not get all the courses it is the author of'
        assert {self.course1.pk, self.course2.pk} == set([c['id'] for c in get_resp]), \
            'The teacher did not get all the courses it is the author of'

        get_resp = api.get(self, 'courses', user=self.teacher2)['courses']
        assert len(get_resp) == 2, 'The teacher did not get all the courses it is the author of or is participating in'
        assert is_response(get_resp, self.course2, self.course3), \
            'The teacher did not get all the courses it is the author of'

        # Get author course
        get_resp = api.get(self, 'courses', params={'pk': self.course1.pk}, user=self.teacher1)

        # Check not participating
        get_resp = api.get(self, 'courses', params={'pk': self.course1.pk}, user=self.teacher2, status=403)

        # Check participating
        get_resp = api.get(self, 'courses', params={'pk': self.course2.pk}, user=self.teacher2)

    def test_create(self):
        # Test courses with same name and abbreviation
        api.create(self, 'courses', params=self.create_params, user=self.teacher1)
        api.create(self, 'courses', params=self.create_params, user=self.teacher1)

        # Test admin without is_teacher can make a course
        self.admin.is_teacher = False
        self.admin.save()
        api.create(self, 'courses', params=self.create_params, user=self.admin)

        # Check that students cannot make new courses
        api.create(self, 'courses', params=self.create_params, user=self.student, status=403)

    def test_update(self):
        # Test if other then a superuser or the author self can update the course
        api.update(self, 'courses', params={'pk': self.course1.pk, 'abbreviation': 'TC2'},
                   user=self.teacher2, status=403)
        api.update(self, 'courses', params={'pk': self.course2.pk, 'abbreviation': 'TC2'},
                   user=self.teacher2, status=403)

        update_resp = api.update(self, 'courses', params={'pk': self.course2.pk, 'abbreviation': 'TC2'},
                                 user=self.teacher1)['course']
        assert update_resp['abbreviation'] == 'TC2', 'Teacher could not update the course'
        update_resp = api.update(self, 'courses', params={'pk': self.course2.pk, 'abbreviation': 'TC3'},
                                 user=self.admin)['course']
        assert update_resp['abbreviation'] == 'TC3', 'Superuser could not update the course'

    def test_delete(self):
        # Test if only authors and superusers can delete courses
        api.delete(self, 'courses', params={'pk': self.course1.pk}, user=self.teacher2, status=403)
        api.delete(self, 'courses', params={'pk': self.course1.pk}, user=self.teacher1)
        api.delete(self, 'courses', params={'pk': self.course2.pk}, user=self.admin)
