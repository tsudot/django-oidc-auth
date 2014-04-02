from urlparse import urljoin
import mock
from nose import tools

from oidc_auth.models import OpenIDProvider


class TestOpenIDPRovider(object):
    @mock.patch('requests.get')
    def test_discover_by_url(self, get_mock):
        issuer = 'http://example.it'
        configs = {
            'issuer': issuer,
            'authorization_endpoint': urljoin(issuer, 'authorize'),
            'token_endpoint': urljoin(issuer, 'token'),
            'userinfo_endpoint': urljoin(issuer, 'userinfo_endpoint'),
            'jwks_uri': urljoin(issuer, 'jwks_uri'),
        }

        response_mock = get_mock.return_value
        response_mock.status_code = 200
        response_mock.json.return_value = configs

        provider = OpenIDProvider.discover(issuer=issuer)

        get_mock.assert_called_with(urljoin(issuer, '.well-known/openid-configuration'))
        tools.assert_is_instance(provider, OpenIDProvider)
        tools.assert_equal(provider.issuer, configs['issuer'])
        tools.assert_equal(provider.authorization_endpoint, configs['authorization_endpoint'])
        tools.assert_equal(provider.token_endpoint, configs['token_endpoint'])
        tools.assert_equal(provider.userinfo_endpoint, configs['userinfo_endpoint'])
        tools.assert_equal(provider.jwks_uri, configs['jwks_uri'])
