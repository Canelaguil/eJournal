import factory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Comment'
