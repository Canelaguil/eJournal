from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import URLValidator
from VLE.models import Field
import VLE.utils.generic_utils as utils
from datetime import datetime

import re
import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

TEXT = 't'
RICH_TEXT = 'rt'
IMG = 'i'
FILE = 'f'
VIDEO = 'v'
PDF = 'p'
URL = 'u'
DATE = 'd'
SELECTION = 's'


# Base 64 image is roughly 37% larger than a plain image
def validate_profile_picture_base64(urlData):
    """Checks if the original size does not exceed 2MB AFTER encoding."""
    if len(urlData) > settings.USER_MAX_FILE_SIZE_BYTES * 1.37:
        raise ValidationError("Max size of file is %s Bytes" % settings.USER_MAX_FILE_SIZE_BYTES)


def validate_user_file(inMemoryUploadedFile, user):
    """Checks if size does not exceed 2MB. Or the user has reached his maximum storage space."""
    if inMemoryUploadedFile.size > settings.USER_MAX_FILE_SIZE_BYTES:
        raise ValidationError("Max size of file is %s Bytes" % settings.USER_MAX_FILE_SIZE_BYTES)

    user_files = user.userfile_set.all()
    # Fast check for allowed user storage space
    if settings.USER_MAX_TOTAL_STORAGE_BYTES - len(user_files) * settings.USER_MAX_FILE_SIZE_BYTES <= \
       inMemoryUploadedFile.size:
        # Slow check for allowed user storage space
        file_size_sum = 0
        for user_file in user_files:
            file_size_sum += user_file.file.size
        if file_size_sum > settings.USER_MAX_TOTAL_STORAGE_BYTES:
            raise ValidationError('Unsufficient storage space.')


def validate_email_files(files):
    """Checks if total size does not exceed 10MB."""
    size = 0
    for file in files:
        size += file.size
        if size > settings.USER_MAX_EMAIL_ATTACHMENT_BYTES:
            raise ValidationError("Maximum email attachments size is %s Bytes." %
                                  settings.USER_MAX_EMAIL_ATTACHMENT_BYTES)


def validate_password(password):
    """Validates password by length, having a capital letter and a special character."""
    if len(password) < 8:
        raise ValidationError("Password needs to contain at least 8 characters.")
    if password == password.lower():
        raise ValidationError("Password needs to contain at least 1 capital letter.")
    if re.match(r'^\w+$', password):
        raise ValidationError("Password needs to contain a special character.")


def validate_entry_content(data, field):
    """Validates the given data based on its field type, any validation error will be thrown."""
    if not data:
        return

    if field.type == URL:
        try:
            url_validate = URLValidator(schemes=('http', 'https', 'ftp', 'ftps'))
            url_validate(data)
        except ValidationError as e:
            raise e

    if field.type == SELECTION:
        if data not in json.loads(field.options):
            raise ValidationError("Selection not in options")

    if field.type == DATE:
        try:
            datetime.strptime(data, '%Y-%m-%d')
        except ValueError as e:
            raise ValidationError(str(e))
