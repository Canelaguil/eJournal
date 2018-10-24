"""
File handling related utilites.
"""
import json
import os
import shutil

from django.conf import settings
from django.db.models import Q


def get_path(userfile, filename):
    """Upload user files into their respective directories. Following MEDIA_ROOT/uID/aID/<file>

    Uploaded files not part of an entry yet, and are treated as temporary until linked to an entry."""
    return '{}/{}/{}'.format(str(userfile.author.id), str(userfile.assignment.id), filename)


def get_profile_picture_path(user, filename):
    """Upload user profile pictures into their respective directories. Following MEDIA_ROOT/uID/profile_picture"""
    return '{}/profile_picture'.format(str(user.id))


def compress_all_user_data(user, extra_data_dict=None, archive_extension='zip'):
    """Compresses all user files found in MEDIA_ROOT/uid into a single archiveself.

    If an extra data dictionary is provided, this is json dumped and included in the archive as
    information.json.
    The archive is stored in MEDIA_ROOT/{username}_data_archive.{archive_extension}.
    Please note that this archive is overwritten if it already exists."""
    user_file_dir_path = os.path.join(settings.MEDIA_ROOT, str(user.id))
    archive_name = user.username + '_data_archive'
    archive_ouput_base_name = os.path.join(settings.MEDIA_ROOT, archive_name)
    archive_ouput_path = archive_ouput_base_name + '.' + archive_extension

    if extra_data_dict:
        extra_data_dump_name = 'information.json'
        extra_data_dump_path = os.path.join(user_file_dir_path, extra_data_dump_name)
        os.makedirs(os.path.dirname(extra_data_dump_path), exist_ok=True)
        with open(extra_data_dump_path, 'w') as file:
            file.write(json.dumps(extra_data_dict))

    shutil.make_archive(archive_ouput_base_name, archive_extension, user_file_dir_path)

    return archive_ouput_path


def make_permanent_file_content(user_file, content, node):
    """Upates a UserFile content, node and enty. Removing temp status."""
    user_file.content = content
    user_file.node = node
    user_file.entry = content.entry
    user_file.save()


def get_temp_user_file(user, assignment, file_name, entry=None, node=None, content=None):
    """Retrieves the most recently added tempfile specified by assignment and name.

    Returns None if no file was found."""
    return user.userfile_set.filter(author=user, assignment=assignment, node=node, entry=entry,
                                    content=content, file_name=file_name).order_by('-creation_date').first()


def remove_temp_user_files(user):
    """Deletes floating user files."""
    user.userfile_set.filter(Q(node=None) | Q(entry=None) | Q(content=None)).delete()
