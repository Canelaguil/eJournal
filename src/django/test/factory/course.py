import VLE.models
import factory


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Course'

    name = 'Academische Vaardigheden 1'
    abbreviation = "AVI1"
    startdate = factory.Faker('date_between', start_date="-10y", end_date="-1y")
    enddate = factory.Faker('date_between', start_date="+1y", end_date="+10y")

    student_role = factory.RelatedFactory('test.factory.role.StudentRoleFactory', 'course')
    ta_role = factory.RelatedFactory('test.factory.role.TaRoleFactory', 'course')

    author_participation = factory.Maybe('author', None,
                                         factory.RelatedFactory('test.factory.participation.ParticipationFactory',
                                                                'course',
                                                                user=factory.SelfAttribute('..author'),
                                                                role=factory.RelatedFactory(
                                                                    'test.factory.role.TeacherRoleFactory', 'course')))


class LtiCourseFactory(CourseFactory):
    lti_id = factory.RelatedFactory('test.factory.lti.LtiFactory', 'course', for_model=VLE.models.Lti_ids.COURSE)
