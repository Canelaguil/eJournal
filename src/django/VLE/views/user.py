"""
user.py.

In this file are all the user api requests.
"""
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework import viewsets
from rest_framework.decorators import action

from VLE.serializers import UserSerializer, OwnUserSerializer, EntrySerializer
from VLE.models import User, Journal, UserFile, Assignment, Node, Entry
from VLE.views import responses as response
import VLE.utils.generic_utils as utils
import VLE.factory as factory
from VLE.utils import email_handling
from VLE.utils import file_handling
import VLE.validators as validators
import VLE.permissions as permissions

import jwt
import json
import os


class UserView(viewsets.ViewSet):
    def list(self, request):
        """Get all users.

        Arguments:
        request -- request data

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
        On succes:
            success -- with the course data

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        if not (permissions.can_add_users_to_a_course(request.user) or request.user.is_superuser):
            return response.forbidden(description="Only teachers and administrators are allowed to request all user \
                                       data.")

        serializer = UserSerializer(User.objects.all(), many=True)
        return response.success({'users': serializer.data})

    def retrieve(self, request, pk):
        """Get the user data of the requested user.

        Arguments:
        request -- request data
        pk -- user ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the user doesn't exists
        On success:
            success -- with the user data
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        if int(pk) == 0:
            pk = request.user.id

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return response.not_found('User does not exist.')

        if request.user == user or request.user.is_superuser:
            serializer = OwnUserSerializer(user, many=False)
        elif permissions.is_user_supervisor(user, request.user):
            serializer = UserSerializer(user, many=False)
        else:
            return response.forbidden("You are not allowed to view this users information.")

        return response.success({'user': serializer.data})

    def create(self, request):
        """Create a new user.

        Arguments:
        request -- request data
            username -- username
            password -- password
            first_name -- (optinal) first name
            last_name -- (optinal) last name
            email -- (optinal) email
            jwt_params -- (optinal) jwt params to get the lti information from
                user_id -- id of the user
                user_image -- user image
                roles -- role of the user

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when username or password is not set
            bad request -- when email/username/lti id already exists
            bad request -- when email/password is invalid
        On succes:
            success -- with the newly created user data
        """
        if 'jwt_params' in request.data and request.data['jwt_params'] != '':
            try:
                lti_params = jwt.decode(request.data['jwt_params'], settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.exceptions.ExpiredSignatureError:
                return response.forbidden(
                    description='Your session has expired. Please go back to your learning environment and try again.')
            except jwt.exceptions.InvalidSignatureError:
                return response.unauthorized(description='Invalid LTI parameters given. Please go back to your \
                                             learning environment and try again.')
            lti_id, user_image = utils.optional_params(lti_params, 'user_id', 'custom_user_image')
            is_teacher = json.load(open(settings.LTI_ROLE_CONFIG_PATH))['Teacher'] in lti_params['roles']
        else:
            lti_id, user_image, is_teacher = None, None, False

        try:
            username, password = utils.required_params(request.data, 'username', 'password')
            first_name, last_name, email = utils.optional_params(request.data, 'first_name', 'last_name', 'email')
        except KeyError:
            return response.keyerror('username', 'password')

        if email and User.objects.filter(email=email).exists():
            return response.bad_request('That email address belongs to another user.')

        try:
            validate_email(email)
        except ValidationError:
            return response.bad_request('Invalid email address.')

        if User.objects.filter(username=username).exists():
            return response.bad_request('User with this username already exists.')

        if lti_id is not None and User.objects.filter(lti_id=lti_id).exists():
            return response.bad_request('User with this lti id already exists.')

        try:
            validators.validate_password(password)
        except ValidationError as e:
            return response.bad_request(e.args[0])

        user = factory.make_user(username, password, email=email, lti_id=lti_id, is_teacher=is_teacher,
                                 first_name=first_name, last_name=last_name, profile_picture=user_image,
                                 verified_email=True if lti_id else False)

        if lti_id is None:
            email_handling.send_email_verification_link(user)

        return response.created({'user': UserSerializer(user).data})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing user.

        Arguments:
        request -- request data
            jwt_params -- jwt params to get the lti information from
                user_id -- id of the user
                user_image -- user image
                roles -- role of the user
        pk -- user ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            forbidden -- when the user is not superuser or pk is not the same as the logged in user
            not found -- when the user doesnt exists
            bad request -- when the data is invalid
        On success:
            success -- with the updated user
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        pk = kwargs.get('pk')
        if int(pk) == 0:
            pk = request.user.id
        if not (request.user.pk == int(pk) or request.user.is_superuser):
            return response.forbidden()

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return request.not_found('User does not exist.')

        if 'jwt_params' in request.data and request.data['jwt_params'] != '':
            try:
                lti_params = jwt.decode(request.data['jwt_params'], settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.exceptions.ExpiredSignatureError:
                return response.forbidden(
                    description='The canvas link has expired, 15 minutes have passed. Please retry from canvas.')
            except jwt.exceptions.InvalidSignatureError:
                return response.unauthorized(description='Invalid LTI parameters given. Please retry from canvas.')
            lti_id, user_email, user_full_name, user_image = utils.optional_params(lti_params, 'user_id',
                                                                                   'custom_user_email',
                                                                                   'custom_user_full_name',
                                                                                   'custom_user_image')
            is_teacher = json.load(open(settings.LTI_ROLE_CONFIG_PATH))['Teacher'] in lti_params['roles']
        else:
            lti_id, user_email, user_full_name, user_image, is_teacher = None, None, None, None, False
        if user_image is not None:
            user.profile_picture = user_image
        if user_email is not None:
            user.email = user_email
            user.verified_email = True
        if user_full_name is not None:
            splitname = user_full_name.split(' ')
            user.first_name = splitname[0]
            user.last_name = user_full_name[len(splitname[0])+1:]
        if is_teacher:
            user.is_teacher = is_teacher

        if lti_id:
            if User.objects.filter(lti_id=lti_id).exists() and User.objects.filter(lti_id=lti_id) != user:
                return response.bad_request('User with this lti id already exists.')
            user.lti_id = lti_id

        user.save()
        serializer = OwnUserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return response.bad_request()
        serializer.save()
        return response.success({'user': serializer.data})

    def destroy(self, request, pk):
        """Delete a user.

        Arguments:
        request -- request data
        pk -- user ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the user does not exist
        On success:
            success -- deleted message
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        if not request.user.is_superuser:
            return response.forbidden('You are not allowed to delete a user.')

        if int(pk) == 0:
            pk = request.user.id

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return response.not_found('User does not exist.')

        user.delete()
        return response.deleted(description='Sucesfully deleted user.')

    @action(['patch'], detail=False)
    def password(self, request):
        """Change the password of a user.

        Arguments:
        request -- request data
            new_password -- new password of the user
            old_password -- current password of the user

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when new or old password is not set
            bad request -- when the password is invalid
        On success:
            success -- with a success description
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        try:
            new_password, old_password = utils.required_params(request.data, 'new_password', 'old_password')
        except KeyError:
            return response.keyerror('new_password', 'old_password')

        if not request.user.check_password(old_password):
            return response.bad_request('Wrong password.')

        if validators.validate_password(new_password):
            return response.bad_request(validators.validate_password(new_password))

        request.user.set_password(new_password)
        request.user.save()
        return response.success(description='Succesfully changed the password.')

    # TODO: limit this request for end users, otherwise its really easy to DDOS the server.
    @action(methods=['get'], detail=True)
    def GDPR(self, request, pk):
        """Get a zip file of all the userdata.

        Arguments:
        request -- request data
        pk -- user ID to download the files from

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            forbidden -- when its not a superuser nor their own data
        On success:
            success -- a zip file of all the userdata with all their files
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        if int(pk) == 0:
            pk = request.user.id

        user = User.objects.get(pk=pk)

        # Check the right permissions to get this users data, either be the user of the data or be an admin.
        if not (user.is_superuser or request.user.id == pk):
            return response.forbidden('You are not allowed to view this user\'s data.')

        profile = UserSerializer(user).data
        journals = Journal.objects.filter(user=pk)
        journal_dict = {}
        for journal in journals:
            # Select the nodes of this journal but only the ones with entries.
            entry_ids = Node.objects.filter(journal=journal).exclude(entry__isnull=True).values_list('entry', flat=True)
            entries = Entry.objects.filter(id__in=entry_ids)
            # Serialize all entries and put them into the entries dictionary with the assignment name key.
            journal_dict.update({
                journal.assignment.name: EntrySerializer(entries, context={'user': request.user}, many=True).data
            })

        archive_path = file_handling.compress_all_user_data(user, {'profile': profile, 'journals': journal_dict})

        return response.file(archive_path)

    @action(methods=['get'], detail=True)
    def download(self, request, pk):
        """Get a user file by name if it exists.

        Arguments:
        request -- the request that was sent
            file_name -- filename to download
        pk -- user ID

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when file_name is not set
            bad_request -- when the file was not found
            forbidden -- when its not a superuser nor their own data
        On success:
            success -- a zip file of all the userdata with all their files
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        if int(pk) == 0:
            pk = request.user.id

        try:
            file_name, = utils.required_params(request.query_params, 'file_name')
        except KeyError:
            return response.keyerror('file_name')

        try:
            user_file = UserFile.objects.get(author=pk, file_name=file_name)
        except UserFile.DoesNotExist:
            return response.bad_request(file_name + ' was not found.')

        if user_file.author.id is not request.user.id and \
           not permissions.has_assignment_permission(
                request.user, user_file.assignment, 'can_view_assignment_journals'):
            return response.forbidden('Forbidden to view: %s by author ID: %s.' % (file_name, pk))

        return response.file(os.path.join(settings.MEDIA_ROOT, user_file.file.name))

    # TODO P Test changes
    @action(methods=['post'], detail=False)
    def upload(self, request):
        """Update user profile picture.

        No validation is performed beyond a size check of the file and the available space for the user.

        Arguments:
        request -- request data
            file -- filelike data
            assignment_id -- assignment ID

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when file is not set
            bad_request -- when the file was not found
        On success:
            success -- a zip file of all the userdata with all their files
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        if not request.FILES or 'file' not in request.FILES or 'assignment_id' not in request.POST:
            return response.bad_request('File or assignment_id not found')

        try:
            validators.validate_user_file(request.FILES['file'])
        except ValidationError as e:
            return response.bad_request(e.args[0])

        user_files = request.user.userfile_set.all()

        # Fast check for allowed user storage space
        if settings.USER_MAX_TOTAL_STORAGE_BYTES - len(user_files) * settings.USER_MAX_FILE_SIZE_BYTES <= \
           request.FILES['file'].size:
            # Slow check for allowed user storage space
            file_size_sum = 0
            for user_file in user_files:
                file_size_sum += user_file.file.size
            if file_size_sum > settings.USER_MAX_TOTAL_STORAGE_BYTES:
                return response.bad_request('Unsufficient user storage space.')

        # Ensure an old copy of the file is removed when updating a file with the same name.
        try:
            old_user_file = user_files.get(file_name=request.FILES['file'].name)
            old_user_file.file.delete()
            old_user_file.delete()
        except UserFile.DoesNotExist:
            pass

        try:
            assignment = Assignment.objects.get(pk=request.POST['assignment_id'])
        except Assignment.DoesNotExist:
            return response.bad_request('Assignment with id {:s} was not found.'.format(request.POST['assignment_id']))

        if not Assignment.objects.filter(courses__users=request.user, pk=assignment.pk):
            return response.forbidden('You cannot upload a file to: {:s}.'.format(assignment.name))

        factory.make_user_file(request.FILES['file'], request.user, assignment)

        return response.success(description='Succesfully uploaded {:s}.'.format(request.FILES['file'].name))

    @action(['post'], detail=False)
    def set_profile_picture(self, request):
        """Update user profile picture.

        Arguments:
        request -- request data
            file -- a base64 encoded image

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when url_data is not set
            bad_request -- when the file is not valid
        On success:
            success -- a zip file of all the userdata with all their files
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            utils.required_params(request.data, 'file')
        except KeyError:
            return response.keyerror('file')

        try:
            validators.validate_profile_picture_base64(request.data['file'])
        except ValidationError as e:
            return response.bad_request(e.args[0])

        request.user.profile_picture = request.data['file']
        request.user.save()

        return response.success(description='Succesfully updated profile picture')
