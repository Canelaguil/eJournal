"""
permissions.py.

All the permission functions.
"""
from collections import defaultdict

from django.forms.models import model_to_dict

import VLE.models
from VLE.utils.error_handling import VLEProgrammingError

GENERAL_PERMISSIONS = ['can_edit_institute_details', 'can_add_course']
COURSE_PERMISSIONS = ['can_edit_course_details', 'can_delete_course', 'can_edit_course_roles',
                      'can_view_course_users', 'can_add_course_users', 'can_delete_course_users',
                      'can_add_course_user_group', 'can_delete_course_user_group', 'can_edit_course_user_group',
                      'can_add_assignment', 'can_delete_assignment']
ASSIGNMENT_PERMISSIONS = ['can_edit_assignment', 'can_view_all_journals', 'can_grade',
                          'can_publish_grades', 'can_have_journal', 'can_comment', 'can_view_unpublished_assignment']


def has_general_permission(user, permission):
    """Check if the user has the needed "global" permission.

    Arguments:
    user -- user that did the request.
    permission -- the permission string to check.

    Raises VLEProgrammingError when the passed permission is not a "General Permission".
    """
    if permission not in GENERAL_PERMISSIONS:
        raise VLEProgrammingError("Permission " + permission + " is not a general level permission.")

    if user.is_superuser:
        return True

    # If the user is a teacher, he is allowed to create courses on the platform.
    if user.is_teacher and permission == 'can_add_course':
        return True

    return False


def has_course_permission(user, permission, course):
    """Check if the user has the needed permission in the given course.

    Arguments:
    user -- user that did the request.
    course -- course used to check against.
    permission -- the permission string to check.

    Raises VLEProgrammingError when the passed permission is not a "Course Permission".
    Raises VLEParticipationError when the user is not participating in the course.
    """
    if permission not in COURSE_PERMISSIONS:
        raise VLEProgrammingError("Permission " + permission + " is not a course level permission.")

    if user.is_superuser:
        return True

    user.check_participation(course)

    role = VLE.models.Participation.objects.get(user=user, course=course).role
    permissions = model_to_dict(role)

    return permission in permissions and permissions[permission]


def has_assignment_permission(user, permission, assignment):
    """Check if the user has the needed permission in the given assignment.

    Arguments:
    user -- user that did the request.
    assignment -- assignment used to check against.
    permission -- the permission string to check.

    Raises VLEProgrammingError when the passed permission is not an "Assignment Permission".
    Raises VLEParticipationError when the user is not participating in the assignment.
    """

    if permission not in ASSIGNMENT_PERMISSIONS:
        raise VLEProgrammingError("Permission " + permission + " is not an assignment level permission.")

    if user.is_superuser:
        if permission == 'can_have_journal':
            return False
        return True

    user.check_participation(assignment)

    permissions = defaultdict(lambda: False)
    for course in assignment.courses.all():
        if user.is_participant(course):
            role = VLE.models.Participation.objects.get(user=user, course=course).role
            role_permissions = model_to_dict(role)
            permissions = {key: (role_permissions[key] or permissions[key]) for key in ASSIGNMENT_PERMISSIONS}

    # Apply negations
    if permissions['can_have_journal'] and permissions['can_view_all_journals']:
        permissions['can_have_journal'] = False

    return permissions[permission]


def is_user_supervisor_of(supervisor, user):
    """Checks whether the user is a participant in any of the assignments where the supervisor has the permission of
    can_view_course_users or where the supervisor is linked to the user through an assignment where the supervisor
    has the permission can_view_all_journals."""
    for course in supervisor.participations.all():
        if supervisor.has_permission('can_view_course_users', course):
            if course.participation_set.filter(user=user).exists():
                return True
            for assignment in course.assignment_set.filter(journal__user=user):
                if supervisor.has_permission('can_view_all_journals', assignment):
                    return True

    return False


def serialize_general_permissions(user):
    return {key: has_general_permission(user, key) for key in GENERAL_PERMISSIONS}


def serialize_course_permissions(user, course):
    return {key: has_course_permission(user, key, course) for key in COURSE_PERMISSIONS}


def serialize_assignment_permissions(user, assignment):
    return {key: has_assignment_permission(user, key, assignment) for key in ASSIGNMENT_PERMISSIONS}
