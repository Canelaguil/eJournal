import test.factory as factory
from test.utils import api
from test.utils.response import in_response

from django.test import TestCase


class GroupAPITest(TestCase):
    def setUp(self):
        self.teacher = factory.Teacher()
        self.course = factory.Course(author=self.teacher)
        self.create_params = {'name': 'test', 'course_id': self.course.pk}
        self.group = factory.Group(course=self.course)

    def test_rest(self):
        # Test the basic rest functionality as a superuser
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=factory.Admin())

        # Test the basic rest functionality as a teacher
        api.test_rest(self, 'groups',
                      create_params=self.create_params,
                      get_params={'course_id': self.course.pk}, get_status=405, get_is_create=False,
                      update_params={'name': 'test2'},
                      user=self.teacher)

        # Test the basic rest functionality as a student
        api.test_rest(self, 'groups',
                      create_params=self.create_params, get_status=405, get_is_create=False,
                      create_status=403,
                      user=factory.User())

    def test_get(self):
        # Test all groups from course
        api.get(self, 'groups', user=self.teacher, status=400)
        api.get(self, 'groups', params={'course_id': self.course.pk}, user=factory.User(), status=403)
        api.get(self, 'groups', params={'course_id': self.course.pk}, user=factory.Admin())
        get_resp = api.get(self, 'groups', params={'course_id': self.course.pk}, user=self.teacher)['groups']
        assert in_response(get_resp, self.group), 'Group that is added to  the course, should also be returned'

    def test_create(self):
        # Test required params
        api.create(self, 'groups', user=self.teacher, status=400)

        # Test unconnected admin
        api.create(self, 'groups', params={'course_id': self.course.pk, 'name': 'Test'}, user=factory.Admin())

        # Test duplicate
        api.create(self, 'groups', params={'course_id': self.course.pk, 'name': 'Test'},
                   user=self.teacher, status=400)

        # Test not authorized teacher
        api.create(self, 'groups', params={'course_id': self.course.pk, 'name': 'Test'},
                   user=factory.Teacher(), status=403)

        # Test student
        api.create(self, 'groups', params={'course_id': self.course.pk, 'name': 'Test'},
                   user=factory.User(), status=403)

    def test_update(self):
        # Test required params
        api.update(self, 'groups', params={'pk': self.group.pk}, user=factory.Admin(), status=400)

        # Test unconnected admin
        resp = api.update(self, 'groups', params={'pk': self.group.pk, 'name': 'Test2'}, user=factory.Admin())['group']
        assert resp['name'] == 'Test2'

        # Test duplicate
        factory.Group(name='duplicate', course=self.course)
        factory.Group(name='other_duplicate')
        api.update(self, 'groups', params={'pk': self.group.pk, 'name': 'duplicate'}, user=factory.Admin(), status=400)
        api.update(self, 'groups', params={'pk': self.group.pk, 'name': 'other_duplicate'}, user=factory.Admin())

    def test_delete(self):
        api.delete(self, 'groups', params={'pk': self.group.pk}, user=factory.User(), status=403)
        api.delete(self, 'groups', params={'pk': self.group.pk}, user=factory.Teacher(), status=403)
        api.delete(self, 'groups', params={'pk': self.group.pk}, user=factory.Admin())
