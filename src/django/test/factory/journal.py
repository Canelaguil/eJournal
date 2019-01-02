import factory
import VLE.models


class JournalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Journal'

    user = factory.SubFactory('test.factory.user.UserFactory')
    assignment = factory.SubFactory('test.factory.assignment.AssignmentFactory')

    @factory.post_generation
    def add_user_to_assignment(self, create, extracted):
        for course in self.assignment.courses.all():
            role = VLE.models.Role.objects.get(course=course, name='Student')
            VLE.models.Participation.objects.create(course=course, user=self.user, role=role)
