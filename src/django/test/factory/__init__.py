from test.factory.assignment import AssignmentFactory
from test.factory.course import CourseFactory
from test.factory.user import UserFactory, TeacherFactory, AdminFactory
from test.factory.format import FormatFactory
from test.factory.template import TemplateFactory
from test.factory.group import GroupFactory, LtiGroupFactory
from test.factory.lti import LtiFactory
from test.factory.participation import ParticipationFactory, GroupParticipationFactory
from test.factory.journal import JournalFactory

Assignment = AssignmentFactory
Course = CourseFactory

User = UserFactory
Teacher = TeacherFactory
Admin = AdminFactory

Format = FormatFactory
Template = TemplateFactory

Group = GroupFactory
LtiGroup = LtiGroupFactory

Lti = LtiFactory

Participation = ParticipationFactory
GroupParticipation = GroupParticipationFactory

Journal = JournalFactory
