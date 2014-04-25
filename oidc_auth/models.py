import string
import random
import json
from urlparse import urljoin
import requests
from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth import get_user_model
from jwkest.jwk import load_jwks_from_url
from jwkest.jws import JWS
from jwkest.jwk import SYMKey

from . import errors
from .settings import oidc_settings
from .utils import log, b64decode

UserModel = get_user_model()


class Nonce(models.Model):
    issuer_url = models.URLField()
    state = models.CharField(max_length=255, unique=True)
    redirect_url = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s' % self.state

    def __init__(self, *args, **kwargs):
        self._provider = None
        super(Nonce, self).__init__(*args, **kwargs)

    @classmethod
    def generate(cls, redirect_url, issuer, length=oidc_settings.NONCE_LENGTH):
        """This method generates and returns a nonce, an unique generated
        string. If the maximum of retries is exceeded, it returns None.
        """
        CHARS = string.letters + string.digits

        for i in range(5):
            _hash = ''.join(random.choice(CHARS) for n in range(length))

            try:
                log.debug('Attempt %s to save nonce %s to issuer %s' % (i+1,
                    _hash, issuer))
                return cls.objects.create(issuer_url=issuer, state=_hash,
                        redirect_url=redirect_url)
            except IntegrityError:
                pass

        log.debug('Maximum of retries to create a nonce to issuer %s '
                  'exceeded! Max: 5' % issuer)

    @property
    def provider(self):
        """This method will fetch the related provider from the database
        and cache it inside an object var.
        """
        provider = self._provider

        if not provider:
            provider = OpenIDProvider.objects.get(issuer=self.issuer_url)

        return provider


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
    jwks_uri = models.URLField(null=True, blank=True)
    signing_alg = models.CharField(max_length=5, choices=SIGNING_ALGS, default=HS256)

    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    def __unicode__(self):
        return self.issuer

    @classmethod
    def discover(cls, issuer=None, credentials={}, save=True):
        """Returns a known OIDC Endpoint. If it doesn't exist in the database,
        then it'll fetch its data according to OpenID Connect Discovery spec.
        """
        if not (issuer or credentials):
            raise ValueError('You should provide either an issuer or credentials')

        if not issuer:
            issuer = cls._get_issuer(credentials['id_token'])

        try:
            provider = cls.objects.get(issuer=issuer)
            log.debug('Provider %s already discovered' % issuer)
            return provider
        except cls.DoesNotExist:
            pass

        log.debug('Provider %s not discovered yet, proceed discovery' % issuer)
        discover_endpoint = urljoin(issuer, '.well-known/openid-configuration')
        response = requests.get(discover_endpoint)

        if response.status_code != 200:
            raise errors.RequestError(discover_endpoint, response.status_code)

        configs = response.json()
        provider = cls()

        provider.issuer = configs['issuer']
        provider.authorization_endpoint = configs['authorization_endpoint']
        provider.token_endpoint = configs['token_endpoint']
        provider.userinfo_endpoint = configs['userinfo_endpoint']
        provider.jwks_uri = configs['jwks_uri']

        if save:
            provider.save()

        log.debug('Provider %s succesfully discovered' % issuer)
        return provider

    @property
    def client_credentials(self):
        return self.client_id, self.client_secret

    @property
    def signing_keys(self):
        if self.signing_alg == self.RS256:
            # TODO perform caching, OBVIOUS
            return load_jwks_from_url(self.jwks_uri)

        return [SYMKey(key=str(self.client_secret))]

    def verify_id_token(self, token):
        log.debug('Verifying token %s' % token)
        header, claims, signature = token.split('.')
        header = b64decode(header)
        claims = b64decode(claims)

        if not signature:
            raise errors.InvalidIdToken()

        if header['alg'] not in ['HS256', 'RS256']:
            raise errors.UnsuppportedSigningMethod(header['alg'], ['HS256', 'RS256'])

        id_token = JWS().verify_compact(token, self.signing_keys)
        log.debug('Token verified, %s' % id_token)
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
    issuer = models.ForeignKey(OpenIDProvider)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
            related_name='oidc_account')

    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s: %s' % (self.sub, self.user)

    @classmethod
    def get_or_create(cls, id_token, access_token, refresh_token, provider):
        try:
            oidc_acc = cls.objects.get(sub=id_token['sub'])

            # Updating with new tokens
            oidc_acc.access_token = access_token
            oidc_acc.refresh_token = refresh_token
            oidc_acc.save()

            log.debug('OpenIDUser found, sub %s' % oidc_acc.sub)
            return oidc_acc
        except cls.DoesNotExist:
            pass

        claims = cls._get_userinfo(provider, id_token['sub'],
                access_token, refresh_token)

        try:
            user = UserModel.objects.get(username=claims['preferred_username'])
        except UserModel.DoesNotExist:
            user = UserModel()

            user.username = claims['preferred_username']
            user.email = claims['email']
            user.first_name = claims['given_name']
            user.last_name = claims['family_name']
            user.set_unusable_password()

            user.save()

        log.debug("OpenIDUser for sub %s not found, so it'll be created" % id_token['sub'])
        return cls.objects.create(sub=id_token['sub'], issuer=provider,
                user=user, access_token=access_token, refresh_token=refresh_token)

    @classmethod
    def _get_userinfo(self, provider, sub, access_token, refresh_token):
        # TODO encapsulate this?
        log.debug('Requesting userinfo in %s. sub: %s, access_token: %s' % (
            provider.userinfo_endpoint, sub, access_token))
        response = requests.get(provider.userinfo_endpoint, headers={
            'Authorization': 'Bearer %s' % access_token
        })

        if response.status_code != 200:
            raise errors.RequestError(provider.userinfo_endpoint, response.status_code)

        claims = response.json()

        if claims['sub'] != sub:
            raise errors.InvalidUserInfo()

        name = '%s %s' % (claims['given_name'], claims['family_name'])
        log.debug('userinfo of sub: %s -> name: %s, preferred_username: %s, email: %s' % (sub,
            name, claims['preferred_username'], claims['email']))

        return claims
