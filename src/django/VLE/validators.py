from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import URLValidator
from VLE.models import Field
import VLE.utils.generic_utils as utils
import re


TEXT = 't'
RICH_TEXT = 'rt'
IMG = 'i'
FILE = 'f'
VIDEO = 'v'
PDF = 'p'
URL = 'u'


# Base 64 image is roughly 37% larger than a plain image
def validate_profile_picture_base64(urlData):
    """Checks if the original size does not exceed 2MB AFTER encoding."""
    if len(urlData) > settings.USER_MAX_FILE_SIZE_BYTES * 1.37:
        raise ValidationError("Max size of file is %s Bytes" % settings.USER_MAX_FILE_SIZE_BYTES)


def validate_user_file(inMemoryUploadedFile):
    """Checks if size does not exceed 2MB."""
    if inMemoryUploadedFile.size > settings.USER_MAX_FILE_SIZE_BYTES:
        raise ValidationError("Max size of file is %s Bytes" % settings.USER_MAX_FILE_SIZE_BYTES)


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


def validate_entry_content(content_list):
    """Validates the given data based on its field type, any validation error will be raised."""
    for content in content_list:
        try:
            id, data = utils.required_params(content, "id", "data")
        except KeyError as e:
            raise e

        if not data:
            continue

        field = Field.objects.get(pk=id)

        if field.type == URL:
            try:
                url_validate = URLValidator(schemes=('http', 'https', 'ftp', 'ftps'))
                url_validate(data)
            except ValidationError as e:
                raise e
