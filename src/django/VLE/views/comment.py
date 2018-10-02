"""
comment.py.

In this file are all the comment api requests.
"""
from rest_framework import viewsets
from datetime import datetime

from VLE.serializers import CommentSerializer
from VLE.models import Comment, Entry, Assignment, Journal
import VLE.views.responses as response
import VLE.permissions as permissions
import VLE.utils.generic_utils as utils
import VLE.factory as factory


class CommentView(viewsets.ViewSet):
    """Comment view.

    This class creates the following api paths:
    GET /comment/ -- gets all the comments of the specific entry
    POST /comment/ -- create a new comment
    GET /comment/<pk> -- gets a specific comment
    PATCH /comment/<pk> -- partially update an comment
    DEL /comment/<pk> -- delete an comment
    """

    def list(self, request):
        """Get the comments belonging to an entry.

        Arguments:
        request -- request data
            entry_id -- entry ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the course does not exist
            forbidden -- when its not their own journal, or the user is not allowed to grade that journal
        On succes:
            success -- with a list of the comments belonging to the entry

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            entry_id, = utils.required_params(request.query_params, "entry_id")
        except KeyError:
            return response.keyerror("entry_id")

        try:
            entry = Entry.objects.get(pk=entry_id)
        except Entry.DoesNotExist:
            return response.not_found('Entry does not exist.')

        if entry.node.journal.user != request.user and \
           not permissions.has_assignment_permission(
                request.user, entry.node.journal.assignment, 'can_view_assignment_journals'):
            return response.forbidden('You are not allowed to view journals of other participants.')

        if permissions.has_assignment_permission(request.user, entry.node.journal.assignment, 'can_grade'):
            comments = Comment.objects.filter(entry=entry)
        else:
            comments = Comment.objects.filter(entry=entry, published=True)

        serializer = CommentSerializer(comments, many=True)
        return response.success({'comments': serializer.data})

    def create(self, request):
        """Create a new comment.

        Arguments:
        request -- request data
            entry_id -- entry ID
            text -- comment text
            published -- publishment state

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            key_error -- missing keys
            not_found -- could not find the entry, author or assignment

        On success:
            succes -- with the assignment data

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            entry_id, text, published = utils.required_params(request.data, "entry_id", "text", "published")
        except KeyError:
            return response.keyerror("entry_id", "text", "published")

        try:
            entry = Entry.objects.get(pk=entry_id)
            journal = Journal.objects.get(node__entry=entry)
            assignment = Assignment.objects.get(journal=journal)
        except (Assignment.DoesNotExist, Journal.DoesNotExist, Entry.DoesNotExist):
            return response.not_found('Entry, journal or assignment does not exist.')

        if not permissions.has_assignment_permission(request.user, assignment, 'can_comment') or \
           not (permissions.has_assignment_permission(request.user, assignment, 'can_view_assignment_journals') or
                journal.user == request.user):
            return response.forbidden('You are not allowed to comment on this journal')

        published = published or not permissions.has_assignment_permission(request.user, assignment,
                                                                           'can_grade')

        comment = factory.make_comment(entry, request.user, text, published)
        return response.created({'comment': CommentSerializer(comment).data})

    def retrieve(self, request, pk=None):
        """Retrieve a comment.

        Arguments:
        request -- request data
        pk -- assignment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not_found -- could not find the course with the given id
            forbidden -- not allowed to retrieve assignments in this course

        On success:
            succes -- with the comment data

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return response.not_found('Comment does not exist.')

        if comment.entry.node.journal.user != request.user and \
           not permissions.has_assignment_permission(
                request.user, comment.entry.node.journal.assignment, 'can_view_assignment_journals'):
            return response.forbidden('You are not allowed to view journals of other participants.')

        serializer = CommentSerializer(comment)

        return response.success({'comment': serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """Update an existing comment.

        Arguments:
        request -- request data
            text -- comment text
        pk -- comment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            keyerror -- when comment_id or text is not set
            not found -- when the comment does not exist
            forbidden -- when the user is not allowed to comment
            unauthorized -- when the user is unauthorized to edit the assignment
        On success:
            success -- with the updated comment

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        comment_id = kwargs.get('pk')

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return response.not_found('Comment does not exist.')

        journal = comment.entry.node.journal

        if not permissions.has_assignment_permission(request.user, journal.assignment,
                                                     'can_comment'):
            return response.forbidden('You are not allowed to comment on this entry.')

        if not (comment.author.id == request.user.id or request.user.is_superuser):
            return response.forbidden('You are not allowed to edit this comment.')

        req_data = request.data
        req_data['last_edited'] = datetime.now()

        serializer = CommentSerializer(comment, data=req_data, partial=True)
        if not serializer.is_valid():
            response.bad_request()
        serializer.save()
        return response.success({'comment': serializer.data})

    def destroy(self, request, *args, **kwargs):
        """Delete an existing comment from an entry.

        Arguments:
        request -- request data
        pk -- comment ID

        Returns:
        On failure:
            unauthorized -- when the user is not logged in
            not found -- when the comment or author does not exist
            forbidden -- when the user cannot delete the assignment
        On success:
            success -- with a message that the comment was deleted

        """
        if not request.user.is_authenticated:
            return response.unauthorized()

        comment_id = kwargs.get('pk')

        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return response.not_found('Comment does not exist.')

        if not (request.user.is_superuser or request.user.id == comment.author.id):
            return response.forbidden(description='You are not allowed to delete this comment.')

        Comment.objects.get(id=comment_id).delete()
        return response.success(description='Successfully deleted comment.')
