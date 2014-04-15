import string
import random
import json
from urlparse import urljoin
import requests
from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth import get_user_model
from jwkest.jwk import load_jwks
from jwkest.jws import JWS
from jwkest.jwk import SYMKey

from . import errors
from .settings import oidc_settings
from .utils import b64decode

UserModel = get_user_model()



class Nonce(models.Model):
    issuer_url = models.URLField()
    state = models.CharField(max_length=255, unique=True)
    redirect_url = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Nonce: %s' % self.hash

    @classmethod
    def generate(cls, redirect_url, issuer, length=oidc_settings.NONCE_LENGTH):
        CHARS = string.letters + string.digits

        for _ in range(5):
            _hash = ''.join(random.choice(CHARS) for n in range(length))

            try:
                return cls.objects.create(issuer_url=issuer, state=_hash,
                        redirect_url=redirect_url)
            except IntegrityError:
                pass


class OpenIDProvider(models.Model):
    RS256 = 'RS256'
    HS256 = 'HS256'
    SIGNING_ALGS = (
        (RS256, 'RS256'),
        (HS256, 'HS256'),
    )

    issuer = models.URLField(unique=True)
    authorization_endpoint = models.URLField()
    token_endpoint = models.URLField()
    userinfo_endpoint = models.URLField()
    jwks_uri = models.URLField()
    signing_alg = models.CharField(max_length=5, choices=SIGNING_ALGS, default=RS256)

    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    def __unicode__(self):
        return self.issuer

    @classmethod
    def discover(cls, issuer=None, credentials={}, save=True):
        if not (issuer or credentials):
            raise ValueError('You should provide either an issuer or credentials')

        if not issuer:
            issuer = cls._get_issuer(credentials['id_token'])

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

    @property
    def signing_keys(self):
        if self.signing_alg == self.RS256:
            return load_jwks(requests.get(self.jwks_uri).text)

        return [SYMKey(key=self.client_secret)]

    def verify_id_token(self, token):
        header, claims, signature = token.split('.')
        header = b64decode(header)
        claims = b64decode(claims)

        if not signature:
            raise errors.InvalidIdToken()

        if header['alg'] not in ['HS256', 'RS256']:
            raise errors.UnsuppportedSigningmethod(header['alg'], ['HS256', 'RS256'])

        id_token = JWS().verify_compact(token, self.signing_keys)
        return json.loads(id_token)

    @staticmethod
    def _get_issuer(token):
        """Parses an id_token and returns its issuer.

        An id_token is a string containing 3 b64-encrypted hashes,
        joined by a dot, like:

            <header>.<claims>.<signature>

        We only need to parse the claims, which contains the 'iss' field
        we're looking for.
        """
        _, jwt, _ = token.split('.')

        return b64decode(jwt)['iss']


class OpenIDUser(models.Model):
    sub = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='oidc_account')
    issuer = models.ForeignKey(OpenIDProvider)
    profile = models.URLField()

    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s: %s' % (self.sub, self.user)

    @classmethod
    def get_or_create(cls, id_token, access_token, refresh_token, provider):
        try:
            obj = cls.objects.get(sub=id_token['sub'])
            obj.access_token = access_token
            obj.refresh_token = refresh_token
            obj.save()
            return obj
        except cls.DoesNotExist:
            pass

        email, profile = cls._get_userinfo(provider, id_token['sub'],
                access_token, refresh_token)

        try:
            user = UserModel()
            user.username = email
            user.set_unusable_password()
            user.save()
        except IntegrityError:
            user = UserModel.objects.get(username=email)

        return cls.objects.create(sub=id_token['sub'], issuer=provider,
                user=user, profile=profile, access_token=access_token,
                refresh_token=refresh_token)

    @classmethod
    def _get_userinfo(self, provider, sub, access_token, refresh_token):
        response = requests.get(provider.userinfo_endpoint, headers={
            'Authorization': 'Bearer %s' % access_token
        })

        if response.status_code != 200:
            raise RuntimeError()  # TODO fix this

        claims = response.json()

        if claims['sub'] != sub:
            raise RuntimeError('Invalid sub')  # TODO fix this

        return claims['email'], claims['profile']
