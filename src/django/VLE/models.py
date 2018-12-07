"""
models.py.

Database file
"""
import os

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now

import VLE.permissions as permissions
from VLE.utils import sanitization
from VLE.utils.error_handling import (VLEParticipationError,
                                      VLEPermissionError, VLEProgrammingError,
                                      VLEUnverifiedEmailError)
from VLE.utils.file_handling import get_path


class Instance(models.Model):
    """Global settings for the running instance."""
    allow_standalone_registration = models.BooleanField(
        default=True
    )
    name = models.TextField(
        default='eJournal'
    )

    def to_string(self, user=None):
        return self.name


class UserFile(models.Model):
    """UserFile.

    UserFile is a file uploaded by the user stored in MEDIA_ROOT/uID/aID/<file>
    - author: The user who uploaded the file.
    - file_name: The name of the file (no parts of the path to the file included).
    - creation_date: The time and date the file was uploaded.
    - content_type: The mimetype supplied by the user (unvalidated).
    - assignment: The assignment that the UserFile is linked to.
    - node: The node that the UserFile is linked to.
    - entry: The entry that the UserFile is linked to.
    - content: The content that UserFile is linked to.

    Note that deleting the assignment, node or content will also delete the UserFile.
    UserFiles uploaded initially have no node or content set, and are considered temporary untill the journal post
    is made and the corresponding node and content are set.
    """
    file = models.FileField(
        null=False,
        upload_to=get_path
    )
    file_name = models.TextField(
        null=False
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=False
    )
    content_type = models.TextField(
        null=False
    )
    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
        null=False
    )
    node = models.ForeignKey(
        'Node',
        on_delete=models.CASCADE,
        null=True
    )
    entry = models.ForeignKey(
        'Entry',
        on_delete=models.CASCADE,
        null=True
    )
    content = models.ForeignKey(
        'Content',
        on_delete=models.CASCADE,
        null=True
    )
    creation_date = models.DateTimeField(editable=False)
    last_edited = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.creation_date = timezone.now()
        self.last_edited = timezone.now()

        return super(UserFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(UserFile, self).delete(*args, **kwargs)

    def to_string(self, user=None):
        return "UserFile"


@receiver(models.signals.post_delete, sender=UserFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `UserFile` object is deleted."""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class User(AbstractUser):
    """User.

    User is an entity in the database with the following features:
    - full_name: full name of the user
    - email: email of the user.
    - verified_email: Boolean to indicate if the user has validated their email adress.
    - USERNAME_FIELD: username of the username.
    - password: the hash of the password of the user.
    - lti_id: the DLO id of the user.
    """

    full_name = models.CharField(
        null=True,
        max_length=50
    )
    email = models.EmailField(
        unique=True,
    )
    verified_email = models.BooleanField(
        default=False
    )
    lti_id = models.TextField(
        null=True,
        unique=True,
        blank=True,
    )
    profile_picture = models.TextField(
        null=True
    )
    is_teacher = models.BooleanField(default=False)
    grade_notifications = models.BooleanField(
        default=True
    )
    comment_notifications = models.BooleanField(
        default=False
    )

    def check_permission(self, permission, obj=None, message=None):
        """
        Throws a VLEPermissionError when the user does not have the specified permission, as defined by
        has_permission.
        """
        if not self.has_permission(permission, obj):
            raise VLEPermissionError(permission, message)

    def has_permission(self, permission, obj=None):
        """
        Returns whether the user has the given permission.
        If obj is None, it tests the general permissions.
        If obj is a Course, it tests the course permissions.
        If obj is an Assignment, it tests the assignment permissions.
        Raises a VLEProgramming error when misused.
        """
        if obj is None:
            return permissions.has_general_permission(self, permission)
        if isinstance(obj, Course):
            return permissions.has_course_permission(self, permission, obj)
        if isinstance(obj, Assignment):
            return permissions.has_assignment_permission(self, permission, obj)
        raise VLEProgrammingError("Permission object must be of type None, Course or Assignment.")

    def check_participation(self, obj):
        if not self.is_participant(obj):
            raise VLEParticipationError(obj, self)

    def check_verified_email(self):
        if not self.verified_email:
            raise VLEUnverifiedEmailError()

    def is_participant(self, obj):
        if isinstance(obj, Course):
            return Course.objects.filter(pk=obj.pk, users=self).exists()
        if isinstance(obj, Assignment):
            return Assignment.objects.filter(pk=obj.pk, courses__users=self).exists()
        raise VLEProgrammingError("Participant object must be of type Course or Assignment.")

    def check_can_view(self, obj):
        if not self.can_view(obj):
            raise VLEPermissionError(message='You are not allowed to view {}'.format(str(obj)))

    def can_view(self, obj):
        if isinstance(obj, Journal):
            if obj.user != self:
                return self.has_permission('can_view_all_journals', obj.assignment)
            else:
                return self.has_permission('can_have_journal', obj.assignment)
        elif isinstance(obj, Assignment):
            if self.is_participant(obj):
                return obj.is_published or self.has_permission('can_view_unpublished_assignment', obj)
            else:
                return False

    def to_string(self, user=None):
        if user is None:
            return "User"
        if not (self.is_superuser or self == user or permissions.is_user_supervisor_of(user, self)):
            return "User"
        return self.username + " (" + str(self.pk) + ")"


class Course(models.Model):
    """Course.

    A Course entity has the following features:
    - name: name of the course.
    - author: the creator of the course.
    - abbrevation: a max three letter abbrevation of the course name.
    - startdate: the date that the course starts.
    - lti_ids: the ids of the course linked over LTI.
    """

    name = models.TextField()
    abbreviation = models.TextField(
        max_length=10,
        default='XXXX',
    )

    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )

    users = models.ManyToManyField(
        'User',
        related_name='participations',
        through='Participation',
        through_fields=('course', 'user'),
    )

    startdate = models.DateField(
        null=True,
    )
    enddate = models.DateField(
        null=True,
    )

    def to_string(self, user=None):
        if user is None:
            return "Course"
        if not user.can_view(self):
            return "Course"

        return self.name + " (" + str(self.pk) + ")"


class Group(models.Model):
    """Group.

    A Group entity has the following features:
    - name: the name of the group
    - course: the course where the group belongs to
    """
    name = models.TextField()

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    lti_id = models.TextField(
        null=True,
        unique=False,
    )

    class Meta:
        """Meta data for the model: unique_together."""
        unique_together = ('name', 'course')

    def to_string(self, user=None):
        if user is None:
            return "Group"
        if not user.can_view(self.course):
            return "Group"
        return self.name + " (" + str(self.pk) + ")"


class Role(models.Model):
    """Role.

    A complete overview of the role requirements can be found here:
    https://docs.google.com/spreadsheets/d/1M7KnEKL3cG9PMWfQi9HIpRJ5xUMou4Y2plnRgke--Tk

    A role defines the permissions of a user group within a course.
    - name: name of the role
    - list of permissions (can_...)
    """
    name = models.TextField()

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    can_edit_course_details = models.BooleanField(default=False)
    can_delete_course = models.BooleanField(default=False)
    can_edit_course_roles = models.BooleanField(default=False)
    can_view_course_users = models.BooleanField(default=False)
    can_add_course_users = models.BooleanField(default=False)
    can_delete_course_users = models.BooleanField(default=False)
    can_add_course_user_group = models.BooleanField(default=False)
    can_delete_course_user_group = models.BooleanField(default=False)
    can_edit_course_user_group = models.BooleanField(default=False)
    can_add_assignment = models.BooleanField(default=False)
    can_delete_assignment = models.BooleanField(default=False)

    can_edit_assignment = models.BooleanField(default=False)
    can_view_all_journals = models.BooleanField(default=False)
    can_grade = models.BooleanField(default=False)
    can_publish_grades = models.BooleanField(default=False)
    can_have_journal = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=False)
    can_view_unpublished_assignment = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.can_add_course_users and not self.can_view_course_users:
            raise ValidationError('A user needs to view course users in order to add them.')

        if self.can_delete_course_users and not self.can_view_course_users:
            raise ValidationError('A user needs to view course users in order to remove them.')

        if self.can_edit_course_user_group and not self.can_view_course_users:
            raise ValidationError('A user needs to view course users in order to manage user groups.')

        if self.can_view_all_journals and self.can_have_journal:
            raise ValidationError('An administrative user is not allowed to have a journal in the same course.')

        if self.can_grade and not self.can_view_all_journals:
            raise ValidationError('A user needs to be able to view journals in order to grade them.')

        if self.can_publish_grades and not (self.can_view_all_journals and self.can_grade):
            raise ValidationError('A user should not be able to publish grades without being able to view or grade \
                                  the journals.')

        if self.can_comment and not (self.can_view_all_journals or self.can_have_journal):
            raise ValidationError('A user requires a journal to comment on.')

        super(Role, self).save(*args, **kwargs)

    def to_string(self, user=None):
        if user is None:
            return "Role"
        if not user.can_view(self.course):
            return "Role"

        return self.name + " (" + str(self.pk) + ")"

    class Meta:
        """Meta data for the model: unique_together."""

        unique_together = ('name', 'course',)


class Participation(models.Model):
    """Participation.

    A participation defines the way a user interacts within a certain course.
    The user is now linked to the course, and has a set of permissions
    associated with its role.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role',
    )
    group = models.ForeignKey(
        Group,
        null=True,
        on_delete=models.CASCADE,
        default=None,
    )

    class Meta:
        """Meta data for the model: unique_together."""

        unique_together = ('user', 'course',)

    def to_string(self, user=None):
        if user is None:
            return "Participation"
        if not user.can_view(self.course):
            return "Participation"

        return "user: {}, course: {}, role: {}".format(
            self.user.to_string(user), self.course.to_string(user), self.role.to_string(user))


class Assignment(models.Model):
    """Assignment.

    An Assignment entity has the following features:
    - name: name of the assignment.
    - description: description for the assignment.
    - courses: a foreign key linked to the courses this assignment
    is part of.
    - format: a one-to-one key linked to the format this assignment
    holds. The format determines how a students' journal is structured.
    - lti_ids: The lti ids of the assignment linked over lti.
    """

    name = models.TextField()
    description = models.TextField(
        null=True,
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    is_published = models.BooleanField(default=False)
    points_possible = models.IntegerField(
        'points_possible',
        default=10
    )
    unlock_date = models.DateTimeField(
        'unlock_date',
        null=True,
        blank=True
    )
    due_date = models.DateTimeField(
        'due_date',
        null=True,
        blank=True
    )
    lock_date = models.DateTimeField(
        'lock_date',
        null=True,
        blank=True
    )
    courses = models.ManyToManyField(Course)

    format = models.OneToOneField(
        'Format',
        on_delete=models.CASCADE
    )

    def is_locked(self):
        return self.unlock_date and self.unlock_date > now() or self.lock_date and self.lock_date < now()

    def is_due(self):
        return self.due_date and self.due_date < now()

    def save(self, *args, **kwargs):
        self.description = sanitization.strip_script_tags(self.description)

        return super(Assignment, self).save(*args, **kwargs)

    def to_string(self, user=None):
        if user is None:
            return "Assignment"
        if not user.can_view(self):
            return "Assignment"

        return self.name + " (" + str(self.pk) + ")"


class Journal(models.Model):
    """Journal.

    A journal is a collection of Nodes that holds the student's
    entries, deadlines and more. It contains the following:
    - assignment: a foreign key linked to an assignment.
    - user: a foreign key linked to a user.
    """

    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )

    sourcedid = models.TextField(
        'sourcedid',
        null=True
    )

    grade_url = models.TextField(
        'grade_url',
        null=True
    )

    def to_string(self, user=None):
        if user is None:
            return "Journal"
        if not user.can_view(self):
            return "Journal"

        return "the {0} journal of {1}".format(self.assignment.name, self.user.username)

    class Meta:
        """A class for meta data.

        - unique_together: assignment and user must be unique together.
        """

        unique_together = ('assignment', 'user',)


class Node(models.Model):
    """Node.

    The Node is an Timeline component.
    It can represent many things.
    There are three types of nodes:
    -Progress
        A node that merely is a deadline,
        and contains no entry. This deadline
        contains a 'target point amount'
        which should be reached before the
        deadline has passed.
        This type of node has to be predefined in
        the Format. In the Format it is assigned a
        deadline and a 'target point amount'.
    -Entry
        A node that is merely an entry,
        and contains no deadline. The entry
        can count toward a total
        'received point amount' which is deadlined
        by one or more Progress nodes.
        This type node can be created by the student
        an unlimited amount of times. It holds one
        of the by format predefined 'global templates'.
    -Entrydeadline
        A node that is both an entry and a deadline.
        This node is entirely separate from the
        Progress and Entry node.
        This type of node has to be predefined in
        the Format. In the Format it is assigned a
        deadline and a 'forced template'.
    """

    PROGRESS = 'p'
    ENTRY = 'e'
    ENTRYDEADLINE = 'd'
    ADDNODE = 'a'
    TYPES = (
        (PROGRESS, 'progress'),
        (ENTRY, 'entry'),
        (ENTRYDEADLINE, 'entrydeadline'),
    )

    type = models.TextField(
        max_length=4,
        choices=TYPES,
    )

    entry = models.OneToOneField(
        'Entry',
        null=True,
        on_delete=models.SET_NULL,
    )

    journal = models.ForeignKey(
        'Journal',
        on_delete=models.CASCADE,
    )

    preset = models.ForeignKey(
        'PresetNode',
        null=True,
        on_delete=models.CASCADE,
    )

    def to_string(self, user=None):
        return "Node"


class Format(models.Model):
    """Format.

    Format of a journal.
    The format determines how a students' journal is structured.
    See PresetNodes for attached 'default' nodes.
    - available_templates are those available in 'Entry' nodes.
      'Entrydeadline' nodes hold their own forced template.
    """

    PERCENTAGE = 'PE'
    GRADE = 'GR'
    TYPES = (
        (PERCENTAGE, 'percentage'),
        (GRADE, 'from 0 to 10'),
    )
    grade_type = models.TextField(
        max_length=2,
        choices=TYPES,
        default=PERCENTAGE,
    )
    unused_templates = models.ManyToManyField(
        'Template',
        related_name='unused_templates',
    )

    available_templates = models.ManyToManyField(
        'Template',
        related_name='available_templates',
    )

    def to_string(self, user=None):
        return "Format"


class PresetNode(models.Model):
    """PresetNode.

    A preset node is a node that has been pre-defined by the teacher.
    It contains the following features:
    - description: user defined text description of the preset node.
    - type: the type of the preset node (progress or entrydeadline node).
    - deadline: the deadline for this preset node.
    - forced_template: the template for this preset node - null if PROGRESS node.
    - format: a foreign key linked to a format.
    """

    TYPES = (
        (Node.PROGRESS, 'progress'),
        (Node.ENTRYDEADLINE, 'entrydeadline'),
    )

    description = models.TextField(
        null=True,
    )

    type = models.TextField(
        max_length=4,
        choices=TYPES,
    )

    target = models.IntegerField(
        null=True,
    )

    deadline = models.DateTimeField()

    forced_template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
    )

    format = models.ForeignKey(
        'Format',
        on_delete=models.CASCADE
    )

    def is_due(self):
        return self.deadline < now() or self.format.assignment.is_due()

    def to_string(self, user=None):
        return "PresetNode"


