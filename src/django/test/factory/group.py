import factory


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Group'

    name = factory.Sequence(lambda x: 'A' + str(x))
    course = factory.SubFactory('test.factory.course.CourseFactory')


class LtiGroupFactory(GroupFactory):
    lti_id = factory.Sequence(lambda x: x)
