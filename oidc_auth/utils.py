import json
from base64 import b64decode as python_b64decode
import logging

from .settings import oidc_settings


def scopes():
    _scopes = set(oidc_settings.SCOPES)
    _scopes.update({'openid', 'profile', 'email'})

    return ' '.join(_scopes)


def b64decode(token):
    token += ('=' * (len(token) % 4))
    decoded = python_b64decode(token)
    return json.loads(decoded)


log = logging.getLogger('oidc_auth')
log.addHandler(logging.NullHandler())
