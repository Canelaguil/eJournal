"""
WSGI config for VLE project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import logging
import os
import sys

from django.core.wsgi import get_wsgi_application

logging.basicConfig(stream=sys.stderr)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VLE.settings.production")
path = '{{DIR}}'
if path not in sys.path:
    sys.path.append(path)
application = get_wsgi_application()
