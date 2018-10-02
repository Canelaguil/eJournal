"""
permissions.py.

All the permission functions.
"""
from VLE.models import Participation, Assignment

from django.forms.models import model_to_dict


def get_role(user, course):
    """Get the role (with permissions) of the given user in the given course.

    Arguments:
    user -- user that did the request.
    cID -- course ID used to validate the request.
    """
    try:
        # First attempt to get the participation of the user within the course.
        return Participation.objects.get(user=user, course=course).role
    except Participation.DoesNotExist:
        return None


def get_permissions(user, cID=-1):
    """Get permissions given a user.

    Get the permissions of the given user in the given course. The
    permissions are returned in dictionary format. For site-wide permissions
    when the user is not within a course, use cID == -1.

    Arguments:
    user -- user that did the request.
    cID -- course ID used to retrieve the permissions. -1 for permissions
    outside of a course.
    """
    roleDict = {}

    if user.is_superuser:
        # For system wide permissions, not course specific.
        # Administrators should not be able to view grades.
        roleDict = {
            "can_edit_institute_details": True,
            "can_add_course": True,

            "can_edit_course_details": True,
            "can_delete_course": True,
            "can_edit_course_roles": True,
            "can_view_course_users": True,
            "can_add_course_users": True,
            "can_delete_course_users": True,
            "can_add_course_user_group": True,
            "can_delete_course_user_group": True,
            "can_edit_course_user_group": True,
            "can_add_assignment": True,
            "can_delete_assignment": True,

            "can_edit_assignment": True,
            "can_view_assignment_journals": True,
            "can_grade": True,
            "can_publish_grades": True,
            "can_have_journal": False,
            "can_comment": True
        }
    elif cID == -1:
        # No course ID was given. The user has no permissions.
        roleDict = {
            "can_edit_institute_details": False,
            "can_add_course": False,

            "can_edit_course_details": False,
            "can_delete_course": False,
            "can_edit_course_roles": False,
            "can_view_course_users": False,
            "can_add_course_users": False,
            "can_delete_course_users": False,
            "can_add_course_user_group": False,
            "can_delete_course_user_group": False,
            "can_edit_course_user_group": False,
            "can_add_assignment": False,
            "can_delete_assignment": False,

            "can_edit_assignment": False,
            "can_view_assignment_journals": False,
            "can_grade": False,
            "can_publish_grades": False,
            "can_have_journal": False,
            "can_comment": False
        }

        # If the user is not in a specific course, but he is a teacher, he is
        # allowed to create courses on the platform.
        if user.is_teacher:
            roleDict["can_add_course"] = True
    else:
        # The course ID was given. Return the permissions of the user as dictionary.
        role = get_role(user, cID)

        # The role might not actually exist in the database, so return an
        # empty permission list.
        if not role:
            return {}

        roleDict = model_to_dict(role)
        roleDict["can_edit_institute_details"] = False

    return roleDict


def get_assignment_id_permissions(user, aID):
    """Merge permissions from all courses that are linked to the assignment.

    Arguments:
    user -- user that did the request
    aID -- the assignment ID
    """
    assignment = Assignment.objects.get(pk=aID)
    roleDict = get_assignment_permissions(user, assignment)
    return roleDict


def get_assignment_permissions(user, assignment):
    """Merge permissions from all courses that are linked to the assignment.

    If the user has the permission in any of the courses, it will have the permission
    for this assignment.
    """
    result = {}
    for course in assignment.courses.all():
        if Participation.objects.filter(user=user, course=course).count() > 0:
            result = {key: value or (result[key] if key in result else False)
                      for key, value in get_permissions(user, course.pk).items()}
    return result


def has_permissions(user, cID, permission_list):
    """Check if the user has the needed permissions.

    Do this by checking every permission, and returning False once a permission
    is insufficient.

    Arguments:
    user -- user that did the request.
    cID -- course ID used to validate the request.
    permission_list -- the list of permissions to check.
    """
    permissions = get_permissions(user, cID)

    for permission in permission_list:
        if permission not in permissions or not permissions[permission]:
            return False

    return True


def has_permission(user, cID, permission):
    """Check if the user has the needed permissions.

    Do this by checking every permission, and returning False once a permission
    is insufficient.

    Arguments:
    user -- user that did the request.
    cID -- course ID used to validate the request.
    permission -- the permission string to check.
    """
    permissions = get_permissions(user, cID)
    return permission in permissions and permissions[permission]


def has_assignment_permissions(user, assignment, permission_list):
    """Check if the user has the needed permissions.

    Do this by checking every permission, and returning False once a permission
    is insufficient.

    Arguments:
    user -- user that did the request.
    assignment -- the assignment used to validate the request.
    permissionList -- the list of permissions to check.
    """
    permissions = get_assignment_permissions(user, assignment)

    for permission in permission_list:
        if permission not in permissions or not permissions[permission]:
            return False

    return True


def has_assignment_permission(user, assignment, permission):
    """Check whether the user has the correct permission for an assignment.

    Arguments:
    user -- user that did the request.
    assignment -- the assignment used to validate the request.
    permission -- the permissions to check.
    """
    permissions = get_assignment_permissions(user, assignment)
    return permission in permissions and permissions[permission]


def is_user_in_course(user, course):
    """Check whether the user is in a given course or not.

    Arguments:
    user -- the user to be checked if in a course or not
    course -- the course to check with

    Returns True if the user is in the course, else False.
    """
    return Participation.objects.filter(user=user, course=course).exists()


def is_user_supervisor(user, supervisor):
    """Checks whether the user is a participant in any of the assignments where the supervisor has the permission of
    can_view_course_users or where the supervisor is linked to the user through an assignment where the supervisor
    has the permission can_view_assignment_journals."""
    for course in supervisor.participations.all():
        if get_permissions(supervisor, course.pk).can_view_course_users:
            if course.participations.filter(user=user).exists():
                return True
            if course.assignment_set.filter(journal__user=user).exists() and \
               has_permission(supervisor, course.pk, 'can_view_assignment_journals'):
                return True

    return False


def can_add_users_to_a_course(user):
    """Checks if the user can add users to one or more of his courses."""
    for course in user.participations.all():
        if get_permissions(user, course.pk).can_add_course_users:
            return True

    return False


def get_all_user_permissions(user):
    """Returns a dictionary with all user permissions.

    Arguments:
    user -- The user whose permissions are requested.

    Returns {all_permission:
        course{id}: permisions
        assignment{id}: permissions
        general: permissions
    }"""

    permissions = {}
    courses = user.participations.all()

    permissions['general'] = get_permissions(user, -1)

    for course in courses:
        permissions['course' + str(course.id)] = get_permissions(user, course.id)

    assignments = Assignment.objects.none()
    for course in courses:
        # Returns all assignments linked to a course if a grader.
        if permissions['course' + str(course.id)]['can_grade']:
            assignments |= course.assignment_set.all()
        else:
            assignments |= Assignment.objects.filter(courses=course, journal__user=user)

    assignments = assignments.distinct()

    for assignment in assignments:
        permissions['assignment' + str(assignment.id)] = get_assignment_id_permissions(user, assignment.id)
        # Ensure top level permission include can_grade for any course
        if permissions['assignment' + str(assignment.id)]['can_grade']:
            permissions['general']['can_grade'] = True

    return permissions
