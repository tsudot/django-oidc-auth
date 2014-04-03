import json
from jwkest.jws import JWS
from django.contrib.auth import get_user_model

from .models import OpenIDProvider, OpenIDUser

UserModel = get_user_model()


class OpenIDConnectBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = True

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

    def authenticate(self, **kwargs):
        try:
            credentials = kwargs.get('credentials')
            if not credentials:
                return None
    
            provider = OpenIDProvider.discover(credentials=credentials)
            id_token = JWS().verify_compact(credentials['id_token'], provider.signing_keys())

            oidc_user = OpenIDUser.get_or_create(json.loads(id_token),
                    credentials['access_token'],
                    credentials.get('refresh_token', ''),
                    provider)
        except Exception as e:
            import ipdb; ipdb.set_trace()

        return oidc_user.user
