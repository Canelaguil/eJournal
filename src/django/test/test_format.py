import test.factory as factory
from test.utils import api

from django.test import TestCase

import VLE.serializers as serialize


class FormatAPITest(TestCase):
    def setUp(self):
        self.teacher = factory.Teacher()
        self.admin = factory.Admin()
        self.course = factory.Course(author=self.teacher)
        self.assignment = factory.Assignment(courses=[self.course])
        self.template = factory.Template()
        self.format = factory.Format(assignment=self.assignment)
        self.format.available_templates.add(self.template)
        self.update_dict = {
            'assignment_details': {
                'name': 'Colloq',
                'description': 'description1',
                'is_published': True
            },
            'templates': serialize.TemplateSerializer(self.format.available_templates.all(), many=True).data,
            'removed_presets': [],
            'removed_templates': [],
            'presets': [],
            'unused_templates': []
        }

    def test_update(self):
        # TODO: Improve template testing
        api.update(self, 'formats', params={
                'pk': self.assignment.pk, 'assignment_details': None,
                'templates': [], 'presets': [], 'unused_templates': [], 'removed_presets': [],
                'removed_templates': []
            }, user=factory.User(), status=403)
        api.update(self, 'formats', params={
                'pk': self.assignment.pk, 'assignment_details': None,
                'templates': [], 'presets': [], 'unused_templates': [], 'removed_presets': [],
                'removed_templates': []
            }, user=self.teacher)
        api.update(self, 'formats', params={
                'pk': self.assignment.pk, 'assignment_details': None,
                'templates': [], 'presets': [], 'unused_templates': [], 'removed_presets': [],
                'removed_templates': []
            }, user=factory.Admin())
