"""
email.py.

In this file are all the email api requests.
This includes:
    /forgot_password/ -- to get the names belonging to the ids
"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponse
from django.utils.html import escape
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
import VLE.validators as validators
from VLE.models import User
from VLE.utils import email_handling


def index(request):
    return HttpResponse(escape(repr(request)))


@api_view(['POST'])
@permission_classes((AllowAny, ))
def forgot_password(request):
    """Handles a forgot password request.

    Arguments:
        username -- User claimed username.
        email -- User claimed email.
        token -- Django stateless token, invalidated after password change or after a set time (by default three days).

    Generates a recovery token if a matching user can be found by either the prodived username or email.
    """
    username, email = utils.optional_params(request.data, 'username', 'email')

    # We are retrieving the username based on either the username or email
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.get(email=email)

    email_handling.send_password_recovery_link(user)
    return response.success(
        description='An email was sent to {}, please follow the email for instructions.'.format(user.email))


@api_view(['POST'])
@permission_classes((AllowAny, ))
def recover_password(request):
    """Handles a reset password request.

    Arguments:
        username -- User claimed username.
        recovery_token -- Django stateless token, invalidated after password change or after a set time
            (by default three days).
        new_password -- The new user desired password.

    Updates password if the recovery_token is valid.
    """
    username, recovery_token, new_password = utils.required_params(
        request.data, 'username', 'recovery_token', 'new_password')

    user = User.objects.get(username=username)

    recovery_token, = utils.required_params(request.data, 'recovery_token')
    token_generator = PasswordResetTokenGenerator()
    if not token_generator.check_token(user, recovery_token):
        return response.bad_request('Invalid recovery token.')

    validators.validate_password(new_password)

    user.set_password(new_password)
    user.save()

    return response.success(description='Successfully changed the password, you can now log in.')


@api_view(['POST'])
def verify_email(request):
    """Handles an email verification request.

    Arguments:
        token -- User claimed email verification token.

    Updates the email verification status.
    """
    if request.user.verified_email:
        return response.success(description='Email address already verified.')

    token, = utils.required_params(request.data, 'token')
    token_generator = PasswordResetTokenGenerator()
    if not token_generator.check_token(request.user, token):
        return response.bad_request(description='Invalid email recovery token.')

    request.user.verified_email = True
    request.user.save()
    return response.success(description='Successfully verified your email address.')


@api_view(['POST'])
def request_email_verification(request):
    """Request an email with a verifcation link for the users email address."""
    if request.user.verified_email:
        return response.bad_request(description='Email address already verified.')

    email_handling.send_email_verification_link(request.user)
    return response.success(
        description='An email was sent to {}, please follow the email for instructions.'.format(request.user.email))


@api_view(['POST'])
def send_feedback(request):
    """Send an email with feedback to the developers.

    Arguments:
    request -- the request that was sent.
        topic -- the topic of the feedback.
        type -- the type of feedback.
        feedback -- the actual feedback.
        browser -- the browser of the user who sends the feedback.
        files -- potential files as attachments.

    Returns:
    On failure:
        bad request -- when required keys are missing or file sizes too big.
        unauthorized -- when the user is not logged in.
    On success:
        success -- with a description.
    """
    request.user.check_verified_email()
    utils.required_params(request.POST, 'topic', 'feedback', 'ftype', 'user_agent')

    files = request.FILES.getlist('files')
    validators.validate_email_files(files)
    email_handling.send_email_feedback(request.user, files, **request.POST)
    return response.success(description='Feedback was successfully received, thank you!')
