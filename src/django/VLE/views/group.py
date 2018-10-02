"""
group.py.

In this file are all the group api requests.
"""
from rest_framework import viewsets

import VLE.serializers as serialize
import VLE.views.responses as response
from VLE.models import Course, Group
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.factory as factory


class GroupView(viewsets.ViewSet):
    serializer_class = serialize.GroupSerializer

    def list(self, request):
        """Get the groups from a course for the user.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exists
            forbidden -- when the user is not part of the course
        On succes:
            success -- with the group data

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course_id = int(request.query_params['course_id'])
        except KeyError:
            return response.key_error('course_id')

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not a participant of this course.')
        if not (role.can_edit_course_user_group or role.can_add_course_user_group or role.can_delete_course_user_group):
            return response.forbidden('You are not allowed to manage the user groups of this course.')

        queryset = Group.objects.filter(course=course)
        serializer = self.serializer_class(queryset, many=True, context={'user': request.user, 'course': course})

        return response.success({'groups': serializer.data})

    def create(self, request):
        """Create a new course group.

        Arguments:
        request -- the request that was send with
            name -- name of the course group
            course_id -- course ID of the course
            lti_id -- (optional) lti_id to link the course to

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            forbidden -- when the user has no permission to create new groups
        On success, with the course group.
        """
        user = request.user
        if not user.is_authenticated:
            return response.unauthorized()

        try:
            name, course_id = utils.required_params(request.data, "name", "course_id")
            lti_id = utils.optional_params(request.data, 'lti_id')
        except KeyError:
            return response.keyerror("name", "course_id")

        role = permissions.get_role(user, course_id)
        if not role.can_add_course_user_group:
            return response.forbidden("You are not allowed to create a course group.")

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        if Group.objects.filter(name=name, course=course).exists():
            return response.bad_request('Course group with that name already exists.')

        course_group = factory.make_course_group(name, course, lti_id)
        serializer = self.serializer_class(course_group, many=False)
        return response.created({'group': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing course group.

        Arguments:
        request -- request data
        data -- the new data for the course group
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exists
            forbidden -- when the user is not in the course
            unauthorized -- when the user is unauthorized to edit the course
            bad_request -- when there is invalid data in the request
        On success:
            success -- with the new course data
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            old_group_name, new_group_name = utils.required_params(request.data, "old_group_name", "new_group_name")
        except KeyError:
            return response.keyerror("old_group_name", "new_group_name")

        course_id = kwargs.get('pk')
        try:
            course = Course.objects.get(pk=course_id)
            group = Group.objects.get(name=old_group_name, course=course)
        except (Course.DoesNotExist, Group.DoesNotExist):
            return response.not_found('Course or group does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not a participant of this course.')
        elif not role.can_edit_course_user_group:
            return response.unauthorized('You are unauthorized to edit this course group.')

        if not new_group_name:
            return response.bad_request('Group name is not allowed to be empty.')

        if Group.objects.filter(name=request.data['new_group_name'], course=course).exists():
            return response.bad_request('Course group with that name already exists.')

        group.name = new_group_name
        serializer = self.serializer_class(group, data=request.data, partial=True)
        if not serializer.is_valid():
            response.bad_request()
        serializer.save()
        return response.success({'group': serializer.data})

    def destroy(self, request, *args, **kwargs):
        """Delete an existing course group.

        Arguments:
        request -- request data
        pk -- course ID

        Returns:
        On failure:
            not found -- when the course does not exists
            unauthorized -- when the user is not logged in
            forbidden -- when the user is not in the course
        On success:
            success -- with a message that the course group was deleted
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        course_id = kwargs.get('pk')

        try:
            name = request.query_params['group_name']
        except KeyError:
            return response.keyerror('group_name')

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist')

        role = permissions.get_role(request.user, course_id)
        if role is None:
            return response.unauthorized(description="You are unauthorized to view this course.")
        elif not role.can_delete_course_user_group:
            return response.forbidden(description="You are unauthorized to delete this course group.")

        try:
            group = Group.objects.get(name=name, course=course)
        except Group.DoesNotExist:
            return response.not_found('Group does not exists')

        group.delete()
        return response.success(description='Sucesfully deleted course group.')
