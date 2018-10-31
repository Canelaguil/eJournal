"""
test_utils.py.

Test helper functions.
"""

import json

from django.urls import reverse

import VLE.factory as factory
from VLE.models import Role


def assert_response(obj, result, status):
    try:
        obj.assertEquals(result.status_code, status, 'Failed response was: ' + str(result.json()))
    except ValueError:
        obj.assertEquals(result.status_code, status, 'Failed response was: ' + str(result))


def set_up_user_and_auth(username, password, email, full_name=None,
                         is_superuser=False, is_teacher=False):
    """Set up a user with the possibility of global permissions.

    Arguments:
    username -- username for the user
    password -- password for the user
    full_name -- full name

    Returns the user and its credentials
    """
    user = factory.make_user(username, password, email, is_superuser=is_superuser, is_teacher=is_teacher,
                             full_name=full_name)
    return username, password, user


def set_up_participation(user, course, role):
    """Set up a student in a course."""
    q_role = Role.objects.get(name=role, course=course)
    return factory.make_participation(user, course, q_role)


def set_up_users(name, n):
    """Set up some students.

    Arguments:
    name -- the base for the incremental names for the users
    n -- number of students to be made

    Returns a list of users with incremental naming.
    """
    users = []
    for i in range(n):
        users.append(factory.make_user(name + str(i), 'pass', 'test@ts.com' + str(i)))
    return users


def set_up_journal(assignment, template, user, n):
    """Set up a journal for an user with n entries.

    Arguments:
    assignment -- the assignment of the journal
    template -- the entry template for the entries
    user -- the user of the journal
    n -- number of entries

    Returns a journal with entries attached.
    """
    journal = factory.make_journal(assignment, user)

    for entry in set_up_entries(template, n):
        factory.make_node(journal, entry)

    return journal


def set_up_entries(template, n):
    """Set up some entries.

    Arguments:
    template -- the template to be used for the entries
    n -- number of entriest to be made

    Returns a list of entries that uses the same template.
    """
    entries = []
    for i in range(n):
        entries.append(factory.make_entry(template))
    return entries


def set_up_courses(name, n, author=None, lti_id=False):
    """Set up some courses.

    Arguments:
    name -- the base for the incremental names for the courses
    n -- number of courses to be made
    author -- the user who made the course and it automatically will be teacher
    lti_id -- a boolean to determine if to give lti ids

    Returns a list of courses.
    """
    courses = []
    if lti_id:
        for i in range(n):
            courses.append(factory.make_course(name + str(i), name[0] + str(i), author=author, lti_id=str(i)))
    else:
        for i in range(n):
            courses.append(factory.make_course(name + str(i), name[0] + str(i), author=author))
    return courses


def set_up_assignments(name, desc, n, course, lti_id=False, is_published=True):
    """Set up some assignments.

    Arguments:
    name -- the base for the incremental names for the assignments
    desc -- the base for the incremental description for the assignments
    n -- number of assignments to be made.
    lti_id -- a boolean to determine if to give lti ids

    Returns a list of assignments.
    """
    assignments = []
    if lti_id:
        for i in range(n):
            assignments.append(factory.make_assignment(name + str(i), desc + str(i),
                                                       lti_id=str(i), courses=[course], is_published=is_published))
    else:
        for i in range(n):
            assignments.append(factory.make_assignment(name + str(i), desc + str(i), courses=[course],
                                                       is_published=is_published))
    return assignments


def logging_in(obj, username, password, status=200):
    """Login using username and password.

    Arguments:
    username -- username
    password -- password
    status -- status it checks for after login (default 200)

    Returns the loggin in user.
    """
    result = obj.client.post(reverse('token_obtain_pair'),
                             json.dumps({'username': username, 'password': password}),
                             content_type='application/json')
    assert_response(obj, result, status)
    return result


def api_get_call(obj, url, login, status=200, params={}):
    """Send an get api call.

    Arguments:
    url -- url to send the call to
    login -- credentials of the logged in user
    status -- status it checks for after login (default 200)

    returns the whatever the api call returns
    """
    result = obj.client.get(url, params,
                            HTTP_AUTHORIZATION='Bearer {0}'.format(login.data['access']))
    assert_response(obj, result, status)
    return result


def test_unauthorized_api_get_call(obj, url, params={}):
    """Test unauthorized api get calls.

    Arguments
    url -- url to send the call to
    params -- extra parameters that the api needs
    """
    result = obj.client.get(url, params, format='json')
    obj.assertEquals(result.status_code, 401, 'Failed response was: ' + str(result.json()))


def api_post_call(obj, url, params, login=None, status=200):
    """Send and get api call.

    Arguments:
    url -- url to send the call to
    params -- extra parameters that the api needs
    login -- credentials of the logged in user
    status -- status it checks for after login (default 200)

    returns the whatever the api call returns
    """
    if not login:
        result = obj.client.post(url, json.dumps(params), content_type='application/json')
    else:
        result = obj.client.post(url, json.dumps(params), content_type='application/json',
                                 HTTP_AUTHORIZATION='Bearer {0}'.format(login.data['access']))
    assert_response(obj, result, status)
    return result


def api_patch_call(obj, url, params, login, status=200):
    """Send and get patch api call.

    Arguments:
    url -- url to send the call to
    params -- extra parameters that the api needs
    login -- credentials of the logged in user
    status -- status it checks for after login (default 200)

    returns the whatever the api call returns
    """
    result = obj.client.patch(url, json.dumps(params), content_type='application/json',
                              HTTP_AUTHORIZATION='Bearer {0}'.format(login.data['access']))
    assert_response(obj, result, status)
    return result


def api_del_call(obj, url, login, params={}, status=200):
    """Send and get delete api call.

    Arguments:
    url -- url to send the call to
    params -- extra parameters that the api needs
    login -- credentials of the logged in user
    status -- status it checks for after login (default 200)

    returns the whatever the api call returns
    """
    result = obj.client.delete(url, params, content_type='application/json',
                               HTTP_AUTHORIZATION='Bearer {0}'.format(login.data['access']))
    assert_response(obj, result, status)
    return result


def test_unauthorized_api_post_call(obj, url, params):
    """Test unauthorized api post calls.

    Arguments
    url -- url to send the call to
    params -- extra parameters that the api needs
    """
    result = obj.client.post(url, json.dumps(params), content_type='application/json')
    obj.assertEquals(result.status_code, 401, 'Failed response was: ' + str(result.json()))
