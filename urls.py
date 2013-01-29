from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$',              'extension_app.views.lookup'),
    url(r'^lookup$',        'extension_app.views.lookup'),
    url(r'^lookup_submit$', 'extension_app.views.lookup_submit'),
    url(r'^extend$',        'extension_app.views.extend'),
    url(r'^custom_extend$', 'extension_app.views.extend'),
    url(r'^result$',        'extension_app.views.results'),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/var/www/extension/extension_app/static', 'show_indexes':True}),

    # url(r'^$', 'extension.views.home', name='home'),
    # url(r'^extension/', include('extension.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django_cas.views.login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout'),
)