class Entry(models.Model):
    """Entry.

    An Entry has the following features:
    - journal: a foreign key linked to an Journal.
    - creation_date: the date and time when the entry was posted.
    - grade: grade the entry has
    - published: if its a published grade or not
    - last_edited: when the etry was last edited
    """
    NEED_SUBMISSION = 'Submission need to be send to VLE'
    SEND_SUBMISSION = 'Submission is successfully recieved by VLE'
    GRADING = 'Grade need to be send to VLE'
    LINK_COMPLETE = 'Everything is send to VLE'
    TYPES = (
        (NEED_SUBMISSION, 'entry_submission'),
        (SEND_SUBMISSION, 'entry_submitted'),
        (GRADING, 'grade_submission'),
        (LINK_COMPLETE, 'done'),
    )

    # TODO Should not be nullable
    template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        null=True,
    )
    grade = models.FloatField(
        default=None,
        null=True,
    )
    published = models.BooleanField(
        default=False
    )
    creation_date = models.DateTimeField(editable=False)
    last_edited = models.DateTimeField()

    vle_coupling = models.TextField(
        default=NEED_SUBMISSION,
        choices=TYPES,
    )

    def is_due(self):
        return (self.node.preset and self.node.preset.is_due()) or self.node.journal.assignment.is_due()

    def save(self, *args, **kwargs):
        if not self.pk:
            now = timezone.now()
            self.creation_date = now
            self.last_edited = now

        return super(Entry, self).save(*args, **kwargs)

    def to_string(self, user=None):
        return "Entry"


