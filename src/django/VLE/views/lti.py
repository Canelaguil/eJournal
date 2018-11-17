import datetime

import jwt
from django.conf import settings
from django.http import QueryDict
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import VLE.lti_launch as lti
import VLE.utils.responses as response
from VLE.utils.error_handling import VLEMissingRequiredKey

# VUE ENTRY STATE
KEY_ERR = '-2'
BAD_AUTH = '-1'

NO_USER = '0'
LOGGED_IN = '1'

NO_COURSE = '0'
NO_ASSIGN = '1'
NEW_COURSE = '2'
NEW_ASSIGN = '3'
FINISH_T = '4'
FINISH_S = '5'


def decode_lti_params(jwt_params):
    return jwt.decode(jwt_params, settings.SECRET_KEY, algorithms=['HS256'])


def encode_lti_params(jwt_params):
    return jwt.encode(jwt_params, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')


@api_view(['GET'])
def get_lti_params_from_jwt(request, jwt_params):
    """Handle the controlflow for course/assignment create, connect and select.

    Returns the data needed for the correct entry place.
    """
    user = request.user
    lti_params = decode_lti_params(jwt_params)

    try:
        role = [settings.LTI_ROLES[r] if r in settings.LTI_ROLES else r for r in lti.roles_to_list(lti_params)]
        payload = dict()

        # convert LTI param for True to python True
        if 'custom_assignment_publish' in lti_params:
            lti_params['custom_assignment_publish'] = lti_params['custom_assignment_publish'] == 'true'
        else:
            lti_params['custom_assignment_publish'] = False
        course = lti.check_course_lti(lti_params, user, role)
        if course is None:
            if 'Teacher' in role:
                payload['state'] = NEW_COURSE
                payload['lti_cName'] = lti_params['custom_course_name']
                if 'context_label' in lti_params:
                    payload['lti_abbr'] = lti_params['context_label']
                else:
                    payload['lti_abbr'] = ''
                payload['lti_cID'] = lti_params['custom_course_id']
                payload['lti_course_start'] = lti_params['custom_course_start']
                payload['lti_aName'] = lti_params['custom_assignment_title']
                payload['lti_aID'] = lti_params['custom_assignment_id']
                payload['lti_aUnlock'] = lti_params['custom_assignment_unlock']
                payload['lti_aDue'] = lti_params['custom_assignment_due']
                payload['lti_aLock'] = lti_params['custom_assignment_lock']
                payload['lti_points_possible'] = lti_params['custom_assignment_points']
                payload['lti_aPublished'] = lti_params['custom_assignment_publish']

                return response.success({'params': payload})
            else:
                return response.not_found('The course you are looking for cannot be found. \
                    Most likely your teacher has not finished setting up the course.')

        assignment = lti.check_assignment_lti(lti_params)
        if assignment is None:
            if 'Teacher' in role:
                payload['state'] = NEW_ASSIGN
                payload['cID'] = course.pk
                payload['lti_aName'] = lti_params['custom_assignment_title']
                payload['lti_aID'] = lti_params['custom_assignment_id']
                payload['lti_aUnlock'] = lti_params['custom_assignment_unlock']
                payload['lti_aDue'] = lti_params['custom_assignment_due']
                payload['lti_aLock'] = lti_params['custom_assignment_lock']
                payload['lti_points_possible'] = lti_params['custom_assignment_points']
                payload['lti_aPublished'] = lti_params['custom_assignment_publish']

                return response.success({'params': payload})
            else:
                return response.not_found('The assignment you are looking for cannot be found. \
                    Either your teacher has not finished setting up the assignment, or it has been moved to another \
                    course. Please contact your course administrator.')

        journal = lti.select_create_journal(lti_params, user, assignment)
        jID = journal.pk if journal is not None else None
        state = FINISH_T if user.has_permission('can_view_all_journals', assignment) else FINISH_S
    except KeyError as err:
        raise VLEMissingRequiredKey(err)

    payload['state'] = state
    payload['cID'] = course.pk
    payload['aID'] = assignment.pk
    payload['jID'] = jID
    return response.success(payload={'params': payload})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def lti_launch(request):
    """Django view for the lti post request.

    Verifies the given LTI parameters based on our secret, if a user can be found based on the verified parameters
    a redirection link is send with corresponding JW access and refresh token to allow for a user login. If no user
    can be found on our end, but the LTI parameters were verified nonetheless, we are dealing with a new user and
    redirect with additional parameters that will allow for the creation of a new user.

    If the parameters are not validated a redirection is send with the parameter state set to BAD_AUTH.
    """
    secret = settings.LTI_SECRET
    key = settings.LTI_KEY

    authenticated, err = lti.OAuthRequestValidater.check_signature(
        key, secret, request)

    if authenticated:
        params = request.POST.dict()

        user = lti.check_user_lti(params)

        params['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        lti_params = encode_lti_params(params)

        try:
            if user is None:
                query = QueryDict(mutable=True)
                query['state'] = NO_USER
                query['lti_params'] = lti_params
                query['username'] = params['custom_username']

                if 'custom_user_full_name' in params:
                    fullname = params['custom_user_full_name']
                    splitname = fullname.split(' ')
                    query['firstname'] = splitname[0]
                    query['lastname'] = fullname[len(splitname[0])+1:]

                if 'custom_user_email' in params:
                    query['email'] = params['custom_user_email']

                return redirect(lti.create_lti_query_link(query))

            refresh = TokenObtainPairSerializer.get_token(user)
            query = QueryDict.fromkeys(['lti_params'], lti_params, mutable=True)
            query['jwt_access'] = str(refresh.access_token)
            query['jwt_refresh'] = str(refresh)
            query['state'] = LOGGED_IN
        except KeyError as err:
            query = QueryDict.fromkeys(['state'], KEY_ERR, mutable=True)
            query['description'] = 'The request is missing the following parameter: {0}.'.format(err)
            redirect(lti.create_lti_query_link(query))

        return redirect(lti.create_lti_query_link(query))

    return redirect(lti.create_lti_query_link(QueryDict.fromkeys(['state'], BAD_AUTH, mutable=True)))
