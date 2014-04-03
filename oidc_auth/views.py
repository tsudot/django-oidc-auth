from urllib import urlencode
from django.http import HttpResponseBadRequest
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
import requests

from . import utils
from .settings import oidc_settings
from .forms import OpenIDConnectForm
from .models import OpenIDProvider, Nonce


def login_begin(request, template_name='oidc/login.html',
        form_class=OpenIDConnectForm,
        login_complete_view='oidc-complete',
        redirect_field_name=REDIRECT_FIELD_NAME):

    if oidc_settings.DEFAULT_ENDPOINT or request.method == 'POST':
        return _redirect(request, login_complete_view, form_class)

    return render(request, template_name)


def _redirect(request, login_complete_view, form_class):
    redirect_url = oidc_settings.DEFAULT_ENDPOINT
    if not redirect_url:
        form = form_class(request.POST)
        if form.is_valid():
            redirect_url = form.cleaned_data['issuer']
        else:
            raise RuntimeError()  # TODO fix this

    provider = OpenIDProvider.discover(issuer=redirect_url)
    params = urlencode({
        'response_type': 'code',
        'scope': utils.scopes(),
        'redirect_uri': request.build_absolute_uri(reverse(login_complete_view)),
        'client_id': oidc_settings.CLIENT_ID,
        'state': Nonce.generate(provider.issuer)
    })

    return redirect('%s?%s' % (provider.authorization_endpoint, params))
    

def login_complete(request, login_complete_view='oidc-complete'):
    if 'code' not in request.GET and 'state' not in request.GET:
        return HttpResponseBadRequest('Invalid request')

    issuer = Nonce.objects.get(hash=request.GET['state']).issuer_url
    provider = OpenIDProvider.objects.get(issuer=issuer)

    params = {
        'grant_type': 'authorization_code',
        'code': request.GET['code'],
        'redirect_uri': request.build_absolute_uri(reverse(login_complete_view)),
    }

    response = requests.post(provider.token_endpoint, auth=provider.client_credentials,
            params=params)

    from django.http import HttpResponse
    return HttpResponse('ok')
