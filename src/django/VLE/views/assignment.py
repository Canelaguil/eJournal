"""
assignment.py.

In this file are all the assignment api requests.
"""
from rest_framework import viewsets
from rest_framework.decorators import action

import VLE.factory as factory
import VLE.lti_grade_passback as lti_grade
import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
from VLE.models import Assignment, Course, Entry, Lti_ids
from VLE.serializers import AssignmentSerializer
from VLE.utils.error_handling import VLEMissingRequiredKey, VLEParamWrongType


class AssignmentView(viewsets.ViewSet):
    """Assignment view.

    This class creates the following api paths:
    GET /assignments/ -- gets all the assignments
    POST /assignments/ -- create a new assignment
    GET /assignments/<pk> -- gets a specific assignment
    PATCH /assignments/<pk> -- partially update an assignment
    DEL /assignments/<pk> -- delete an assignment
    GET /assignments/upcoming/ -- get the upcoming assignments of the logged in user
    """

    def list(self, request):
        """Get the assignments from a course for the user.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when the user is not part of the course
        On succes:
            success -- with the assignment data

        """
        course_id, = utils.required_typed_params(request.query_params, (int, 'course_id'))
        course = Course.objects.get(pk=course_id)

        request.user.check_participation(course)

        # Consider all assignments that the user is in, or can grade.
        assignments = []
        for assignment in course.assignment_set.all():
            if request.user.can_view(assignment):
                assignments.append(assignment)

        serializer = AssignmentSerializer(assignments, many=True, context={'user': request.user, 'course': course})

        data = serializer.data
        for i, assignment in enumerate(data):
            data[i]['lti_couples'] = len(Lti_ids.objects.filter(assignment=assignment['id']))
        return response.success({'assignments': data})

    def create(self, request):
        """Create a new assignment.

        Arguments:
        request -- request data
            name -- name of the assignment
            description -- description of the assignment
            course_id -- id of the course the assignment belongs to
            points_possible -- the possible amount of points for the assignment
            unlock_date -- (optional) date the assignment becomes available on
            due_date -- (optional) date the assignment is due for
            lock_date -- (optional) date the assignment becomes unavailable on
            lti_id -- id labeled link to LTI instance

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not_found -- could not find the course with the given id
            key_error -- missing keys
            forbidden -- the user is not allowed to create assignments in this course

        On success:
            succes -- with the assignment data

        """
        name, description, course_id = utils.required_params(request.data, "name", "description", "course_id")
        points_possible, unlock_date, due_date, lock_date, lti_id, is_published = \
            utils.optional_params(request.data, "points_possible", "unlock_date", "due_date", "lock_date", "lti_id",
                                  "is_published")
        course = Course.objects.get(pk=course_id)

        request.user.check_permission('can_add_assignment', course)

        assignment = factory.make_assignment(name, description, courses=[course],
                                             author=request.user, lti_id=lti_id,
                                             points_possible=points_possible,
                                             unlock_date=unlock_date, due_date=due_date,
                                             lock_date=lock_date, is_published=is_published)

        for user in course.users.all():
            factory.make_journal(assignment, user)

        serializer = AssignmentSerializer(assignment, context={'user': request.user, 'course': course})
        return response.created({'assignment': serializer.data})

    def retrieve(self, request, pk=None):
        """Retrieve an assignment.

        Arguments:
        request -- request data
            lti -- if this is set, the pk is an lti_id, not a 'normal' id
            course_id -- get information about that course
        pk -- assignment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not_found -- could not find the course with the given id
            forbidden -- not allowed to retrieve assignments in this course

        On success:
            succes -- with the assignment data

        """
        if 'lti' in request.query_params:
            assignment = Assignment.objects.get(lti_ids__lti_id=pk, lti_ids__for_model=Lti_ids.ASSIGNMENT)
        else:
            assignment = Assignment.objects.get(pk=pk)

        try:
            course_id, = utils.required_typed_params(request.query_params, (int, 'course_id'))
            course = Course.objects.get(id=course_id)
        except (VLEMissingRequiredKey, VLEParamWrongType):
            course = None

        request.user.check_can_view(assignment)

        serializer = AssignmentSerializer(
            assignment,
            context={'user': request.user, 'course': course,
                     'journals': request.user.has_permission('can_grade', assignment)}
        )

        return response.success({'assignment': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing assignment.

        Arguments:
        request -- request data
            data -- the new data for the assignment
        pk -- assignment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the assignment does not exist
            forbidden -- User not allowed to edit this assignment
            unauthorized -- when the user is unauthorized to edit the assignment
            bad_request -- when there is invalid data in the request
        On success:
            success -- with the new assignment data

        """
        # Get data
        pk, = utils.required_typed_params(kwargs, (int, 'pk'))
        assignment = Assignment.objects.get(pk=pk)
        published, = utils.optional_params(request.data, 'published')

        # Remove data that must not be changed by the serializer
        req_data = request.data
        req_data.pop('published', None)
        if not (request.user.is_superuser or request.user == assignment.author):
            req_data.pop('author', None)

        response_data = {}

        # Publish is possible and asked for
        if published:
            request.user.check_permission('can_publish_grades', assignment)
            self.publish(request, assignment)
            response_data['published'] = published

        # Update assignment data is possible and asked for
        if req_data:
            if 'lti_id' in req_data:
                factory.make_lti_ids(lti_id=req_data['lti_id'], for_model=Lti_ids.ASSIGNMENT, assignment=assignment)

            # If a entry has been submitted to one of the journals of the journal it cannot be unpublished
            if assignment.is_published and 'is_published' in req_data and not req_data['is_published'] and \
               Entry.objects.filter(node__journal__assignment=assignment).exists():
                return response.bad_request(
                    'You are not allowed to unpublish an assignment that already has submissions.')

            serializer = AssignmentSerializer(assignment, data=req_data, context={'user': request.user}, partial=True)
            if not serializer.is_valid():
                response.bad_request()
            serializer.save()
            response_data['assignment'] = serializer.data

        return response.success(response_data)

    def destroy(self, request, *args, **kwargs):
        """Delete an existing assignment from a course.

        Arguments:
        request -- request data
            course_id -- the course ID of course this assignment belongs to
        pk -- assignment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the assignment or course does not exist
            unauthorized -- when the user is not logged in
            forbidden -- when the user cannot delete the assignment
        On success:
            success -- with a message that the course was deleted

        """
        assignment_id, = utils.required_typed_params(kwargs, (int, 'pk'))
        course_id, = utils.required_typed_params(request.query_params, (int, 'course_id'))
        assignment = Assignment.objects.get(pk=assignment_id)
        course = Course.objects.get(pk=course_id)

        request.user.check_permission('can_delete_assignment', course)

        assignment.courses.remove(course)
        assignment.save()

        # If the assignment is only connected to one course, delete it completely
        if assignment.courses.count() == 0:
            assignment.delete()
            return response.success(description='Successfully deleted the assignment.')
        else:
            return response.success(description='Successfully removed the assignment from {}.'.format(str(course)))

    @action(methods=['get'], detail=False)
    def upcoming(self, request):
        """Get upcoming deadlines for the requested user.

        Arguments:
        request -- request data
            course_id -- course ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
        On success:
            success -- upcoming assignments

        """
        try:
            course_id, = utils.required_typed_params(request.query_params, (int, 'course_id'))
            courses = [Course.objects.get(pk=course_id)]
        except (VLEMissingRequiredKey, VLEParamWrongType):
            courses = request.user.participations.all()

        deadline_list = []

        # TODO: change query to a query that selects all upcoming assignments connected to the user.
        for course in courses:
            if request.user.is_participant(course):
                for assignment in Assignment.objects.filter(courses=course.id, is_published=True).all():
                    deadline_list.append(
                        AssignmentSerializer(assignment, context={'user': request.user, 'course': course}).data)

        return response.success({'upcoming': deadline_list})

    @action(methods=['patch'], detail=True)
    def published_state(self, request, *args, **kwargs):
        """Update the grade publish status for whole assignment.

        Arguments:
        request -- the request that was send with
            published -- new published state
        pk -- assignment ID

        Returns a json string if it was successful or not.
        """
        assignment_id, = utils.required_typed_params(kwargs, (int, 'pk'))
        published, = utils.required_params(request.data, 'published')
        assignment = Assignment.objects.get(pk=assignment_id)

        request.user.check_permission('can_publish_grades', assignment)

        self.publish(request, assignment, published)

        return response.success(payload={'new_published': published})

    def publish(self, request, assignment, published=True):
        utils.publish_all_assignment_grades(assignment, published)
        if published:
            for journal in assignment.journal_set.all():
                if journal.sourcedid is not None and journal.grade_url is not None:
                    lti_grade.replace_result(journal)
