from django.test import TestCase

from VLE.models import Course, Assignment, Role

import VLE.factory as factory
import VLE.serializers as serialize
import test.test_utils as test


class DeleteApiTests(TestCase):
    def setUp(self):
        """Setup"""
        self.username, self.password, self.user = test.set_up_user_and_auth('test', 'test123', 'testt@testt.com')
        self.course = factory.make_course("Beeldbewerken", "BB")

    def test_delete_course(self):
        """Test delete_course"""
        login = test.logging_in(self, self.username, self.password)

        bb = factory.make_course("Beeldbewerken", "BB")
        factory.make_course("Portfolio Academische Vaardigheden", "PAV")

        role = factory.make_role_default_no_perms("teacher", bb, can_delete_course=True)
        factory.make_participation(user=self.user, course=bb, role=role)

        test.api_del_call(self, '/courses/' + str(bb.pk) + '/', login)

        self.assertEquals(Course.objects.filter(name="Beeldbewerken").count(), 1)
        self.assertEquals(Course.objects.filter(name="Portfolio Academische Vaardigheden").count(), 1)

    def delete_user_from_course(self):
        """Test delete_user_from_course"""
        login = test.logging_in(self, self.username, self.password)

        course = factory.make_course("Beeldbewerken", "BB")

        rein = factory.make_user("Rein", "123", "r@r.com")
        lars = factory.make_user("Lars", "123", "l@l.com")

        role = factory.make_role_default_no_perms("test", course)
        factory.make_participation(rein, course, role=role)
        factory.make_participation(lars, course, role=role)

        test.api_del_call(self,
                          '/participations/' + course.pk + '/',
                          {'user_id': rein.user_role.pk},
                          login)

        participations = course.participation_set.all()
        participations = [serialize.participation_to_dict(participation)
                          for participation in participations]

        self.assertEquals(participations.count(), 1)
        self.assertEquals(participations[0]['name'], 'Lars')

    def test_delete_assignment(self):
        """Test delete_assignment."""
        login = test.logging_in(self, self.username, self.password)

        course1 = factory.make_course("Portfolio Academische Vaardigheden", "PAV")
        course2 = factory.make_course("BeeldBewerken", "BB")

        assign1 = factory.make_assignment("Colloq", "In de opdracht...1", self.user)
        assign2 = factory.make_assignment("Logboek", "In de opdracht...2", self.user)

        role = factory.make_role_default_no_perms("teacher", self.course, can_delete_assignment=True)
        factory.make_participation(user=self.user, course=self.course, role=role)

        role = factory.make_role_default_no_perms("teacher", course1, can_delete_assignment=True)
        factory.make_participation(user=self.user, course=course1, role=role)

        role = factory.make_role_default_no_perms("teacher", course2, can_delete_assignment=True)
        factory.make_participation(user=self.user, course=course2, role=role)

        assign1.courses.add(course1)
        assign1.courses.add(course2)
        assign2.courses.add(course1)

        test.api_del_call(self, '/assignments/' + str(assign1.pk) + '/?course_id=1', login)
        assignment = Assignment.objects.get(pk=1)
        self.assertEquals(assignment.courses.count(), 2)

        test.api_del_call(self, '/assignments/1/?course_id=1', login)
        self.assertEquals(Assignment.objects.filter(pk=1).count(), 1)

    def test_delete_course_role(self):
        """Test delete course roles"""
        teacher_user = 'Teacher'
        teacher_pass = 'pass'
        teacher = factory.make_user(teacher_user, teacher_pass, "teach@teach.com")
        teacher_role = factory.make_role_teacher("TE", self.course)
        factory.make_participation(teacher, self.course, teacher_role)
        factory.make_role_ta('TA2', self.course)
        login = test.logging_in(self, teacher_user, teacher_pass)
        test.api_del_call(
            self, '/roles/' + str(self.course.pk) + '/?name=TA2', login)

        self.assertEquals(Role.objects.filter(name='TA2', course=Course.objects.get(pk=1)).count(), 0)
