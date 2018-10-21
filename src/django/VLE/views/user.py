"""
user.py.

In this file are all the user api requests.
"""
from smtplib import SMTPAuthenticationError

from django.conf import settings
from django.core.validators import validate_email
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

import VLE.factory as factory
import VLE.lti_launch as lti_launch
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
import VLE.validators as validators
from VLE.models import (Assignment, Content, Entry, Journal, Node, User,
                        UserFile)
from VLE.serializers import EntrySerializer, OwnUserSerializer, UserSerializer
from VLE.utils import email_handling, file_handling
from VLE.views import lti


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
        if not request.user.is_superuser:
            return response.forbidden('Only administrators are allowed to request all user data.')

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
        if int(pk) == 0:
            pk = request.user.id

        user = User.objects.get(pk=pk)

        if request.user == user or request.user.is_superuser:
            serializer = OwnUserSerializer(user, many=False)
        elif permissions.is_user_supervisor_of(request.user, user):
            serializer = UserSerializer(user, many=False)
        else:
            return response.forbidden('You are not allowed to view this users information.')

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
            bad request -- when email/username/lti id already exists
            bad request -- when email/password is invalid
        On succes:
            success -- with the newly created user data
        """
        jwt_params, = utils.optional_params(request.data, 'jwt_params')
        if jwt_params:
            lti_params = lti.decode_lti_params(jwt_params)
            lti_id, user_image = utils.optional_params(lti_params, 'user_id', 'custom_user_image')
            is_teacher = settings.ROLES['Teacher'] in lti_launch.roles_to_list(lti_params)
        else:
            lti_id, user_image, is_teacher = None, None, False

        username, password = utils.required_params(request.data, 'username', 'password')
        first_name, last_name, email = utils.optional_params(request.data, 'first_name', 'last_name', 'email')

        if email and User.objects.filter(email=email).exists():
            return response.bad_request('User with this email already exists.')

        validate_email(email)

        if User.objects.filter(username=username).exists():
            return response.bad_request('User with this username already exists.')

        if lti_id is not None and User.objects.filter(lti_id=lti_id).exists():
            return response.bad_request('User with this lti id already exists.')

        validators.validate_password(password)

        user = factory.make_user(username, password, email=email, lti_id=lti_id, is_teacher=is_teacher,
                                 first_name=first_name, last_name=last_name, lti_image=user_image,
                                 verified_email=True if lti_id else False)

        if lti_id is None:
            try:
                email_handling.send_email_verification_link(user)
            except SMTPAuthenticationError as err:
                user.delete()
                raise err

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
        pk, = utils.required_typed_params(kwargs, (int, 'pk'))
        if pk == 0:
            pk = request.user.pk
        if not (request.user.pk == pk or request.user.is_superuser):
            return response.forbidden()

        user = User.objects.get(pk=pk)

        jwt_params = utils.optional_params(request.data, 'jwt_params')
        if jwt_params:
            lti_params = lti.decode_lti_params(jwt_params)
            lti_id, user_email, user_full_name, user_image = utils.optional_params(
                lti_params, 'user_id', 'custom_user_email', 'custom_user_full_name', 'custom_user_image')
            is_teacher = settings.ROLES['Teacher'] in lti_launch.roles_to_list(lti_params)
        else:
            lti_id, user_email, user_full_name, user_image, is_teacher = None, None, None, None, False

        if user_image is not None:
            user.lti_image = user_image
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
            if User.objects.filter(lti_id=lti_id) != user:
                return response.bad_request('User with this lti id already exists.')
            user.lti_id = lti_id

        user.save()
        if user.lti_id:
            gn, cn, pp = utils.optional_params(
                request.data, 'grade_notifications', 'comment_notifications', 'profile_picture')
            data = {
                'grade_notifications': gn,
                'comment_notifications': cn,
                'profile_picture': pp
            }
        else:
            data = request.data
        serializer = OwnUserSerializer(user, data=data, partial=True)
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
        if not request.user.is_superuser:
            return response.forbidden('You are not allowed to delete a user.')

        if int(pk) == 0:
            pk = request.user.id

        user = User.objects.get(pk=pk)

        if len(User.objects.filter(is_superuser=True)) == 1:
            return response.bad_request('There is only 1 superuser left and therefore cannot be deleted')

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
            bad request -- when the password is invalid
        On success:
            success -- with a success description
        """
        new_password, old_password = utils.required_params(request.data, 'new_password', 'old_password')

        if not request.user.check_password(old_password):
            return response.bad_request('Wrong password.')

        if validators.validate_password(new_password):
            return response.bad_request(validators.validate_password(new_password))

        request.user.set_password(new_password)
        request.user.save()
        return response.success(description='Successfully changed the password.')

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
                journal.assignment.name: EntrySerializer(
                    entries, context={'user': request.user, 'comments': True}, many=True).data
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
            bad_request -- when the file was not found
            forbidden -- when its not a superuser nor their own data
        On success:
            success -- a zip file of all the userdata with all their files
        """
        if int(pk) == 0:
            pk = request.user.id

        file_name, entry_id, node_id, content_id = utils.required_typed_params(
            request.query_params, (str, 'file_name'), (int, 'entry_id'), (int, 'node_id'), (int, 'content_id'))

        try:
            user_file = UserFile.objects.get(author=pk, file_name=file_name, entry=entry_id, node=node_id,
                                             content=content_id)

            if user_file.author != request.user:
                request.user.check_permission('can_view_all_journals', user_file.assignment)

        except (UserFile.DoesNotExist, ValueError):
            return response.bad_request(file_name + ' was not found.')

        return response.file(user_file)

    @action(methods=['post'], detail=False)
    def upload(self, request):
        """Upload a user file.

        No validation is performed beyond a size check of the file and the available space for the user.
        At the time of creation, the UserFile is uploaded but not attached to an entry yet. This UserFile is treated
        as temporary untill the actual entry is created and the node and content are updated.

        Arguments:
        request -- request data
            file -- filelike data
            assignment_id -- assignment ID
            content_id -- content ID, should be null when creating a NEW entry.

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            bad_request -- when the file, assignment was not found or the validation failed.
        On success:
            success -- name of the file.
        """
        assignment_id, content_id = utils.required_params(request.POST, 'assignment_id', 'content_id')
        assignment = Assignment.objects.get(pk=assignment_id)

        request.user.check_participation()

        if not (request.FILES and 'file' in request.FILES):
            return response.bad_request('No accompanying file found in the request.')
        validators.validate_user_file(request.FILES['file'], request.user)

        if content_id == 'null':
            factory.make_user_file(request.FILES['file'], request.user, assignment)
        else:
            try:
                content = Content.objects.get(pk=int(content_id), entry__node__journal__user=request.user)
            except Content.DoesNotExist:
                return response.bad_request('Content with id {:s} was not found.'.format(content_id))

            factory.make_user_file(request.FILES['file'], request.user, assignment, content=content)

        return response.success(description='Successfully uploaded {:s}.'.format(request.FILES['file'].name))

    @action(methods=['post'], detail=False)
    def upload_profile_picture(self, request):
        """Update user profile picture.

        Arguments:
        request -- request data
            file -- jpeg/png/gif image data

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            bad_request -- when the file is not valid
        On success:
            success -- nothing
        """
        utils.required_params(request.data, 'file')

        validators.validate_profile_picture(request.data['file'])

        request.user.profile_picture = request.data['file']
        request.user.lti_image = None
        request.user.save()

        return response.success(description='Succesfully updated profile picture')

    @action(methods=['get'], detail=True)
    def download_profile_picture(self, request, pk):
        """Download a profile picture.

        Arguments:
        request -- the request that was sent
        pk -- user ID

        Returns
        On failure:
            unauthorized -- when the user is not logged in
            bad_request -- when the file was not found
        On success:
            success -- bytebuffer with image
        """
        if int(pk) == 0:
            pk = request.user.id

        user = User.objects.get(pk=pk)

        return response.file(user.profile_picture.path)

    def get_permissions(self):
        if self.request.path == '/users/' and self.request.method == 'POST':
            return [AllowAny()]
        else:
            return [permission() for permission in self.permission_classes]
