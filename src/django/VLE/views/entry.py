"""
entry.py.

In this file are all the entry api requests.
"""
from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action

import VLE.factory as factory
import VLE.lti_grade_passback as lti_grade
import VLE.serializers as serialize
import VLE.timeline as timeline
import VLE.utils.entry_utils as entry_utils
import VLE.utils.file_handling as file_handling
import VLE.utils.generic_utils as utils
import VLE.utils.responses as response
import VLE.validators as validators
from VLE.models import Comment, Entry, Field, Journal, Node, Template


class EntryView(viewsets.ViewSet):
    """Entry view.

    This class creates the following api paths:
    POST /entries/ -- create a new entry
    PATCH /entries/<pk> -- partially update an entry
    """

    def create(self, request):
        """Create a new entry.

        Deletes remaining temporary user files if successful.

        Arguments:
        request -- the request that was send with
            journal_id -- the journal id
            template_id -- the template id to create the entry with
            node_id -- optional: the node to bind the entry to (only for entrydeadlines)
            content -- the list of {tag, data} tuples to bind data to a template field.
        """
        journal_id, template_id, content_list = utils.required_params(
            request.data, "journal_id", "template_id", "content")
        node_id, = utils.optional_params(request.data, "node_id")

        journal = Journal.objects.get(pk=journal_id, user=request.user)
        assignment = journal.assignment
        template = Template.objects.get(pk=template_id)

        request.user.check_permission('can_have_journal', assignment)

        if assignment.is_locked():
            return response.forbidden('The assignment is locked, no entries can be added.')

        # Check if the template is available
        if not (node_id or assignment.format.available_templates.filter(pk=template.pk).exists()):
            return response.forbidden('Entry template is not available.')

        entry_utils.check_required_fields(template, content_list)
        # Check if its an entry for a specific node
        if node_id:
            node = Node.objects.get(pk=node_id, journal=journal)
            resp = self.add_entry_to_node(node, template)
            if resp is not True:
                return resp
        # If not, check for available templates
        else:
            entry = factory.make_entry(template)
            node = factory.make_node(journal, entry)

        # Notify teacher on new entry
        lti_grade.needs_grading(node)

        for content in content_list:
            data, field_id = utils.required_params(content, 'data', 'id')
            field = Field.objects.get(pk=field_id)
            validators.validate_entry_content(data, field)

            created_content = factory.make_content(node.entry, data, field)

            if field.type in ['i', 'f', 'p']:  # Image, file or PDF
                user_file = file_handling.get_temp_user_file(request.user, assignment, content['data'])
                if user_file is None:
                    node.entry.delete()
                    return response.bad_request('One of your files was not correctly uploaded, please try gain.')

                file_handling.make_permanent_file_content(user_file, created_content, node)

        # Delete old userfiles
        file_handling.remove_temp_user_files(request.user)

        return response.created({
            'added': entry_utils.get_node_index(journal, node, request.user),
            'nodes': timeline.get_nodes(journal, request.user),
            'entry': serialize.EntrySerializer(entry, context={'user': request.user}).data
        })

    def add_entry_to_node(self, node, template):
        if not (node.preset and node.preset.forced_template == template):
            return response.forbidden('Invalid template for preset node.')

        if node.type != Node.ENTRYDEADLINE:
            return response.bad_request('Passed node is not an EntryDeadline node.')

        if node.entry:
            return response.bad_request('Passed node already contains an entry.')

        if node.preset.is_due():
            return response.bad_request('The deadline has already passed.')

        node.entry = factory.make_entry(template)
        node.save()
        return True

    def partial_update(self, request, *args, **kwargs):
        """Update an existing entry.

        Arguments:
        request -- request data
            data -- the new data for the course
        pk -- assignment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the entry does not exist
            forbidden -- User not allowed to edit this entry
            unauthorized -- when the user is unauthorized to edit the entry
            bad_request -- when there is invalid data in the request
        On success:
            success -- with the new entry data

        """
        content_list, = utils.required_typed_params(request.data, (list, 'content'))

        entry_id, = utils.required_typed_params(kwargs, (int, 'pk'))
        entry = Entry.objects.get(pk=entry_id)
        journal = entry.node.journal
        assignment = journal.assignment

        if assignment.is_locked():
            return response.forbidden('The assignment is locked, no entries can changed.')

        request.user.check_permission('can_have_journal', assignment)

        if not (journal.user == request.user or request.user.is_superuser):
            return response.forbidden('You are not allowed to edit someone else\'s entry.')
        if entry.grade is not None:
            return response.bad_request('You are not allowed to edit graded entries.')
        if entry.is_due():
            return response.bad_request('You are not allowed to edit entries past their due date.')

        # Attempt to edit the entries content.
        for content in content_list:
            field_id, data, content_id = utils.required_params(content, 'id', 'data', 'contentID')
            field = Field.objects.get(pk=field_id)
            old_content = entry.content_set.get(pk=content_id)
            validators.validate_entry_content(data, field)

            if old_content.field.pk != int(field_id):
                return response.bad_request('The given content does not match the accompanying field type.')

            if not data:
                old_content.delete()
                continue

            entry_utils.patch_entry_content(request.user, entry, old_content, field, data, assignment)

            file_handling.remove_temp_user_files(request.user)

        req_data = request.data
        req_data.pop('content', None)
        req_data.pop('published', None)
        req_data.pop('grade', None)
        req_data['last_edited'] = datetime.now()
        serializer = serialize.EntrySerializer(entry, data=req_data, partial=True, context={'user': request.user})
        if not serializer.is_valid():
            return response.bad_request()
        serializer.save()

        return response.success({'entry': serializer.data})

    def destroy(self, request, *args, **kwargs):
        """Delete an entry and the node it belongs to.

        Arguments:
        request -- request data
        pk -- entry ID

        Returns:
        On failure:
            not found -- when the course does not exist
            unauthorized -- when the user is not logged in
            forbidden -- when the user is not in the course
        On success:
            success -- with a message that the course was deleted
        """
        pk, = utils.required_typed_params(kwargs, (int, 'pk'))

        entry = Entry.objects.get(pk=pk)
        journal = entry.node.journal
        assignment = journal.assignment

        if journal.user == request.user:
            request.user.check_permission('can_have_journal', assignment, 'You cannot delete entries.')
            if entry.grade:
                return response.forbidden('You cannot delete graded entries.')
            if entry.is_due():
                return response.forbidden('You cannot delete an entry for which the deadline has already passed.')
            if assignment.is_locked():
                return response.forbidden('You cannot delete a locked entry.')

        elif not request.user.is_superuser:
            return response.forbidden('You are not allowed to delete someone else\'s entry.')

        if entry.node.type != Node.ENTRYDEADLINE:
            entry.node.delete()
        entry.delete()
        return response.success(description='Successfully deleted entry.')

    @action(methods=['patch'], detail=True)
    def grade(self, request, pk):
        entry = Entry.objects.get(pk=pk)
        journal = entry.node.journal
        assignment = journal.assignment
        grade, published = utils.optional_typed_params(request.data, (float, 'grade'), (bool, 'published'))

        if grade:
            request.user.check_permission('can_grade', assignment)
            if grade < 0:
                return response.bad_request('Grade must be greater than or equal to zero.')
            entry.grade = grade

        if published is not None:
            if published is not True and entry.published is True:
                return response.bad_request('A published entry cannot be unpublished.')
            request.user.check_permission('can_publish_grades', assignment)
            entry.published = published
            if published:
                Comment.objects.filter(entry=entry).update(published=True)

        entry.save()
        return response.success({
            'entry': serialize.EntrySerializer(entry, context={'user': request.user}).data,
            'lti': lti_grade.replace_result(journal)
        })
