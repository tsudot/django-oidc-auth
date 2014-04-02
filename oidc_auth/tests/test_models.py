from urlparse import urljoin
import mock
from nose import tools

from oidc_auth.models import OpenIDProvider


class TestOpenIDPRovider(object):
    def __init__(self):
        self.issuer = 'http://example.it'
        self.configs = {
            'issuer': self.issuer,
            'authorization_endpoint': urljoin(self.issuer, 'authorize'),
            'token_endpoint': urljoin(self.issuer, 'token'),
            'userinfo_endpoint': urljoin(self.issuer, 'userinfo_endpoint'),
            'jwks_uri': urljoin(self.issuer, 'jwks_uri'),
        }

        # to be used with requests lib
        self.response_mock = mock.MagicMock()
        self.response_mock.status_code = 200
        self.response_mock.json.return_value = self.configs
    
    def tearDown(self):
        OpenIDProvider.objects.all().delete()
    
    def assert_provider_valid(self, provider, credentials=None):
        if not credentials:
            credentials = self.configs

        tools.assert_is_instance(provider, OpenIDProvider)
        tools.assert_equal(provider.issuer, credentials['issuer'])
        tools.assert_equal(provider.authorization_endpoint, credentials['authorization_endpoint'])
        tools.assert_equal(provider.token_endpoint, credentials['token_endpoint'])
        tools.assert_equal(provider.userinfo_endpoint, credentials['userinfo_endpoint'])
        tools.assert_equal(provider.jwks_uri, credentials['jwks_uri'])

    @mock.patch('requests.get')
    def test_discover_by_url(self, get_mock):
        get_mock.return_value = self.response_mock

        provider = OpenIDProvider.discover(issuer=self.issuer)

        get_mock.assert_called_with(urljoin(self.issuer, '.well-known/openid-configuration'))
        self.assert_provider_valid(provider)

    @mock.patch('requests.get')
    @mock.patch('oidc_auth.models._get_issuer')
    def test_discover_by_credentials(self, get_issuer_mock, get_mock):
        credentials = {
            'id_token': 'imagine this is a hash'
        }

        get_issuer_mock.return_value = self.issuer
        get_mock.return_value = self.response_mock

        provider = OpenIDProvider.discover(credentials=credentials)
        
        get_issuer_mock.assert_called_with(credentials['id_token'])
        self.assert_provider_valid(provider)
