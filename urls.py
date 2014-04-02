from django.conf.urls import patterns, url, include


urlpatterns = patterns('views',
    url(r'^$', 'index'),
    url(r'^oidc/', include('oidc_auth.urls')),
)
