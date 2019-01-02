import test.factory.role

import factory

import VLE.models


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'VLE.Course'

    name = 'Academische Vaardigheden 1'
    abbreviation = "AVI1"
    startdate = factory.Faker('date_between', start_date="-10y", end_date="-1y")
    enddate = factory.Faker('date_between', start_date="+1y", end_date="+10y")

    student_role = factory.RelatedFactory('test.factory.role.StudentRoleFactory', 'course')
    ta_role = factory.RelatedFactory('test.factory.role.TaRoleFactory', 'course')
    author = factory.SubFactory('test.factory.user.TeacherFactory')

    @factory.post_generation
    def author_participation(self, create, extracted):
        if not create:
            return

        # Ensure TeacherRole is always created.
        role = test.factory.role.TeacherRoleFactory(course=self)

        if extracted:
            return extracted

        participation = VLE.models.Participation(course=self, user=self.author, role=role)
        participation.save()

        return participation


class LtiCourseFactory(CourseFactory):
    lti_id = factory.RelatedFactory('test.factory.lti.LtiFactory', 'course', for_model=VLE.models.Lti_ids.COURSE)
