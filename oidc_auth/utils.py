from .settings import oidc_settings


def scopes():
    scopes = set(oidc_settings.SCOPES)
    scopes.update({'openid', 'profile', 'email'})

    return ' '.join(scopes)
