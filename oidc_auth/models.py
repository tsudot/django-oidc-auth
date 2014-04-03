import string
import hashlib
import random
import json
from base64 import b64decode
from urlparse import urljoin
import requests
from django.db import models, IntegrityError

from .settings import oidc_settings


def _get_issuer(token):
    """Parses an id_token and returns its issuer.
    
    An id_token is a string containing 3 b64-encrypted hashes,
    joined by a dot, like:

        <header>.<claims>.<signature>

    We only need to parse the claims, which contains the 'iss' field
    we're looking for.
    """

    _, jwt, _ = token.split('.')
    jwt = jwt + ('=' * (len(jwt) % 4))

    claims = b64decode(jwt)

    return json.loads(claims)['iss']


class Nonce(models.Model):
    issuer_url = models.URLField()
    hash = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return 'Nonce: %s' % self.hash

    @classmethod
    def generate(cls, issuer, length=oidc_settings.NONCE_LENGTH):
        CHARS = string.letters + string.digits

        for _ in range(5):
            sequence = ''.join(random.choice(CHARS) for n in range(length))
            _hash = hashlib.sha1(sequence).hexdigest()

            if not cls.objects.filter(hash=_hash).exists():
                try:
                    cls.objects.create(issuer_url=issuer, hash=_hash)
                    return _hash
                except IntegrityError:
                    pass
        
        raise RuntimeError()  # TODO fix this, error maximum retries

class OpenIDProvider(models.Model):
    issuer = models.URLField(unique=True)
    authorization_endpoint = models.URLField()
    token_endpoint = models.URLField()
    userinfo_endpoint = models.URLField()
    jwks_uri = models.URLField()

    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    @classmethod
    def discover(cls, issuer=None, credentials={}, save=True):
        if not (issuer or credentials):
            raise ValueError('You should provide either an issuer or credentials')

        if not issuer:
            issuer = _get_issuer(credentials['id_token'])

        try:
            return cls.objects.get(issuer=issuer)
        except cls.DoesNotExist:
            pass

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

    @property
    def client_credentials(self):
        return self.client_id, self.client_secret
