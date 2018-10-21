from datetime import datetime, timezone

import oauth2
from django.conf import settings

import VLE.factory as factory
from VLE.models import Journal, Lti_ids, Role, User


class OAuthRequestValidater(object):
    """OAuth request validater class for Django Requests"""

    def __init__(self, key, secret):
        """
        Constructor which creates a consumer object with the given key and
        secret.
        """
        super(OAuthRequestValidater, self).__init__()
        self.consumer_key = key
        self.consumer_secret = secret

        self.oauth_server = oauth2.Server()
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        self.oauth_server.add_signature_method(signature_method)
        self.oauth_consumer = oauth2.Consumer(
            self.consumer_key, self.consumer_secret
        )

    def parse_request(self, request):
        """
        Parses a django request to return the method, url, header and post data.
        """
        return request.method, request.build_absolute_uri(), request.META, \
            request.POST.dict()

    def is_valid(self, request):
        """
        Checks if the signature of the given request is valid based on the
        consumers secret en key
        """
        try:
            method, url, head, param = self.parse_request(request)

            oauth_request = oauth2.Request.from_request(
                method, url, headers=head, parameters=param)

            self.oauth_server.verify_request(oauth_request,
                                             self.oauth_consumer, {})

        except (oauth2.Error, ValueError) as err:
            return False, err
        # Signature was valid
        return True, None

    @classmethod
    def check_signature(cls, key, secret, request):
        """Validate OAuth request using the python-oauth2 library.

        https://github.com/simplegeo/python-oauth2.
        """
        validator = OAuthRequestValidater(key, secret)
        return validator.is_valid(request)


def roles_to_list(params):
    roles = list()
    for role in params['roles'].split(','):
        roles.append(role.split('/')[-1].lower())
    return roles


def check_user_lti(request):
    """Check is an user with the lti_id exists"""
    lti_user_id = request['user_id']

    users = User.objects.filter(lti_id=lti_user_id)
    if users.count() > 0:
        user = users[0]
        if 'custom_user_image' in request:
            user.lti_image = request['custom_user_image']
            user.save()

        if 'roles' in request and settings.ROLES['Teacher'] in roles_to_list(request):
            user.is_teacher = True
            user.save()
        return user
    return None


def create_lti_query_link(query):
    """
    Creates link to lti page with the given parameters

    Arguments
    query -- QueryDict of the query variables

    returns the link
    """
    link = settings.BASELINK
    link += '/LtiLogin'
    link += '?'
    link += query.urlencode()
    return link


def check_course_lti(request, user, role):
    """Check is an course with the lti_id exists"""
    course_id = request['custom_course_id']
    lti_couples = Lti_ids.objects.filter(lti_id=course_id, for_model=Lti_ids.COURSE)

    if lti_couples.count() > 0:
        course = lti_couples[0].course
        if user not in course.users.all():
            for r in settings.ROLES:
                if r in role or r == 'Student':
                    factory.make_participation(user, course, Role.objects.get(name=r, course=course))
                    break
        return course
    return None


def check_assignment_lti(request):
    """Check is an assignment with the lti_id exists"""
    assign_id = request['custom_assignment_id']
    lti_couples = Lti_ids.objects.filter(lti_id=assign_id, for_model=Lti_ids.ASSIGNMENT)
    if lti_couples.count() > 0:
        return lti_couples[0].assignment
    return None


def select_create_journal(request, user, assignment):
    """
    Select or create the requested journal.
    """
    if assignment is not None and user is not None:
        journals = Journal.objects.filter(user=user, assignment=assignment)
        if journals.count() > 0:
            journal = journals[0]
        else:
            journal = factory.make_journal(assignment, user)

        within_assignment_timeframe = False
        try:
            begin = datetime.strptime(request['custom_assignment_unlock'], '%Y-%m-%d %X %z')
            end = datetime.strptime(request['custom_assignment_due'], '%Y-%m-%d %X %z')
            now = datetime.now(timezone.utc)
            within_assignment_timeframe = begin < now < end
        except (ValueError, KeyError):
            pass

        if (journal.grade_url is None or within_assignment_timeframe) and 'lis_outcome_service_url' in request:
            journal.grade_url = request['lis_outcome_service_url']
            journal.save()
        if (journal.sourcedid is None or within_assignment_timeframe) and 'lis_result_sourcedid' in request:
            journal.sourcedid = request['lis_result_sourcedid']
            journal.save()
    else:
        journal = None
    return journal
