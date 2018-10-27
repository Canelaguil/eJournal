
import VLE.factory as factory


def setup_user(name, is_superuser=False, is_teacher=False, password='Pa$$word!'):
    user = setup_users(name, 1, is_superuser=is_superuser, is_teacher=is_teacher)[0]
    return {'user': user, 'username': user.username, 'password': user.password}


def setup_users(name, count, is_superuser=False, is_teacher=False, password='Pa$$word!'):
    users = []
    for i in range(count):
        users.append(factory.make_user(username='{}{}'.format(name, i), password=password,
                                       email='{}{}@ejourn.al'.format(name, i),
                                       is_superuser=is_superuser, is_teacher=is_teacher))
    return users


def assert_response(obj, result, status):
    try:
        obj.assertEquals(result.status_code, status, 'Failed response was: ' + str(result.json()))
    except ValueError:
        obj.assertEquals(result.status_code, status, 'Failed response was: ' + str(result))
