import factory

DEFAULT_PASSWORD = 'pass'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.User'

    username = factory.Sequence(lambda x: "user{}".format(x))
    email = factory.Sequence(lambda x: 'email{}@example.com'.format(x))
    password = factory.PostGenerationMethodCall('set_password', DEFAULT_PASSWORD)
    verified_email = True

    profile_picture = '/static/unknown-profile.png'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class TeacherFactory(UserFactory):
    username = factory.Sequence(lambda x: "teacher{}".format(x))
    is_teacher = True


class AdminFactory(UserFactory):
    username = factory.Sequence(lambda x: "admin{}".format(x))
    is_superuser = True
