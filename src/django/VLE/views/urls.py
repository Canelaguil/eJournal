from rest_framework import routers

from VLE.views.assignment import AssignmentView
from VLE.views.comment import CommentView
from VLE.views.course import CourseView
from VLE.views.entry import EntryView
from VLE.views.format import FormatView
from VLE.views.group import GroupView
from VLE.views.instance import InstanceView
from VLE.views.journal import JournalView
from VLE.views.node import NodeView
from VLE.views.participation import ParticipationView
from VLE.views.role import RoleView
from VLE.views.user import UserView

router = routers.DefaultRouter()
router.register(r'instance', InstanceView, base_name='instance')
router.register(r'courses', CourseView, base_name='course')
router.register(r'groups', GroupView, base_name='group')
router.register(r'roles', RoleView, base_name='role')
router.register(r'users', UserView, base_name='user')
router.register(r'assignments', AssignmentView, base_name='assignment')
router.register(r'nodes', NodeView, base_name='node')
router.register(r'comments', CommentView, base_name='comment')
router.register(r'participations', ParticipationView, base_name='participation')
router.register(r'journals', JournalView, base_name='journal')
router.register(r'entries', EntryView, base_name='entry')
router.register(r'formats', FormatView, base_name='format')

urlpatterns = router.urls
