"""
timeline.py.

Useful timeline functions.
"""
from django.db.models import Case, When
from django.utils import timezone

from VLE.models import Node
from VLE.serializers import EntrySerializer, TemplateSerializer


def get_sorted_nodes(journal):
    """Get sorted nodes.

    Get all the nodes of a journal in sorted order.
    Order is default by deadline.
    """
    return journal.node_set.annotate(
        sort_deadline=Case(
            When(type=Node.ENTRY, then='entry__creation_date'),
            default='preset__deadline')
    ).order_by('sort_deadline')


def get_nodes(journal, user=None):
    """Convert a journal to a list of node dictionaries.

    First sorts the nodes on date, then attempts to add an
    add-node if the user can add to the journal, the subsequent
    progress node is in the future and maximally one.
    """
    can_add = user and journal.user == user and user.has_permission('can_have_journal', journal.assignment)

    node_list = []
    for node in get_sorted_nodes(journal):
        # If there is a progress node upcoming, and there are stackable entries before the deadline
        # add an ADDNODE
        if node.type == Node.PROGRESS:
            is_future = (node.preset.deadline - timezone.now()).total_seconds() > 0
            if can_add and is_future:
                add_node = get_add_node(journal)
                if add_node:
                    node_list.append(add_node)
                can_add = False

        if node.type == Node.ENTRY:
            node_list.append(get_entry_node(node, user))
        elif node.type == Node.ENTRYDEADLINE:
            node_list.append(get_deadline(node, user))
        elif node.type == Node.PROGRESS:
            node_list.append(get_progress(node))

    if can_add and not journal.assignment.is_due():
        add_node = get_add_node(journal)
        if add_node:
            node_list.append(add_node)

    return node_list


# TODO: Make serializers for these functions as well (if possible)
def get_add_node(journal):
    """Convert a add_node to a dictionary."""
    if not journal or journal.assignment.format.available_templates.count() == 0:
        return None
    return {
        'type': Node.ADDNODE,
        'nID': -1,
        'templates': TemplateSerializer(journal.assignment.format.available_templates.all(), many=True).data
    }


def get_entry_node(node, user):
    return {
        'type': node.type,
        'nID': node.id,
        'jID': node.journal.id,
        'entry': EntrySerializer(node.entry, context={'user': user}).data if node.entry else None,
    } if node else None


def get_deadline(node, user):
    """Convert entrydeadline to a dictionary."""
    return {
        'description': node.preset.description,
        'type': node.type,
        'nID': node.id,
        'jID': node.journal.id,
        'deadline': node.preset.deadline,
        'template': TemplateSerializer(node.preset.forced_template).data,
        'entry': EntrySerializer(node.entry, context={'user': user}).data if node.entry else None,
    } if node else None


def get_progress(node):
    """Convert progress node to dictionary."""
    return {
        'description': node.preset.description,
        'type': node.type,
        'nID': node.id,
        'jID': node.journal.id,
        'deadline': node.preset.deadline,
        'target': node.preset.target,
    } if node else None
