from urlparse import urlparse, parse_qs
from django.test import Client
from nose import tools
import mock

from .utils import OIDCTestCase
from oidc_auth.models import OpenIDProvider
from oidc_auth.settings import oidc_settings



class TestAuthorizationPhase(OIDCTestCase):
    def __init__(self):
        super(TestAuthorizationPhase, self).__init__()
        self.client = Client()

    def tearDown(self):
        OpenIDProvider.objects.all().delete()

    def test_get_login(self):
        response = self.client.get('/oidc/login/')
        
        tools.assert_equal(response.status_code, 200)
        tools.assert_true(any(t.name == 'oidc/login.html' for t in response.templates))
    
    @mock.patch('requests.get')
    def test_post_login(self, get_mock):
        get_mock.return_value = self.response_mock

        with oidc_settings.override(CLIENT_ID='12345'):
            response = self.client.post('/oidc/login/', data={
                'issuer': 'http://example.it'
            })
    
        tools.assert_equal(response.status_code, 302)

        redirect_url = urlparse(response['Location'])
        tools.assert_equal('http://example.it', '%s://%s' % (redirect_url.scheme, redirect_url.hostname))

        params = parse_qs(redirect_url.query)
        tools.assert_equal(set(params.keys()),
            {'response_type', 'scope', 'redirect_uri', 'client_id'})

    @mock.patch('requests.get')
    def test_login_default_endpoint(self, get_mock):
        configs = dict(self.configs,
                authorization_endpoint='http://default.example.it/authorize')
        get_mock.return_value.status_code = 200
        get_mock.return_value.json.return_value = configs

        with oidc_settings.override(DEFAULT_ENDPOINT='http://default.example.it'):
            response = self.client.get('/oidc/login/')
    
        tools.assert_equal(response.status_code, 302)
        redirect_url = urlparse(response['Location'])
        tools.assert_equal('default.example.it', redirect_url.hostname)
