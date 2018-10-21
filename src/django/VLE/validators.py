import re

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


def validate_profile_picture(urlData):
    """Checks if size does not exceed 2MB. Checks if picture is a supported image type."""
    if urlData.size > settings.USER_MAX_FILE_SIZE_BYTES:
        raise ValidationError("Max size of file is {} Bytes".format(settings.USER_MAX_FILE_SIZE_BYTES))

    main, sub = urlData.content_type.split('/')
    if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
        raise ValidationError("Please use a JPEG, GIF or PNG image.")


def validate_user_file(inMemoryUploadedFile, user):
    """Checks if size does not exceed 2MB. Or the user has reached his maximum storage space."""
    if inMemoryUploadedFile.size > settings.USER_MAX_FILE_SIZE_BYTES:
        raise ValidationError("Max size of file is {} Bytes".format(settings.USER_MAX_FILE_SIZE_BYTES))

    user_files = user.userfile_set.all()
    # Fast check for allowed user storage space
    if settings.USER_MAX_TOTAL_STORAGE_BYTES - len(user_files) * settings.USER_MAX_FILE_SIZE_BYTES <= \
       inMemoryUploadedFile.size:
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
    if not data:
        return

    if field.type == URL:
        url_validate = URLValidator(schemes=('http', 'https', 'ftp', 'ftps'))
        url_validate(data)
