"""
test_responses.py

This file tests whether all HTTP responses behave as required.
"""
import json

from django.http import JsonResponse
from django.test import TestCase

import VLE.utils.responses as responses


class ResponsesTests(TestCase):
    """Test the responses system.

    Test whether the HTTP responses behave as required.
    """

    def test_response_type(self):
        """Test whether the response type is correct."""
        response = responses.bad_request()

        self.assertTrue(isinstance(response, JsonResponse))

    def test_response_fields(self):
        """Test whether the response fields get filled in the correct way."""
        description = "Test description"
        test_key = "miscellaneous"
        test_value = "Test payload"
        response = responses.json_response(payload={test_key: test_value}, description=description, status=400)

        content = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(content["description"], description)
        self.assertEqual(content[test_key], test_value)

    def test_success(self):
        """Test whether the no content header contains the correct code."""
        response = responses.success()

        self.assertEqual(response.status_code, 200)
