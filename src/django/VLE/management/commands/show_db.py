"""
Print the database.

Print the user, course, assignment and journal table.
"""
import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Show the user, course, assignment and journal table."""

    help = 'Show the user, course, assignment and journal table.'

    def create_connection(self, db_file):
        """Create connection between the db_file and python."""
        try:
            return sqlite3.connect(db_file)
        except Exception as err:
            print(err)
        return None

    def handle(self, *args, **options):
        """Show the tables.

        These tables are: user, course, assignment and journal table
        """
        database = 'VLE.db'
        tables = ["user", "course", "assignment", "journal"]
        conn = self.create_connection(database)
        for table in tables:
            print(table)
            cur = conn.cursor()
            cur.execute("SELECT * FROM VLE_{}".format(table))
            for row in cur.fetchall():
                print(row)
            print()
        conn.close()
