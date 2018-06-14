from django.core.management.base import BaseCommand
from VLE.models import *
from faker import Faker
import random
faker = Faker()


class Command(BaseCommand):
    help = 'Generates data for the database.'

    def gen_prepared_data(self, ):
        """Generate useful data to test with.

        These are preselected users and are assigned to courses to run tests with.
        """
        users_examples = [
            {"username": "Lars", "type": "SD"},
            {"username": "Rick", "type": "SD"},
            {"username": "Dennis", "type": "SD"},
            {"username": "Zi", "type": "TA"},
            {"username": "Jeroen", "type": "TE"},
            {"username": "Maarten", "type": "SU"}
        ]
        courses_examples = [
            {"name": "Portofolio Academische Vaardigheden 1", "abbr": "PAV"},
            {"name": "Portofolio Academische Vaardigheden 2", "abbr": "PAV"},
            {"name": "Beeldbewerken", "abbr": "BB"},
            {"name": "Automaten en Formele Talen", "abbr": "AFT"}
        ]
        assign_examples = [
            {"name": "Logboek", "courses": [0, 1, 2, 3]},
            {"name": "colloquium", "courses": [0]},
            {"name": "Verslag", "courses": [0, 1]},
        ]
        journal_examples = [
            {"assigns": 0, "users": 0},
            {"assigns": 1, "users": 2},
        ]

        users = []
        for u in users_examples:
            user = User(username=u["username"])
            user.set_password('pass')
            user.save()
            users.append(user)

        courses = []
        for c in courses_examples:
            course = Course(name=c["name"], abbreviation=c["abbr"])
            course.save()
            course.authors.add(users[2])
            course.authors.add(users[3])
            courses.append(course)

        assignments = []
        for a in assign_examples:
            assignment = Assignment(name=a["name"])
            assignment.save()
            for course in a["courses"]:
                assignment.courses.add(courses[course])
            assignments.append(assignment)

        journals = []
        for j in journal_examples:
            journal = Journal(assignment=assignments[j["assigns"]], user=users[j["users"]])
            journal.save()

    def gen_random_users(self, amount):
        """
        Generate random users.
        """
        used_email = [email['email'] for email in User.objects.all().values('email')]
        used_names = [email['username'] for email in User.objects.all().values('username')]
        used_lti = [email['lti_id'] for email in User.objects.all().values('lti_id')]

        for _ in range(amount):
            user = User()
            user.email = faker.ascii_safe_email()
            # Generate unique email or exit.
            user.email = faker.ascii_safe_email()
            counter = 0
            while(user.email in used_email and counter < 10000):
                user.email = faker.ascii_safe_email()
                counter += 1
            if counter == 10000:
                print("Could not find unique email")
                exit()

            # Generate unique name or exit.
            user.username = faker.name()
            counter = 0
            while(user.username in used_names and counter < 10000):
                user.username = faker.name()
                counter += 1
            if counter == 10000:
                print("Could not find unique username")
                exit()

            user.set_password(faker.password())

            # Generate unique lti_id.
            user.lti_id = faker.name()
            counter = 0
            while(user.lti_id in used_lti and counter < 10000):
                user.lti_id = faker.name()
                counter += 1
            if counter == 10000:
                print("Could not find unique lti_id")
                exit()

            user.save()
            used_email.append(user.email)
            used_names.append(user.username)
            used_lti.append(user.lti_id)

    def gen_random_courses(self, amount):
        """
        Generate random courses.
        """
        for _ in range(amount):
            course = Course()
            course.save()
            course.name = faker.company()

            teachers = User.objects.all()
            teacher_amount = random.randint(1, 3)
            if len(teachers) > 0:
                course.authors.add(*(random.choices(teachers, k=teacher_amount)))

            course.abbrevation = random.choices(course.name, k=4)
            course.startdate = faker.date_this_decade(before_today=True)
            course.save()

    def gen_roles(self):
        """
        Generate roles for participation in courses.
        """
        ta = Role()
        ta.name = "TA"

        ta.can_edit_grades = True
        ta.can_view_grades = True
        ta.can_edit_assignment = True
        ta.can_view_assignment = True
        ta.can_submit_assignment = True
        ta.save()

        student = Role()
        student.name = "student"

        student.can_edit_grades = False
        student.can_view_grades = False
        student.can_edit_assignment = False
        student.can_view_assignment = True
        student.can_submit_assignment = True
        student.save()

    def gen_random_participation_for_each_user(self):
        """
        Generate participants to link students to courses with a role.
        """
        courses = Course.objects.all()
        participation_list = list()
        if courses.count() > 0:
            for user in User.objects.all():
                participation = Participation()
                participation.user = user
                participation.course = courses[random.randint(0, len(courses) - 1)]
                participation.role = random.choice(Role.objects.all())
                participation_list.append(participation)

        # Using a bulk create speeds the process up.
        Participation.objects.bulk_create(participation_list)

    def gen_random_assignments(self, amount):
        """
        Generate random assignments.
        """
        for _ in range(amount):
            if Course.objects.all().count() == 0:
                continue
            assignment = Assignment()
            assignment.save()
            assignment.name = faker.catch_phrase()
            assignment.description = faker.paragraph()
            courses = Course.objects.all()
            course_list = list()
            for course in random.choices(courses, k=3):
                if assignment.courses.count():
                    course_list.append(course)
                else:
                    if random.randint(1, 101) > 70:
                        course_list.append(course)

            assignment.courses.add(*(course_list))
            assignment.save()

    def gen_random_journals(self, amount):
        """
        Generate random journals.
        """
        assignments = Assignment.objects.all()
        users = User.objects.all()
        journal_list = list()
        for _ in range(amount):
            if assignments.count() == 0:
                continue
            journal = Journal()
            journal.assignment = random.choice(assignments)
            journal.user = random.choice(users)
            journal_list.append(journal)

        # Using a bulk create speeds the process up.
        Journal.objects.bulk_create(journal_list)

    def gen_random_entries(self, amount):
        """
        Generate random entries.
        """
        journals = Journal.objects.all()
        entry_list = list()
        for _ in range(amount):
            if journals.count() == 0:
                continue
            entry = Entry()
            entry.journal = random.choice(journals)
            entry.datetime = faker.date_time_this_month(before_now=True)
            entry.late = faker.boolean()
            entry_list.append(entry)

        # Using a bulk create speeds the process up.
        Entry.objects.bulk_create(entry_list)

    def handle(self, *args, **options):
        """This function generates data to test and fill the database with.

        It has both useful test data and randomly created data to create a more real life example.
        """

        # Preselected items
        self.gen_prepared_data()

        amount = 10
        # Random users
        self.gen_random_users(amount*10)
        # Random course
        self.gen_random_courses(amount)
        # Create the roles
        self.gen_roles()
        # Random participation
        self.gen_random_participation_for_each_user()
        # Random assignments
        self.gen_random_assignments(amount*10)
        # Random journals
        self.gen_random_journals(amount*100)
        # Random entries
        self.gen_random_entries(amount*1000)
