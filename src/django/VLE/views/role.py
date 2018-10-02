
from rest_framework import viewsets

import VLE.permissions as permissions
import VLE.views.responses as response
from VLE.serializers import RoleSerializer
from VLE.models import Course, Role, Assignment, User
import VLE.factory as factory
from django.core.exceptions import ValidationError


class RoleView(viewsets.ViewSet):
    def list(self, request):
        """Get course roles.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to edit its roles
        On success:
            success -- list of all the roles in the course

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course_id = request.query_params['course_id']
        except KeyError:
            return response.keyerror('course_id')
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not allowed to view this course.')
        elif not role.can_edit_course_roles:
            return response.forbidden('You are not allowed to edit course roles.')

        roles = Role.objects.filter(course=course_id)
        serializer = RoleSerializer(roles, many=True)
        return response.success({'roles': serializer.data})

    def retrieve(self, request, pk=0):
        """Get the permissions of a user connected to a course / assignment.

        Arguments:
        request -- the request that was sent
            course_id -- course ID
            assignment_id -- assignment ID
        pk -- user ID (0 = logged in user)

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course is not found
            forbidden -- when the user is not in the course
        On success:
            success -- with a list of the permissions

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            user = request.user if int(pk) == 0 else User.objects.get(int(pk))
        except User.DoesNotExist:
            return response.not_found('User does not exist.')

        # Return course permissions if course_id is set
        try:
            course_id = request.query_params['course_id']
            try:
                if int(course_id) > 0:
                    Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                return response.not_found('Course does not exist.')

            perms = permissions.get_permissions(user, int(course_id))
            if perms is None:
                return response.forbidden('You are not a participant of this course.')

            return response.success({'role': perms})
        # Return assignment permissions if assignment_id is set
        except KeyError:
            try:
                assignment_id = request.query_params['assignment_id']
                try:
                    perms = permissions.get_assignment_id_permissions(request.user, assignment_id)
                    return response.success({'role': perms})
                except Assignment.DoesNotExist:
                    return response.not_found('Assignment does not exist.')
        # Return keyerror is course_id nor assignment_id is set
            except KeyError:
                return response.keyerror('course_id or assignment_id')

    def create(self, request):
        """Create course role.

        Arguments:
        request -- request data
            course_id -- course ID
            name -- role name
            permissions -- permissions to change (default everything is false)

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to edit its roles
        On success:
            success -- newly created course

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course = Course.objects.get(pk=request.data['course_id'])
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not a participant of this course.')
        elif not role.can_edit_course_roles:
            return response.forbidden('You do not have the permission to create roles for this course.')

        try:
            role = factory.make_role_default_no_perms(request.data['name'], course, **request.data['permissions'])
        except ValidationError as e:
            return response.bad_request(e.args[0])
        except Exception:
            return response.bad_request()

        serializer = RoleSerializer(role, many=False)
        return response.created({'role': serializer.data})

    def partial_update(self, request, pk):
        """Updates course roles.

        Arguments:
        request -- request data
            roles -- each role of the course that needs to be updated
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to edit its roles
            keyerror -- when roles or roles.name is not set
            bad_request -- if
        On success:
            success -- list of all the roles in the course

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not in this course.')
        elif not role.can_edit_course_roles:
            return response.forbidden('You cannot edit roles of this course.')

        if 'roles' not in request.data:
            return response.keyerror('roles')

        resp = []

        for new_role in request.data['roles']:
            if 'name' not in new_role:
                return response.keyerror('roles.name')

            try:
                role = Role.objects.get(name=new_role['name'], course=course)
            except Role.DoesNotExist:
                role = factory.make_role_default_no_perms(new_role['name'], course)
            serializer = RoleSerializer(role, data=new_role, partial=True)
            if not serializer.is_valid():
                response.bad_request()

            try:
                serializer.save()
            except ValidationError as e:
                return response.bad_request(e.args[0])

            resp.append(serializer.data)
        return response.success({'roles': resp})

    def destroy(self, request, pk):
        """Delete course role.

        Arguments:
        request -- request data
            name -- role name
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when name is not set
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to edit its roles
        On success:
            success -- newly created course

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            name = request.query_params['name']
        except KeyError:
            return response.keyerror('name')

        # Users can only delete course roles with can_edit_course_roles
        role = permissions.get_role(request.user, pk)
        if role is None:
            return response.forbidden(description="You have no access to this course")
        elif not role.can_edit_course_roles:
            return response.forbidden(description="You have no permissions to delete this course role.")

        if name in ['Student', 'TA', 'Teacher']:
            return response.bad_request("Default roles 'Student', 'TA' and 'Teacher' cannot be deleted.")

        Role.objects.get(name=name, course=pk).delete()
        return response.success(description='Succesfully deleted role from course.')
