from rest_framework import viewsets
from rest_framework.decorators import action

from VLE.models import Course, User, Role, Journal, Participation, Group
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.factory as factory
import VLE.views.responses as response
from VLE.serializers import UserSerializer


class ParticipationView(viewsets.ViewSet):
    def list(self, request):
        """Get all users and their roles for a given course.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when course_id is not set as a parameter
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to view its participants
        On success:
            success -- list of all the users and their role
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course_id, = utils.required_params(request.query_params, "course_id")
        except KeyError:
            return response.keyerror('course_id')

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not a participant of this course.')
        elif not role.can_view_course_users:
            return response.forbidden('You cannot view the participants of this course.')

        users = UserSerializer(course.users, context={'course': course}, many=True).data
        return response.success({'participants': users})

    def create(self, request):
        """Add a user to a course.

        Arguments:
        request -- request data
            user_id -- user ID
            course_id -- course ID
            role -- name of the role (default: Student)

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when course or user is not found
            forbidden -- when the logged in user is not connected to the course
            bad request -- when the new user is already connected to the course
            not found -- when the role doesnt exist
        On success:
            success -- success message
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            user_id, course_id = utils.required_params(request.data, 'user_id', 'course_id')
            role_name, = utils.optional_params(request.data, 'role')
            if not role_name:
                role_name = 'Student'
        except KeyError:
            return response.keyerror('user_id', 'course_id')

        try:
            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=course_id)
        except (User.DoesNotExist, Course.DoesNotExist):
            return response.not_found('User or course does not exist')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not in this course.')
        elif not role.can_add_course_users:
            return response.forbidden('You cannot add users to this course.')

        if permissions.is_user_in_course(user, course):
            return response.bad_request('User already participates in the course.')

        try:
            role = Role.objects.get(name=role_name, course=course)
        except Role.DoesNotExist:
            return response.not_found('Role does not exist.')

        factory.make_participation(user, course, role)

        assignments = course.assignment_set.all()
        role = permissions.get_role(user, course_id)
        if role.can_have_journal:
            for assignment in assignments:
                if not Journal.objects.filter(assignment=assignment, user=user).exists():
                    factory.make_journal(assignment, user)
        return response.success(description='Succesfully added student to course.')

    def partial_update(self, request, pk):
        """Update user role in a course.

        Arguments:
        request -- request data
            user_id -- user ID
            role -- name of the role (default: Student)
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when the user_id is not set
            not found -- when the perticipation is not found
            forbidden -- when the user is not connected to the course
            forbidden -- when the user is not allowed to change the perticipation
        On success:
            success -- with the new role name
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        try:
            user_id, = utils.required_params(request.data, 'user_id')
            role_name, group_name = utils.optional_params(request.data, 'role', 'group')
            if not role_name:
                role_name = 'Student'
        except KeyError:
            return response.keyerror("user_id")

        try:
            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=pk)
            participation = Participation.objects.get(user=user, course=course)
        except (Participation.DoesNotExist, Course.DoesNotExist, User.DoesNotExist):
            return response.not_found('Participation, User or Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not in this course.')
        elif not role.can_edit_course_roles:
            return response.forbidden('You cannot edit the roles of this course.')

        participation.role = Role.objects.get(name=role_name, course=course)

        if group_name:
            try:
                participation.group = Group.objects.get(name=group_name, course=course)
            except (Group.DoesNotExist):
                return response.not_found('Group does not exist.')
        else:
            participation.group = None

        participation.save()
        serializer = UserSerializer(participation.user, context={'course': course})
        return response.success({'user': serializer.data}, description='Succesfully updated participation.')

    def destroy(self, request, pk):
        """Remove a user from the course.

        request -- request data
            user_id -- user ID
        pk -- course ID
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        try:
            user_id, = utils.required_params(request.query_params, 'user_id')
        except KeyError:
            return response.keyerror('user_id')

        try:
            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=pk)
            participation = Participation.objects.get(user=user, course=course)
        except (Participation.DoesNotExist, Role.DoesNotExist, Course.DoesNotExist):
            return response.not_found('Participation or Course')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.unauthorized(description="You have no access to this course")
        elif not role.can_delete_course_users:
            return response.forbidden(description="You are not allowed to delete this user.")

        participation.delete()
        return response.success(description='Sucesfully removed user from course.')

    @action(methods=['get'], detail=False)
    def unenrolled(self, request):
        """Get all users that are not in the given course.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when course_id is not set as a parameter
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to view its participants
        On success:
            success -- list of all the users and their role
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course_id, = utils.required_params(request.query_params, "course_id")
        except KeyError:
            return response.keyerror('course_id')

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        role = permissions.get_role(request.user, course)
        if role is None:
            return response.forbidden('You are not in this course.')
        elif not role.can_add_course_users:
            return response.forbidden('You are not allowed to add course users.')

        ids_in_course = course.participation_set.all().values('user__id')
        users = User.objects.all().exclude(id__in=ids_in_course)
        return response.success({'participants': UserSerializer(users, many=True).data})
