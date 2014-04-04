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
######################## home #########################
    url(r'^$', 'nabbeshreports.maps.views.home', name='home'),
 
######################## main metrics #################
 
 
    url(r'^mainmetrics$', 'nabbeshreports.maps.views.dashboard'),
    url(r'^dashboard_getdata$', 'nabbeshreports.maps.views.dashboard_getdata'),
    url(r'^analytics_getdata$', 'nabbeshreports.maps.views.analytics_getdata'),
    
    

######################## Freelancers ##################    
    
    url(r'^freelancerdemographicprofile$', 'nabbeshreports.maps.views.freelancerdemography_report'),
    url(r'^freelancerdemography_getdata$', 'nabbeshreports.maps.views.freelancerdemography_getdata'), 
    
    url(r'^freelancersgender$', 'nabbeshreports.maps.views.freelancersgender_report'),
    url(r'^freelancersgender_getdata$', 'nabbeshreports.maps.views.freelancersgender_getdata'),    
    
    url(r'^freelancersages$', 'nabbeshreports.maps.views.freelancersages_report'),
    url(r'^freelancersages_getdata$', 'nabbeshreports.maps.views.freelancersages_getdata'),   
    
    url(r'^freelancerseducation$', 'nabbeshreports.maps.views.freelancerseducation_report'),
    url(r'^freelancerseducation_getdata$', 'nabbeshreports.maps.views.freelancerseducation_getdata'),      
    
    url(r'^topfreelancers$', 'nabbeshreports.maps.views.top_freelancers'),  
    url(r'^top_freelancers_getdata$', 'nabbeshreports.maps.views.top_freelancers_getdata'),


######################## Employers ####################
    url(r'^topemployers$', 'nabbeshreports.maps.views.top_employers'),
    url(r'^top_employers_getdata$', 'nabbeshreports.maps.views.top_employers_getdata'),



######################## Activity #####################

    url(r'^jobsemployersstatistics$', 'nabbeshreports.maps.views.jobs_employers_statistics'),
    url(r'^jobs_employers_statistics_getdata$', 'nabbeshreports.maps.views.jobs_employers_statistics_getdata'),
    
    url(r'^jobsapplicationsstatistics$', 'nabbeshreports.maps.views.jobs_applications_statistics'),
    url(r'^jobs_applications_statistics_getdata$', 'nabbeshreports.maps.views.jobs_applications_statistics_getdata'), 
    url(r'^jobs_communications_getdata$', 'nabbeshreports.maps.views.jobs_communications_getdata'),  

    url(r'^employersfunnel$', 'nabbeshreports.maps.views.sign_job_proposal_invoice'),     
    url(r'^sign_job_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_job_proposal_invoice_getdata'),
   
    url(r'^freelancersfunnel$', 'nabbeshreports.maps.views.sign_application_proposal_invoice'),
    url(r'^sign_application_proposal_invoice_getdata$', 'nabbeshreports.maps.views.sign_application_proposal_invoice_getdata'),
    
    url(r'^crosscountryapps$', 'nabbeshreports.maps.views.crosscountryapps_report'),    
    url(r'^crosscountryapps_getdata$', 'nabbeshreports.maps.views.crosscountryapps_getdata'),    
    url(r'^geocodes$', 'nabbeshreports.maps.views.geocodes'),    
    
    url(r'^jobsappsstatsreport$', 'nabbeshreports.maps.views.jobs_apps_stats_report'),  
    url(r'^jobs_apps_stats_getdata$', 'nabbeshreports.maps.views.jobs_apps_stats_getdata'),
  
    url(r'^signups_apps_retention_getdata$', 'nabbeshreports.maps.views.signups_apps_retention_getdata'),
    url(r'^signupsappsretention$', 'nabbeshreports.maps.views.signups_apps_retention_report'),

    url(r'^jobs_apps_retention_getdata$', 'nabbeshreports.maps.views.jobs_apps_retention_getdata'),
    url(r'^jobsappsretention$', 'nabbeshreports.maps.views.jobs_apps_retention_report'),

    url(r'^signups_jobs_retention_getdata$', 'nabbeshreports.maps.views.signups_jobs_retention_getdata'),
    url(r'^signupsjobsretention$', 'nabbeshreports.maps.views.signups_jobs_retention_report'),
    
    url(r'^activities_countries_getdata$', 'nabbeshreports.maps.views.activities_countries_getdata'),
    url(r'^activitiescountries$', 'nabbeshreports.maps.views.activities_countries_report'),
#################### Finance ##########################    

    url(r'^proposals_getdata$', 'nabbeshreports.maps.views.proposals_getdata'),
    url(r'^proposals$', 'nabbeshreports.maps.views.proposals_report'),

    url(r'^invoices_getdata$', 'nabbeshreports.maps.views.invoices_getdata'),
    url(r'^invoices$', 'nabbeshreports.maps.views.invoices_report'),


################## Skills #############################

    url(r'^skillsdemographicprofile$', 'nabbeshreports.maps.views.skillsdemography_report'),
    url(r'^skillsdemography_getdata$', 'nabbeshreports.maps.views.skillsdemography_getdata'),  
    url(r'^skillsdemographydetails_getdata$', 'nabbeshreports.maps.views.skillsdemographydetails_getdata'),   
    
    url(r'^skillsdistribution$', 'nabbeshreports.maps.views.skillsdistribution_report'),
    url(r'^skillsdistribution_getdata$', 'nabbeshreports.maps.views.skillsdistribution_getdata'), 

#######################################################    

    url(r'^vistest_report$', 'nabbeshreports.maps.views.vistest_report'),

    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_STATIC}),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    
    
)


