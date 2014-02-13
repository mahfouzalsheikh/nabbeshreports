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
    
    url(r'^freelancerseducation_report$', 'nabbeshreports.maps.views.freelancerseducation_report', name='freelancerseducation_report'),
    url(r'^freelancerseducation_getdata$', 'nabbeshreports.maps.views.freelancerseducation_getdata', name='freelancerseducation_getdata'),
    
    url(r'^freelancersages_report$', 'nabbeshreports.maps.views.freelancersages_report', name='freelancersages_report'),
    url(r'^freelancersages_getdata$', 'nabbeshreports.maps.views.freelancersages_getdata', name='freelancersages_getdata'),
    

    url(r'^dashboard$', 'nabbeshreports.maps.views.dashboard', name='dashboard'),
    url(r'^dashboard_getdata$', 'nabbeshreports.maps.views.dashboard_getdata', name='dashboard_getdata'),
    
    url(r'^jobs_employers_statistics$', 'nabbeshreports.maps.views.jobs_employers_statistics', name='jobs_employers_statistics'),
    url(r'^jobs_employers_statistics_getdata$', 'nabbeshreports.maps.views.jobs_employers_statistics_getdata', name='jobs_employers_statistics_getdata'),
    
    url(r'^jobs_applications_statistics$', 'nabbeshreports.maps.views.jobs_applications_statistics', name='jobs_applications_statistics'),
    url(r'^jobs_applications_statistics_getdata$', 'nabbeshreports.maps.views.jobs_applications_statistics_getdata', name='jobs_applications_statistics_getdata'),
    
    url(r'^jobs_communications_getdata$', 'nabbeshreports.maps.views.jobs_communications_getdata', name='jobs_communications_getdata'),
    

    url(r'^sign_job_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_job_proposal_invoice_getdata', name='sign_job_proposal_invoice_getdata'),
    url(r'^sign_job_proposal_invoice$', 'nabbeshreports.maps.views.sign_job_proposal_invoice', name='sign_job_proposal_invoice'),
    
    url(r'^sign_application_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_application_proposal_invoice_getdata', name='sign_application_proposal_invoice_getdata'),
    url(r'^sign_application_proposal_invoice$', 'nabbeshreports.maps.views.sign_application_proposal_invoice', name='sign_application_proposal_invoice'),
    
    url(r'^top_freelancers_getdata$', 'nabbeshreports.maps.views.top_freelancers_getdata', name='top_freelancers_getdata'),
    url(r'^top_freelancers$', 'nabbeshreports.maps.views.top_freelancers', name='top_freelancers'),
    
    url(r'^top_employers_getdata$', 'nabbeshreports.maps.views.top_employers_getdata', name='top_employers_getdata'),
    url(r'^top_employers$', 'nabbeshreports.maps.views.top_employers', name='top_employers'),
    
    
    url(r'^skillsdemography_report$', 'nabbeshreports.maps.views.skillsdemography_report', name='skillsdemography_report'),
    url(r'^skillsdemography_getdata$', 'nabbeshreports.maps.views.skillsdemography_getdata', name='skillsdemography_getdata'),  
    url(r'^skillsdemographydetails_getdata$', 'nabbeshreports.maps.views.skillsdemographydetails_getdata', name='skillsdemographydetails_getdata'),   
    
    url(r'^crosscountryapps_getdata$', 'nabbeshreports.maps.views.crosscountryapps_getdata', name='crosscountryapps_getdata'),
    url(r'^crosscountryapps_report$', 'nabbeshreports.maps.views.crosscountryapps_report', name='crosscountryapps_report'),    
    url(r'^geocodes$', 'nabbeshreports.maps.views.geocodes', name='geocodes'),
  
    
    url(r'^proposals_getdata$', 'nabbeshreports.maps.views.proposals_getdata', name='proposals_getdata'),
    url(r'^proposals_report$', 'nabbeshreports.maps.views.proposals_report', name='proposals_report'),

#    url(r'^invoices_getdata$', 'nabbeshreports.maps.views.invoices_getdata', name='invoices_getdata'),
#    url(r'^invoices_report$', 'nabbeshreports.maps.views.invoices_report', name='invoices_report'),

#    url(r'^escrow_getdata$', 'nabbeshreports.maps.views.escrow_getdata', name='escrow_getdata'),
#    url(r'^escrow_report$', 'nabbeshreports.maps.views.escrow_report', name='escrow_report'),

    
    url(r'^googleanalytics_report$', 'nabbeshreports.maps.views.googleanalytics_report', name='googleanalytics_report'),
    
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_STATIC}),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    
    
)


