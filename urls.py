from django.conf.urls import patterns, url, include
#from django.conf.urls.defaults import *
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
    url(r'^$', 'maps.views.home', name='home'),
 
######################## main metrics #################
 
 
    url(r'^mainmetrics$', 'maps.views.dashboard'),
    url(r'^dashboard_getdata$', 'maps.views.dashboard_getdata'),
    
    url(r'^growthdashboard$', 'maps.views.growth_dashboard'),
    url(r'^growthdashboard_getdata$', 'maps.views.growthdashboard_getdata'),
    
    url(r'^analytics_getdata$', 'maps.views.analytics_getdata'),
    
    

######################## Community ##################    
    
    url(r'^freelancerdemographicprofile$', 'maps.views.freelancerdemography_report'),
    url(r'^freelancerdemography_getdata$', 'maps.views.freelancerdemography_getdata'), 
    
    url(r'^freelancersgender$', 'maps.views.freelancersgender_report'),
    url(r'^freelancersgender_getdata$', 'maps.views.freelancersgender_getdata'),    
    
    url(r'^freelancersages$', 'maps.views.freelancersages_report'),
    url(r'^freelancersages_getdata$', 'maps.views.freelancersages_getdata'),   
    
    url(r'^freelancerseducation$', 'maps.views.freelancerseducation_report'),
    url(r'^freelancerseducation_getdata$', 'maps.views.freelancerseducation_getdata'),      

    url(r'^jobscategories$', 'maps.views.jobs_categories_report'),
    url(r'^jobscategories_getdata$', 'maps.views.jobs_categories_getdata'),      
    
    url(r'^topfreelancers$', 'maps.views.top_freelancers'),  
    url(r'^top_freelancers_getdata$', 'maps.views.top_freelancers_getdata'),


    url(r'^topemployers$', 'maps.views.top_employers'),
    url(r'^top_employers_getdata$', 'maps.views.top_employers_getdata'),
    
    url(r'^crmclients$', 'maps.views.crmclients_report'),
    url(r'^crmclients_getdata$', 'maps.views.crmclients_getdata'),
    
    url(r'^useractivities$', 'maps.views.user_report'),
    url(r'^useractivities/([0-9]{1,7})$', 'maps.views.user_report'),
    #url(r'^useractivities$', 'maps.views.user_report'),
    url(r'^find_user_getdata$', 'maps.views.find_user_getdata'),    
    url(r'^user_personalinfo_getdata$', 'maps.views.user_personalinfo_getdata'),
    url(r'^user_jobs_getdata$', 'maps.views.user_jobs_getdata'),
    url(r'user_applications_getdata$', 'maps.views.user_applications_getdata'),


######################## Activity #####################

    url(r'^jobsemployersstatistics$', 'maps.views.jobs_employers_statistics'),
    url(r'^jobs_employers_statistics_getdata$', 'maps.views.jobs_employers_statistics_getdata', name='maps.views.jobs_employers_statistics_getdata'),
    
    url(r'^jobsapplicationsstatistics$', 'maps.views.jobs_applications_statistics'),
    url(r'^jobs_applications_statistics_getdata$', 'maps.views.jobs_applications_statistics_getdata'), 
    url(r'^jobs_communications_getdata$', 'maps.views.jobs_communications_getdata'),  


    url(r'^paymentstracking$', 'maps.views.paymentstracking_report'),
    url(r'^paymentstracking_getdata$', 'maps.views.paymentstracking_getdata'), 
    url(r'^paymentstracking_actions_getdata$', 'maps.views.paymentstracking_actions_getdata'),  


    url(r'^employersfunnel$', 'maps.views.sign_job_proposal_invoice'),     
    url(r'^sign_job_proposal_invoice_getdata$', 'maps.views.sign_job_proposal_invoice_getdata'),
   
    url(r'^freelancersfunnel$', 'maps.views.sign_application_proposal_invoice'),
    url(r'^sign_application_proposal_invoice_getdata$', 'maps.views.sign_application_proposal_invoice_getdata'),
    
    url(r'^crosscountryapps$', 'maps.views.crosscountryapps_report'),    
    url(r'^crosscountryapps_getdata$', 'maps.views.crosscountryapps_getdata'),    
    url(r'^geocodes$', 'maps.views.geocodes'),    
     
    url(r'^jobsappsstatsreport$', 'maps.views.jobs_apps_stats_report'),  
    url(r'^jobs_apps_stats_getdata$', 'maps.views.jobs_apps_stats_getdata'),
  
    url(r'^signups_apps_retention_getdata$', 'maps.views.signups_apps_retention_getdata'),
    url(r'^signupsappsretention$', 'maps.views.signups_apps_retention_report'),

    url(r'^jobs_apps_retention_getdata$', 'maps.views.jobs_apps_retention_getdata'),
    url(r'^jobsappsretention$', 'maps.views.jobs_apps_retention_report'),

    url(r'^signups_jobs_retention_getdata$', 'maps.views.signups_jobs_retention_getdata'),
    url(r'^signupsjobsretention$', 'maps.views.signups_jobs_retention_report'),
    
    url(r'^activities_countries_getdata$', 'maps.views.activities_countries_getdata'),
    url(r'^activitiescountries$', 'maps.views.activities_countries_report'),
    
    
    url(r'^dealaveragetime_getdata$', 'maps.views.dealaveragetime_getdata'),
    url(r'^dealsaveragetimegeneral_getdata$', 'maps.views.dealsaveragetimegeneral_getdata'),      
    url(r'^dealaveragetime$', 'maps.views.dealaveragetime_report'),
  
    
