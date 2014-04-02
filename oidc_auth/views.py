from urllib import urlencode
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from . import utils
from .settings import oidc_settings
from .forms import OpenIDConnectForm
from .models import OpenIDProvider


def login_begin(request, template_name='oidc/login.html',
        form_class=OpenIDConnectForm,
        login_complete_view='oidc-complete',
        redirect_field_name=REDIRECT_FIELD_NAME):

    if request.method == 'POST':
        return _redirect(request, login_complete_view, form_class)

    return render(request, template_name)


def _redirect(request, login_complete_view, form_class):
    form = form_class(request.POST)

    if form.is_valid():
        provider = OpenIDProvider.discover(issuer=form.cleaned_data['issuer'])
        params = urlencode({
            'response_type': 'code',
            'scope': utils.scopes(),
            'redirect_uri': request.build_absolute_uri(reverse(login_complete_view)),
            'client_id': oidc_settings.CLIENT_ID,
        })

        return redirect('%s?%s' % (provider.authorization_endpoint, params))
    
    # TODO what to do in case of fail?

def login_complete(request):
    pass
