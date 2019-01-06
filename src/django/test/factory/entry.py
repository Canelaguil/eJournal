import factory


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Entry'
