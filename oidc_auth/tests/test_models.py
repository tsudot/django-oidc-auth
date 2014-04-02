from urlparse import urljoin
import mock
from nose import tools

from .utils import OIDCTestCase
from oidc_auth.models import OpenIDProvider


class TestOpenIDPRovider(OIDCTestCase):
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

    @mock.patch('requests.get')
    def test_discover_existing_provider(self, get_mock):
        existing_provider = OpenIDProvider.objects.create(issuer='http://example.it')
        get_mock.return_value = self.response_mock

        found_provider = OpenIDProvider.discover(issuer='http://example.it')

        tools.assert_equal(found_provider.id, existing_provider.id)
