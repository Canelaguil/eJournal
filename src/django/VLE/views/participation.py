from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action

import VLE.factory as factory
import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
from VLE.models import Course, Group, Journal, Participation, Role, User
from VLE.serializers import ParticipationSerializer, UserSerializer


class ParticipationView(viewsets.ViewSet):
    def list(self, request):
        """Get all users and their roles for a given course.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to view its participants
        On success:
            success -- list of all the users and their role
        """
        course_id, = utils.required_params(request.query_params, "course_id")

        course = Course.objects.get(pk=course_id)

        request.user.check_permission('can_view_course_users', course)

        users = UserSerializer(course.users, context={'course': course}, many=True).data
        return response.success({'participants': users})

    def retrieve(self, request, pk=None):
        """Get own participation data from the course ID.

        Arguments:
        request -- request data
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
        On success:
            success -- with the participation data
        """
        course = Course.objects.get(pk=pk)

        request.user.check_participation(course)

        participation = Participation.objects.get(user=request.user, course=course)

        serializer = ParticipationSerializer(participation)
        return response.success({'participant': serializer.data})

    def create(self, request):
        """Add a user to a course.

        Arguments:
        request -- request data
            user_id -- user ID
            course_id -- course ID

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
        user_id, course_id = utils.required_params(request.data, 'user_id', 'course_id')
        role_name = 'Student'

        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=course_id)

        request.user.check_permission('can_add_course_users', course)

        if user.is_participant(course):
            return response.bad_request('User already participates in the course.')

        role = Role.objects.get(name=role_name, course=course)

        factory.make_participation(user, course, role)

        assignments = course.assignment_set.all()
        for assignment in assignments:
            if not Journal.objects.filter(assignment=assignment, user=user).exists():
                factory.make_journal(assignment, user)
        return response.success(description='Successfully added student to course.')

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
            not found -- when the perticipation is not found
            forbidden -- when the user is not connected to the course
            forbidden -- when the user is not allowed to change the perticipation
        On success:
            success -- with the new role name
        """
        user_id, = utils.required_params(request.data, 'user_id')
        role_name, group_name = utils.optional_params(request.data, 'role', 'group')

        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=pk)
        participation = Participation.objects.get(user=user, course=course)
        request.user.check_permission('can_edit_course_user_group', course)

        if role_name:
            request.user.check_permission('can_edit_course_roles', course)
            participation.role = Role.objects.get(name=role_name, course=course)

        if group_name:
            participation.group = Group.objects.get(name=group_name, course=course)
        elif 'group' in request.data:
            participation.group = None

        participation.save()
        serializer = UserSerializer(participation.user, context={'course': course})
        return response.success({'user': serializer.data}, description='Successfully updated participation.')

    def destroy(self, request, pk):
        """Remove a user from the course.

        request -- request data
            user_id -- user ID
        pk -- course ID
        """
        user_id, = utils.required_params(request.query_params, 'user_id')

        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=pk)
        participation = Participation.objects.get(user=user, course=course)

        request.user.check_permission('can_delete_course_users', course)

        participation.delete()
        return response.success(description='Sucesfully removed user from course.')

    @action(methods=['get'], detail=False)
    def unenrolled(self, request):
        """Get all users that are not in the given course.

        Arguments:
        request -- request data
            course_id -- course ID
            unenrolled_query -- query that needs to match with the unenrolled users

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            forbidden -- when the user is unauthorized to view its participants
        On success:
            success -- list of all the users and their role
        """
        course_id, unenrolled_query = utils.required_params(request.query_params, 'course_id', 'unenrolled_query')
        if ' ' in unenrolled_query:
            first_name = unenrolled_query.split(' ', 1)[0]
            last_name = unenrolled_query.split(' ', 1)[1]

        course = Course.objects.get(pk=course_id)
        request.user.check_permission('can_add_course_users', course)

        ids_in_course = course.participation_set.all().values('user__id')
        users = User.objects.all().exclude(id__in=ids_in_course)

        if len(unenrolled_query) < 5:
            user = users.filter(username=unenrolled_query)
            if user:
                return response.success({'participants': UserSerializer(user, many=True).data})
            else:
                return response.success({'participants': []})

        found_users = users.filter(Q(username__contains=unenrolled_query) |
                                   Q(first_name__contains=unenrolled_query) |
                                   Q(last_name__contains=unenrolled_query))

        if ' ' in unenrolled_query:
            found_users = found_users | users.filter(first_name__contains=first_name, last_name__contains=last_name)

        return response.success({'participants': UserSerializer(found_users, many=True).data})
