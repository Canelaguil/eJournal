"""
test_gradepassback.py.

Test the lti grade passback.
"""
from django.conf import settings
from django.test import TestCase

import VLE.factory as factory
import VLE.lti_grade_passback as lti_grade
from VLE.models import Entry, Role, Template


class GradePassBackRequestXMLTest(TestCase):
    """Test XML grade passpack.

    Test if the gradepassback XML can be created.

    """
    def setUp(self):
        """Setup."""
        self.course = factory.make_course('TestCourse', 'aaaa', lti_id='asdf')
        self.user = factory.make_user('TestUser', 'Pass', 'ltiTest@test.com')
        factory.make_participation(self.user, self.course, Role.objects.get(name='Student', course=self.course))
        self.assignment = factory.make_assignment("TestAss", "TestDescr", points_possible=100, courses=[self.course])
        self.journal = factory.make_journal(self.assignment, self.user)
        self.journal.sourcedid = 'f6d552'
        self.journal.grade_url = 'http://127.0.0.1:8000/grade_passback'

    def test_create_grade_passback(self):
        """Test if the GradePassBackRequest is correctly created when a journal is given"""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal, send_score=True)
        self.assertIsNotNone(passback.score)
        self.assertIsNotNone(passback.url)
        self.assertIsNotNone(passback.sourcedid)

    def test_create_grade_passback_no_journal(self):
        """Test if the GradePassBackRequest is correctly created when no journal is given"""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, None)
        self.assertIsNone(passback.score)
        self.assertIsNone(passback.url)
        self.assertIsNone(passback.sourcedid)

    def test_create_xml_no_score_no_data(self):
        """Test create xml with no score or data set."""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, None)
        result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version>\
<imsx_messageIdentifier>0</imsx_messageIdentifier></imsx_POXRequestHeaderInfo>\
</imsx_POXHeader><imsx_POXBody><replaceResultRequest><resultRecord><sourcedGUID><sourcedId />\
</sourcedGUID></resultRecord></replaceResultRequest></imsx_POXBody></imsx_POXEnvelopeRequest>'
        self.assertEqual(result, passback.create_xml())

    def test_create_xml_with_score(self):
        """Test create xml with the score set."""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal, send_score=True)
        result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>0\
</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody><replaceResultRequest>\
<resultRecord><sourcedGUID><sourcedId>f6d552</sourcedId></sourcedGUID><result><resultScore><language>en</language>\
<textString>0.0</textString></resultScore></result></resultRecord></replaceResultRequest></imsx_POXBody>\
</imsx_POXEnvelopeRequest>'

        self.assertEqual(result, passback.create_xml())

    def test_create_xml_with_data_text(self):
        """Test create xml."""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal,
                                                  result_data={'text': 'New entry'})
        result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>0\
</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody><replaceResultRequest>\
<resultRecord><sourcedGUID><sourcedId>f6d552</sourcedId></sourcedGUID><result><resultData>\
<text>New entry</text></resultData></result></resultRecord></replaceResultRequest>\
</imsx_POXBody></imsx_POXEnvelopeRequest>'
        self.assertEqual(result, passback.create_xml())

    def test_create_xml_with_data_url(self):
        """Test create xml."""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal,
                                                  result_data={'url': 'http://127.0.0.1:8000/grade_passback'})
        result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>0\
</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody><replaceResultRequest>\
<resultRecord><sourcedGUID><sourcedId>f6d552</sourcedId></sourcedGUID><result><resultData>\
<url>http://127.0.0.1:8000/grade_passback</url></resultData></result></resultRecord></replaceResultRequest>\
</imsx_POXBody></imsx_POXEnvelopeRequest>'
        self.assertEqual(result, passback.create_xml())

    def test_create_xml_with_data_url_timestamp(self):
            """Test create xml."""
            passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal,
                                                      submitted_at='2017-04-16T18:54:36.736+00:00',
                                                      result_data={'url': 'http://127.0.0.1:8000/grade_passback'})
            result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>0\
