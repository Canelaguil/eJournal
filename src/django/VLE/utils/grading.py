import VLE.lti_grade_passback as lti_grade
from VLE.models import Comment, Entry


def publish_all_assignment_grades(assignment, published):
    """Set published all not None grades from an assignment.

    - assignment: the assignment in question
    - published: either True or False. If True show the grade to student.
    """
    Entry.objects.filter(node__journal__assignment=assignment).exclude(grade=None).update(published=published)
    if published:
        Comment.objects.filter(entry__node__journal__assignment=assignment) \
                       .exclude(entry__grade=None).update(published=True)
        for journal in assignment.journal_set.all():
            if journal.sourcedid is not None and journal.grade_url is not None:
                lti_grade.replace_result(journal)


def publish_all_journal_grades(journal, published):
    """Set published all not None grades from a journal.

    - journal: the journal in question
    - published: either True or False. If True show the grade to student.
    """
    Entry.objects.filter(node__journal=journal).exclude(grade=None).update(published=published)
    if published:
        Comment.objects.filter(entry__node__journal=journal).exclude(entry__grade=None).update(published=True)
