import factory


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Group'

    name = factory.Sequence(lambda x: 'A' + x)


class LtiGroupFactory(GroupFactory):
    lti_id = factory.Sequence(lambda x: x)