class Counter(models.Model):
    """Counter.

    A single counter class which can be used to keep track of incremental values
    which do not belong to another object like the message ID for LTI messages.
    """

    name = models.TextField(
        null=False
    )
    count = models.IntegerField(
        default=0
    )

    def to_string(self, user=None):
        return self.name + " is on " + self.count


class Template(models.Model):
    """Template.

    A template for an Entry.
    """

    name = models.TextField()
    max_grade = models.IntegerField(
        default=1,
    )

    def to_string(self, user=None):
        return "Template"


class Field(models.Model):
    """Field.

    Defines the fields of an Template
    """

    TEXT = 't'
    RICH_TEXT = 'rt'
    IMG = 'i'
    FILE = 'f'
    VIDEO = 'v'
    PDF = 'p'
    URL = 'u'
    DATE = 'd'
    SELECTION = 's'
    TYPES = (
        (TEXT, 'text'),
        (RICH_TEXT, 'rich text'),
        (IMG, 'img'),
        (PDF, 'pdf'),
        (FILE, 'file'),
        (VIDEO, 'vid'),
        (URL, 'url'),
        (DATE, 'date'),
        (SELECTION, 'selection')
    )
    type = models.TextField(
        max_length=4,
        choices=TYPES,
        default=TEXT,
    )
    title = models.TextField()
    description = models.TextField(
        null=True
    )
    options = models.TextField(
        null=True
    )
    location = models.IntegerField()
    template = models.ForeignKey(
        'Template',
        on_delete=models.CASCADE
    )
    required = models.BooleanField()

    def to_string(self, user=None):
        return "Field"


