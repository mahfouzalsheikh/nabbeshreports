from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static


#from django.conf.urls import patterns, include, url
#from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'nabbeshreports.maps.views.home', name='home'),
    url(r'^userlist/(?P<day>\d{2})-(?P<month>\d{2})-(?P<year>\d{4})$', 'nabbeshreports.maps.views.userlist', name='userlist'),
    url(r'^skillslist/$', 'nabbeshreports.maps.views.skillslist', name='skillslist'),
    url(r'^skillslist/(\d{4})/$', 'nabbeshreports.maps.views.skillslistp', name='skillslistp'),
    url(r'^userlistparam$', 'nabbeshreports.maps.views.userlistparam', name='userlistparam'),
    url(r'^markerlist$', 'nabbeshreports.maps.views.markerlist', name='markerlist'),
    url(r'^applicationlist$', 'nabbeshreports.maps.views.applicationlist', name='applicationlist'),
    url(r'^skillsstatistics$', 'nabbeshreports.maps.views.skillsstatistics', name='skillsstatistics'),

    url(r'^report1$', 'nabbeshreports.maps.views.report1', name='report1'),

    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_STATIC}),

)
