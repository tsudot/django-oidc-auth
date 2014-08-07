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

        get_mock.assert_called_with(urljoin(self.issuer, '.well-known/openid-configuration'), verify=True)
        self.assert_provider_valid(provider)

    @mock.patch('requests.get')
    def test_discover_by_credentials(self, get_mock):
        credentials = {
            'id_token': 'imagine this is a hash'
        }

        get_mock.return_value = self.response_mock

        with mock.patch.object(OpenIDProvider, '_get_issuer') as _get_issuer:
            _get_issuer.return_value = self.issuer
            provider = OpenIDProvider.discover(credentials=credentials)
            _get_issuer.assert_called_with(credentials['id_token'])

        self.assert_provider_valid(provider)

    @mock.patch('requests.get')
    def test_discover_existing_provider(self, get_mock):
        existing_provider = OpenIDProvider.objects.create(issuer='http://example.it')
        get_mock.return_value = self.response_mock

        found_provider = OpenIDProvider.discover(issuer='http://example.it')

        tools.assert_equal(found_provider.id, existing_provider.id)

    def test_get_default_provider(self):
        pass
