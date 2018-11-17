"""
format.py.

In this file are all the Format api requests.
"""
from rest_framework import viewsets

import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
from VLE.models import Assignment
from VLE.serializers import (AssignmentDetailsSerializer, AssignmentSerializer,
                             FormatSerializer)


class FormatView(viewsets.ViewSet):
    """Format view.

    This class creates the following api paths:
    GET /formats/ -- gets all the formats
    PATCH /formats/<pk> -- partially update an format
    """

    def retrieve(self, request, pk):
        """Get the format attached to an assignment.

        Arguments:
        request -- the request that was sent
        pk -- the assignment id

        Returns a json string containing the format as well as the
        corresponding assignment name and description.
        """
        assignment = Assignment.objects.get(pk=pk)

        request.user.check_can_view(assignment)
        request.user.check_permission('can_edit_assignment', assignment)

        serializer = FormatSerializer(assignment.format)
        assignment_details = AssignmentDetailsSerializer(assignment)

        return response.success({'format': serializer.data, 'assignment_details': assignment_details.data})

    def partial_update(self, request, pk):
        """Update an existing journal format.

        Arguments:
        request -- request data
            templates -- the list of templates to bind to the format
            presets -- the list of presets to bind to the format
            unused_templates -- the list of templates that are bound to the template
                                deck, but are not used in presets nor the entry templates.
            removed_presets -- presets to be removed
            removed_templates -- templates to be removed
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
        assignment_details, templates, presets, unused_templates, removed_presets, removed_templates \
            = utils.required_params(request.data, "assignment_details", "templates", "presets",
                                    "unused_templates", "removed_presets", "removed_templates")

        assignment = Assignment.objects.get(pk=pk)
        format = assignment.format
        request.user.check_permission('can_edit_assignment', assignment)

        # Check if the assignment can be unpublished
        is_published, = utils.optional_params(assignment_details, 'is_published')
        if not assignment.can_unpublish() and is_published is False:
            return response.bad_request('You cannot unpublish an assignment that already has submissions.')

        # Remove data that must not be changed by the serializer
        req_data = assignment_details
        req_data.pop('published', None)
        if not (request.user.is_superuser or request.user == assignment.author):
            req_data.pop('author', None)

        # Update the assignment details
        serializer = AssignmentSerializer(assignment, data=req_data, context={'user': request.user}, partial=True)
        if not serializer.is_valid():
            return response.bad_request('Invalid data.')
        serializer.save()

        template_map = {}
        utils.update_presets(assignment, presets, template_map)
        utils.update_templates(format.available_templates, templates, template_map)
        utils.update_templates(format.unused_templates, unused_templates, template_map)

        # Swap templates from lists if they occur in the other:
        # If a template was previously unused, but is now used, swap it to available templates, and vice versa.
        utils.swap_templates(format.available_templates, unused_templates, format.unused_templates)
        utils.swap_templates(format.unused_templates, templates, format.available_templates)

        utils.delete_presets(format.presetnode_set, removed_presets)
        utils.delete_templates(format.available_templates, removed_templates)
        utils.delete_templates(format.unused_templates, removed_templates)

        serializer = FormatSerializer(format)
        assignment_details = AssignmentDetailsSerializer(assignment)

        return response.success({'format': serializer.data, 'assignment_details': assignment_details.data})
