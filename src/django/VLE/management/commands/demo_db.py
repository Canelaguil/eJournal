"""
Demo generate script.

A script that generates demo data.
It generates a teacher and student account. The teacher has permissions.
"""

import random

from django.core.management.base import BaseCommand
from faker import Faker

import VLE.factory as factory
from VLE.models import Field, Journal, Node, Role

faker = Faker()


class Command(BaseCommand):
    """Generates data for the database for the demo."""

    help = 'Generates useful data for the database.'

    def gen_users(self):
        """Generate a student and teacher."""
        users_examples = [
            {
                "username": "Student",
                "email": "thamj@msn.com",
                "verified_email": True,
                "full_name": "Jan Klaassen",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": False,
            }, {
                "username": "Student2",
                "email": "test@test1.test",
                "verified_email": True,
                "full_name": "Henk Doorn",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": False,
            }, {
                "username": "Student3",
                "email": "test@test2.test",
                "verified_email": True,
                "full_name": "Siemen Gerry",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": False,
            }, {
                "username": "Student4",
                "email": "test@test3.test",
                "verified_email": True,
                "full_name": "Annet Stien",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": False,
            }, {
                "username": "Student5",
                "email": "test@test4.test",
                "verified_email": True,
                "full_name": "Maarten van den Wijngaerd",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": False,
            }, {
                "username": "Teacher",
                "email": "test@test5.test",
                "verified_email": True,
                "full_name": "Marco Polo",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": True
            }, {
                "username": "Teacher2",
                "email": "test@test6.test",
                "verified_email": True,
                "full_name": "Manfred Sigurdsson",
                "pass": "pass",
                "is_superuser": False,
                "is_teacher": True
            }, {
                "username": "Admin",
                "email": "test@test7.test",
                "verified_email": True,
                "full_name": "Best Admin",
                "pass": "pass",
                "is_superuser": True,
                "is_teacher": True
            },
        ]

        self.users = []
        for u in users_examples:
            self.users.append(factory.make_user(u['username'], u['pass'], u['email'], is_superuser=u['is_superuser'],
                                                is_teacher=u['is_teacher'], full_name=u['full_name'],
                                                verified_email=u['verified_email']))

    def gen_courses(self):
        """Generate the courses PAV and Beeldbewerken."""
        courses_examples = [
            {
                "name": "Academische Vaardigheden Informatica 1",
                "abbr": "AVI1",
                "students": [0, 1, 2, 3, 4],
                "teachers": [5],
            }, {
                "name": "Academische Vaardigheden Informatica 2",
                "abbr": "AVI2",
                "students": [0, 1, 2, 3, 4],
                "teachers": [5],
            }, {
                "name": "Beeldbewerken",
                "abbr": "IPCV",
                "students": [0, 1, 2],
                "teachers": [6],
            }, {
                "name": "Reflectie op de Digitale Samenleving",
                "abbr": "RDS",
                "students": [3, 4],
                "teachers": [6],
            }
        ]
        self.courses = []
        for c in courses_examples:
            startdate = faker.date_this_decade(before_today=True)
            enddate = faker.date_this_decade(before_today=False)
            teacher = self.users[random.choice(c["teachers"])]
            course = factory.make_course(c["name"], c["abbr"], startdate, enddate, teacher)
            role = Role.objects.get(name='Student', course=course)
            for sid in c["students"]:
                student = self.users[sid]
                factory.make_participation(student, course, role)

            self.courses.append(course)

    def gen_templates(self):
        """Generate templates.

        One with title, summary, experience and requested points.
        One with only a title.
        """
        template_examples = [
            {
                "name": "Colloquium",
                "fields": [
                    {"title": "Title", "location": 0, "type": Field.TEXT},
                    {"title": "Summary", "location": 1, "type": Field.TEXT},
                    {"title": "Experience", "location": 2, "type": Field.TEXT},
                    {"title": "Requested Points", "location": 3, "type": Field.TEXT},
                ]
            }, {
                "name": "Report",
                "fields": [
                    {"title": "Title", "location": 0, "type": Field.TEXT},
                    {"title": "Introduction", "location": 1, "type": Field.TEXT},
                    {"title": "Method", "location": 2, "type": Field.TEXT},
                    {"title": "Results", "location": 3, "type": Field.TEXT},
                    {"title": "Discussion", "location": 4, "type": Field.TEXT},
                ]
            }, {
                "name": "Essay",
                "fields": [
                    {"title": "Title", "location": 0, "type": Field.TEXT},
                    {"title": "Introduction", "location": 1, "type": Field.TEXT},
                    {"title": "Body", "location": 2, "type": Field.TEXT},
                    {"title": "Conclusion", "location": 3, "type": Field.TEXT},
                ]
            }
        ]

        self.templates = []
        for t in template_examples:
            template = factory.make_entry_template(t["name"])
            for f in t["fields"]:
                factory.make_field(template, f["title"], f["location"], f["type"])

            self.templates.append(template)

    def gen_format(self):
        """Generate a assignment format."""
        format_examples = [
            {
                "templates": [],
                "presets": [
                    {"type": Node.ENTRYDEADLINE, "template": 1}
                ]
            },
            {
                "templates": [],
                "presets": [
                    {"type": Node.ENTRYDEADLINE, "template": 2}
                ]
            },
            {
                "templates": [0],
                "presets": [
                    {"type": Node.PROGRESS, "points": 5},
                    {"type": Node.PROGRESS, "points": 10}
                ]
            },
        ]

        self.formats = []
        for f in format_examples:
            templates = [self.templates[template] for template in f["templates"]]
            format = factory.make_format(templates)

            deadline_date = faker.date_time_between(start_date="now", end_date="+1m", tzinfo=None)
            deadline_end = faker.date_time_between(start_date="+5m", end_date="+1y")

            for p in f["presets"]:
                deadline_date = faker.date_time_between_dates(datetime_start=deadline_date, datetime_end=deadline_end)

                if p["type"] == Node.PROGRESS:
                    factory.make_progress_node(format, deadline_date, p["points"])
                elif p["type"] == Node.ENTRYDEADLINE:
                    factory.make_entrydeadline_node(format, deadline_date, self.templates[p["template"]])

            self.formats.append(format)

    def gen_assignments(self):
        """Generate assignments."""
        assign_examples = [
            {
                "name": "Colloquium",
                "description": "Report your attendance at colloquia here.",
                "courses": [0, 1],
                "format": 2,
                "author": 5,
            },
            {
                "name": "Report",
                "description": "Report your findings here.",
                "courses": [2],
                "format": 0,
                "author": 6,
            },
            {
                "name": "Essay",
                "description": "Publish iterations of your essay here.",
                "courses": [3],
                "format": 1,
                "author": 6,
            },
        ]

        self.assignments = []
        for a in assign_examples:
            author = self.users[a["author"]]
            format = self.formats[a["format"]]
            assignment = factory.make_assignment(a["name"], a["description"], author, format)

            for course in a["courses"]:
                assignment.courses.add(self.courses[course])
            self.assignments.append(assignment)

    def gen_journals(self):
        """Generate journals."""
        self.journals = []
        for c in self.courses:
            for a in c.assignment_set.all():
                for u in c.users.all():
                    if c.author == u:
                        continue

                    if not Journal.objects.filter(assignment=a, user=u).exists():
                        journal = factory.make_journal(a, u)
                        self.journals.append(journal)

    def handle(self, *args, **options):
        """Generate data to test and fill the database with.

        This only contains the 'useful data'. For random data, execute demo_db as well.
        """
        self.gen_users()
        self.gen_courses()
        self.gen_templates()
        self.gen_format()
        self.gen_assignments()
        self.gen_journals()
