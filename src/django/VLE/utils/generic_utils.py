"""
Utilities.

A library with useful functions.
"""
import VLE.factory as factory
from VLE.models import Comment, Entry, Node, PresetNode, Template
from VLE.utils.error_handling import VLEMissingRequiredKey, VLEParamWrongType


# START: API-POST functions
def required_params(post, *keys):
    """Get required post parameters, throwing KeyError if not present."""
    if keys and not post:
        raise VLEMissingRequiredKey()

    result = []
    for key in keys:
        try:
            result.append(post[key])
        except KeyError as err:
            raise VLEMissingRequiredKey(err)

    return result


def optional_params(post, *keys):
    """Get optional post parameters, filling them as None if not present."""
    if keys and not post:
        raise VLEMissingRequiredKey()

    result = []
    for key in keys:
        if key in post:
            if post[key] == '':
                result.append(None)
            else:
                result.append(post[key])
        else:
            result.append(None)
    return result


def required_typed_params(post, *keys):
    if keys and not post:
        raise VLEMissingRequiredKey()

    result = []
    for func, key in keys:
        try:
            result.append(func(post[key]))
        except ValueError as err:
            raise VLEParamWrongType(err)
        except KeyError as err:
            raise VLEMissingRequiredKey(err)

    return result
# END: API-POST functions


# START: journal stat functions
def get_journal_entries(journal):
    """Get the journal entries from a journal.

    - journal: the journal in question.

    Returns a QuerySet of entries from a journal.
    """
    return Entry.objects.filter(node__journal=journal)


def get_points_possible(journal):
    """Get the maximum amount of points for an assignment."""
    return journal.assignment.points_possible


def get_acquired_points(entries):
    """Get the number of acquired points from a set of entries.

    - entries: the journal in question.

    Returns the total number of points depending on the grade type.
    """
    total_grade = 0
    for entry in entries:
        if entry.published:
            total_grade += entry.grade if entry.grade is not None else 0
    return total_grade


def get_submitted_count(entries):
    """Count the number of submitted entries.

    - entries: the entries to count with.

    Returns the submitted entry count.
    """
    return entries.count()


def get_graded_count(entries):
    """Count the number of graded entries.

    - entries: the entries to count with.

    Returns the graded entry count.
    """
    return entries.exclude(grade=None).count()


def get_published_count(entries):
    """Count the number of published entries.

    - entries: the entries to count with.

    Returns the published entry count.
    """
    return entries.filter(published=True).count()
# END journal stat functions


# START grading functions
def publish_all_assignment_grades(assignment, published):
    """Set published all not None grades from an assignment.

    - assignment: the assignment in question
    - published: either True or False. If True show the grade to student.
    """
    Entry.objects.filter(node__journal__assignment=assignment).exclude(grade=None).update(published=published)
    if published:
        (Comment.objects.filter(entry__node__journal__assignment=assignment)
         .exclude(entry__grade=None).update(published=True))


def publish_all_journal_grades(journal, published):
    """Set published all not None grades from a journal.

    - journal: the journal in question
    - published: either True or False. If True show the grade to student.
    """
    Entry.objects.filter(node__journal=journal).exclude(grade=None).update(published=published)
    if published:
        Comment.objects.filter(entry__node__journal=journal).exclude(entry__grade=None).update(published=True)
# END grading functions


def update_templates(result_list, templates, template_map):
    """Create new templates for those which have changed, and removes the old one.

    Entries have to keep their original template, so that the content
    does not change after a template update, therefore when a template
    is updated, the template is recreated from scratch and bound to
    all nodes that use the previous template, if there were any.
    """
    for template_field in templates:
        if 'updated' in template_field and template_field['updated']:
            # Create the new template and add it to the format.
            if 'id' in template_field and template_field['id'] < 0 and template_field['id'] in template_map:
                new_template = template_map[template_field['id']]
            else:
                new_template = parse_template(template_field)

            result_list.add(new_template)

            # Update presets to use the new template.
            if 'id' in template_field and template_field['id'] > 0:
                template = Template.objects.get(pk=template_field['id'])
                presets = PresetNode.objects.filter(forced_template=template).all()
                for preset in presets:
                    preset.forced_template = new_template
                    preset.save()

                result_list.remove(template)


def parse_template(template_dict):
    """Parse a new template according to the passed JSON-serialized template."""
    name = template_dict['name']
    fields = template_dict['field_set']

    template = factory.make_entry_template(name)

    for field in fields:
        type = field['type']
        title = field['title']
        location = field['location']
        required = field['required']
        description = field['description']

        factory.make_field(template, title, location, type, required, description)

    template.save()
    return template


def swap_templates(from_list, goal_list, target_list):
    """Swap templates from from_list to target_list if they are present in goal_list."""
    for template in goal_list:
        if from_list.filter(pk=template['id']).count() > 0:
            template = from_list.get(pk=template['id'])
            from_list.remove(template)
            target_list.add(template)


def update_journals(journals, preset, created):
    """Create or update the preset node in all relevant journals.

    Arguments:
    journals -- the journals to update.
    preset -- the preset node to update the journals with.
    created -- whether the preset node was newly created.
    """
    if created:
        for journal in journals:
            factory.make_node(journal, None, preset.type, preset)
    else:
        for journal in journals:
            journal.node_set.filter(preset=preset).update(type=preset.type)


def update_presets(assignment, presets, template_map):
    """Update preset nodes in the assignment according to the passed list.

    Arguments:
    assignment -- the assignment to update the presets in.
    presets -- a list of JSON-serialized presets.
    """
    format = assignment.format
    for preset in presets:
        exists = 'id' in preset
        id, type, description, deadline, target, template = \
            optional_params(preset, 'id', 'type', 'description', 'deadline', 'target', 'template')

        if exists:
            preset_node = PresetNode.objects.get(pk=preset['id'])
        else:
            preset_node = PresetNode(format=format)

        type_changed = preset_node.type != type
        preset_node.description = description
        preset_node.type = type
        preset_node.deadline = deadline

        if preset_node.type == Node.PROGRESS:
            preset_node.target = target
        elif preset_node.type == Node.ENTRYDEADLINE:
            template_field = template

            if 'id' in template_field:
                if template_field['id'] > 0:
                    preset_node.forced_template = Template.objects.get(pk=template_field['id'])
                else:
                    if template_field['id'] in template_map:
                        preset_node.forced_template = template_map[template_field['id']]
                    else:
                        preset_node.forced_template = parse_template(template_field)
                        template_map[template_field['id']] = preset_node.forced_template
            else:
                preset_node.forced_template = parse_template(template_field)

        preset_node.save()
        if type_changed:
            update_journals(assignment.journal_set.all(), preset_node, not exists)


def delete_presets(presets, remove_presets):
    """Deletes all presets in remove_presets from presets. """
    ids = []
    for preset in remove_presets:
        ids.append(preset['id'])

    presets.filter(pk__in=ids).delete()


def delete_templates(templates, remove_templates):
    """Deletes all templates in remove_templates from templates. """
    ids = []
    remove_ids = []
    for template in remove_templates:
        if Entry.objects.filter(id=template['id']).count() == 0:
            remove_ids.append(template['id'])
        ids.append(template['id'])

    templates.filter(pk__in=remove_ids).delete()
    templates.set(templates.exclude(pk__in=ids))
