
import test.test_utils as test

from django.test import TestCase

from VLE.models import Instance


class InstanceApiTests(TestCase):

        def setUp(self):
            # Create superuser
            self.supername, self.superpass, self.user = test.set_up_user_and_auth('super', 'pass', 'super@user.com')
            self.user.is_superuser = True
            self.user.save()

            # Create student
            self.studentname, self.studentpass, self.student = test.set_up_user_and_auth(
                'student', 'pass', 'student@user.com')
            self.instance_data = {
                'name': 'UvA',
            }

        def test_get_instance(self):
            student = test.logging_in(self, self.studentname, self.studentpass)
            superuser = test.logging_in(self, self.supername, self.superpass)

            test.api_get_call(self, '/instance/0/', login=student)
            test.api_get_call(self, '/instance/0/', login=superuser)
            self.assertEqual(Instance.objects.get(pk=1).name, 'eJournal')

        def test_update_instance(self):
            student = test.logging_in(self, self.studentname, self.studentpass)
            superuser = test.logging_in(self, self.supername, self.superpass)

            test.api_patch_call(self, '/instance/0/', {'name': 'UvA'}, login=student, status=403)
            test.api_patch_call(self, '/instance/0/', {'name': 'UvA'}, login=superuser)
            self.assertEqual(Instance.objects.get(pk=1).name, 'UvA')
