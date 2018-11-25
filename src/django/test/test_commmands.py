"""
test_datagenerator.py.

Test the database generator commands.
"""
from django.core.management import call_command
from django.test import TestCase


class CommandsTestCase(TestCase):
    """Test the self made commands.

    Tests preset_db, demo_db and random_db.
    """

    def test_presetdb(self):
        """Test preset_db."""
        call_command('preset_db', *self.args, **self.opts)