#################### Finance ##########################    

    url(r'^proposals_getdata$', 'maps.views.proposals_getdata'),
    url(r'^proposals$', 'maps.views.proposals_report'),

    url(r'^invoices_getdata$', 'maps.views.invoices_getdata'),
    url(r'^invoices$', 'maps.views.invoices_report'),
    
    url(r'^pendinginvoices_getdata$', 'maps.views.pendinginvoices_getdata'),
    url(r'^pendingratings_getdata$', 'maps.views.pendingratings_getdata'),
    url(r'^pendinginvoices$', 'maps.views.pendinginvoices_report'),
    
    url(r'^payers_getdata$', 'maps.views.payers_getdata'),
    url(r'^payers$', 'maps.views.payers_report'),

    url(r'^payees_getdata$', 'maps.views.payees_getdata'),
    url(r'^payees$', 'maps.views.payees_report'),

    url(r'^payments_getdata$', 'maps.views.payments_getdata'),
    url(r'^payments$', 'maps.views.payments_report'),
    
    url(r'^revenue_getdata$', 'maps.views.revenue_getdata'),
    url(r'^revenue$', 'maps.views.revenue_report'),

################## Skills #############################

    url(r'^skillsdemographicprofile$', 'maps.views.skillsdemography_report'),
    url(r'^skillsdemography_getdata$', 'maps.views.skillsdemography_getdata'),  
    url(r'^skillsdemographydetails_getdata$', 'maps.views.skillsdemographydetails_getdata'),   
    
    url(r'^skillsdistribution$', 'maps.views.skillsdistribution_report'),
    url(r'^skillsdistribution_getdata$', 'maps.views.skillsdistribution_getdata'), 


################## Totals #############################

    url(r'^totalusers_getdata$', 'maps.views.total_users_getdata'), 
    url(r'^totaljobs_getdata$', 'maps.views.total_jobs_getdata'),
    url(r'^totalskills_getdata$', 'maps.views.total_skills_getdata'),          
    url(r'^totalproposals_getdata$', 'maps.views.total_proposals_getdata'),    
    url(r'^totalapplications_getdata$', 'maps.views.total_applications_getdata'), 
    url(r'^totalmessages_getdata$', 'maps.views.total_messages_getdata'),   
    url(r'^totalinvoices_getdata$', 'maps.views.total_invoices_getdata'),            
    url(r'^totalescrow_getdata$', 'maps.views.total_escrow_getdata'),    
    
    url(r'^trackingmessages_getdata$', 'maps.views.tracking_messages_getdata'),
    url(r'^userprofileinfo_getdata$', 'maps.views.userprofileinfo_getdata'),
    url(r'^trackingvisitors_getdata$', 'maps.views.tracking_visitors_getdata'),
    
#######################################################    

    url(r'^crm_notes_getdata$', 'maps.views.crm_notes_getdata'),
    url(r'^crm_notes_add$', 'maps.views.crm_notes_add'),
    url(r'^crm_notes_delete$', 'maps.views.crm_notes_delete'),

    url(r'^photogallery$', 'maps.views.photogallery_report'),
    url(r'^photogallery_getdata$', 'maps.views.photogallery_getdata'),
    
    url(r'^leakagedetection$', 'maps.views.leakagedetection_report'),
    url(r'^leakagedetection_getdata$', 'maps.views.leakagedetection_getdata'),
   
    url(r'^skillscategorizer$', 'maps.views.skillscategorizer_tool'),
    url(r'^addcategory$', 'maps.views.addcategory'),
    url(r'^updatecategory$', 'maps.views.updatecategory'),    
    url(r'^deletecategory$', 'maps.views.deletecategory'),
    url(r'^getcategories$', 'maps.views.getcategories'),
    url(r'^getcategoriestree$', 'maps.views.getcategoriestree'),
    url(r'^getcategoriesbubbles$', 'maps.views.getcategoriesbubbles'),
    url(r'^getcurrentskill$', 'maps.views.getcurrentskill'),
    url(r'^getsuggestedskillslist$', 'maps.views.getsuggestedskillslist'),  
    url(r'^suggestcategory$', 'maps.views.suggestcategory'),  
    url(r'^getskillsbycategory$', 'maps.views.getskillsbycategory'),  
    url(r'^categorize$', 'maps.views.categorize'),
    url(r'^categorizegroup$', 'maps.views.categorizegroup'),
    url(r'^uncategorize$', 'maps.views.uncategorize'),
    url(r'^uncategorizegroup$', 'maps.views.uncategorizegroup'),
    url(r'^updateskillcat$', 'maps.views.updateskillcat'),
    url(r'^updateskillgroupcat$', 'maps.views.updateskillgroupcat'),
    url(r'^categorizationstatus$', 'maps.views.categorizationstatus'),    
    url(r'^suggestcategory$', 'maps.views.suggestcategory'),  
    
    
    url(r'^download$', 'maps.views.download'),  
    
    url(r'^tracker$', 'maps.views.tracker_image'),  
   
    url(r'^emailcampaigns$', 'maps.views.campaigns_report'),
    url(r'^campaigns_list_getdata$', 'maps.views.campaigns_list_getdata'),    
    url(r'^emailcampaign_getdata$', 'maps.views.emailcampaign_getdata'),
    
    
    url(r'^vistest_report$', 'maps.views.vistest_report'),
    url(r'^categorypacks_report$', 'maps.views.categorypacks_report'),

    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_STATIC}),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    
    
)


