
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle


class GDPRThrottle(SimpleRateThrottle):
    rate = api_settings.DEFAULT_THROTTLE_RATES['gdpr']
    history = []

    def allow_request(self, request, view):
        """
        allow_request is run before every call.
        This is to potentially throttle a user when it calls a certain api call too many times

        When user calls user/{id}/GDPR for more then api_settings.DEFAULT_THROTTLE_RATES['gdpr'] a day,
        it returns a 429 error.
        """
        if request.path != '/users/0/GDPR/':
            return True
        if request.user.is_superuser:
            return True
        return super(GDPRThrottle, self).allow_request(request, view)

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
