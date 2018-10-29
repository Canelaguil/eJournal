import factory


class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Assignment'

    name = 'Logboek'
    # description = 'Logboek for all your logging purposes'
    # author = factory.SubFactory('test.factory.user.TeacherFactory')

    format = factory.RelatedFactory('test.factory.format.FormatFactory', 'assignment')

    @factory.post_generation
    def courses(self, create, extracted):
        if not create:
            return

        if extracted:
            for course in extracted:
                self.courses.add(course)
