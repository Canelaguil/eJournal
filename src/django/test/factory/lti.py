import factory


class LtiFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Lti_ids'

    lti_id = factory.Sequence(lambda x: x)
