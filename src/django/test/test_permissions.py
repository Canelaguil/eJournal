"""
test_permissions.py

This file tests whether all permissions behave as required.
"""
import datetime

from django.test import TestCase
from django.core.validators import ValidationError

import VLE.factory as factory
import VLE.permissions as permissions
from VLE.utils.error_handling import VLEProgrammingError


class PermissionTests(TestCase):
    """Test the permission system.

    Test whether the permissions behave as required.
    """

    def setUp(self):
        self.user = factory.make_user('Username', 'Password', email='some@email.address')

        self.course1 = factory.make_course('Course', 'crs', startdate=datetime.date.today())
        self.course2 = factory.make_course('Course2', 'crs2', startdate=datetime.date.today())
        self.course_independent = factory.make_course('Independent Course', 'crs3', startdate=datetime.date.today())

        self.assignment = factory.make_assignment('Assignment', 'Assignment linked to multiple courses.',
                                                  courses=[self.course1, self.course2])
        self.assignment_independent = factory.make_assignment('Assignment2', 'Assignment linked to separate course.',
                                                              courses=[self.course_independent])

    def test_no_permissions(self):
        """Ensure the user has no permissions when given no permissions."""
        role = factory.make_role_default_no_perms('SD', self.course_independent)
        factory.make_participation(self.user, self.course_independent, role)

        self.assertFalse(self.user.has_permission('can_edit_institute_details'))
        self.assertFalse(self.user.has_permission('can_add_course'))
        self.assertFalse(self.user.has_permission('can_delete_course', self.course_independent))
        self.assertFalse(self.user.has_permission('can_have_journal', self.assignment_independent))

    def test_permission(self):
        """Test whether the user has only the given permission."""
        role = factory.make_role_default_no_perms("SD", self.course_independent, can_delete_assignment=True)
        factory.make_participation(self.user, self.course_independent, role)

        self.assertTrue(self.user.has_permission('can_delete_assignment', self.course_independent))

        self.assertFalse(self.user.has_permission('can_delete_course_user_group', self.course_independent))
        self.assertFalse(self.user.has_permission('can_delete_assignment', self.course1))
        self.assertFalse(self.user.has_permission('can_delete_assignment', self.course2))

    def test_assignment_permission(self):
        """Test whether the user has only the given assignment permission."""
        role = factory.make_role_default_no_perms("SD", self.course_independent, can_have_journal=True)
        factory.make_participation(self.user, self.course_independent, role)

        self.assertTrue(self.user.has_permission('can_have_journal', self.assignment_independent))

        self.assertFalse(self.user.has_permission('can_add_course'))
        self.assertFalse(self.user.has_permission('can_edit_assignment', self.assignment_independent))
        self.assertFalse(self.user.has_permission('can_have_journal', self.assignment))

    def test_multi_course_assignment_permission(self):
        """Test whether the assignment has the correct permissions when bound to multiple courses."""
        role = factory.make_role_default_no_perms("SD", self.course1, can_have_journal=True)
        factory.make_participation(self.user, self.course1, role)
        role = factory.make_role_default_no_perms("SD", self.course2, can_have_journal=False)
        factory.make_participation(self.user, self.course2, role)

        self.assertTrue(self.user.has_permission('can_have_journal', self.assignment))

        self.assertFalse(self.user.has_permission('can_edit_assignment', self.assignment))

    def test_multi_course_assignment_negations(self):
        """Test whether the assignment has the correct permissions when bound to multiple courses,
        by negation."""
        role = factory.make_role_default_no_perms("SD", self.course1, can_have_journal=True)
        factory.make_participation(self.user, self.course1, role)
        role = factory.make_role_default_no_perms("SD", self.course2, can_view_assignment_journals=True)
        factory.make_participation(self.user, self.course2, role)

        self.assertTrue(self.user.has_permission('can_view_assignment_journals', self.assignment))

        self.assertFalse(self.user.has_permission('can_have_journal', self.assignment))

    def test_permission_constraints(self):
        factory.make_role_default_no_perms("SD1", self.course1,
                                           can_have_journal=True)
        factory.make_role_default_no_perms("SD2", self.course1,
                                           can_view_assignment_journals=True)
        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SD3", self.course1,
                          can_have_journal=True, can_view_assignment_journals=True)

        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SD4", self.course1,
                          can_add_course_users=True)
        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SD5", self.course1,
                          can_delete_course_users=True)
        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SD6", self.course1,
                          can_edit_course_user_group=True)
        factory.make_role_default_no_perms("SD7", self.course1,
                                           can_add_course_users=True, can_view_course_users=True)
        factory.make_role_default_no_perms("SD8", self.course1,
                                           can_delete_course_users=True, can_view_course_users=True)
        factory.make_role_default_no_perms("SD9", self.course1,
                                           can_edit_course_user_group=True, can_view_course_users=True)

        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SDA", self.course1,
                          can_grade=True)
        factory.make_role_default_no_perms("SDB", self.course1,
                                           can_grade=True, can_view_assignment_journals=True)

        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SDC", self.course1,
                          can_publish_grades=True)
        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SDD", self.course1,
                          can_publish_grades=True, can_view_assignment_journals=True)
        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SDE", self.course1,
                          can_publish_grades=True, can_grade=True)
        factory.make_role_default_no_perms("SDF", self.course1,
                                           can_publish_grades=True, can_grade=True, can_view_assignment_journals=True)

        self.assertRaises(ValidationError, factory.make_role_default_no_perms, "SDG", self.course1,
                          can_comment=True)
        factory.make_role_default_no_perms("SDH", self.course1,
                                           can_comment=True, can_view_assignment_journals=True)
        factory.make_role_default_no_perms("SDI", self.course1,
                                           can_comment=True, can_have_journal=True)

    def test_admin_permissions(self):
        """Test if the admin has all permissions."""
        user = factory.make_user('superuser', 'password', email='some@other', is_superuser=True)

        self.assertTrue(user.has_permission('can_edit_institute_details'))
        self.assertTrue(user.has_permission('can_add_course'))
        self.assertTrue(user.has_permission('can_delete_course', self.course_independent))
        self.assertTrue(user.has_permission('can_edit_assignment', self.assignment_independent))

        self.assertFalse(user.has_permission('can_have_journal', self.assignment_independent))

    def test_teacher_permissions(self):
        """Test if the teacher has the right general permissions."""
        user = factory.make_user('teacher', 'password', email='some@other', is_teacher=True)

        self.assertTrue(user.has_permission('can_add_course'))

        self.assertFalse(user.has_permission('can_edit_institute_details'))
        self.assertFalse(user.has_permission('can_delete_course', self.course_independent))
        self.assertFalse(user.has_permission('can_edit_assignment', self.assignment_independent))
        self.assertFalse(user.has_permission('can_have_journal', self.assignment_independent))

    def test_invalid_permission(self):
        """Ensure the call does not silently fail when passed an invalid permission."""
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'invalid')
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'invalid', self.course_independent)
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'invalid', self.assignment_independent)

    def test_invalid_usage(self):
        """Ensure the call does not silently fail when passed an invalid argument."""
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_have_journal', 5)

    def test_invalid_level(self):
        """Ensure the call of a valid permission on an incorrect level does not silently fail."""
        # General permission on course and assignment level.
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_add_course', self.course_independent)
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_add_course', self.assignment)

        # Course permission on general and assignment level.
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_delete_course')
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_delete_course', self.assignment)

        # Assignment permission on general and course level.
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_have_journal')
        self.assertRaises(VLEProgrammingError, self.user.has_permission, 'can_have_journal', self.course_independent)

    def test_is_course_participant(self):
        """Test if is_participant correctly represents whether the user is participating
        in a course or not."""
        role = factory.make_role_default_no_perms("SD", self.course_independent)
        factory.make_participation(self.user, self.course_independent, role)

        self.assertTrue(self.user.is_participant(self.course_independent))

        self.assertFalse(self.user.is_participant(self.course1))
        self.assertFalse(self.user.is_participant(self.course2))

    def test_is_assignment_participant(self):
        """Test if is_participant correctly represent whether the user is participating
        in an assignment or not."""
        role = factory.make_role_default_no_perms("SD", self.course_independent)
        factory.make_participation(self.user, self.course_independent, role)

        self.assertTrue(self.user.is_participant(self.assignment_independent))

        self.assertFalse(self.user.is_participant(self.assignment))

    def test_is_multi_participant(self):
        """Test if participating in one course does not implicitly participate the user
        in another course or assignment."""
        role = factory.make_role_default_no_perms("SD", self.course1)
        factory.make_participation(self.user, self.course1, role)

        self.assertTrue(self.user.is_participant(self.course1))
        self.assertTrue(self.user.is_participant(self.assignment))

        self.assertFalse(self.user.is_participant(self.course2))
        self.assertFalse(self.user.is_participant(self.course_independent))
        self.assertFalse(self.user.is_participant(self.assignment_independent))

    def test_is_participant_invalid(self):
        self.assertRaises(VLEProgrammingError, self.user.is_participant, None)
        self.assertRaises(VLEProgrammingError, self.user.is_participant, 5)
        self.assertRaises(VLEProgrammingError, self.user.is_participant, 'something')

    def test_serialize(self):
        result = permissions.serialize_general_permissions(self.user)
        self.assertFalse(result['can_edit_institute_details'])
        self.assertFalse(result['can_add_course'])
        self.assertEquals(len(permissions.GENERAL_PERMISSIONS), len(result))

        role = factory.make_role_default_no_perms("SD", self.course_independent,
                                                  can_view_course_users=True, can_edit_assignment=True)
        factory.make_participation(self.user, self.course_independent, role)

        result = permissions.serialize_course_permissions(self.user, self.course_independent)
        self.assertTrue(result['can_view_course_users'])
        self.assertFalse(result['can_edit_course_details'])
        self.assertEquals(len(permissions.COURSE_PERMISSIONS), len(result))

        result = permissions.serialize_assignment_permissions(self.user, self.assignment_independent)
        self.assertTrue(result['can_edit_assignment'])
        self.assertFalse(result['can_have_journal'])
        self.assertEquals(len(permissions.ASSIGNMENT_PERMISSIONS), len(result))
