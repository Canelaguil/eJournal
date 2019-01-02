"""
Serializers.

Functions to convert certain data to other formats.
"""
from django.db.models import Min, Q, Sum
from django.utils import timezone
from rest_framework import serializers

import VLE.permissions as permissions
from VLE.models import (Assignment, Comment, Content, Course, Entry, Field,
                        Format, Group, Instance, Journal, Lti_ids, Node,
                        Participation, PresetNode, Role, Template, User)


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = ('allow_standalone_registration', 'name')


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'name', 'profile_picture', 'is_teacher', 'lti_id', 'id',
                  'role', 'group')
        read_only_fields = ('id', 'lti_id', 'is_teacher', 'username')

    def get_name(self, user):
        return user.first_name + ' ' + user.last_name

    def get_role(self, user):
        if 'course' not in self.context or not self.context['course']:
            return None

        role = Participation.objects.get(user=user, course=self.context['course']).role

        if role:
            return role.name
        else:
            return None

    def get_group(self, user):
        if 'course' not in self.context or not self.context['course']:
            return None
        try:
            group = Participation.objects.get(user=user, course=self.context['course']).group
        except Participation.DoesNotExist:
            return None

        if group:
            return group.name
        else:
            return None


class OwnUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'permissions',
                  'name', 'lti_id', 'profile_picture', 'is_teacher', 'grade_notifications', 'comment_notifications',
                  'verified_email')
        read_only_fields = ('id', 'permissions', 'lti_id', 'is_teacher', 'verified_email', 'username')

    def get_name(self, user):
        return user.first_name + ' ' + user.last_name

    def get_permissions(self, user):
        """Returns a dictionary with all user permissions.

        Arguments:
        user -- The user whose permissions are requested.

        Returns {all_permission:
            course{id}: permisions
            assignment{id}: permissions
            general: permissions
        }"""
        perms = {}
        courses = user.participations.all()

        perms['general'] = permissions.serialize_general_permissions(user)

        for course in courses:
            perms['course' + str(course.id)] = permissions.serialize_course_permissions(user, course)

        assignments = set()
        for course in courses:
            for assignment in course.assignment_set.all():
                if user.has_permission('can_grade', assignment) or user.has_permission('can_have_journal', assignment):
                    assignments.add(assignment)

        for assignment in assignments:
            perms['assignment' + str(assignment.id)] = permissions.serialize_assignment_permissions(user, assignment)

        return perms


class CourseSerializer(serializers.ModelSerializer):
    lti_linked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        exclude = ('author', 'users', )
        read_only_fields = ('id', )
        depth = 1

    def get_lti_linked(self, course):
        return Lti_ids.objects.filter(course=course.pk).exists()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('id', 'course', 'lti_id')


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = '__all__'
        read_only_fields = ('id', )
        depth = 1


class AssignmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('id', 'name', 'description', 'points_possible', 'unlock_date', 'due_date', 'lock_date',
                  'is_published')
        read_only_fields = ('id', )


class AssignmentSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    journal = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    journals = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ('id', )

    def get_deadline(self, assignment):
        # Student deadlines
        if 'user' in self.context and self.context['user'] and \
           self.context['user'].has_permission('can_have_journal', assignment):
            journal = Journal.objects.get(assignment=assignment, user=self.context['user'])
            nodes = journal.node_set.order_by('preset__deadline')
            if not nodes:
                return None

            deadline = self._get_student_deadline(nodes)
            if deadline:
                return deadline
            elif journal.assignment.lock_date and journal.assignment.lock_date < timezone.now():
                return journal.assignment.due_date
            else:
                return None

        # Teacher deadline
        else:
            return self._get_teacher_deadline(assignment)

    def _get_teacher_deadline(self, assignment):
        return assignment.journal_set \
            .filter(
                Q(node__entry__grade__isnull=True) | Q(node__entry__published=False),
                node__entry__isnull=False) \
            .values('node__entry__last_edited') \
            .aggregate(Min('node__entry__last_edited'))['node__entry__last_edited__min']

    def _get_student_deadline(self, nodes):
        """Get student deadline.

        This function gets the first upcoming deadline.
        It checks for the first entrydeadline that still need to submitted and still can be, or for the first
        progressnode that is not yet fullfilled.
        """
        t_grade = 0
        deadline = None
        for node in nodes:
            # Sum published grades to check if PROGRESS node is fullfiled
            if node.type in ['e', 'd'] and node.entry and node.entry.grade:
                if node.entry.published:
                    t_grade += node.entry.grade
            # Set the deadline to the first ENTRYDEADLINE node date
            elif node.type == 'd' and not node.entry and node.preset.deadline > timezone.now():
                deadline = node.preset.deadline
                break
            # Set the deadline to first not fullfilled PROGRESS node date
            elif node.type == 'p':
                if node.preset.target > t_grade:
                    deadline = node.preset.deadline
                    break

        return deadline

    def get_journal(self, assignment):
        if not ('user' in self.context and self.context['user']):
            return None
        if not self.context['user'].has_permission('can_have_journal', assignment):
            return None
        return Journal.objects.get(assignment=assignment, user=self.context['user']).pk

    def get_journals(self, assignment):
        """Retrieves the journals of an assignment of the users who have the permission
        to own a journal.
        """
        if 'journals' in self.context and 'course' in self.context \
           and self.context['journals'] and self.context['course']:
            course = self.context['course']
            users = course.participation_set.filter(role__can_have_journal=True).values('user')
            journals = Journal.objects.filter(assignment=assignment, user__in=users)
            return JournalSerializer(journals, many=True, context=self.context).data
        else:
            return None

    def get_stats(self, assignment):
        if 'user' not in self.context or not self.context['user']:
            return None

        # Get the stats from only the course that its linked to, when no courses are supplied.
        if 'course' in self.context and self.context['course']:
            users = User.objects.filter(
                participation__course=self.context['course'], participation__role__can_have_journal=True
            )
        else:
            users = User.objects.filter(
                participation__course__in=assignment.courses.all(), participation__role__can_have_journal=True
            ).distinct()

        stats = {}
        journal_set = assignment.journal_set.filter(user__in=users)
        # Grader stats
        if self.context['user'].has_permission('can_grade', assignment):
            stats['needs_marking'] = journal_set \
                .filter(node__entry__isnull=False, node__entry__grade__isnull=True).count()
            stats['unpublished'] = journal_set \
                .filter(node__entry__isnull=False, node__entry__published=False, node__entry__grade__isnull=False)\
                .count()
        # Other stats
        stats['average_points'] = journal_set \
            .filter(node__entry__grade__isnull=False, node__entry__published=True) \
            .values('node__entry__grade') \
            .aggregate(Sum('node__entry__grade'))['node__entry__grade__sum']
        if stats['average_points']:
            stats['average_points'] /= journal_set.filter(user__in=users).count()

        return stats

    def get_course(self, assignment):
        if 'course' not in self.context or not self.context['course']:
            return None
        if not self.context['course'] in assignment.courses.all():
            return None
        return CourseSerializer(self.context['course']).data

    def get_courses(self, assignment):
        if 'course' in self.context and self.context['course']:
            return None
        return CourseSerializer(assignment.courses, many=True).data


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'
        read_only_fields = ('id', )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'entry', 'author', 'timestamp')

    def get_author(self, comment):
        return UserSerializer(comment.author).data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('id', 'course')


class JournalSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = Journal
        fields = '__all__'
        read_only_fields = ('id', 'assignment', 'user', 'grade_url', 'sourcedid')

    def get_student(self, journal):
        return UserSerializer(journal.user, context=self.context).data

    def get_stats(self, journal):
        return {
            'acquired_points': journal.node_set.filter(entry__published=True)
            .values('entry__grade').aggregate(Sum('entry__grade'))['entry__grade__sum'],
            'graded': journal.node_set.filter(entry__published=True, entry__grade__isnull=False).count(),
            'published': journal.node_set.filter(entry__published=True).count(),
            'submitted': journal.node_set.filter(entry__isnull=False).count(),
            'total_points': journal.assignment.points_possible,
        }


class FormatSerializer(serializers.ModelSerializer):
    unused_templates = serializers.SerializerMethodField()
    templates = serializers.SerializerMethodField(source='available_templates')
    presets = serializers.SerializerMethodField()

    class Meta:
        model = Format
        fields = ('id', 'grade_type', 'unused_templates', 'templates', 'presets')
        read_only_fields = ('id', )

    def get_unused_templates(self, entry):
        return TemplateSerializer(entry.unused_templates.all(), many=True).data

    def get_templates(self, entry):
        return TemplateSerializer(entry.available_templates.all(), many=True).data

    def get_presets(self, entry):
        return PresetNodeSerializer(entry.presetnode_set.all().order_by('deadline'), many=True).data


class PresetNodeSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()

    class Meta:
        model = PresetNode
        fields = ('id', 'description', 'type', 'deadline', 'target', 'template')
        read_only_fields = ('id', )

    def get_deadline(self, entry):
        return entry.deadline.strftime('%Y-%m-%d %H:%M')

    def get_target(self, entry):
        if entry.type == Node.PROGRESS:
            return entry.target
        return None

    def get_template(self, entry):
        if entry.type == Node.ENTRYDEADLINE:
            return TemplateSerializer(entry.forced_template).data
        return None


class EntrySerializer(serializers.ModelSerializer):
    template = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = ('id', 'creation_date', 'published', 'template', 'content',
                  'editable', 'grade', 'last_edited', 'comments')
        read_only_fields = ('id', 'template', 'creation_date', 'content', 'published')

    def get_template(self, entry):
        return TemplateSerializer(entry.template).data

    def get_content(self, entry):
        return ContentSerializer(entry.content_set.all(), many=True).data

    def get_editable(self, entry):
        return entry.grade is None

    def get_grade(self, entry):
        # TODO: Add permission can_view_grade
        if 'user' not in self.context:
            return None
        if entry.published or self.context['user'].has_permission('can_grade', entry.node.journal.assignment):
            return entry.grade
        return None

    def get_comments(self, entry):
        if 'comments' not in self.context:
            return None
        return CommentSerializer(Comment.objects.filter(entry=entry), many=True).data


class TemplateSerializer(serializers.ModelSerializer):
    field_set = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = '__all__'
        read_only_fields = ('id', )

    def get_field_set(self, template):
        return FieldSerializer(template.field_set.all(), many=True).data


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ('id', )


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'
