import json
import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from VLE.utils.error_handling import VLEMissingRequiredKey

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
def validate_profile_picture_base64(url_data):
    """Checks if the original size does not exceed 2MB AFTER encoding."""
    if len(url_data) > settings.USER_MAX_FILE_SIZE_BYTES * 1.37:
        raise ValidationError("Max size of file is {} Bytes".format(settings.USER_MAX_FILE_SIZE_BYTES))


def validate_user_file(in_memory_uploaded_file, user):
    """Checks if size does not exceed 2MB. Or the user has reached his maximum storage space."""
    if in_memory_uploaded_file.size > settings.USER_MAX_FILE_SIZE_BYTES:
        raise ValidationError("Max size of file is {} Bytes".format(settings.USER_MAX_FILE_SIZE_BYTES))

    user_files = user.userfile_set.all()
    # Fast check for allowed user storage space
    if settings.USER_MAX_TOTAL_STORAGE_BYTES - len(user_files) * settings.USER_MAX_FILE_SIZE_BYTES <= \
       in_memory_uploaded_file.size:
        # Slow check for allowed user storage space
        if sum(user_file.file.size for user_file in user_files) > settings.USER_MAX_TOTAL_STORAGE_BYTES:
            raise ValidationError('Unsufficient storage space.')


def validate_email_files(files):
    """Checks if total size does not exceed 10MB."""
    size = 0
    for file in files:
        size += file.size
        if size > settings.USER_MAX_EMAIL_ATTACHMENT_BYTES:
            raise ValidationError(
                "Maximum email attachments size is {} Bytes.".format(settings.USER_MAX_EMAIL_ATTACHMENT_BYTES))


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
    if field.required and not (data or data == ''):
        raise VLEMissingRequiredKey(field)
    if not data:
        return

    if field.type == URL:
        url_validate = URLValidator(schemes=('http', 'https', 'ftp', 'ftps'))
        url_validate(data)

    if field.type == SELECTION:
        if data not in json.loads(field.options):
            raise ValidationError("Selected option is not in the given options")

    if field.type == DATE:
        try:
            datetime.strptime(data, '%Y-%m-%d')
        except ValueError as e:
            raise ValidationError(str(e))