</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody><replaceResultRequest>\
<submissionDetails><submittedAT>2017-04-16T18:54:36.736+00:00</submittedAT></submissionDetails>\
<resultRecord><sourcedGUID><sourcedId>f6d552</sourcedId></sourcedGUID><result><resultData>\
<url>http://127.0.0.1:8000/grade_passback</url></resultData></result></resultRecord></replaceResultRequest>\
</imsx_POXBody></imsx_POXEnvelopeRequest>'
            self.assertEqual(result, passback.create_xml())

    def test_create_xml_with_data_launchUrl(self):
        """Test create xml."""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal,
                                                  result_data={'launchUrl': 'http://127.0.0.1:8000/grade_passback'})
        result = b'<imsx_POXEnvelopeRequest xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXRequestHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier>0\
</imsx_messageIdentifier></imsx_POXRequestHeaderInfo></imsx_POXHeader><imsx_POXBody><replaceResultRequest>\
<resultRecord><sourcedGUID><sourcedId>f6d552</sourcedId></sourcedGUID><result><resultData>\
<ltiLaunchUrl>http://127.0.0.1:8000/grade_passback</ltiLaunchUrl></resultData></result></resultRecord>\
</replaceResultRequest></imsx_POXBody></imsx_POXEnvelopeRequest>'
        self.assertEqual(result, passback.create_xml())

    def test_message_id_incrementor(self):
        """Test if the ID incrementor is implemented."""
        now = lti_grade.GradePassBackRequest.get_message_id_and_increment()
        self.assertTrue(int(now) + 1 == int(lti_grade.GradePassBackRequest.get_message_id_and_increment()))

    def test_parse_return_xml(self):
        """"""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal)
        xml = b'<?xml version="1.0" encoding="UTF-8"?>\
<imsx_POXEnvelopeResponse xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXResponseHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier/>\
<imsx_statusInfo><imsx_codeMajor>success</imsx_codeMajor><imsx_severity>status</imsx_severity>\
<imsx_description>grade replaced</imsx_description><imsx_messageRefIdentifier>2</imsx_messageRefIdentifier>\
<imsx_operationRefIdentifier>replaceResult</imsx_operationRefIdentifier></imsx_statusInfo>\
</imsx_POXResponseHeaderInfo></imsx_POXHeader><imsx_POXBody>\
<replaceResultResponse/></imsx_POXBody></imsx_POXEnvelopeResponse>'
        data = passback.parse_return_xml(xml)
        self.assertEqual(data['severity'], 'status')
        self.assertEqual(data['code_mayor'], 'success')
        self.assertEqual(data['description'],  'grade replaced')

    def test_parse_return_empty_xml(self):
        """"""
        passback = lti_grade.GradePassBackRequest(settings.LTI_SECRET, settings.LTI_KEY, self.journal)
        xml = b'<?xml version="1.0" encoding="UTF-8"?>\
<imsx_POXEnvelopeResponse xmlns="http://www.imsglobal.org/services/ltiv1p1/xsd/imsoms_v1p0">\
<imsx_POXHeader><imsx_POXResponseHeaderInfo><imsx_version>V1.0</imsx_version><imsx_messageIdentifier/>\
<imsx_statusInfo><imsx_messageRefIdentifier>2</imsx_messageRefIdentifier>\
<imsx_operationRefIdentifier>replaceResult</imsx_operationRefIdentifier></imsx_statusInfo>\
</imsx_POXResponseHeaderInfo></imsx_POXHeader><imsx_POXBody>\
<replaceResultResponse/></imsx_POXBody></imsx_POXEnvelopeResponse>'
        data = passback.parse_return_xml(xml)
        self.assertEqual(data['severity'], None)
        self.assertEqual(data['code_mayor'], None)
        self.assertEqual(data['description'],  'not found')

    def test_check_if_need_VLE_publish_no_journals(self):
        """Hopefully doesnt crash."""
        course = factory.make_course('TestCourse', 'aaaa', lti_id='qqsa')
        assign = factory.make_assignment("TestAss", "TestDescr", lti_id='aasas', courses=[course])
        lti_grade.check_if_need_VLE_publish(assign)

    def test_check_if_need_VLE_publish_journals_nothing_needed(self):
        """Hopefully doesnt crash."""
        lti_grade.check_if_need_VLE_publish(self.assignment)

    def test_check_if_need_VLE_publish_journals(self):
        """Hopefully doesnt crash."""
        entry = factory.make_entry(Template.objects.filter(name='Default Template')[0])
        entry.published = True
        entry.vle_coupling = Entry.GRADING
        entry.save()
        factory.make_node(self.journal, entry)
        entry1 = factory.make_entry(Template.objects.filter(name='Default Template')[0])
        entry1.save()
        factory.make_node(self.journal, entry1)
        lti_grade.check_if_need_VLE_publish(self.assignment)

    def test_change_Entry_vle_coupling(self):
        """Hopefully doesnt crash."""
        entry = factory.make_entry(Template.objects.filter(name='Default Template')[0])
        entry.published = True
        entry.save()
        factory.make_node(self.journal, entry)
        lti_grade.change_Entry_vle_coupling(self.journal, Entry.GRADING)
        for entry in Entry.objects.filter(published=True,
                                          node__journal=self.journal).exclude(vle_coupling=Entry.LINK_COMPLETE):
            self.assertEqual(entry.vle_coupling, Entry.GRADING)

    def test_replace_result_no_url(self):
        """Hopefully doesnt crash."""
        entry = factory.make_entry(Template.objects.filter(name='Default Template')[0])
        entry.published = True
        entry.save()
        factory.make_node(self.journal, entry)
        self.journal.sourcedid = None
        self.journal.grade_url = None
        self.journal.save()

        self.assertEqual(lti_grade.replace_result(self.journal), None)
