"""
course.py.

In this file are all the course api requests.
"""
from rest_framework import viewsets
from rest_framework.decorators import action

import VLE.views.responses as response
import VLE.serializers as serialize
from VLE.models import Course, Lti_ids, Participation
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.factory as factory


class CourseView(viewsets.ViewSet):
    serializer_class = serialize.CourseSerializer

    def list(self, request):
        """Get the courses that the user participates in.

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

        queryset = request.user.participations.all()
        serializer = self.serializer_class(queryset, many=True)
        return response.success({'courses': serializer.data})

    def create(self, request):
        """Create a new course.

        Arguments:
        request -- request data
            name -- name of the course
            abbreviation -- abbreviation of the course
            startdate -- (optional) date when the course starts
            enddate -- (optional) date when the course ends
            lti_id -- (optional) lti_id to link the course to

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            forbidden -- when the user has no permission to create new courses
        On succes:
            success -- with the course data
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        perm = permissions.get_permissions(request.user)

        if not perm['can_add_course']:
            return response.forbidden('You are not allowed to create a course.')

        try:
            name, abbr = utils.required_params(request.data, 'name', 'abbreviation')
            startdate, enddate, lti_id = utils.optional_params(request.data, 'startdate', 'enddate', 'lti_id')
        except KeyError:
            return response.keyerror('name', 'abbreviation')

        course = factory.make_course(name, abbr, startdate, enddate, request.user, lti_id)

        serializer = self.serializer_class(course, many=False)
        return response.created({'course': serializer.data})

    def retrieve(self, request, pk=None):
        """Get the course data from the course ID.

        Arguments:
        request -- request data
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
        On success:
            success -- with the course data
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        if not permissions.is_user_in_course(request.user, course):
            return response.forbidden('You are not a participant of this course.')

        serializer = self.serializer_class(course, many=False)
        return response.success({'course': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing course.

        Arguments:
        request -- request data
            data -- the new data for the course
        pk -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
            unauthorized -- when the user is unauthorized to edit the course
            bad_request -- when there is invalid data in the request
        On success:
            success -- with the new course data
        """
        pk = kwargs.get('pk')
        if not request.user.is_authenticated or \
           not request.user.participations.filter(pk=pk):
            return response.unauthorized()

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        if not Participation.objects.filter(user=request.user, course=course).exists():
            return response.forbidden('You are not a participant of this course.')

        if not permissions.get_role(request.user, course).can_edit_course_details:
            return response.unauthorized('You are unauthorized to edit this course.')

        data = request.data
        if 'lti_id' in data:
            factory.make_lti_ids(lti_id=data['lti_id'], for_model=Lti_ids.COURSE, course=course)

        serializer = self.serializer_class(course, data=data, partial=True)
        if not serializer.is_valid():
            response.bad_request()
        serializer.save()
        return response.success({'course': serializer.data})

    def destroy(self, request, *args, **kwargs):
        """Delete an existing course.

        Arguments:
        request -- request data
        pk -- course ID

        Returns:
        On failure:
            not found -- when the course does not exist
            unauthorized -- when the user is not logged in
            forbidden -- when the user is not in the course
        On success:
            success -- with a message that the course was deleted
        """
        if not request.user.is_authenticated:
            return response.unauthorized()
        pk = kwargs.get('pk')

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return response.not_found('Course does not exist.')

        if not Participation.objects.filter(user=request.user, course=course).exists():
            return response.unauthorized(description="You are unauthorized to view this course.")

        if not permissions.get_role(request.user, pk).can_delete_course:
            return response.forbidden(description="You are unauthorized to delete this course.")

        course.delete()
        return response.success(description='Sucesfully deleted course.')

    @action(methods=['get'], detail=False)
    def linkable(self, request):
        """Get linkable courses.

        Gets all courses that the current user either participates in or is allowed to edit the course details of.
        A user can then link this course to Canvas.

        Arguments:
        request -- request data

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not in the course
        On success:
            success -- with a message that the course was deleted
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        if not (request.user.is_teacher or request.user.is_superuser):
            return response.forbidden("You are not allowed to link courses.")

        unlinked_courses = Course.objects.filter(participation__user=request.user.id,
                                                 participation__role__can_edit_course_details=True)
        serializer = serialize.CourseSerializer(unlinked_courses, many=True)
        data = serializer.data
        for i, course in enumerate(data):
            data[i]['lti_couples'] = len(Lti_ids.objects.filter(course=course['id']))
        return response.success({'courses': data})
