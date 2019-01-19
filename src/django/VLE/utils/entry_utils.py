"""
Entry utilities.

A library with utilities related to entries.
"""
import VLE.timeline as timeline
from VLE import factory
from VLE.models import Field, Node
from VLE.utils import file_handling
from VLE.utils.error_handling import VLEBadRequest, VLEMissingRequiredField


def patch_entry_content(user, entry, old_content, field, data, assignment):
    """Creates new content for an entry, deleting the current content.

    If no temporary file is stored to replace the current content, the old content is kept as is."""
    if field.type in ['i', 'f', 'p']:
        new_file = file_handling.get_temp_user_file(user, assignment, data, content=old_content)

        if new_file:
            # As this get does not rely on user given data, no error should be needed.
            old_file = user.userfile_set.get(author=user, assignment=assignment, node=entry.node, entry=entry,
                                             content=old_content, file_name=old_content.data)
            old_file.delete()
            file_handling.make_permanent_file_content(new_file, old_content, entry.node)

    old_content.data = data
    old_content.save()


def get_node_index(journal, node, user):
    for i, result_node in enumerate(timeline.get_nodes(journal, user)):
        if result_node['nID'] == node.id:
            return i


def check_required_fields(template, content):
    required_fields = Field.objects.filter(template=template, required=True)
    received_ids = [field['id'] for field in content if field['data'] != '']
    for field in required_fields:
        if field.id not in received_ids:
            raise VLEMissingRequiredField(field)


def add_entry_to_node(node, template):
    if not (node.preset and node.preset.forced_template == template):
        raise VLEBadRequest('Invalid template for preset node.')

    if node.type != Node.ENTRYDEADLINE:
        raise VLEBadRequest('Passed node is not an EntryDeadline node.')

    if node.entry:
        raise VLEBadRequest('Passed node already contains an entry.')

    if node.preset.is_due():
        raise VLEBadRequest('The deadline has already passed.')

    return factory.make_entry(template)
