from django.conf.urls import patterns, url, include


urlpatterns = patterns('views',
    url(r'^$', 'index'),
    url(r'^oidc/', include('django_oidc_client.urls')),
)
