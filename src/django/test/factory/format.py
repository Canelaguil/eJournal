import factory


class FormatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Format'

    # unused_templates
    # available_templates
