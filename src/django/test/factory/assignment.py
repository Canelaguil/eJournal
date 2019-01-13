import test.factory.course

import factory


class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Assignment'

    name = 'Logboek'
    description = 'Logboek for all your logging purposes'
    is_published = True
    author = factory.SubFactory('test.factory.user.TeacherFactory')

    format = factory.SubFactory('test.factory.format.FormatFactory')

    @factory.post_generation
    def courses(self, create, extracted):
        if not create:
            return

        if extracted:
            for course in extracted:
                self.courses.add(course)
                p = factory.SubFactory('test.factory.participation.ParticipationFactory')
                p.user = self.author,
                p.course = course
                p.role = factory.SubFactory('test.factory.role.TeacherRoleFactory')
        else:
            course = test.factory.course.CourseFactory()
            self.courses.add(course)
