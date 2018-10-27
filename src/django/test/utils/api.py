"""
utils.py

Helpter function for the test enviroment.
"""

import json
from django.urls import reverse
import VLE.utils.generic_utils as utils
import test.utils.generic_utils as test_utils


def format_url(obj, url, params, function):
    # add / to from and back
    if url[0] != '/':
        url = '/' + url
    if url[-1] != '/':
        url += '/'

    # set primary key if its not a create, when no pk is supplied, default to 0
    if function != obj.client.post:
        pk = params.pop('pk', 0)
        url += '{}/'.format(pk)

    # add params to the url if it cant have a body
    if function in [obj.client.get, obj.client.delete]:
        url += '?'
        for key, value in params.items():
            url += '{}={}&'.format(key, value)
        # Remove last & or ? when there are no params
        url = url[:-1]

    return url


def login(obj, username, password, status=200):
    """Login using username and password.

    Arguments:
    user -- user to login as
    status -- status it checks for after login (default 200)

    Returns the loggin in user.
    """
    return post(obj, reverse('token_obtain_pair'),
                params={'username': username, 'password': password}, status=status)


def test_rest(obj, url, create_params=None, delete_params=None, update_params=None, get_is_create=True,
              username=None, password='Pa$$word!',
              create_status=201, get_status=200, delete_status=200, get_status_when_unauthorized=401):
    # Create the object that is given
    create_object = create(obj, url, params=create_params, username=username, password=password, status=create_status)
    if create_status != 201:
        return
    create_object.pop('description', None)
    pk, = utils.required_typed_params(list(create_object.values())[0], (int, 'id'))

    # Get that same object
    get(obj, url, params={'pk': pk}, status=get_status_when_unauthorized)
    get_object = get(obj, url, params={'pk': pk}, username=username, password=password, status=get_status)
    if get_status != 200:
        return
    get_object.pop('description', None)

    # Check if the created object is the same as the one it got
    if get_is_create:
        obj.assertEquals(create_object, get_object)

    # Update the object
    if update_params is not None:
        if not isinstance(update_params, list):
            update_params = [update_params]

        for to_update in update_params:
            changes, status = utils.optional_params(to_update, 'changes', 'status')
            if status is None:
                status = 200
            update_object = update(obj, url, params=changes, username=username, password=password, status=status)
            update_object.pop('description', None)

    # Delete the object
    if delete_params is None:
        delete_params = dict()
    delete(obj, url, params={'pk': pk, **delete_params}, username=username, password=password, status=delete_status)


def get(obj, url, params=None, username=None, password='Pa$$word!', status=200, result=None):
    return call(obj, obj.client.get, url,
                params=params, username=username, password=password, status=status, result=result)


def create(obj, url, params=None, username=None, password='Pa$$word!', status=201, result=None):
    return call(obj, obj.client.post, url,
                params=params, username=username, password=password, status=status, result=result)


def post(obj, url, params=None, username=None, password='Pa$$word!', status=200, result=None):
    return call(obj, obj.client.post, url,
                params=params, username=username, password=password, status=status, result=result)


def update(obj, url, params=None, username=None, password='Pa$$word!', status=200, result=None):
    return call(obj, obj.client.patch, url,
                params=params, username=username, password=password, status=status, result=result)


def patch(obj, url, params=None, username=None, password='Pa$$word!', status=200, result=None):
    return call(obj, obj.client.patch, url,
                params=params, username=username, password=password, status=status, result=result)


def delete(obj, url, params=None, username=None, password='Pa$$word!', status=200, result=None):
    return call(obj, obj.client.delete, url,
                params=params, username=username, password=password, status=status, result=result)


def call(obj, function, url, params=None,
         username=None, password='Pa$$word!',
         status=200, status_when_unauthorized=401, result=None,
         content_type='application/json'):
    # Set params to an empty dictionary when its None this cant be done in the parameters themself as that can give
    # unwanted results when calling the function multiple times
    if params is None:
        params = dict()

    url = format_url(obj, url, params, function)

    if username is None:
        if function in [obj.client.get, obj.client.delete]:
            result = function(url, content_type=content_type)
        else:
            result = function(url, json.dumps(params), content_type=content_type)
    else:
        logged_user = login(obj, username, password)
        access, = utils.required_params(logged_user, 'access')
        if function in [obj.client.get, obj.client.delete]:
            result = function(url, content_type=content_type, HTTP_AUTHORIZATION='Bearer ' + access)
        else:
            result = function(url, json.dumps(params), content_type=content_type, HTTP_AUTHORIZATION='Bearer ' + access)

    test_utils.assert_response(obj, result, status)
    try:
        return result.json()
    except AttributeError:
        return result