class Content(models.Model):
    """Content.

    Defines the content of an Entry
    """

    entry = models.ForeignKey(
        'Entry',
        on_delete=models.CASCADE
    )
    field = models.ForeignKey(
        'Field',
        on_delete=models.SET_NULL,
        null=True
    )
    data = models.TextField(
        null=True
    )

    def save(self, *args, **kwargs):
        self.data = sanitization.strip_script_tags(self.data)

        return super(Content, self).save(*args, **kwargs)

    def to_string(self, user=None):
        return "Content"


class Comment(models.Model):
    """Comment.

    Comments contain the comments given to the entries.
    It is linked to a single entry with a single author and the comment text.
    """

    entry = models.ForeignKey(
        'Entry',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True
    )
    text = models.TextField()
    published = models.BooleanField(
        default=True
    )
    creation_date = models.DateTimeField(editable=False)
    last_edited = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.creation_date = timezone.now()
        self.last_edited = timezone.now()
        self.text = sanitization.strip_script_tags(self.text)
        return super(Comment, self).save(*args, **kwargs)

    def to_string(self, user=None):
        return "Comment"


class Lti_ids(models.Model):
    """Lti ids

    Contains the lti ids for course and assignments as one course/assignment
    on our site needs to be able to link to multiple course/assignment in the
    linked VLE.
    """
    ASSIGNMENT = 'Assignment'
    COURSE = 'Course'
    TYPES = ((ASSIGNMENT, 'Assignment'), (COURSE, 'Course'))

    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
        null=True
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        null=True
    )

    lti_id = models.TextField()
    for_model = models.TextField(
        choices=TYPES
    )

    def to_string(self, user=None):
        return "Lti_ids"

    class Meta:
        """A class for meta data.

        - unique_together: assignment and user must be unique together.
        """

        unique_together = ('lti_id', 'for_model',)
