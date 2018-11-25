import factory


class JournalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Journal'

    user = factory.SubFactory('test.factory.user.UserFactory')
    assignment = factory.SubFactory('test.factory.assignment.AssignmentFactory')

    @factory.post_generation
    def author(self, create, extracted):
        if not create:
            return

        if extracted:
            self.user = extracted
            if not self.assignment.courses.exists():
                print(factory.SubFactory('test.factory.course.CourseFactory').course)
                self.assignment.courses.add(factory.SubFactory('test.factory.course.CourseFactory'))
            for course in self.assignment.courses.all():
                p = factory.SubFactory('test.factory.participation.ParticipationFactory')
                p.user = extracted,
                p.course = course
                p.role = factory.SubFactory('test.factory.role.StudentRoleFactory')
                print(course)
            print(self.assignment.courses.all())
            print(self.user)
