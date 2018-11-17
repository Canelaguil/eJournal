import factory


class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Template'

    name = 'default text'
    max_grade = 10
