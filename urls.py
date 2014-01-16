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
    #url(r'^userlist/(?P<day>\d{2})-(?P<month>\d{2})-(?P<year>\d{4})$', 'nabbeshreports.maps.views.userlist', name='userlist'),
    #url(r'^skillslist/$', 'nabbeshreports.maps.views.skillslist', name='skillslist'),
    #url(r'^skillslist/(\d{4})/$', 'nabbeshreports.maps.views.skillslistp', name='skillslistp'),
    #url(r'^userlistparam$', 'nabbeshreports.maps.views.userlistparam', name='userlistparam'),
    #url(r'^markerlist$', 'nabbeshreports.maps.views.markerlist', name='markerlist'),
    #url(r'^applicationlist$', 'nabbeshreports.maps.views.applicationlist', name='applicationlist'),
    #url(r'^skillsstatistics$', 'nabbeshreports.maps.views.skillsstatistics', name='skillsstatistics'),

    url(r'^freelancerdemography_report$', 'nabbeshreports.maps.views.freelancerdemography_report', name='freelancerdemography_report'),
    url(r'^freelancerdemography_getdata$', 'nabbeshreports.maps.views.freelancerdemography_getdata', name='freelancerdemography_getdata'),

    url(r'^freelancersgender_report$', 'nabbeshreports.maps.views.freelancersgender_report', name='freelancersgender_report'),
    url(r'^freelancersgender_getdata$', 'nabbeshreports.maps.views.freelancersgender_getdata', name='freelancersgender_getdata'),
    
    url(r'^freelancersages_report$', 'nabbeshreports.maps.views.freelancersages_report', name='freelancersages_report'),
    url(r'^freelancersages_getdata$', 'nabbeshreports.maps.views.freelancersages_getdata', name='freelancersages_getdata'),
    

    url(r'^dashboard$', 'nabbeshreports.maps.views.dashboard', name='dashboard'),
    url(r'^dashboard_getdata$', 'nabbeshreports.maps.views.dashboard_getdata', name='dashboard_getdata'),
    
    url(r'^jobs_employers_statistics$', 'nabbeshreports.maps.views.jobs_employers_statistics', name='jobs_employers_statistics'),
    url(r'^jobs_employers_statistics_getdata$', 'nabbeshreports.maps.views.jobs_employers_statistics_getdata', name='jobs_employers_statistics_getdata'),
    
    url(r'^jobs_applications_statistics$', 'nabbeshreports.maps.views.jobs_applications_statistics', name='jobs_applications_statistics'),
    url(r'^jobs_applications_statistics_getdata$', 'nabbeshreports.maps.views.jobs_applications_statistics_getdata', name='jobs_applications_statistics_getdata'),

    url(r'^sign_job_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_job_proposal_invoice_getdata', name='sign_job_proposal_invoice_getdata'),
    url(r'^sign_job_proposal_invoice$', 'nabbeshreports.maps.views.sign_job_proposal_invoice', name='sign_job_proposal_invoice'),
    
    url(r'^sign_application_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_application_proposal_invoice_getdata', name='sign_application_proposal_invoice_getdata'),
    url(r'^sign_application_proposal_invoice$', 'nabbeshreports.maps.views.sign_application_proposal_invoice', name='sign_application_proposal_invoice'),
    
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_STATIC}),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    #url(r'^accounts/', include('nabbeshreports.accounts.urls')),
    
)


