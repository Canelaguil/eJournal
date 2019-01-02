"""
test_database.py.

Test the database tables.
"""
import datetime

from django.test import TestCase

import VLE.factory as factory
from VLE.models import Content, Entry, Field, Journal


class DataBaseTests(TestCase):
    """Test the database.

    Test all the tables in the database.
    """

    def setUp(self):
        """Setup."""
        self.u1 = factory.make_user("Zi", "pass", "z@z.com")

        self.jf1 = factory.make_format()
        self.jf2 = factory.make_format()

        self.a1 = factory.make_assignment('tcolloq', 'description', format=self.jf1)

        self.et1 = factory.make_entry_template('temp1')
        self.et2 = factory.make_entry_template('temp2')

        self.f1 = factory.make_field(self.et1, "test0", "1")
        self.f2 = factory.make_field(self.et1, "test2", "2")
        self.f3 = factory.make_field(self.et2, "test1", "1")

        self.j1 = factory.make_journal(self.a1, self.u1)

        self.e1 = factory.make_entry(self.et1)
        self.e2 = factory.make_entry(self.et2)

        self.c1 = factory.make_content(self.e1, "testcontent1", self.f1)
        self.c2 = factory.make_content(self.e1, "testcontent2", self.f2)
        self.c3 = factory.make_content(self.e2, "testcontent3", self.f3)

        self.jf1.available_templates.add()
        self.jf2.available_templates.add()

        self.usr = factory.make_user('teun', '1234', email='t@t.com', lti_id='a')
        self.crs = factory.make_course('test course please ignore', 'XXXX', startdate=datetime.date.today())

    def test_foreignkeys(self):
        """Test the foreign keys in the database."""
        user_test = factory.make_user('lers', 'lers123', 'lers@uva.nl', '123456')
        course_test = factory.make_course('tname', 'XXXX', datetime.date.today())
        factory.make_format()
        template = factory.make_entry_template("some_template")
        entr_test = factory.make_entry(template)
        field = factory.make_field(template, "test1", "1")
        factory.make_content(entr_test, "data", field)
        course_test.author = user_test

        ass_test = factory.make_assignment(name='tcolloq', description='description')
        ass_test.courses.add(course_test)
        journ_test = factory.make_journal(user=user_test, assignment=ass_test)

        self.assertEquals(entr_test.template.pk, template.pk)
        self.assertEquals(journ_test.user.pk, user_test.pk)
        self.assertEquals(journ_test.assignment.pk, ass_test.pk)
        self.assertEquals(course_test.author.pk, user_test.pk)

    def test_on_delete(self):
        """Test the on_delete relations in the database."""
        self.f1.delete()
        self.assertEquals(Field.objects.filter(title='test0').count(), 0)
        self.assertEquals(Content.objects.get(pk=self.c1.pk).field, None)

        self.et1.delete()
        self.et2.delete()

        self.assertEquals(Field.objects.all().count(), 0)

        self.e1.delete()

        self.assertEquals(Content.objects.filter(data='testcontent1').count(), 0)
        self.assertEquals(Content.objects.filter(data='testcontent2').count(), 0)

        self.u1.delete()

        self.assertEquals(Content.objects.all().count(), 1)
        self.assertEquals(Entry.objects.all().count(), 1)
        self.assertEquals(Journal.objects.all().count(), 0)
