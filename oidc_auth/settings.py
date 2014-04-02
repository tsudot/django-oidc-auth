from contextlib import contextmanager
from django.conf import settings


DEFAULTS = {
    'DEFAULT_ENDPOINT': None,
    'SCOPES': ('openid', 'profile', 'email'),
    'CLIENT_ID': None,
    'CLIENT_SECRET': None,
    'NONCE_LENGTH': 8
}

USER_SETTINGS = getattr(settings, 'OIDC_AUTH', {})


class OIDCSettings(object):
    """Shamelessly copied from django-oauth-toolkit"""

    def __init__(self, user_settings, defaults):
        self.user_settings = user_settings
        self.defaults = defaults
        self.patched_settings = {}

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid oidc_auth setting: %s' % attr)

        return (self.patched_settings.get(attr)
                or self.user_settings.get(attr)
                or self.defaults[attr])

    @contextmanager
    def override(self, **kwargs):
        self.patched_settings = kwargs
        yield
        self.patched_settings = {}


oidc_settings = OIDCSettings(USER_SETTINGS, DEFAULTS)
