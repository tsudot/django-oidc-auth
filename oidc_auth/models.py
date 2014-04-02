import json
from base64 import b64decode
from urlparse import urljoin
import requests
from django.db import models


def _get_issuer(token):
    """Parses an id_token and returns its issuer.
    
    An id_token is a string containing 3 b64-encrypted hashes,
    joined by a dot, like:

        <header>.<claims>.<signature>

    We only need to parse the claims, which contains the 'iss' field
    we're looking for.
    """

    _, jwt, _ = token.split('.')
    claims = b64decode(jwt)

    return json.loads(claims)['iss']


class OpenIDProvider(models.Model):
    issuer = models.URLField(unique=True)
    authorization_endpoint = models.URLField()
    token_endpoint = models.URLField()
    userinfo_endpoint = models.URLField()
    jwks_uri = models.URLField()

    @classmethod
    def discover(cls, issuer=None, credentials={}, save=True):
        if not (issuer or credentials):
            raise ValueError('You should provide either an issuer or credentials')

        if not issuer:
            issuer = _get_issuer(credentials['id_token'])

        discover_endpoint = urljoin(issuer, '.well-known/openid-configuration')
        response = requests.get(discover_endpoint)

        if response.status_code != 200:
            raise RuntimeError()  # TODO change this

        configs = response.json()
        provider = cls()

        provider.issuer = configs['issuer']
        provider.authorization_endpoint = configs['authorization_endpoint']
        provider.token_endpoint = configs['token_endpoint']
        provider.userinfo_endpoint = configs['userinfo_endpoint']
        provider.jwks_uri = configs['jwks_uri']

        if save:
            provider.save()

        return provider
