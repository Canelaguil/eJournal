"""
entry.py.

In this file are all the entry api requests.
"""
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import datetime

from VLE.models import Journal, Node, Content, Field, Template, Entry, Comment
import VLE.views.responses as response
import VLE.factory as factory
import VLE.utils.generic_utils as utils
import VLE.lti_grade_passback as lti_grade
import VLE.timeline as timeline
import VLE.permissions as permissions
import VLE.serializers as serialize
import VLE.validators as validators


class EntryView(viewsets.ViewSet):
    """Entry view.

    This class creates the following api paths:
    POST /entries/ -- create a new entry
    PATCH /entries/<pk> -- partially update an entry
    """

    def create(self, request):
        """Create a new entry.

        Arguments:
        request -- the request that was send with
            journal_id -- the journal id
            template_id -- the template id to create the entry with
            node_id -- optional: the node to bind the entry to (only for entrydeadlines)
            content -- the list of {tag, data} tuples to bind data to a template field.
        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            journal_id, template_id, content_list = utils.required_params(
                request.data, "journal_id", "template_id", "content")
            node_id, = utils.optional_params(request.data, "node_id")
        except KeyError:
            return response.keyerror("journal_id", "template_id", "content")

        try:
            validators.validate_entry_content(content_list)
        except ValidationError as e:
            return response.bad_request(e.args[0])
        except KeyError:
            return response.keyerror('content.id', 'content.data')

        try:
            journal = Journal.objects.get(pk=journal_id, user=request.user)
            template = Template.objects.get(pk=template_id)
        except (Journal.DoesNotExist, Template.DoesNotExist):
            return response.not_found('Journal or Template does not exist.')

        if not journal.assignment.format.available_templates.all().filter(pk=template.pk).exists():
            return response.forbidden('Entry template is not available.')

        if not permissions.has_assignment_permission(request.user, journal.assignment, 'can_have_journal'):
            return response.forbidden('You are not allowed to create an entry for this journal.')

        if (journal.assignment.unlock_date and journal.assignment.unlock_date > datetime.now()) or \
           (journal.assignment.lock_date and journal.assignment.lock_date < datetime.now()):
            return response.forbidden('The assignment is locked, no entries can be added.')

        # If node id is passed, the entry should be attached to a pre-existing node (entrydeadline node)
        if node_id:
            try:
                node = Node.objects.get(pk=node_id, journal=journal)
            except Node.DoesNotExist:
                return response.not_found('Node does not exist.')

            if node.type != Node.ENTRYDEADLINE:
                return response.bad_request('Passed node is not an EntryDeadline node.')

            if node.entry:
                return response.bad_request('Passed node already contains an entry.')

            if node.preset.deadline < now() or \
               (journal.assignment.due_date and journal.assignment.due_date < datetime.now()):
                return response.bad_request('The deadline has already passed.')

            node.entry = factory.make_entry(template)
            node.save()

        else:
            entry = factory.make_entry(template)
            node = factory.make_node(journal, entry)

        if journal.sourcedid is not None and journal.grade_url is not None:
            lti_grade.needs_grading(journal, node.id)

        for content in content_list:
            try:
                field = Field.objects.get(pk=content['id'])
            except Field.DoesNotExist:
                return response.not_found('Field does not exist.')

            factory.make_content(node.entry, content['data'], field)

        # Find the new index of the new node so that the client can automatically scroll to it.
        result = timeline.get_nodes(journal, request.user)
        added = -1
        for i, result_node in enumerate(result):
            if result_node['nID'] == node.id:
                added = i
                break

        return response.created({
            'added': added,
            'nodes': timeline.get_nodes(journal, request.user)
        })

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
        if not request.user.is_authenticated:
            return response.unauthorized()

        pk = kwargs.get('pk')

        try:
            entry = Entry.objects.get(pk=pk)
        except Entry.DoesNotExist:
            return response.not_found('Entry does not exist.')

        grade, published, content_list = utils.optional_params(request.data, "grade", "published", "content")

        journal = entry.node.journal

        if grade and \
           not permissions.has_assignment_permission(request.user, journal.assignment, 'can_grade'):
            return response.forbidden('You cannot grade or publish entries.')
        elif isinstance(grade, (int, float)) and grade < 0:
            return response.bad_request('Grade must be greater or equal to zero.')
        elif grade:
            entry.grade = grade

        if published is not None and \
           not permissions.has_assignment_permission(request.user, journal.assignment, 'can_publish_grades'):
            return response.forbidden('You cannot publish entries.')

        if ((journal.assignment.unlock_date and journal.assignment.unlock_date > datetime.now()) or
            (journal.assignment.lock_date and journal.assignment.lock_date < datetime.now())) and \
           not permissions.has_assignment_permission(request.user, journal.assignment,
                                                     'can_view_assignment_journals'):
            return response.bad_request('The assignment is locked and unavailable for students.')

        if published is not None:
            entry.published = published
            try:
                entry.save()
            except ValueError:
                return response.bad_request('Invalid grade or published state.')
            if published:
                Comment.objects.filter(entry=entry).update(published=True)

        # Attempt to edit the entries content.
        if content_list:
            if not (journal.user == request.user or request.user.is_superuser):
                response.forbidden('You are not allowed to edit someone else\'s entry.')

            if not permissions.has_assignment_permission(request.user, journal.assignment, 'can_have_journal'):
                return response.forbidden('You are not allowed to have a journal.')

            if entry.grade is not None:
                return response.bad_request('You are not allowed to edit graded entries.')

            if entry.node.type == Node.ENTRYDEADLINE and entry.node.preset.deadline < now() or \
               (journal.assignment.due_date and journal.assignment.due_date < datetime.now()):
                return response.bad_request('You are not allowed to edit entries past their due date.')

            try:
                validators.validate_entry_content(content_list)
            except ValidationError as e:
                return response.bad_request(e.args[0])
            except KeyError:
                return response.keyerror('content.id', 'content.data')

            Content.objects.filter(entry=entry).all().delete()

            for content in content_list:
                try:
                    field = Field.objects.get(pk=content['id'])
                except Field.DoesNotExist:
                    return response.not_found('Field does not exist.')

                if content['data']:
                    factory.make_content(entry, content['data'], field)

        req_data = request.data
        if 'content' in req_data:
            del req_data['content']
        if content_list:
            req_data['last_edited'] = datetime.now()
        serializer = serialize.EntrySerializer(entry, data=req_data, partial=True, context={'user': request.user})
        if not serializer.is_valid():
            response.bad_request()

        try:
            serializer.save()
        except ValueError:
            return response.bad_request('Invalid grade or published state.')
        if published and journal.sourcedid is not None and journal.grade_url is not None:
            payload = lti_grade.replace_result(journal)
        else:
            payload = dict()

        return response.success({'entry': serializer.data, 'lti': payload})

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
        if not request.user.is_authenticated:
            return response.unauthorized()
        pk = kwargs.get('pk')

        try:
            entry = Entry.objects.get(pk=pk)
            journal = entry.node.journal
        except Entry.DoesNotExist:
            return response.not_found('Entry does not exist.')

        if not (journal.user == request.user or request.user.is_superuser):
            return response.forbidden('You are not allowed to delete someone else\'s entry.')

        if entry.grade:
            return response.forbidden('You cannot delete graded entries.')

        if entry.node.type == Node.ENTRYDEADLINE and \
           permissions.has_assignment_permission(request.user, journal.assignment, 'can_have_journal'):
            return response.forbidden('You cannot delete deadlines.')

        if journal.assignment.due_date and journal.assignment.due_date < datetime.now() and \
           permissions.has_assignment_permission(request.user, journal.assignment, 'can_have_journal'):
            return response.forbidden('You cannot delete an entry whose deadline deadline has already passed.')

        if (journal.assignment.unlock_date and journal.assignment.unlock_date > datetime.now()) or \
           (journal.assignment.lock_date and journal.assignment.lock_date < datetime.now()) and \
           permissions.has_assignment_permission(request.user, journal.assignment, 'can_have_journal'):
            return response.forbidden('You cannot delete a locked entry.')

        entry.node.delete()
        entry.delete()
        return response.success(description='Sucesfully deleted entry.')
