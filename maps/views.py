# Create your views here.
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.template import Context, loader
from django.http import HttpResponse
from django.shortcuts import render_to_response
from legacy.models import Users, AuthUser, SkillsSkill
from django.utils import simplejson
from django.template import Template, Context
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
import datetime
import time
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import connection
from django.db import connections
from django.contrib.auth.decorators import login_required,user_passes_test
import sys
import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from django.contrib.admin.views.decorators import staff_member_required

import urllib
import itertools
import json
from django.utils.timezone import utc


# Declare constants and set configuration values

# The file with the OAuth 2.0 Client details for authentication and authorization.
CLIENT_SECRETS = 'client_secrets.json'

# A helpful message to display if the CLIENT_SECRETS file is missing.
MISSING_CLIENT_SECRETS_MESSAGE = '%s is missing' % CLIENT_SECRETS

# The Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/analytics.readonly',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

# A file to store the access token
TOKEN_FILE_NAME = 'analytics.dat'

def prepare_credentials():
  # Retrieve existing credendials
  storage = Storage(TOKEN_FILE_NAME)
  
  credentials = storage.get()
  print credentials
  # If existing credentials are invalid and Run Auth flow
  # the run method will store any new credentials
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage) #run Auth Flow and store credentials

  return credentials
  
def initialize_service():
  # 1. Create an http object
  http = httplib2.Http()
  
  # 2. Authorize the http object
  # In this tutorial we first try to retrieve stored credentials. If
  # none are found then run the Auth Flow. This is handled by the
  # prepare_credentials() function defined earlier in the tutorial
  credentials = prepare_credentials()
  
  http = credentials.authorize(http)  # authorize the http object

  # 3. Build the Analytics Service Object with the authorized http object
  return build('analytics', 'v3', http=http)
  
 


@login_required(login_url='/accounts/login/')
def home(request):    
    t = loader.get_template('index.html')   
    return render_to_response('index.html', context_instance=RequestContext(request))


def customQuery(sql, db):
    ###print sql
    if db==0:
        result=customQueryOffline(sql)
        #print result
        return result
    elif db==1:
        result=customQueryLive(sql)
        #print result
        return result
    elif db==2: 
        result=customQueryOld(sql)
        #print result
        return result    
    elif db==3:
        result=customQuerySendy(sql)
        return result 
    elif db==4:
        result=customQueryLiveWrite(sql)
        return result           
    
    


def customQueryOffline(sql):
    cursor = connections['offline'].cursor()    
    cursor.execute(sql,[])
    #transaction.commit_unless_managed(using='offline')
    
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list 

def customQueryLive(sql): 
    cursor = connections['live'].cursor()
    cursor.execute(sql,[])
    #transaction.commit_unless_managed(using='live')
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list 

def customQueryOld(sql): 
    cursor = connections['old'].cursor()
    cursor.execute(sql,[])
    #transaction.commit_unless_managed(using='live')
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list 


def customQuerySendy(sql): 
    
    cursor = connections['sendy'].cursor()
    cursor.execute(sql,[])
    #transaction.commit_unless_managed(using='live')
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list 

def customQueryLiveWrite(sql): 
    cursor = connections['livewrite'].cursor()
    cursor.execute(sql,[])
    #transaction.commit_unless_managed(using='live')
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list     


def customQueryNoResults(sql, db):
    ###print sql
    if db==0:
        result=customQueryNoResultsOffline(sql)
        #print result
        return result
    elif db==1:
        result=customQueryNoResultsLive(sql)
        #print result
        return result
    elif db==2: 
        result=customQueryNoResultsOld(sql)
        #print result
        return result    
    elif db==3:
        result=customQueryNoResultsSendy(sql)
        return result    
    elif db==4:
        result=customQueryNoResultsLiveWrite(sql)
        return result           

def customQueryNoResultsLive(sql):
    cursor = connections['live'].cursor()    
   
    result = cursor.execute(sql,[])
    cursor.execute("COMMIT;")
    print result
    return 'done' 

def customQueryNoResultsOffline(sql):
    cursor = connections['offline'].cursor()    
   
    result = cursor.execute(sql,[])
    cursor.execute("COMMIT;")
    print result
    return 'done'

def customQueryNoResultsOld(sql):
    cursor = connections['old'].cursor()    
   
    result = cursor.execute(sql,[])
    cursor.execute("COMMIT;")
    print result
    return 'done'

def customQueryNoResultsSendy(sql):
    cursor = connections['sendy'].cursor()    
   
    result = cursor.execute(sql,[])
    cursor.execute("COMMIT;")
    print result
    return 'done' 

def customQueryNoResultsLiveWrite(sql):
    cursor = connections['livewrite'].cursor()    
   
    result = cursor.execute(sql,[])
    cursor.execute("COMMIT;")
    print result
    return 'done'               
       
@login_required(login_url='/accounts/login/')       
def freelancerdemography_report(request):
    
    t = loader.get_template('./reports/freelancerdemography_report.html')
    c = Context({
        'freelancerdemography_report': freelancerdemography_report,
    })
    return render_to_response('./reports/freelancerdemography_report.html', context_instance=RequestContext(request))

    
    
@csrf_exempt
def freelancerdemography_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        grouper = objs['grouper']
        sql = ("select "+grouper+", count(id) as usercount from users where "+grouper+" is not null and "+grouper+" <>''  group by "+grouper+" order by usercount desc")
 
        results = customQuery(sql,1)

        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('freelancersdemography.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        
        
        
        
        
@login_required(login_url='/accounts/login/')
def freelancersgender_report(request):
    
    t = loader.get_template('./reports/freelancersgender_report.html')
    c = Context({
        'freelancersgender_report': freelancersgender_report,
    })
    #return HttpResponse(t.render(c))
    return render_to_response('./reports/freelancersgender_report.html', context_instance=RequestContext(request))
    
            
@csrf_exempt
def freelancersgender_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)
        
        #detect("https://s3.amazonaws.com/fideloper.com/faces_orig.jpg")
        
        sql = "select usercount, case gender when 0 then 'Male' when 1 then 'Female' end from \
         (select count(*) as usercount, gender from users where gender < 2 group by gender) total;"
        results = customQuery(sql,1)
        print results
 
        c = Context({'genders': results})
   
        return HttpResponse(render_to_string('freelancersgender.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        
        
        
@login_required(login_url='/accounts/login/')
def freelancerseducation_report(request):
    
    t = loader.get_template('./reports/freelancerseducation_report.html')
    c = Context({
        'freelancerseducation_report': freelancerseducation_report,
    })
    return render_to_response('./reports/freelancerseducation_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def freelancerseducation_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select  case degree when 6 then 'Bachelor of Science' when 7 then 'High School' when 5 then 'Bachelor of Arts' when 4 then 'Executive MBA' when 3 then 'MBA' when 2 then 'Masters' when 1 then 'PHD' end as education, usercount from (select count(distinct u.id ) as usercount, edu.degree from education edu inner join users u on edu.id_user=u.id group by edu.degree) total"
        
        #print sql
        results = customQuery(sql,1)
        print results
 
        c = Context({'educations': results})
   
        return HttpResponse(render_to_string('freelancerseducation.json', c, context_instance=RequestContext(request)), mimetype='application/json')



@login_required(login_url='/accounts/login/')
def jobs_categories_report(request):
    
    t = loader.get_template('./reports/jobs_categories_report.html')
    c = Context({
        'jobs_categories_report': jobs_categories_report,
    })
    return render_to_response('./reports/jobs_categories_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def jobs_categories_getdata(request):
    if request.method == 'POST':

        objs = simplejson.loads(request.raw_post_data)
        print objs
        
        fromdate = objs['fromdate']  + ' 00:00:00+00'
        todate = objs['todate'] + ' 23:59:59+00'

        sql = "select final.category,final.total_jobs,final.converted as paid_invoices, final.paid_amount, round(100 * total_jobs/ sum(total_jobs) over(), 2),   round(100 * converted::numeric/ total_jobs::numeric, 2)  from ( select category, count(distinct job_id) as total_jobs,  sum( paid_invoices) as converted, sum(paid_amount) as paid_amount, count(distinct case when paid_invoices>0 then job_id else null end) as converted_count from (select distinct  catjobs.*,  count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as paid_invoices, sum(distinct case when ci.status=4 then cii.unit_price*cii.quantity else 0 end) as paid_amount from ( select job_id,cat_id, category  from ( select cj.id as job_id, cats.id as cat_id, cats.name as category, similarity(cj.title, cats.name) as coef from contracts_job cj inner join contracts_requiredskill crs on crs.job_id=cj.id  left outer join skills_skills_subcategories sssc on sssc.skill_id=crs.skill_id left outer  join skills_subcategories ssc on ssc.id=sssc.subcategory_id inner join skills_subcategories cats on cats.id=ssc.category_id where cj.approved=true and cj.created_at>='"+ fromdate +"' and cj.created_at<='"+todate+"'   group by cj.id, cats.id order by job_id, coef desc ) t1 where coef= (select max(coef) from  ( select cj.id as job_id, cats.id as cat_id, similarity(cj.title, cats.name) as coef from contracts_job cj inner join contracts_requiredskill crs on crs.job_id=cj.id  left outer join skills_skills_subcategories sssc on sssc.skill_id=crs.skill_id left outer  join skills_subcategories ssc on ssc.id=sssc.subcategory_id inner join skills_subcategories cats on cats.id=ssc.category_id where cj.approved=true and cj.created_at>='"+ fromdate +"' and cj.created_at<='"+todate+"' and category<>'All' group by cj.id, cats.id  order by job_id, coef desc ) t2 where t1.job_id=t2.job_id)) catjobs left outer join contracts_application ca on catjobs.job_id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_invoice ci on ci.message_ptr_id=cm.id left outer join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id group by catjobs.job_id, catjobs.cat_id, catjobs.category) total group by category order by total_jobs desc ) final "
        
        print sql
        results = customQuery(sql,1)
        print results
 
        c = Context({'categories': results})
   
        return HttpResponse(render_to_string('jobs_categories.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        

@login_required(login_url='/accounts/login/')
def freelancersages_report(request):
    
    t = loader.get_template('./reports/freelancersages_report.html')
    c = Context({
        'freelancersages_report': freelancersgender_report,
    })
    #return HttpResponse(t.render(c))
    return render_to_response('./reports/freelancersages_report.html', context_instance=RequestContext(request))

@csrf_exempt            
def freelancersages_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select  sum(ucount) as usercounts,case when ageu <18 then '1) Under 18' when ageu >= 18 and ageu<=24 then '2) 18 to 24' when ageu >= 25 and ageu<=34 then '3) 25 to 34' when ageu >= 35 then '4) Over 35' END as age_range from (select count(total.id) as ucount, 2013 - total.yobn as ageu from (select t1.id, t1.yob :: integer yobn from(select id, substring(dob,length(dob)-3, length(dob)) as yob from users where dob<>'') t1 where t1.yob ~E'^\\\d+$') total group by ageu order by ageu) total group by age_range order by age_range;"
        results = customQuery(sql,1)

        #print sql
        c = Context({'ages': results})
        return HttpResponse(render_to_string('freelancersages.json', c, context_instance=RequestContext(request)), mimetype='application/json')        
        
        
 
@login_required(login_url='/accounts/login/')	
def dashboard(request):
    
    t = loader.get_template('./reports/dashboard.html')
    return render_to_response('./reports/dashboard.html', context_instance=RequestContext(request))
    


@csrf_exempt 
def datefieldtostring(datefieldname, segment):
    day = " Trim(' ' from to_char(date_part('day' , "+datefieldname+"),'09'))  "    
    week = " Trim(' ' from to_char(date_part('week' , "+datefieldname+" + interval '1 DAY'),'09'))  "
    month = " Trim(' ' from to_char(date_part('month' , "+datefieldname+"),'09'))  "
    year = " date_part('year' , "+datefieldname+") "  

    
    if segment== "Day":
        return year+ "||'-'||"+month+"||'-'||"+ day
    elif segment=="Week":
        return year+"||'-'||"+week
    elif segment=="Month":   
        return year+ "||'-'||"+month
    else:
        return year
     
    
    

   
@csrf_exempt 
def dashboard_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        
        grouppertext= objs['limit']
 
        print grouppertext
               
        header_sql = ("select msgdate,COALESCE(message_count,0) as message_count,COALESCE(nmessage_count,0) as nmessage_count,COALESCE(allusers_count,0) as allusers_count,COALESCE(freelancer_count,0) as freelancer_count,COALESCE(employers_count,0) as employers_count,COALESCE(realemployers_count,0) as realemployers_count ,COALESCE(job_count,0) as job_count, COALESCE(proposal_count,0) as proposal_count, COALESCE(paidproposal_count,0) as paidproposal_count, COALESCE(application_count,0) as application_count,COALESCE(invitation_count,0) as invitation_count , COALESCE(invoice_count,0) as invoice_count,COALESCE(invoicepaid_count,0) as invoicepaid_count,round(COALESCE(invperjobavg,0),2) as invperjobavg, round(COALESCE(appperjobavg::numeric,0),2) as appperjobavg, COALESCE(depositrequest_count,0) , COALESCE(depositrequestpaid_count,0)  from ")
        
        workflow_messages_sql = ("(select count(distinct id) as message_count,"+datefieldtostring("timestamp", grouppertext) + " as msgdate from contracts_message where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by msgdate) contractsmessages left outer join ")
        
        allusers_sql = ("(select count(distinct u.id) as allusers_count, "+datefieldtostring("date_joined", grouppertext) + " as datejoined from users u inner join auth_user au on au.id=u.django_user_id where date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) allusers on contractsmessages.msgdate=allusers.datejoined left outer join")
        
        freelancers_sql = ("(select count(distinct u.id) as freelancer_count, "+datefieldtostring("date_joined", grouppertext) + " as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_freelancer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) freelancers on contractsmessages.msgdate=freelancers.datejoined left outer join")
        
        employers_sql = ("(select count(distinct u.id) as employers_count, "+datefieldtostring("date_joined", grouppertext) + " as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_employer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) employers on freelancers.datejoined=employers.datejoined left outer join")
        
        realemployers_sql = ("(select count(distinct u.id) as realemployers_count, "+datefieldtostring("date_joined", grouppertext) + " as datejoined from users u inner join auth_user au on au.id=u.django_user_id inner join contracts_job cj on cj.employer_id=u.id where  date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) realemployers on contractsmessages.msgdate=realemployers.datejoined left outer join")
        
        jobs_sql =("(select count(id) as job_count,  "+datefieldtostring("created_at", grouppertext) + " as createdat from contracts_job  where approved=true and created_at>='"+t1+"' and created_at<='"+t2+"' group by createdat) jobs on jobs.createdat=contractsmessages.msgdate  left outer join")
        
        contractsmessages_sql = ("(select count(distinct id) as nmessage_count, "+datefieldtostring("sent_at", grouppertext) + " as sentat from messages_message where sent_at>='"+t1+"' and sent_at<='"+t2+"' group by sentat) messages on messages.sentat=contractsmessages.msgdate   left outer join")
        
        porposals_sql  = ("(select "+datefieldtostring("timestamp", grouppertext) + " as proposalsent,count(*) as proposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalsent) proposals on proposals.proposalsent=contractsmessages.msgdate left outer join ")
                
        proposalspaid_sql = ("(select "+datefieldtostring("cp.payed_timestamp", grouppertext) + " as proposalpaid,sum(case when cp.status=4 then 1 else 0 end) as paidproposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where cp.payed_timestamp>='"+t1+"' and cp.payed_timestamp<='"+t2+"'  group by proposalpaid) paidproposals on paidproposals.proposalpaid=contractsmessages.msgdate left outer join ")  
                     
        
        application_sql = ("(select count(distinct id) as application_count,"+datefieldtostring("timestamp", grouppertext) + " as appliedat from contracts_application   where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by appliedat) applications on applications.appliedat=contractsmessages.msgdate left outer join ")
                
        invited_sql = ("(select count(*) as invitation_count, "+datefieldtostring("cj.created_at", grouppertext) + " as invited_at  from contracts_job_invited cji inner join contracts_job cj on cj.id=cji.job_id where cj.created_at>='"+t1+"' and cj.created_at<='"+t2+"' group by invited_at) invitations on invitations.invited_at=contractsmessages.msgdate left outer join")
        
        invoicesent_sql = ("(select count(distinct ci.message_ptr_id) as invoice_count,"+datefieldtostring("timestamp", grouppertext) + " as invoicesent from contracts_invoice ci inner join contracts_message cm on ci.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by invoicesent) invoicessent on invoicessent.invoicesent=contractsmessages.msgdate left outer join ")
        
        invoicepaid_sql = ("(select count(distinct ci.message_ptr_id) as invoicepaid_count,"+datefieldtostring("ci.payed_timestamp", grouppertext) + " as invoicepaid from contracts_invoice ci inner join contracts_message cm on ci.message_ptr_id=cm.id where ci.payed_timestamp>='"+t1+"' and ci.payed_timestamp<='"+t2+"' and ci.status=4 group by invoicepaid) invoicespaid on invoicespaid.invoicepaid=contractsmessages.msgdate left outer join ")
        
        depositrequestsent_sql = ("(select count(distinct cdr.message_ptr_id) as depositrequest_count,"+datefieldtostring("timestamp", grouppertext) + " as depositrequestsent from contracts_depositrequest cdr inner join contracts_message cm on cdr.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by depositrequestsent) depositrequestssent on depositrequestssent.depositrequestsent=contractsmessages.msgdate left outer join ")
        
        depositrequestpaid_sql = ("(select count(distinct cdr.message_ptr_id) as depositrequestpaid_count,"+datefieldtostring("timestamp", grouppertext) + " as depositrequestpaid from contracts_depositrequest cdr inner join contracts_message cm on cdr.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' and cdr.status=4 group by depositrequestpaid) depositrequestspaid on depositrequestspaid.depositrequestpaid=contractsmessages.msgdate left outer join ")       
        
        invperjob_sql = ("(select avg(inv.jobinv) as invperjobavg, "+datefieldtostring("cj.created_at", grouppertext) + " as invsentat from contracts_job cj inner join (select count(cji.id) as jobinv,cji.job_id from contracts_job_invited cji  group by cji.job_id) inv on inv.job_id=cj.id group by invsentat) invitationsperjob on invitationsperjob.invsentat=contractsmessages.msgdate left outer join ")
        
        appperjob_sql = ("(select count(ca.id)::float/count(distinct ca.job_id)::float as appperjobavg,"+datefieldtostring("ca.timestamp", grouppertext) +" as appliedat  from contracts_application ca  group by appliedat) applicationperjob on applicationperjob.appliedat=contractsmessages.msgdate ")
        
        sql = (header_sql + workflow_messages_sql + allusers_sql + freelancers_sql + employers_sql + realemployers_sql + jobs_sql + contractsmessages_sql + porposals_sql + proposalspaid_sql + application_sql +invited_sql+ invoicesent_sql + invoicepaid_sql + depositrequestsent_sql + depositrequestpaid_sql + invperjob_sql +appperjob_sql+  "  order by msgdate")
        
        
        ##print sql
        
        results = customQuery(sql,1)                                     
        c = Context({'statistics': results})   
        return HttpResponse(render_to_string('dashboard.json', c, context_instance=RequestContext(request)), mimetype='application/json')  
    


@login_required(login_url='/accounts/login/')	
def growth_dashboard(request):
    
    t = loader.get_template('./reports/growth_dashboard.html')
    return render_to_response('./reports/growth_dashboard.html', context_instance=RequestContext(request))
   
   
@csrf_exempt 
def growthdashboard_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        
        grouppertext= objs['limit']
        print grouppertext
        metric = objs['metric']
        
        print metric
        if metric== 'All Signups':               
            sql = ("select sp.periodjoined, round(100*joined/(runningtotal-joined+0.00001),3) from (select "+datefieldtostring("date_joined", grouppertext) + " as periodjoined, count(*) as joined from auth_user where date_joined >='"+t1+"' and date_joined <='"+t2+"' group by periodjoined) sp inner join (select "+datefieldtostring("date_joined", grouppertext) + " as periodjoined, sum(count(*)) over (order by "+datefieldtostring("date_joined", grouppertext) + ") as runningtotal from auth_user  group by periodjoined) al on sp.periodjoined=al.periodjoined ")
        
        elif metric== 'Jobs Posted':
            sql = ("select sp.periodcreated, round(100*created/(runningtotal-created+0.00001),3) from  (select  "+datefieldtostring("created_at", grouppertext) +"  as periodcreated, count(*) as created from contracts_job where created_at >='"+t1+"' and created_at <='"+t2+"' group by periodcreated) sp  inner join  (select  "+datefieldtostring("created_at", grouppertext) +" as periodcreated, sum(count(*)) over (order by  "+datefieldtostring("created_at", grouppertext) +"  ) as runningtotal from contracts_job  group by periodcreated) al on sp.periodcreated=al.periodcreated  ")
        
        #print sql
        results = customQuery(sql,1)                                     
        c = Context({'statistics': results, 'metricname': metric})   
        return HttpResponse(render_to_string('growthdashboard.json', c, context_instance=RequestContext(request)), mimetype='application/json')  
    

        
        
@login_required(login_url='/accounts/login/')
def jobs_employers_statistics(request):
    
    t = loader.get_template('./reports/jobs_employers_statistics.html')
    c = Context({
        'jobs_employers_statistics': dashboard,
    })
    return render_to_response('./reports/jobs_employers_statistics.html', context_instance=RequestContext(request))
        
@csrf_exempt 
def jobs_employers_statistics_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        

	period = objs['period']
        grouppertext= objs['limit']
        #grouppertext = "Month"
        if grouppertext=="Month":
            grouper="7"
        elif grouppertext=="Day":
             grouper="10"
        else:
             grouper="4"    
        
        header_sql = ("select datejoined,max(jobs_per_employer),min(jobs_per_employer), round(avg(jobs_per_employer),3), round(median(jobs_per_employer),3)")
        
        from_sql = ("from (select count(cj.id) as jobs_per_employer, u.id,substring(to_char(au.date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from contracts_job cj inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id where au.date_joined>='"+t1+"' and au.date_joined<='"+t2+"'  and cj.created_at<=(date_joined + INTERVAL '"+period+" Day') group by u.id,au.date_joined order by jobs_per_employer desc) total group by datejoined order by datejoined;")
        sql = (header_sql + from_sql)
        

        results = customQuery(sql,1)

        #print results
 
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('jobs_employers_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
@login_required(login_url='/accounts/login/')
def jobs_applications_statistics(request):
    if request.method == 'GET':
    	#objs = simplejson.loads(request.raw_post_data)
    	#print objs
        t = loader.get_template('./reports/jobs_applications_statistics.html')
        #param =  objs['param']
        #c = Context({'jobs_applications_statistics': dashboard, 'param': param})
        
#        return HttpResponse(t.render(c) )
        #return HttpResponse(render_to_string('./reports/jobs_applications_statistics.html', c, context_instance=RequestContext(request)), mimetype='application/html') 
        return render_to_response('./reports/jobs_applications_statistics.html', context_instance=RequestContext(request))
        
        
@csrf_exempt 
def jobs_applications_statistics_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
        keywords = objs['searchkeywords']
        
        contkeywords = objs['contsearchkeywords']
        
        skillkeywords = objs['skillsearchkeywords']
        searchsql = ""
        if keywords <> "":
            searchsql = "and (lower(substring(cj.title,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.email,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.first_name || ' ' || au.last_name,1,40)) like '%%" +keywords.lower() + "%%')"
        
        contsearchsql = "" 
        if contkeywords <> "":    
            contsearchsql = " and cj.id in (select distinct contcj.id from users cont inner join auth_user contauth on contauth.id=cont.django_user_id inner join contracts_application contapp on contapp.applicant_id=cont.id  inner join contracts_job contcj on contcj.id=contapp.job_id  where (lower(substring(contauth.email,1,40)) like '%%" +contkeywords.lower() + "%%' or  lower(substring(contauth.first_name || ' ' || contauth.last_name,1,40)) like '%%" +contkeywords.lower() + "%%') ) "
       
        skillsearchsql = "" 
        if skillkeywords <> "":    
            skillsearchsql = " and  ss.name like '%%" +skillkeywords.lower() + "%%'  " 
       
        budgetsql = "COALESCE(case when effort_unit=1 then budget  else 0 end, 0) as fixedbudget, COALESCE(case when effort_unit=5 then case  when budget_range=1 then '1-100'  when budget_range=2 then '101-250'  when budget_range=3 then '251-1000'  when budget_range=4 then '1001-2000' when budget_range=5 then '2001-5000' when budget_range=6 then '5000+'  when budget_range=7 then null  else null end else null end,'0') as budgetrange "
        
        sql = ("select u.id,au.first_name || ' ' || au.last_name as employer_name,au.email as Employer_Email, u.countrycode || ' ' || u.areacode || ' ' || u.mobile as phone, cj.id as job_id,substring(cj.title,1,200) as job_title,substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16) as created_at, "+budgetsql+" ,count(distinct ca.id) as application_count, count( distinct case when ca.shortlisted=true then ca.id else null end) as shortlisted, count(distinct case when cm.from_applicant=true then cm.id else null end) as applicant_messages, count(distinct case when cm.from_applicant=false then cm.id else null end) as employer_responses,count(distinct cp.message_ptr_id) as proposal_count, count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as acceptedproposal_count, case when cj.status=1 then True when cj.status=2 then False end as JobStatus, cj.approved, u.open_applications_rate*100, count(distinct crm.id) as cn from contracts_job cj left outer join contracts_application ca   on cj.id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id left outer join contracts_requiredskill cr on cr.job_id=cj.id left outer join skills_skill ss on ss.id=cr.skill_id left outer join crm_notes crm on crm.user_id=u.id where  created_at>='"+t1+"' and created_at<='"+t2+"' "+searchsql+ contsearchsql+ skillsearchsql +" group by employer_name,cj.id,job_title,cj.created_at,au.email,phone,u.id order by cj.created_at desc;")
        
        print sql
        results = customQuery(sql,1)
                              
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('jobs_applications_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json') 



@csrf_exempt 
def jobs_communications_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        job_id = objs['job_id']
        #print job_id;
        
        sql = ("select u.id,au.email,au.first_name || ' ' || au.last_name as freelancer_name, u.countrycode || ' ' || u.areacode || ' ' || u.mobile as phone,ca.id as application_id,case when ca.shortlisted=true then 1 else 0 end as shortlisted,count(cp.message_ptr_id) as proposals, sum(case when cp.status=4 then 1 else 0 end) as acceptedproposal_count, sum(case when cm.from_applicant=false then 1 else 0 end) as employer_responses, ca.client_views from contracts_application ca inner join users u on u.id=ca.applicant_id inner join auth_user au on u.django_user_id=au.id inner join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id where job_id= "+job_id+" group by u.id,au.email,freelancer_name, phone, ca.id,shortlisted ;")
        
        #print sql
        results = customQuery(sql,1)
 	#print results	
        print sql
        c = Context({'messages': results})
        return HttpResponse(render_to_string('jobs_communications.json', c, context_instance=RequestContext(request)), mimetype='application/json')             
        




@login_required(login_url='/accounts/login/')
def paymentstracking_report(request):
    if request.method == 'GET':
        return render_to_response('./reports/paymentstracking_report.html', context_instance=RequestContext(request))
        
        
@csrf_exempt 
def paymentstracking_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
               
        
        sql = ("select cpt.id, au.first_name || ' ' ||  au.last_name as fullname,  fra.first_name || ' ' ||  fra.last_name as frfullname, cpt.amount,cpt.card_number, cpt.card_holder_name, cpt.transaction_date, cm.public_id, cpt.order_reference, cj.id as job_id, ca.id as workstream_id from contracts_payforttransaction cpt inner join contracts_message cm on cm.id=cpt.payable_id inner join contracts_application ca on ca.id=cm.application_id inner join contracts_job cj on cj.id=ca.job_id inner join users u on u.id=cj.employer_id inner join auth_user au on au.id=u.django_user_id inner join users fr on fr.id=ca.applicant_id inner join auth_user fra on fra.id=fr.django_user_id where card_number<>'pending'  and cm.timestamp >= '"+t1+"' and cm.timestamp <='"+t2+"' order by cpt.id desc ")
        
        print sql
        results = customQuery(sql,1)
                              
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('paymentstracking.json', c, context_instance=RequestContext(request)), mimetype='application/json') 



@csrf_exempt 
def paymentstracking_actions_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        job_id = objs['job_id']
        print job_id;
        
        sql = ("select  case verb when 1 then 'Proposal issued' when 2 then 'Proposal cancelled'   when 3 then 'Proposal Declined'  when 4 then 'Proposal accepted and deposit paid to escrow'   when 5 then 'Deposit requested by freelancer'  when 6 then 'Deposit cancelled by freelancer'  when 7 then 'Deposit declined by employer'  when 8 then 'Deposit paid to escrow by employer'  when 9 then 'Invoice issued by freelancer'  when 10 then 'Invoice cancelled by freelancer' when 11 then 'Invoice declined by employer' when 12 then 'Invoice paid by employer'  when 13 then 'Invoice closed by customer support' when 14 then 'Refund requested by employer' when 15 then 'Refund issued by freelancer' when 16 then 'Refund declined by freelancer' when 17 then 'Refund request canclled by employer' when 18 then 'Refund request closed by customer support' when 19 then 'Escrow released to freelancer by customer support' when 20 then 'Refund made to employer by customer support' end as action,  related_document_public_id, timestamp, proposal_amount, deposit_amount,invoice_amount, refund_amount, escrow_released_amount, escrow_at_this_point from contracts_workstreamactionreport where application_id="+job_id+" order by timestamp desc ")
        
        #print sql
        results = customQuery(sql,1)
 	#print results	
        print sql
        c = Context({'messages': results})
        return HttpResponse(render_to_string('paymentstracking_actions.json', c, context_instance=RequestContext(request)), mimetype='application/json')  





@login_required(login_url='/accounts/login/')
def sign_job_proposal_invoice(request):
    
    t = loader.get_template('./reports/sign_job_proposal_invoice.html')

    medium = get_mediumliststring()
    source = get_sourceliststring()
    campaign = get_campaignliststring()

    c = Context({'sign_job_proposal_invoice': dashboard, 'medium' : medium, 'source': source, 'campaign': campaign  })
    return render_to_response('./reports/sign_job_proposal_invoice.html',c, context_instance=RequestContext(request))        
        
@csrf_exempt  
def sign_job_proposal_invoice_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        print objs
        cpcchecked = objs['cpcchecked']
        mediumCheckedItems = objs['mediumCheckedItems']
        sourceCheckedItems = objs['sourceCheckedItems']
        campaignCheckedItems = objs['campaignCheckedItems']
        signupchecked = objs['signupchecked']
        t1 = objs['fromdate']
        t2= objs['todate']

        wr="(0)"  
        wheresql =""
        if cpcchecked== "True":
            try:
                wr = getcpcGroupNewAndOld(t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems)
                if wr=="()":
                    wr = "(0)"
            except:
                wr = "(0)"         
            wheresql= " Where au.date_joined >= '"+t1+"' and au.date_joined <= '"+t2+"' and u.id in " +  wr               
        else:
            wheresql = "Where au.date_joined >= '"+t1+"' and au.date_joined <= '"+t2+"'"
           
         
        sql = ("select * from (select count(distinct au.email) as signed_up, count(distinct jobsposted.id) as posted_jobs, count(distinct paidproposal.id) as paid_proposal, count(distinct invoices.applicant_id) as invoices_paid, count(distinct jobsposted.jobid) as jobscount, count(distinct paidproposal.proposalid) as proposalscount, count(distinct invoices.invoiceid) as invoicescount  from users u inner join auth_user au on u.django_user_id=au.id  left outer join (select u1.id,cj.id as jobid from users u1 inner join contracts_job cj on cj.employer_id= u1.id where cj.approved=true) jobsposted on jobsposted.id=u.id left outer join (select u2.id,cp2.message_ptr_id as proposalid from users u2 inner join contracts_application ca2 on ca2.applicant_id=u2.id inner join contracts_message cm2 on cm2.application_id=ca2.id inner join contracts_proposal cp2 on cp2.message_ptr_id=cm2.id where cp2.status=4) paidproposal on paidproposal.id=u.id left outer join (select distinct ca1.job_id,ci.status,ci.message_ptr_id  as invoiceid,ca1.applicant_id from contracts_invoice ci inner join contracts_message cm1 on cm1.id=ci.message_ptr_id inner join contracts_application ca1 on ca1.id=cm1.application_id where ci.status=4) invoices on invoices.applicant_id=u.id " + wheresql +") total ")
        
                   
        #print getcpcGroupNewAndOld()
        print sql 
        results = customQuery(sql,1)	
        print results 
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('sign_job_proposal_invoice.json', c, context_instance=RequestContext(request)), mimetype='application/json')                   
        
        dashboard
@login_required(login_url='/accounts/login/')        
def sign_application_proposal_invoice(request):
    
    t = loader.get_template('./reports/sign_application_proposal_invoice.html')
    medium = get_mediumliststring()
    source = get_sourceliststring()
    campaign = get_campaignliststring()
    
    c = Context({'sign_application_proposal_invoice': dashboard, 'medium' : medium, 'source': source, 'campaign': campaign })
    return render_to_response('./reports/sign_application_proposal_invoice.html',c, context_instance=RequestContext(request))        
        
@csrf_exempt  
def sign_application_proposal_invoice_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        cpcchecked = objs['cpcchecked']
        mediumCheckedItems = objs['mediumCheckedItems']
        sourceCheckedItems = objs['sourceCheckedItems']
        campaignCheckedItems = objs['campaignCheckedItems']
        
        signupchecked = objs['signupchecked']
        t1 = objs['fromdate']
        t2= objs['todate']  
         
        wr="(0)"       
        wheresql =""
        if cpcchecked== "True":
            try:
                wr = getcpcGroupNewAndOld(t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems)
                if wr=="()":
                    wr = "(0)"
            except: 
                print "error"   
            wheresql= " Where au.date_joined >= '"+t1+"' and au.date_joined <= '"+t2+"' and u.id in " +  wr               
        else:
            wheresql = "Where au.date_joined >= '"+t1+"' and au.date_joined <= '"+t2+"'"
        
        sql = ("select count(distinct u.id) as user_count, count(distinct applicants.id) as applicants_count, count(distinct proposals.applicant_id) as proposal_count, count(distinct invoices.applicant_id) as invoice_count, count(distinct applicants.applicationid) as applicationscount, count(distinct proposals.proposalid) as proposalscount, count(distinct invoiceid) as invoicescount from users u inner join auth_user au on u.django_user_id=au.id left outer join (select u1.id,ca.id as applicationid from users u1 inner join contracts_application ca on ca.applicant_id=u1.id) applicants on applicants.id=u.id left outer join (select ca1.applicant_id,ca1.id,cp.message_ptr_id  as proposalid from contracts_application ca1 inner join contracts_message cm on cm.application_id=ca1.id inner join contracts_proposal cp on cp.message_ptr_id=cm.id) proposals on proposals.applicant_id=u.id left outer join (select ca2.applicant_id,ci.message_ptr_id as invoiceid from contracts_message cm1 inner join contracts_invoice ci on ci.message_ptr_id=cm1.id inner join contracts_application ca2 on ca2.id=cm1.application_id) invoices on invoices.applicant_id=u.id " + wheresql)
        
        results = customQuery(sql,1)
 	
        
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('sign_application_proposal_invoice.json', c, context_instance=RequestContext(request)), mimetype='application/json')                   
        
        

@login_required(login_url='/accounts/login/')
def top_freelancers(request):
    
    t = loader.get_template('./reports/top_freelancers.html')
    c = Context({
        'top_freelancers': dashboard,
    })
    return render_to_response('./reports/top_freelancers.html', context_instance=RequestContext(request))   

@csrf_exempt
def top_freelancers_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        
        priority = objs['priority']
        limit = objs['limit']
        searchaql = objs['searchkeywords']
        #t1 = objs['fromdate']  + ' 00:00:00+00'
        #t2 = objs['todate'] + ' 23:59:59+00'
        print priority;
        #keywords = objs['searchkeywords']
        sortsql = ""
        if priority== "Skills Count":
            sortsql= " order by skillscount desc"
        elif priority=="Profile Completion":
            sortsql= " order by profilecompletion desc"
        else:
            sortsql= " order by applicationcount  desc"    

        #print sortsql   
        sql = ("select distinct u.id,au.first_name || ' ' || au.last_name as fullname,au.email, u.countrycode || ' ' || u.areacode || ' ' || u.mobile, case when (u.photo <>'' and u.photo is not null) then 'https://nabbesh-images.s3.amazonaws.com/' || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as photo, usercountry, round(((addedskills::float+hasphoto::float+hasbio::float+employment::float+education::float+visual::float)*100/6)::numeric,0) as profilecompletion,skillscount, applicationcount from users u inner join auth_user au on u.django_user_id=au.id inner join ( select u.id as userid ,u.country as usercountry, case when count(distinct su.skill_id)>0 then 1 else 0 end as addedskills, count(distinct su.skill_id) as skillscount, case when (u.photo is not null and u.photo<>'') then 1 else 0 end as hasphoto, case when (u.bio is not null and u.bio <>'') then 1 else 0 end as hasbio, case when count(distinct ce.id)> 0 then 1 else 0 end as employment, case when count(distinct edu.id)>0 then 1 else 0 end as education, case when count(distinct ct.id)>0 then 1 else 0 end as visual, count(distinct ca.id) as applicationcount from users u inner join auth_user au on u.django_user_id=au.id left outer join skills_users su on su.id_user=u.id left outer join education edu on edu.id_user=u.id inner join canvas_box cb on cb.profile_id=u.id left outer join canvas_employment ce on ce.box_id=cb.id left outer join canvas_thumbnail ct on ct.box_id=cb.id inner join contracts_application ca on ca.applicant_id=u.id group by u.id) total on total.userid=u.id inner join skills_users su1 on su1.id_user=u.id inner join skills_skill ss1 on ss1.id=su1.skill_id where lower(ss1.name) like '%%"+searchaql +"%%'"+ sortsql + " limit "+ limit)
        
        
        #print sql
        results = customQuery(sql,1)
 	#print results	
        c = Context({'users': results})
        return HttpResponse(render_to_string('top_freelancers.json', c, context_instance=RequestContext(request)), mimetype='application/json')             

@login_required(login_url='/accounts/login/')
def top_employers(request):
    
    t = loader.get_template('./reports/top_employers.html')
    c = Context({
        'top_employers': dashboard,
    })
    #return HttpResponse(t.render(c))   
    return render_to_response('./reports/top_employers.html', context_instance=RequestContext(request))

@csrf_exempt 
def top_employers_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        limit = objs['limit']
        priority = objs['priority']
        
        sortsql = ""
        if priority== "Jobs Count":
            sortsql= " order by jobs_count"
        else:
            sortsql= " order by accepted_proposals_count"

        
        sql = ("select u.id, au.first_name || ' ' || au.last_name as fullname , au.email, u.countrycode || ' ' || u.areacode || ' ' || u.mobile, 'http://www.nabbesh.com/profile/' || u.id as homepage, case when (u.photo <>'' and u.photo is not null) then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as photo, u.country, count(distinct cj.id) as jobs_count, count(distinct applications.proposal_id) as accepted_proposals_count from users u inner join auth_user au on u.django_user_id=au.id  left outer join contracts_job cj on cj.employer_id=u.id   left outer join ( select distinct cj1.employer_id,cm1.id as proposal_id from contracts_job cj1 inner join contracts_application ca1 on ca1.job_id=cj1.id inner join contracts_message cm1 on cm1.application_id=ca1.id  inner join contracts_proposal cp1 on cp1.message_ptr_id=cm1.id where cp1.status=4) applications on applications.employer_id=u.id group  by u.id,au.email,fullname,photo,homepage  "+sortsql+"  desc limit " + limit)
        
        ##print sql
        results = customQuery(sql,1)
 	#print results	
        c = Context({'users': results})
        return HttpResponse(render_to_string('top_employers.json', c, context_instance=RequestContext(request)), mimetype='application/json')  
        
@login_required(login_url='/accounts/login/')        
def user_report(request, userid=None):
    
    t = loader.get_template('./reports/user_report.html')
    
    ##print optional
    c = Context({
        'user_report': dashboard, 'userid': userid
    })
    return HttpResponse(t.render(c))
    #return HttpResponse(render_to_string('./reports/user_report.html', c, context_instance=RequestContext(request)), mimetype='application/html')
    #return render_to_response('./reports/user_report.html', context_instance=RequestContext(request))
    
    
@csrf_exempt 
def find_user_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        userid= objs['userid']
        searchtext= objs['userotherinfo']
         
        searchsql=""
        
        if userid!='':
            searchsql = "where u.id = "+userid
        else:
            searchsql = "where lower(au.first_name || ' ' || au.last_name) like '%%"+searchtext.lower()+"%%' or au.email like '%%"+searchtext.lower()+"%%' or lower(cj.title) like '%%"+searchtext.lower()+"%%'  or u.id in (select u.id from contracts_message  cm inner join contracts_application ca on ca.id=cm.application_id inner join users u on u.id=ca.applicant_id where cm.public_id = '"+searchtext+"' union select u.id from contracts_message  cm inner join contracts_application ca on ca.id=cm.application_id inner join contracts_job cj on cj.id=ca.job_id inner join users u on u.id=cj.employer_id where cm.public_id = '"+searchtext+"'  ) limit 10 "
       
        sql = ("select distinct u.id, au.first_name || ' ' || au.last_name, au.email, case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as cphoto from users u    inner join auth_user au on u.django_user_id=au.id left join contracts_job cj on cj.employer_id=u.id " + searchsql )
        ##print sql
        results = customQuery(sql,1)
        
        return HttpResponse(json.dumps(results), mimetype='application/json')  
    
@csrf_exempt 
def user_personalinfo_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        userid= objs['userid']
        sql = ("select u.id,u.django_user_id, au.first_name || ' ' || au.last_name, au.email,  u.countrycode || ' ' || u.areacode || ' ' || u.mobile,  u.country,  u.city, case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as cphoto, u.dob, u.gender, u.formatted_address, u.is_employer, u.is_hobbies_explorer, u.is_freelancer, u.hide_in_search, u.deactivated, u.view_count, u.date_of_birth, u.city, u.country, u.nationality, u.average_rating, u.reviews_count, u.jobs_count, au.is_staff, au.is_active, au.is_superuser, au.last_login, au.date_joined, tv.last_update from  users u inner join auth_user au on u.django_user_Id=au.id left outer join tracking_visitor tv on tv.user_id=au.id where u.id="+ str(userid))        
        ##print sql
        results = customQuery(sql,1)
        
        c = Context({'details': results})
        return HttpResponse(render_to_string('userdetails.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
@csrf_exempt      
def user_jobs_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)

        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
      
        userid = objs["userid"]
        contkeywords = objs['contsearchkeywords']
        
        skillkeywords = objs['skillsearchkeywords']
        
        #print objs
        
        
        contsearchsql = "" 
        if contkeywords <> "":    
            contsearchsql = " and cj.id in (select distinct contcj.id from users cont inner join auth_user contauth on contauth.id=cont.django_user_id inner join contracts_application contapp on contapp.applicant_id=cont.id  inner join contracts_job contcj on contcj.id=contapp.job_id  where (lower(substring(contauth.email,1,40)) like '%%" +contkeywords.lower() + "%%' or  lower(substring(contauth.first_name || ' ' || contauth.last_name,1,40)) like '%%" +contkeywords.lower() + "%%') ) "
       
        skillsearchsql = "" 
        if skillkeywords <> "":    
            skillsearchsql = " and  ss.name like '%%" +skillkeywords.lower() + "%%'  " 
       
        budgetsql = "COALESCE(case when effort_unit=1 then budget  else 0 end, 0) as fixedbudget, COALESCE(case when effort_unit=5 then case  when budget_range=1 then '1-100'  when budget_range=2 then '101-250'  when budget_range=3 then '251-1000'  when budget_range=4 then '1001-2000' when budget_range=5 then '2001-5000' when budget_range=6 then '5000+'  when budget_range=7 then null  else null end else null end,'0') as budgetrange "
        
        sql = ("select u.id,au.first_name || ' ' || au.last_name as employer_name,au.email as Employer_Email, u.countrycode || ' ' || u.areacode || ' ' || u.mobile as phone, cj.id as job_id,substring(cj.title,1,200) as job_title,substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16) as created_at, "+budgetsql+" ,count(distinct ca.id) as application_count, count( distinct case when ca.shortlisted=true then ca.id else null end) as shortlisted, count(distinct case when cm.from_applicant=true then cm.id else null end) as applicant_messages, count(distinct case when cm.from_applicant=false then cm.id else null end) as employer_responses,count(distinct cp.message_ptr_id) as proposal_count, count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as acceptedproposal_count, case when cj.status=1 then True when cj.status=2 then False end as JobStatus, cj.approved, u.open_applications_rate, 0 as fill from contracts_job cj left outer join contracts_application ca   on cj.id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id left outer join contracts_requiredskill cr on cr.job_id=cj.id left outer join skills_skill ss on ss.id=cr.skill_id where u.id = "+str(userid)+"  and created_at>='"+t1+"' and created_at<='"+t2+"' "+ contsearchsql+ skillsearchsql +" group by employer_name,cj.id,job_title,cj.created_at,au.email,phone,u.id order by cj.created_at desc;")
        
        print sql
        results = customQuery(sql,1)
                              
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('jobs_applications_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
        
@csrf_exempt 
def user_applications_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)

        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
      
        userid = objs["userid"]
        
        skillkeywords = objs['skillsearchkeywords']
        
        keywords = objs['searchkeywords']
        

        searchsql = ""
        if keywords <> "":
            searchsql = "and (lower(substring(cj.title,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.email,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.first_name || ' ' || au.last_name,1,40)) like '%%" +keywords.lower() + "%%')"
        
               
        skillsearchsql = "" 
        if skillkeywords <> "":    
            skillsearchsql = " and  ss.name like '%%" +skillkeywords.lower() + "%%'  "   
              
        sql = ("select euser.id,au.first_name || ' ' || au.last_name as employer_name,au.email as Employer_Email, euser.countrycode || ' ' || euser.areacode || ' ' || euser.mobile as phone, cj.id,cj.title, cj.created_at, COALESCE(case when effort_unit=1 then budget  else 0 end, 0) as fixedbudget, COALESCE(case when effort_unit=5 then case  when budget_range=1 then '1-100'  when budget_range=2 then '101-250'  when budget_range=3 then '251-1000'  when budget_range=4 then '1001-2000' when budget_range=5 then '2001-5000' when budget_range=6 then '5000+'  when budget_range=7 then null  else null end else null end,'0') as budgetrange, case when cj.status=1 then True when cj.status=2 then False end as JobStatus, cj.approved, ca.id,  count(distinct cp.message_ptr_id) as proposals, count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as acceptedproposals, count(distinct ci.message_ptr_id) as invoices, count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as acceptedinvoices  from contracts_job cj  inner join contracts_application ca on ca.job_id=cj.id  inner join contracts_message cm on cm.application_id=ca.id inner join users fuser on fuser.id=ca.applicant_id inner join users euser on euser.id=cj.employer_id inner join auth_user au on au.id=euser.django_user_id  left outer join contracts_proposal cp on cp.message_ptr_id=cm.id  left outer join contracts_invoice ci on ci.message_ptr_id=cm.id where fuser.id="+str(userid)+"  and created_at>='"+t1+"' and created_at<='"+t2+"' "+ searchsql+ skillsearchsql +" group by euser.id, employer_name, employer_email, phone, cj.id, ca.id order by ca.timestamp desc")        
        ##print sql
        results = customQuery(sql,1)
        #print results	
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('user_applications.json', c, context_instance=RequestContext(request)), mimetype='application/json')  




@login_required(login_url='/accounts/login/')       
def skillsdemography_report(request):
    
    t = loader.get_template('./reports/skillsdemography_report.html')
    c = Context({
        'skillsdemography_report': freelancerdemography_report,
    })
   
    #return HttpResponse(t.render(c))
    return render_to_response('./reports/skillsdemography_report.html', context_instance=RequestContext(request))
    
    
    
@csrf_exempt
def skillsdemography_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        limit = objs['limit']
        priority = objs['priority']
        
             
        sortsql="users_have_it"
        if priority=="Users Count":
            sortsql="users_have_it"
        elif priority=="Users Country Count":
            sortsql="countries_users"
        elif priority=="Jobs Count":
            sortsql="jobs_require_it"
        elif priority=="Jobs Country Count":
            sortsql="countries_jobs"
        
        sql = ("select skills.name, calc.*, case when calc.jobs_require_it<>0 then cast(calc.users_have_it as real)/cast(calc.jobs_require_it as real) else 0 end as availability_rate from skills_skill skills inner join (select ss.id, count(distinct su.id_user)  as users_have_it, count(distinct u1.country) as countries_users, count(distinct crs.job_id) as jobs_require_it, count(distinct u2.country) as countries_jobs from skills_skill ss left outer join skills_users su on su.skill_id=ss.id inner join users u1 on su.id_user=u1.id left outer join contracts_requiredskill crs on crs.skill_id=ss.id inner join contracts_job cj on cj.id=crs.job_id inner join users u2 on u2.id=cj.employer_id where ss.deleted=false group by ss.id) calc on calc.id=skills.id order by "+sortsql+" desc limit "+ limit)
        
        #print sql 
        results = customQuery(sql,1)
    
        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('skillsdemography.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
        


 
        
        
@csrf_exempt
def skillsdemographydetails_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skill_id= objs['skill_id']
        sql = ("select country, jobs_count,users_count, case when jobs_count<>0 then cast(users_count as real)/cast(jobs_count as real) else 0 end as availability_rate from  (select case when total1.country is not null then total1.country else total2.country end as country, case when total1.jobs_count is not null then total1.jobs_count else 0 end as jobs_count, case when total2.users_count is not null then total2.users_count else 0 end as users_count from ( select count(*) as jobs_count,u.country  from contracts_job cj  inner join users u on cj.employer_id=u.id  inner join contracts_requiredskill crs on crs.job_id=cj.id where crs.skill_id= "+skill_id +" group by u.country) total1 full outer join  (select count(*) as users_count, u.country  from users u  inner join skills_users su on su.id_user=u.id where su.skill_id="+skill_id+" group by u.country) total2 on total1.country=total2.country ) total")
 
        results = customQuery(sql,1)

        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('skillsdemographydetails.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
            

@login_required(login_url='/accounts/login/')        
def skillsdistribution_report(request):
    
    t = loader.get_template('./reports/skillsdistribution_report.html')
    c = Context({
        'skillsdistribution_report': freelancerdemography_report,
    })
   
    return render_to_response('./reports/skillsdistribution_report.html', context_instance=RequestContext(request))

    
    
@csrf_exempt
def skillsdistribution_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        limit = objs['limit']
        priority = objs['priority']
        
        searchkeywords = objs['searchkeywords']     
        
        searchsql = ""
        if searchkeywords <> "":
            searchsql = "and lower(name) like '%%" +searchkeywords.lower() + "%%'"
        
        
        sortsql="userscount"
        if priority=="Users Count":
            sortsql="userscount"        
        elif priority=="Jobs Count":
            sortsql="jobscount"
       
        
        sql = ("select *, case when jobscount<>0 then cast(userscount as real)/cast(jobscount as real) else 0 end as availability_rate  from (select * from (select ss.id, ss.name,count(distinct su.id_user) as userscount, count( distinct cr.job_id) as jobscount  from skills_skill ss left outer join skills_users su on ss.id=su.skill_id left outer join contracts_requiredskill cr on cr.skill_id=ss.id where ss.deleted<>true and ss.published=true and ss.merge_to_id is null group by ss.id ) total where (jobscount<>0 or userscount<>0) "+searchsql+" order by "+sortsql+" desc limit "+limit+") total")
        
        
        #print sql
        results = customQuery(sql,1)     
        c = Context({'countries': results})
        
        return HttpResponse(render_to_string('skillsdistribution.json', c, context_instance=RequestContext(request)), mimetype='application/json') 


@csrf_exempt        
def geocodes(request):
    
    t = loader.get_template('./geocodes.json')
    c = Context({
        'geocodes': geocodes,
    })
    return HttpResponse(t.render(c))
            
            
@login_required(login_url='/accounts/login/')        
def crosscountryapps_report(request):
    
    t = loader.get_template('./reports/crosscountryapps_report.html')
    c = Context({
        'crosscountryapps_report': crosscountryapps_report,
    })
    return render_to_response('./reports/crosscountryapps_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def crosscountryapps_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        grouplevel= objs['grouplevel']
        limit = objs['limit']
        colsql = 'applicants.country as appcountry, applicants.city as appcity,employers.country as empcountry, employers.city as empcity'
        groupsql = 'group by empcountry,empcity,appcountry,appcity'
        if grouplevel == 'Country':
            colsql = 'applicants.country as appcountry,employers.country as empcountry'
            groupsql = 'group by empcountry,appcountry'
            
        sql = ("select *, count(*) as appcount from  (select "+ colsql +" from users applicants  inner join contracts_application ca on ca.applicant_id=applicants.id  inner join contracts_job cj on cj.id=ca.job_id  inner join users employers on employers.id=cj.employer_id where employers.country<>applicants.country) total  where empcountry<>'' and appcountry<>'' " + groupsql + " order by appcount desc limit "+ limit)
 
        results = customQuery(sql,1)
        #print sql
        c = Context({'lines': results})
        if grouplevel=='Country':
	    return HttpResponse(render_to_string('crosscountryapps.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	else:
	    return HttpResponse(render_to_string('crosscityapps.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	    
            
                        
@login_required(login_url='/accounts/login/')         
def proposals_report(request):
    
    t = loader.get_template('./reports/proposals_report.html')
    c = Context({
        'proposals_report': proposals_report,
    })
    return render_to_response('./reports/proposals_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def proposals_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)         
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        grouper="7"
        groupertext = objs['grouper']    
        if groupertext=="Year":
            grouper="4"
        elif groupertext=="Month":
            grouper="7"
        elif groupertext=="Day": 
            grouper="10"             
            
                  
        sql = ("select substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1, "+grouper+") as sentat, COALESCE(sum(case when cp.status=1 then cp.deposit_amount end),0) as New, count(distinct case when cp.status=1 then cp.message_ptr_id else null end) as NewCount, round(COALESCE(avg(case when cp.status=1 then cp.deposit_amount end),0),2) as NewAvg, COALESCE(sum(case when cp.status=2 then cp.deposit_amount end),0) as Canceled, count(distinct case when cp.status=2 then cp.message_ptr_id else null end) as CanceledCount, round(COALESCE(avg(case when cp.status=2 then cp.deposit_amount end),0),2) as CanceledAvg, COALESCE(sum(case when cp.status=3 then cp.deposit_amount end),0) as Declined, count(distinct case when cp.status=3 then cp.message_ptr_id else null end) as DeclinedCount, round(COALESCE(avg(case when cp.status=3 then cp.deposit_amount end),0),2) as Avg, COALESCE(sum(case when cp.status=4 then cp.deposit_amount end),0) as Accepted, count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as AcceptedCount, round(COALESCE(avg(case when cp.status=4 then cp.deposit_amount end),0),2) as AcceptedAvg from contracts_proposal cp inner join contracts_message cm on cm.id=cp.message_ptr_id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"'  group  by sentat order by sentat ") 
        results = customQuery(sql,1)
        c = Context({'proposals': results})        
	return HttpResponse(render_to_string('proposals.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	


@login_required(login_url='/accounts/login/')        
def invoices_report(request):
    
    t = loader.get_template('./reports/invoices_report.html')
    c = Context({
        'invoices_report': invoices_report,
    })
    return render_to_response('./reports/invoices_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def invoices_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)         
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        grouper="7"
        groupertext = objs['grouper']    
        if groupertext=="Year":
            grouper="4"
        elif groupertext=="Month":
            grouper="7"
        elif groupertext=="Day": 
            grouper="10"             
            
                  
        sql = ("select  substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1, "+grouper+") as sentat, round(COALESCE(sum(case when ci.status=1 then quantity * unit_price end),0,2)) as NewAmount, count(distinct case when ci.status=1 then ci.message_ptr_id else null end) as NewCount, round(COALESCE(avg(case when ci.status=1 then quantity * unit_price end),0,2)) as NewAverage, round(COALESCE(sum(case when ci.status=2 then quantity * unit_price end),0,2)) as CancelledAmount, count(distinct case when ci.status=2 then ci.message_ptr_id else null end) as CancelledCount, round(COALESCE(avg(case when ci.status=2 then quantity * unit_price end),0,2)) as CancelledAverage, round(COALESCE(sum(case when ci.status=3 then quantity * unit_price end),0,2)) as DeclinedAmount, count(distinct case when ci.status=3 then ci.message_ptr_id else null end) as DeclinedCount, round(COALESCE(avg(case when ci.status=3 then quantity * unit_price end),0,2)) as DeclinedAverage, round(COALESCE(sum(case when ci.status=4 then quantity * unit_price end),0,2)) as PaidAmount, count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as PaidCount, round(COALESCE(avg(case when ci.status=4 then quantity * unit_price end),0,2)) as PaidAverage  from contracts_invoice ci  inner join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id  inner join contracts_message cm on cm.id=ci.message_ptr_id  where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by sentat  order by sentat ") 
        
        #print sql
        results = customQuery(sql,1)
        c = Context({'invoices': results})        
	return HttpResponse(render_to_string('invoices.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	
            
            
@login_required(login_url='/accounts/login/')
def jobs_apps_stats_report(request):
    
    t = loader.get_template('./reports/jobs_apps_stats_report.html')
    c = Context({
        'jobs_apps_stats_report': jobs_apps_stats_report,
    })
    return render_to_response('./reports/jobs_apps_stats_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def jobs_apps_stats_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)         
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        grouper="7"
        groupertext = objs['grouper']    
        if groupertext=="Year":
            grouper="4"
        elif groupertext=="Month":
            grouper="7"
        elif groupertext=="Day": 
            grouper="10"             
            
                  
        sql = ("select substring(to_char(created_at,'YYYY-MM-DD HH24:MI:SS'),1, "+grouper+")as createdat,count(*) as total, count(case when appscount = 0 then 1 end) as count_0, count(case when (appscount >= 1) and (appscount<=5) then 1 end) as count_1_5,  count(case when (appscount > 5) and (appscount<=10) then 1 end) as count_6_10, count(case when (appscount > 10) and (appscount<=50) then 1 end) as count_11_50, count(case when (appscount > 50) then 1 end) as count_more_50   from (select  cj.id as jobid,cj.created_at, count(distinct ca.id) as appscount from contracts_job cj left outer join contracts_application ca on ca.job_id = cj.id where approved=True and created_at>='"+t1+"' and created_at<='"+t2+"' group by jobid,cj.created_at) total group by createdat order by createdat") 
        
        #print sql
        results = customQuery(sql,1)
        c = Context({'jobs_apps_stats': results})        
	return HttpResponse(render_to_string('jobs_apps_stats.json', c, context_instance=RequestContext(request)), mimetype='application/json')           



@login_required(login_url='/accounts/login/')       
def signups_apps_retention_report(request):
    
    t = loader.get_template('./reports/signups_apps_retention_report.html')
    c = Context({
        'signups_apps_retention_report': signups_apps_retention_report,
    })
    return render_to_response('./reports/signups_apps_retention_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def signups_apps_retention_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)                              
        n=int(objs['period'])
        m=int(objs['month'])     
        dynsql1=""
        dynsql2=""
        for i in range(1,n+1):             
            dynsql1 = dynsql1 + ", round((month"+str(i)+"::float * 100.00 /totalsignup::float)::numeric,2) as applied_month"+str(i)
            dynsql2 = dynsql2 + ",count(distinct case when timestamp >=(date_joined + INTERVAL '"+str(m*(i-1))+" Month') and timestamp <=(date_joined + INTERVAL '"+str(m*i)+" Month') then id else null end) as month"+str(i)
        sql = ("select datejoined,totalsignup "+dynsql1+" from (select substring(to_char(date_joined,'YYYY-MM-DD'),1,4) || '-' || to_char((cast(substring(to_char(date_joined,'YYYY-MM-DD'),6,2) as int)-1)/"+str(m)+"+1,'09') || ' pr' as datejoined,count(distinct id) as totalsignup "+dynsql2+"  from (select u.id,au.date_joined, ca.timestamp from users u inner join auth_user au on u.django_user_id=au.id left outer join contracts_application ca on ca.applicant_id=u.id) total group by datejoined order by datejoined desc) final ") 
        results = customQuery(sql,1)
        c = Context({'signups_apps_retention': results,'n' : xrange(n)})        
	return HttpResponse(render_to_string('signups_apps_retention.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	           


@login_required(login_url='/accounts/login/')        
def signups_jobs_retention_report(request):
    
    t = loader.get_template('./reports/signups_jobs_retention_report.html')
    c = Context({
        'signups_jobs_retention_report': signups_jobs_retention_report,
    })
    return render_to_response('./reports/signups_jobs_retention_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def signups_jobs_retention_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)         
                     
        n=int(objs['period'])
        m=int(objs['month']) 

        dynsql1=""
        dynsql2=""
        for i in range(1,n+1):    
            dynsql1 = dynsql1 + ", round((month"+str(i)+"::float * 100.00 /totalsignup::float)::numeric,2) as applied_month"+str(i)      
            dynsql2 = dynsql2 + ", count(distinct case when created_at >=(date_joined + INTERVAL '"+ str(m*(i-1))+" Month') and created_at <=(date_joined + INTERVAL '"+str(m*i) +" Month') then id else null end) as month"+str(i)
                         
        sql = ("select datejoined,totalsignup "+dynsql1+" from ( select substring(to_char(date_joined,'YYYY-MM-DD'),1,4) || '-' || to_char((cast(substring(to_char(date_joined,'YYYY-MM-DD'),6,2) as int)-1)/"+str(m)+"+1,'09') || ' pr' as datejoined, count(distinct id) as totalsignup "+dynsql2+"  from  ( select u.id,au.date_joined, cj.created_at from  users u  inner join auth_user au on u.django_user_id=au.id left outer join contracts_job cj on cj.employer_id=u.id) total  group by datejoined order by datejoined desc  ) final ") 
        
        
        results = customQuery(sql,1)
        print sql
        #print results
        c = Context({'signups_jobs_retention': results,'n' : xrange(n)})        
	return HttpResponse(render_to_string('signups_jobs_retention.json', c, context_instance=RequestContext(request)), mimetype='application/json')     
	           



@login_required(login_url='/accounts/login/')       
def jobs_apps_retention_report(request):
    
    t = loader.get_template('./reports/jobs_apps_retention_report.html')
    c = Context({
        'jobs_apps_retention_report': jobs_apps_retention_report,
    })
    return render_to_response('./reports/jobs_apps_retention_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def jobs_apps_retention_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)         
                    
        n=int(objs['period'])
        m=int(objs['month'])      
        dynsql1=""
        dynsql2=""
        for i in range(1,n+1): 
            dynsql1 = dynsql1 + ", round((month"+str(i)+"::float * 100.00 /totaljobs::float)::numeric,2) as receivedapp_month" + str(i)
            dynsql2 = dynsql2 + ", count(distinct case when timestamp >=(created_at + INTERVAL '"+str(m*(i-1))+" Month') and timestamp <=(created_at + INTERVAL '"+str(m*i)+" Month') then id else null end) as month"+str(i)

        sql = ("select datejoined,totaljobs " +dynsql1+ " from (select substring(to_char(created_at,'YYYY-MM-DD'),1,4) || '-' || to_char((cast(substring(to_char(created_at,'YYYY-MM-DD'),6,2) as int)-1)/"+str(m)+"+1,'09') || ' pr' as datejoined, count(distinct id) as totaljobs "+ dynsql2 +"  from  ( select cj.id as id, cj.created_at, ca.timestamp from contracts_job cj left outer join contracts_application ca on ca.job_id=cj.id ) total group by datejoined order by datejoined desc) final") 
        results = customQuery(sql,1)
                                   
        c = Context({'jobs_apps_retention': results,'n' : xrange(n)})        
	return HttpResponse(render_to_string('jobs_apps_retention.json', c, context_instance=RequestContext(request)), mimetype='application/json') 




@login_required(login_url='/accounts/login/')         
def activities_countries_report(request):
    
    t = loader.get_template('./reports/activities_countries_report.html')
    c = Context({
        'activities_countries_report': jobs_apps_retention_report,
    })
    return render_to_response('./reports/activities_countries_report.html',c, context_instance=RequestContext(request))
            
@csrf_exempt
def activities_countries_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)         

        sql = ("select distinct u.country, COALESCE(usercount,0) as usercount, COALESCE(jobscount,0) as jobscount, COALESCE(appscount,0) as appscount, COALESCE(proposalcount,0) as proposalcount, COALESCE(invoicecount,0) as invoicecount from users u left outer join (select count(distinct u.id) as usercount, u.country from users u inner join auth_user au on u.django_user_id=au.id group by u.country ) signups on signups.country=u.country left outer join (select count(distinct cj.id) as jobscount,u.country  from contracts_job cj inner join users u on u.id=cj.employer_id  group by u.country) jobs on jobs.country=u.country left outer join (select count(distinct ca.id) as appscount, u.country from contracts_application ca inner join users u on u.id=ca.applicant_id  group by u.country) apps on apps.country=u.country left outer join (select count(distinct cm.id) as proposalcount, u.country from contracts_proposal cp inner join contracts_message cm on cm.id=cp.message_ptr_id inner join contracts_application ca on ca.id=cm.application_id inner join users u on u.id=ca.applicant_id group by u.country) proposals on proposals.country=u.country left outer join (select count(distinct cm.id) as invoicecount, u.country from contracts_invoice ci inner join contracts_message cm on cm.id=ci.message_ptr_id inner join contracts_application ca on ca.id=cm.application_id inner join users u on u.id=ca.applicant_id  group by u.country) invoices on invoices.country=u.country where u.country is not null and u.country<>'' order by usercount desc") 
        #print sql
        results = customQuery(sql,1)
        
       
        print results                           
        c = Context({'countries': results})        
	return HttpResponse(render_to_string('activities_countries.json', c, context_instance=RequestContext(request)), mimetype='application/json') 




@login_required(login_url='/accounts/login/')
def payers_report(request):
    
    t = loader.get_template('./reports/payers_report.html')
    c = Context({
        'payers_report': payers_report,
    })
    return render_to_response('./reports/payers_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def payers_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select distinct u.id,au.first_name || ' ' || au.last_name as fullname, au.email, u.country,cj.id,substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16), cj.title, cii.quantity*cii.unit_price as amount from users u  inner join auth_user au on au.id=u.django_user_id inner join contracts_job cj on cj.employer_id=u.id  inner join contracts_application ca on ca.job_id = cj.id inner join contracts_message cm on cm.application_id=ca.id inner join contracts_invoice ci on ci.message_ptr_id=cm.id inner join contracts_invoiceitem  cii on cii.invoice_id=ci.message_ptr_id where ci.status=4 "
        
        #print sql
        results = customQuery(sql,1)
        print results
 
        c = Context({'payers': results})
   
        return HttpResponse(render_to_string('payers.json', c, context_instance=RequestContext(request)), mimetype='application/json')



@login_required(login_url='/accounts/login/')
def payees_report(request):
    
    t = loader.get_template('./reports/payees_report.html')
    c = Context({
        'payees_report': payers_report,
    })
    return render_to_response('./reports/payees_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def payees_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select  distinct u.id,  au.first_name || ' ' || au.last_name as fullname,  au.email, u.country,cj.id, substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16),   cj.title, cii.quantity*cii.unit_price as amount   from users u    inner join auth_user au on au.id=u.django_user_id   inner join contracts_application ca on ca.applicant_id = u.id  inner join contracts_job cj on cj.id=ca.job_id  inner join contracts_message cm on cm.application_id=ca.id   inner join contracts_invoice ci on ci.message_ptr_id=cm.id   inner join contracts_invoiceitem  cii on cii.invoice_id=ci.message_ptr_id where ci.status=4  "
        
        #print sql
        results = customQuery(sql,1)
        print results
 
        c = Context({'payees': results})
   
        return HttpResponse(render_to_string('payees.json', c, context_instance=RequestContext(request)), mimetype='application/json')


@login_required(login_url='/accounts/login/')
def payments_report(request):
    
    t = loader.get_template('./reports/payments_report.html')
    c = Context({
        'payments_report': payments_report,
    })
    return render_to_response('./reports/payments_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def payments_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = " select distinct  payer.id, aupayer.first_name || ' ' || aupayer.last_name as payerfullname, aupayer.email,  payer.country,   cj.id, substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16),  cj.title, sum( cii.quantity*cii.unit_price )as amount ,  payee.id, aupayee.first_name || ' ' || aupayee.last_name as payeefullname, aupayee.email,  payee.country       from users payee   inner join auth_user aupayee on aupayee.id=payee.django_user_id    inner join contracts_application ca on ca.applicant_id = payee.id    inner join contracts_job cj on cj.id=ca.job_id    inner join users payer on payer.id=cj.employer_id  inner join auth_user aupayer on aupayer.id=payer.django_user_id  inner join contracts_message cm on cm.application_id=ca.id  inner join contracts_invoice ci on ci.message_ptr_id=cm.id  inner join contracts_invoiceitem  cii on cii.invoice_id=ci.message_ptr_id  where ci.status=4   group by payer.id,payerfullname, aupayer.email, payer.country, cj.id, cj.created_at, payee.id, payeefullname, aupayee.email, payee.country  "
        
        #print sql
        results = customQuery(sql,1)
        print results
 
        c = Context({'payments': results})
   
        return HttpResponse(render_to_string('payments.json', c, context_instance=RequestContext(request)), mimetype='application/json')





@login_required(login_url='/accounts/login/')
def revenue_report(request):
    
    
    t = loader.get_template('./reports/revenue_report.html')
    c = Context({
        'revenue_report': revenue_report,
    })
    return render_to_response('./reports/revenue_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def revenue_getdata(request):
    if request.method == 'POST':
        
        print request
        objs = simplejson.loads(request.raw_post_data)
        print objs
        print 'done till here'
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        
        grouppertext= objs['limit']
        sql = "select total1.msgdate, total1.proposals, COALESCE(total2.acceptedproposals,0) as acceptedproposalscount, COALESCE(total2.escrow,0) as acceptedproposalsamount,total1.invoices, COALESCE(total3.paidinvoices,0), COALESCE(total3.invoiceamounts,0), COALESCE(total3.revenue,0), total1.allproposals,COALESCE(total1.deposits,0) as depositesrequests, COALESCE(total4.paiddeposits,0) as paiddepositscount, COALESCE(total4.cdramounts,0) as paiddepositsamount, COALESCE(total2.escrow,0) + COALESCE(total4.cdramounts,0) as escrow from  ( select   " + datefieldtostring("cm.timestamp", grouppertext) + "  as msgdate,  count(distinct cp.message_ptr_id) as proposals,  count(distinct ci.message_ptr_id) as invoices,  count(distinct cdr.message_ptr_id) as deposits, COALESCE(sum(cp.deposit_amount),0) as allproposals  from contracts_message cm left outer join contracts_proposal cp on cp.message_ptr_id=cm.id  left outer join contracts_invoice ci on ci.message_ptr_id=cm.id  left outer join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id  left outer join contracts_depositrequest cdr on cdr.message_ptr_id=cm.id where cm.timestamp >= '"+t1+"' and cm.timestamp <= '"+t2+"' group by msgdate ) total1  left outer  join  (select   " + datefieldtostring("cp.payed_timestamp", grouppertext) + "  as msgdate,  count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as acceptedproposals,   sum(distinct case when cp.status=4 then cp.deposit_amount else 0 end) as escrow,  COALESCE(sum(cp.deposit_amount),0) as allproposals   from  contracts_message cm  left outer join contracts_proposal cp on cp.message_ptr_id=cm.id   where cp.payed_timestamp >= '"+t1+"' and cp.payed_timestamp <= '"+t2+"' group by msgdate ) total2 on total1.msgdate=total2.msgdate   left outer join   (select  " + datefieldtostring("ci.payed_timestamp", grouppertext) + "  as msgdate, count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as paidinvoices,  sum(distinct case when ci.status=4 then cii.unit_price * cii.quantity else 0 end) as invoiceamounts,  sum(distinct case when ci.status=4 then cii.unit_price * quantity * 9 /100 else 0 end) as revenue  from contracts_message cm  left outer join  contracts_invoice ci on ci.message_ptr_id=cm.id left outer join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id  where ci.payed_timestamp >= '"+t1+"' and ci.payed_timestamp <= '"+t2+"' group by msgdate ) total3 on total1.msgdate=total3.msgdate    left outer join    (select   " + datefieldtostring("cdr.payed_timestamp", grouppertext) + " as msgdate,   count(distinct case when cdr.status=4 then cdr.message_ptr_id else null end) as paiddeposits,  sum(distinct case when cdr.status=4 then cdr.amount else 0 end) as cdramounts  from contracts_message cm  left outer join  contracts_depositrequest cdr on cdr.message_ptr_id=cm.id where cdr.payed_timestamp >= '"+t1+"' and cdr.payed_timestamp <= '"+t2+"' group by msgdate ) total4 on total1.msgdate=total4.msgdate  order by msgdate   "
        
        #print sql
        results = customQuery(sql,1)
        #print results
 
        c = Context({'revenue': results})
   
        return HttpResponse(render_to_string('revenue.json', c, context_instance=RequestContext(request)), mimetype='application/json')


@csrf_exempt
def total_users_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate']
        sql = ("select count(id), count(case when is_active=true then 1 else null end), count(case when date_joined>='"+fromdate+"' then id else null end)  from auth_user")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 
        
@csrf_exempt
def total_jobs_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate']     
        sql = ("select count(id), count(case when status=1  then 1 else null end), count(case when created_at>='"+fromdate+"' then 1 else null end) from contracts_job where approved=true")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 

@csrf_exempt
def total_skills_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate']     
        sql = ("select count(*), count(case when published=true and merge_to_id is null then 1 else null end) from skills_skill")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 


@csrf_exempt
def total_proposals_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate']   
        sql = ("select count(distinct cp.message_ptr_id), count(case when cp.status=4 then 1 else null end), count(distinct case when cm.timestamp>='"+fromdate+"' then cm.id else null end), count(distinct case when cp.payed_timestamp>='"+fromdate+"' and cp.status=4 then cm.id else null end)   from contracts_proposal cp inner join contracts_message cm on cm.id=cp.message_ptr_id")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 

@csrf_exempt
def total_applications_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate'] 
        sql = ("select count(*), count(distinct job_id), count(case when timestamp>='"+fromdate+"' then 1 else null end)   from contracts_application")
        
        ##print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 
        
@csrf_exempt
def total_invoices_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate'] 
        sql = ("select count(distinct ci.message_ptr_id), count(case when ci.status=4 then 1 else null end), count(distinct case when cm.timestamp>='"+fromdate+"' then cm.id else null end), count(distinct case when ci.payed_timestamp>='"+fromdate+"' and ci.status=4 then cm.id else null end)   from contracts_invoice ci inner join contracts_message cm on cm.id=ci.message_ptr_id")
        
        #print sql
        
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json') 

@csrf_exempt 
def total_messages_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        fromdate= objs['fromdate']
        print objs['fromdate']
        sql = ("select count(*), count(case when timestamp>='"+fromdate+"' then 1 else null end)  from contracts_message")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json')    

@csrf_exempt 
def total_escrow_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)

        sql = ("select cast(sum(amount_in_escrow) as text)   from contracts_application where amount_in_escrow>0")
        
        #print sql
        results = customQuery(sql,1)
        return HttpResponse(json.dumps(results), mimetype='application/json')    
   
@csrf_exempt 
def tracking_messages_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        maxid= objs['maxid']
        minid= objs['minid']        
        direction = objs['dir']
        wherestring = ""
        if direction=="Up":
            wherestring = " where cm.id>" + str(minid)
        else:
            wherestring = " where cm.id<" + str(maxid)

        sql = ("select total.*, COALESCE(paid.haspayment,0), COALESCE(paid.hasresponse,0)  from (select fr.id, aufr.first_name || ' ' || aufr.last_name, case when (fr.photo <>'' and fr.photo is not null and fr.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(fr.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as frphoto ,  cm.from_applicant,  '' as msg, cm.timestamp , ca.id as application_id, em.id , auem.first_name || ' ' || auem.last_name,  case when (em.photo <>'' and em.photo is not null and em.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(em.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as emphoto, ci.message_ptr_id as invoicenumber,cp.message_ptr_id, substring(cj.title,1,20),cj.id,case when cm.message ~ E'[A-Za-z0-9._%%-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,4}' then true else false end, case when cm.message ~ E'([0-9]{3}\?[0-9]{3}\-?[0-9]{4})' or cm.message ~ E'([0-9]{6})' then true else false end, case when lower(cm.message) like '%%skype%%' then true else false end as skype, case when lower(cm.message) like '%%odesk%%' then true else false end as odesk, case when lower(cm.message) like '%%elance.com%%' then true else false end as elance, fr.average_rating,em.average_rating, ca.public_id as app_Public_id, cm.id as msgid, COALESCE(case when effort_unit=1 then budget  else 0 end, 0) as fixedbudget, COALESCE(case when effort_unit=5 then case  when budget_range=1 then '1-100'  when budget_range=2 then '101-250'  when budget_range=3 then '251-1000'  when budget_range=4 then '1001-2000' when budget_range=5 then '2001-5000' when budget_range=6 then '5000+'  when budget_range=7 then null  else null end else null end,'0') as budgetrange   from  contracts_message cm inner join contracts_application ca on ca.id=cm.application_id inner join contracts_job cj on ca.job_id=cj.id inner join users em on em.id=cj.employer_id inner join auth_user auem on auem.id=em.django_user_id inner join users fr on fr.id=ca.applicant_id inner join auth_user aufr on aufr.id=fr.django_user_id  left outer join contracts_proposal cp on cp.message_ptr_id=cm.id left outer join contracts_invoice ci on ci.message_ptr_id=cm.id  "+wherestring+" ) total left outer join (select ca.id as application_id,count(distinct case when  cp.status=4 then cp.message_ptr_id else null end) as haspayment, count(distinct case when cm.from_applicant=false then cm.id else null end) as hasresponse from contracts_application ca inner join contracts_message cm on cm.application_id=ca.id left outer join  contracts_proposal cp on cp.message_ptr_id=cm.id group by ca.id ) paid on paid.application_id=total.application_id order by total.msgid desc limit 30")        
           
        #print sql       
        
           
        results = customQuery(sql,1)    
        
        if  len(results)!=0:
            if direction=="Down":
                maxid = results[len(results)-1][22]
            else:    
                minid = results[0][22]
        #print results[len(results)-1][22], results[0][22], "--------------------------------"
        c = Context({'messages': results, 'maxid' : maxid, 'minid': minid })   
        return HttpResponse(render_to_string('trackingmessages.json', c, context_instance=RequestContext(request)), mimetype='application/json')



@login_required(login_url='/accounts/login/')
def photogallery_report(request):
    
    
    t = loader.get_template('./reports/photogallery_report.html')
    c = Context({
        'photogallery_report': photogallery_report,
    })
    return render_to_response('./reports/photogallery_report.html', context_instance=RequestContext(request))

@csrf_exempt 
def photogallery_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        maxid= objs['maxid']
        minid= objs['minid']        
        direction = objs['dir']
        wherestring = ""
        if direction=="Up":
            wherestring = " where u.id>" + str(minid)
        else:
            wherestring = " where u.id<" + str(maxid)

        sql = ("select u.id, case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as uphoto, au.first_name || ' ' || au.last_name as fullname from users u inner join auth_user au on u.django_user_id=au.id "+ wherestring +" and u.photo<>'' and u.photo is not null and u.deactivated=false and au.is_active=true order by u.id desc limit 100")        
           
        #print sql       
        
           
        results = customQuery(sql,1)    
        
        if  len(results)!=0:
            if direction=="Down":
                maxid = results[len(results)-1][0]
            else:    
                minid = results[0][0]
        #print results[len(results)-1][22], results[0][22], "--------------------------------"
        c = Context({'users': results, 'maxid' : maxid, 'minid': minid })   
        return HttpResponse(render_to_string('pixslider.json', c, context_instance=RequestContext(request)), mimetype='application/json')


@csrf_exempt 
def leakagedetection_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'        
        keywords = objs['searchkeywords']
        sql = ("select fr.id, aufr.first_name || ' ' || aufr.last_name, case when (fr.photo <>'' and fr.photo is not null and fr.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(fr.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as frphoto ,  cm.from_applicant, '' as msg, substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,16) , ca.id, em.id , auem.first_name || ' ' || auem.last_name,  case when (em.photo <>'' and em.photo is not null and em.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(em.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as emphoto, ci.message_ptr_id as invoicenumber,cp.message_ptr_id, substring(cj.title,1,20),cj.id,case when cm.message ~ E'[A-Za-z0-9._%%-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,4}' then true else false end, case when cm.message ~ E'([0-9]{3}\?[0-9]{3}\-?[0-9]{4})' or cm.message ~ E'([0-9]{6})' then true else false end, case when lower(cm.message) like '%%skype%%' then true else false end as skype, case when lower(cm.message) like '%%"+keywords+"%%' then true else false end as searchkeyword, fr.average_rating,em.average_rating from  contracts_message cm inner join contracts_application ca on ca.id=cm.application_id inner join contracts_job cj on ca.job_id=cj.id inner join users em on em.id=cj.employer_id inner join auth_user auem on auem.id=em.django_user_id inner join users fr on fr.id=ca.applicant_id inner join auth_user aufr on aufr.id=fr.django_user_id  left outer join contracts_proposal cp on cp.message_ptr_id=cm.id left outer join contracts_invoice ci on ci.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' and lower(cm.message) like '%%"+keywords.lower()+"%%'  order by cm.timestamp desc limit 500;")
        
        #print sql    
        results = customQuery(sql,1)      
        c = Context({'messages': results})   
        return HttpResponse(render_to_string('leakagedetection.json', c, context_instance=RequestContext(request)), mimetype='application/json')

@csrf_exempt 
def tracking_visitors_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = ("select distinct u.id, au.first_name || ' ' || au.last_name,tv.last_update, case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as uphoto, tv.url, tv.ip_address from  auth_user au inner join tracking_visitor tv on au.id=tv.user_id  inner join users u on u.django_user_id=au.id where tv.last_update >= (now() - interval '10 minutes') order by tv.last_update desc")        
            
        results = customQuery(sql,1)     
        c = Context({'users': results})   
        return HttpResponse(render_to_string('trackingvisitors.json', c, context_instance=RequestContext(request)), mimetype='application/json')



@login_required(login_url='/accounts/login/')
def pendinginvoices_report(request):
        
    t = loader.get_template('./reports/pendinginvoices_report.html')
    c = Context({
        'pendinginvoices_report': pendinginvoices_report,
    })
    return render_to_response('./reports/pendinginvoices_report.html', context_instance=RequestContext(request))


@csrf_exempt 
def pendinginvoices_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = ("select * from ( select  em.id, ema.first_name || ' ' || ema.last_name as emfullname,  case when (em.photo <>'' and em.photo is not null and em.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(em.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as emphoto, fr.id, fra.first_name || ' ' || fra.last_name as frfullname, case when (fr.photo <>'' and fr.photo is not null and fr.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(fr.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as frphoto, ca.id as applicationid, ca.timestamp, cj.id,cj.title, count(distinct case when cp.status=1 then cp.message_ptr_id else null end) as pendingproposals, count(distinct case when cp.status=4 then cp.message_ptr_id else null end) as paidproposals, count(distinct case when ci.status=1 then ci.message_ptr_id else null end) as pendinginvoices, count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as paidinvoices,  case  when max(cmi.timestamp)>max(cmp.timestamp) then max(cmi.timestamp) else max(cmp.timestamp) end as latestaction  from  contracts_job cj  inner join users em on em.id=cj.employer_id inner join auth_user ema on ema.id=em.django_user_id  inner join contracts_application ca on ca.job_id=cj.id  inner join users fr on fr.id=ca.applicant_id inner join auth_user fra on fra.id=fr.django_user_id inner join contracts_message cmp on cmp.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cmp.id inner join contracts_message cmi on cmi.application_id=ca.id left outer join contracts_invoice ci on ci.message_ptr_id=cmi.id  where cp.status=4  group by ca.id, emfullname, frfullname, cj.id,cj.title, em.photo, fr.photo, em.id, fr.id) total where pendingproposals>0 or pendinginvoices>0 order by latestaction ")        
            
        results = customQuery(sql,1)   
        #print sql  
        c = Context({'details': results})   
        return HttpResponse(render_to_string('userdetails.json', c, context_instance=RequestContext(request)), mimetype='application/json')


@csrf_exempt 
def pendingratings_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = ("select fr.id, aufr.first_name || ' ' || aufr.last_name as frfullname, case when (fr.photo <>'' and fr.photo is not null and fr.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(fr.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as frphoto,   em.id , auem.first_name || ' ' || auem.last_name as emfullname,  case when (em.photo <>'' and em.photo is not null and em.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(em.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as emphoto ,cm.public_id, ci.payed_timestamp, cm.application_id, COALESCE(ccr.creator_user_id,0), COALESCE(cfr.creator_user_id,0) from contracts_invoice ci   inner join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id inner join contracts_message cm on cm.id=ci.message_ptr_id inner join contracts_application ca on ca.id=cm.application_id inner join users fr on fr.id=ca.applicant_id inner join auth_user aufr on aufr.id=fr.django_user_id inner join contracts_job cj on cj.id=ca.job_id inner join users em on em.id=cj.employer_id inner join auth_user auem on auem.id=em.django_user_id left outer join contracts_clientreview ccr on ccr.invoice_id=ci.message_ptr_id left outer join contracts_contractorreview cfr on cfr.invoice_id=ci.message_ptr_id where ci.payed_timestamp is not null and (ccr.creator_user_id is null or cfr.creator_user_id is null) order by payed_timestamp desc")        
            
        results = customQuery(sql,1)   
        #print sql  
        c = Context({'details': results})   
        return HttpResponse(render_to_string('userdetails.json', c, context_instance=RequestContext(request)), mimetype='application/json')

@login_required(login_url='/accounts/login/')
def leakagedetection_report(request):
        
    t = loader.get_template('./reports/leakagedetection_report.html')
    c = Context({
        'leakagedetection_report': leakagedetection_report,
    })
    return render_to_response('./reports/leakagedetection_report.html', context_instance=RequestContext(request))


@csrf_exempt 
def userprofileinfo_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        userid= objs['userid']
        sql = ("select au.first_name || ' ' || au.last_name, au.email, u.countrycode || ' ' || u.areacode || ' ' || u.mobile, u.country, u.city,case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as cphoto from users u inner join auth_user au on u.django_user_id=au.id where u.id="+str(userid))        
        #print sql            
        results = customQuery(sql,1)      
        return HttpResponse(json.dumps(results), mimetype='application/json')    

    

@login_required(login_url='/accounts/login/')
def crmclients_report(request):
    
    t = loader.get_template('./reports/crmclients_report.html')
    c = Context({
        'crmclients': crmclients_report,
    })
    return render_to_response('./reports/crmclients_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def crmclients_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'   
        sql = "select distinct u.id, '' as title, au.first_name, au.last_name, '' as jobtitle, '' as sitename, u.countrycode || ' ' || u.areacode || ' ' || u.mobile as phone, '' as mobile, '' as fax, au.email from users u  inner join auth_user au on u.django_user_id=au.id inner join contracts_job cj on cj.employer_id=u.id where cj.created_at >= '"+t1+"'  and cj.created_at <= '"+t2+"'"         
        #print sql
        results = customQuery(sql,1)

        c = Context({'crmclients': results})   
        return HttpResponse(render_to_string('crmclients.json', c, context_instance=RequestContext(request)), mimetype='application/json')



@login_required(login_url='/accounts/login/')
def dealaveragetime_report(request):
    
    t = loader.get_template('./reports/dealaveragetime_report.html')
    c = Context({
        'dealaveragetime_report': payers_report,
    })
    return render_to_response('./reports/dealaveragetime_report.html', context_instance=RequestContext(request))
            
@csrf_exempt
def dealaveragetime_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00' 
        sql = "select jobtitle  || ' - AppID - ' || id, event, substring(to_char(time1,'YYYY-MM-DD HH24:MI:SS'),1, 19) as time1, substring(to_char(time2,'YYYY-MM-DD HH24:MI:SS'),1, 19) as time2 from ( select substring(cj.title,1, 25) as jobtitle, cj.created_at, ca.id,'Till Proposal' as event, cj.created_at as time1, min(cp.payed_timestamp) as time2 from  contracts_job cj inner join contracts_application ca on ca.job_id=cj.id inner join contracts_message pcm on pcm.application_id=ca.id inner join contracts_proposal cp on cp.message_ptr_id=pcm.id inner join contracts_message icm on icm.application_id=ca.id inner join contracts_invoice ci on ci.message_ptr_id=icm.id where cp.status=4 and ci.status=4 group by cj.id,ca.id,cj.created_at  union select substring(cj.title,1, 25) as jobtitle, cj.created_at , ca.id,'Till Invoice' as event, min(cp.payed_timestamp) as time1, min(ci.payed_timestamp) as time2 from  contracts_job cj inner join contracts_application ca on ca.job_id=cj.id inner join contracts_message pcm on pcm.application_id=ca.id inner join contracts_proposal cp on cp.message_ptr_id=pcm.id inner join contracts_message icm on icm.application_id=ca.id inner join contracts_invoice ci on ci.message_ptr_id=icm.id where cp.status=4 and ci.status=4 group by cj.id,ca.id,cj.created_at) total where created_at >='"+t1+"' and  created_at<='"+t2+"' "         
        
        results = customQuery(sql,1)
        ##print sql
        c = Context({'dealaveragetime': results})   
        return HttpResponse(render_to_string('dealaveragetime.json', c, context_instance=RequestContext(request)), mimetype='application/json')

@csrf_exempt
def dealsaveragetimegeneral_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00' 
 
        grouppertext= objs['grouper']
        #grouppertext = "Month"
        if grouppertext=="Month":
            grouper="7"
        elif grouppertext=="Day":
             grouper="10"
        elif grouppertext=="Year":
             grouper="4"
        else:
             grouper="2"    
        
        print grouper
        sql = "select substring(to_char(created_at,'YYYY-MM-DD HH24:MI:SS'),1, "+grouper+") as period, count(distinct job_id) ,avg(firstproposaldelay), avg(firstinvoicedelay) from (select cj.id as job_id ,ca.id,cj.created_at,  min(cp.payed_timestamp) as proposaltime,  min(ci.payed_timestamp) as invoicetime,  min(cp.payed_timestamp)-cj.created_at as firstproposaldelay, min(ci.payed_timestamp)-cj.created_at  as firstinvoicedelay from  contracts_job cj inner join contracts_application ca on ca.job_id=cj.id inner join contracts_message pcm on pcm.application_id=ca.id inner join contracts_proposal cp on cp.message_ptr_id=pcm.id inner join contracts_message icm on icm.application_id=ca.id inner join contracts_invoice ci on ci.message_ptr_id=icm.id where cp.status=4 and ci.status=4 and cj.created_at >='"+t1+"' and  cj.created_at<='"+t2+"' group by cj.id,ca.id,cj.created_at) total group by period"         
        
        #print sql
        results = customQuery(sql,1)

        c = Context({'dealsaveragetimegeneral': results})   
        return HttpResponse(render_to_string('dealsaveragetimegeneral.json', c, context_instance=RequestContext(request)), mimetype='application/json')

@login_required(login_url='/accounts/login/')    
def vistest_report(request):
    
   
    t = loader.get_template('./reports/vistest_report.html')
    c = Context({
        'vistest_report': vistest_report,
    })
    return HttpResponse(t.render(c))

@login_required(login_url='/accounts/login/')    
def categorypacks_report(request):
    
   
    t = loader.get_template('./reports/categorypacks_report.html')
    c = Context({
        'categorypacks_report': categorypacks_report,
    })
    return HttpResponse(t.render(c))

def getskillname(skillid):
    result = customQuery("select name from skills_skill where id="+skillid,0)    
    return result[0][0]

def decorateelement(element):
    result = list()
    #print element
    for i,item in enumerate(element[0]):
        if i<>0:      
            result.append(str(getskillname(str(item))))            
        else:
            result.append(str(item))         
    return  result

def getskillsgrouppower(listofskills):
    result = 0
    sql = "select  "
    headers = "occurrence"
    skillids = ""
    joins = ""
    wheresql = ""
    
    for i,item  in enumerate(listofskills):
        headers = headers + ", skill" + str(i+1)
        skillids = skillids + ", su" +str(i+1) +".skill_id as skill"+str(i+1)
        if i <> 0:
            joins = joins + " inner join skills_users su"+ str(i+1) +" on su1.id_user=su"+str(i+1)+".id_user "
        
        wheresql = wheresql + " and su"+ str(i+1) + ".skill_id=" + str(item[0])
        
        
    sql = sql + headers + " from (select count(id_user) as "  + headers + " from (select  distinct su1.id_user " +  skillids + " from skills_users su1 " + joins + " where " + wheresql[4:] + "  )  total group by " + headers[12:] + " order by occurrence desc) final" 
    ##print sql   
    result =  customQuery(sql,1)
    #print result
    return result
    
def list_duplicates(seq):
  seen = set()
  seen_add = seen.add
  seen_twice = set( x for x in seq if x in seen or seen_add(x) )
  return list( seen_twice )

def preparetoappend(element):
    if len(list_duplicates(element))>0:
        return False
    else:
        return True
def skillsmining(level,topskills):
    sql = "select skill_id from (select count(distinct id_user) as usercount, skill_id from skills_users group by skill_id order by usercount desc limit "+str(topskills)+" ) total"    
    skills = customQuery(sql,1)    
    params = list()
    for i in range(1,level+1):    
        params.append(skills)        
    results =  list()
    for element in itertools.product(*params):   
        if preparetoappend(element): 
            if not sorted(element) in results:                                    
                results.append(sorted(element))
               # print element
    calculatedresults = list()    
    for element in results:
        calculatedelement = getskillsgrouppower(element)
        if len(calculatedelement)>0:
            #print decorateelement(calculatedelement)
            calculatedresults.append(decorateelement(calculatedelement))
    return calculatedresults

@csrf_exempt     
def miningtest_getdata(request):       
    data = skillsmining(2,50)      
    headers = ["header1", "header2" , "headers3"]
    data.insert(0,headers)
    return HttpResponse(json.dumps(data), mimetype='application/json')  
    

@login_required(login_url='/accounts/login/')     
def miningtest_report(request):
    
   
    t = loader.get_template('./reports/miningtest_report.html')
    c = Context({
        'miningtest_report': miningtest_report,
    })
    return HttpResponse(t.render(c))
    
    
@csrf_exempt
def analytics_getdata(request):
    if request.method == 'POST':
        
        objs = simplejson.loads(request.raw_post_data)        
        t1 = objs['fromdate']
        t2 = objs['todate']                
        limit = objs['limit']
        

        data  = ga_get_visits(t1,t2,limit)
        
        c = Context({'analytics': data})     
        
           
	return HttpResponse(render_to_string('analytics_visitors.json', c, context_instance=RequestContext(request)), mimetype='application/json') 


@csrf_exempt
def getcategoriesbubbles(request):
    if request.method == 'GET':
        #objs = simplejson.loads(request.raw_post_data)                            
        sql = "select 'main' as name, 'null' as maincat, 1 as size union select name, 'main' as maincat, 2 as size from skills_subcategories where category_id=-1  union select final.category,maincat, 100*final.total_jobs as size from ( select category, maincat, count(distinct job_id) as total_jobs,  sum( paid_invoices) as converted, sum(paid_amount) as paid_amount, count(distinct case when paid_invoices>0 then job_id else null end) as converted_count from (select distinct  catjobs.*,  count(distinct case when ci.status=4 then ci.message_ptr_id else null end) as paid_invoices, sum(distinct case when ci.status=4 then cii.unit_price*cii.quantity else 0 end) as paid_amount from ( select job_id,cat_id, category, maincat  from ( select cj.id as job_id, ssc.id as cat_id, ssc.name as category, cats.name as maincat, similarity(cj.title, ssc.name) as coef from contracts_job cj inner join contracts_requiredskill crs on crs.job_id=cj.id  left outer join skills_skills_subcategories sssc on sssc.skill_id=crs.skill_id left outer  join skills_subcategories ssc on ssc.id=sssc.subcategory_id inner join skills_subcategories cats on cats.id=ssc.category_id where cj.approved=true and cj.created_at>'2013-12-01' group by cj.id, ssc.id, cats.id order by job_id, coef desc ) t1 where coef= (select max(coef) from  ( select cj.id as job_id, ssc.id as cat_id, similarity(cj.title, ssc.name) as coef from contracts_job cj inner join contracts_requiredskill crs on crs.job_id=cj.id  left outer join skills_skills_subcategories sssc on sssc.skill_id=crs.skill_id left outer  join skills_subcategories ssc on ssc.id=sssc.subcategory_id inner join skills_subcategories cats on cats.id=ssc.category_id where cj.approved=true and cj.created_at>'2013-12-01' group by cj.id, ssc.id order by job_id, coef desc ) t2 where t1.job_id=t2.job_id)) catjobs left outer join contracts_application ca on catjobs.job_id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_invoice ci on ci.message_ptr_id=cm.id left outer join contracts_invoiceitem cii on cii.invoice_id=ci.message_ptr_id group by catjobs.job_id, catjobs.cat_id, catjobs.category, catjobs.maincat) total group by category, maincat order by total_jobs desc ) final  order by size"
        print sql
        results = customQuery(sql,4)              
        c = Context({'buubles': results})     
        return HttpResponse(render_to_string('flare.json', c, context_instance=RequestContext(request)), mimetype='application/json')
       
       
@staff_member_required       
@login_required(login_url='/accounts/login/')
def skillscategorizer_tool(request):
    
    
    t = loader.get_template('./reports/skillscategorizer_tool.html')
    c = Context({
        'skillscategorizer_tool': skillscategorizer_tool,
    })
    return render_to_response('./reports/skillscategorizer_tool.html', context_instance=RequestContext(request))  
    
    
@csrf_exempt
def addcategory(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        name = objs['name']
        parentId = objs['parentId']

        id = getmaxid("skills_subcategories", 4)               
        
        sql = "insert into skills_subcategories(id,name, category_id) values("+str(id)+",'"+name+"', "+str(parentId)+")"   
        print sql              
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html')

@csrf_exempt
def updatecategory(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        id = objs['id']
        name = objs['name']                
        sql = "update skills_subcategories set name='"+name+"' where id="+str(id)
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html')

@csrf_exempt
def deletecategory(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        id = objs['id']         
        childrensql = "select count(*) from skills_subcategories where category_id="+ str(id)
        chresults = customQuery(childrensql,4)     
        if(chresults[0][0]==0):         
            sql = "delete from skills_subcategories where id="+str(id)        
            results = customQueryNoResults(sql,4)      
        else:
            results= 0
        return HttpResponse(results, mimetype='application/html')      

@csrf_exempt
def getcategories(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)                            
        sql = "select ca.*,count(distinct sc.skill_id) from categories ca  left outer join skills_categories sc  on sc.category_id=ca.id group by ca.id order by ca.id desc"
        results = customQuery(sql,4)              
        return HttpResponse(json.dumps(results), mimetype='application/json')  
        

@csrf_exempt
def getcategoriestree(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)                            
        sql = "select id, name || ' (' || count || ')' as count, category_id   from (select ssc1.id,ssc1.name,ssc1.category_id, count(distinct sssc.skill_id) from  skills_subcategories ssc1  left outer join skills_subcategories ssc2 on ssc2.category_id=ssc1.id  left outer join skills_skills_subcategories sssc on sssc.subcategory_id=ssc2.id where ssc1.category_id=-1 group by ssc1.id union  select ssc.id,ssc.name, category_id, count(distinct sssc.skill_id) from skills_subcategories ssc left outer join skills_skills_subcategories  sssc on sssc.subcategory_id=ssc.id where ssc.category_id<>-1 group by ssc.id) total  where id<>-1 order by id "
        print sql
        results = customQuery(sql,4)              
        #print results
        return HttpResponse(json.dumps(results), mimetype='application/json') 





def getcategorizedskillslistsql():
    sql = "select skill_id from skills_skills_subcategories"
     
    results = customQuery(sql,4) 
                 
    groupsql ="and ss.id not in ("
    if len(results)>0:
        for skill in results:
            groupsql = groupsql + str(skill[0]) + "," 
        groupsql = groupsql[:-1] + ")"    
    else: 
        groupsql = "  " 
       
    return groupsql          

@csrf_exempt
def getcurrentskill(request):
    if request.method == 'POST':
        
        objs = simplejson.loads(request.raw_post_data)    
                                
        sql = "select ss.id,ss.name,count(distinct su.id_user) as userscount from skills_skill ss left outer join skills_users su on su.skill_id=ss.id where ss.published=true and merge_to_id is null and deleted=false " + getcategorizedskillslistsql() +" group by ss.id order by userscount desc limit 1 "
        print sql
        results = customQuery(sql,4)              
        return HttpResponse(json.dumps(results), mimetype='application/json') 
        
@csrf_exempt
def getsuggestedskillslist1(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skillid=objs['skillid']
        sql = "select name from skills_skill where id=" + str(skillid)
        results = customQuery(sql,4) 
        orstring = ""
        words = results[0][0].split()     
        for word in words:
            orstring = orstring + " or lower(ss.name) like '%%"+word.lower()+"%%'"

        finalsql = " select ss.id,ss.name,count(distinct su.id_user) as userscount from skills_skill ss left outer join skills_users su on su.skill_id=ss.id where  ( "+orstring[3:]+" ) and ss.id<>"+str(skillid)+" and ss.published=true and merge_to_id is null and deleted=false " + getcategorizedskillslistsql() +"  group by ss.id order by userscount desc"   
                
        results = customQuery(finalsql,4)
        return HttpResponse(json.dumps(results), mimetype='application/json')


@csrf_exempt
def getsuggestedskillslist(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        skillid=objs['skillid']
        similarity = objs['similarity']
        sql = "select name from skills_skill where id=" + str(skillid)
        results = customQuery(sql,4) 
        orstring = ""
        words = results[0][0].split()     
        for word in words:
            orstring = orstring + " or lower(ss.name) like '%%"+word.lower()+"%%'"

        finalsql = " select ss.id,ss.name,count(distinct su.id_user) as userscount from skills_skill ss left outer join skills_users su on su.skill_id=ss.id where similarity(ss.name,'" + results[0][0] + "') > " + str(similarity)+ "  and ss.id<>"+str(skillid)+" and ss.published=true and merge_to_id is null and deleted=false " + getcategorizedskillslistsql() +"  group by ss.id order by userscount desc"   
        
        print finalsql        
        results = customQuery(finalsql,4)
        return HttpResponse(json.dumps(results), mimetype='application/json')   

@csrf_exempt
def suggestcategory(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        skillid=objs['skillid']
        sql = "select name from skills_skill where id=" + str(skillid)
        results = customQuery(sql,4) 

        words = results[0][0].split()     
        
        finalsql = "select ssc.id,ssc.name, ssc.category_id from (select * from (select name, id from skills_subcategories union select ss.name, sssc.subcategory_id from skills_skill ss inner join skills_skills_subcategories sssc on sssc.skill_id=ss.id ) allsimilars  where similarity(name, '"+ results[0][0] +"') > 0.3) total inner join skills_subcategories ssc on ssc.id=total.id  where ssc.category_id<>-1"
        print finalsql        
        results = customQuery(finalsql,4)
        return HttpResponse(json.dumps(results), mimetype='application/json')  
        
@csrf_exempt
def getskillsbycategory(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        categoryid=objs['categoryid']
        sql = "select skill_id from skills_skills_subcategories where subcategory_id=" + str(categoryid)
        results = customQuery(sql,4) 
        groupsql ="and ss.id  in ("
        if len(results)>0:
            for skill in results:
                groupsql = groupsql + str(skill[0]) + "," 
            groupsql = groupsql[:-1] + ")"    
        else: 
            groupsql = " and ss.id<0 "        
        
        finalsql  = "select ss.id,ss.name,count(distinct su.id_user) as userscount from skills_skill ss left outer join skills_users su on su.skill_id=ss.id where   ss.published=true and merge_to_id is null and deleted=false  "+groupsql+" group by ss.id order by userscount desc"
        print finalsql
        results = customQuery(finalsql,4)
        return HttpResponse(json.dumps(results), mimetype='application/json')               
        
@csrf_exempt
def categorizegroup(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        group = objs['group']
        catsgroup = objs['catsgroup']
        for catid in catsgroup:                  
            for skillid in group:
                id = getmaxid("skills_skills_subcategories",4)             
                sql = "insert into skills_skills_subcategories values("+str(id)+", "+str(skillid)+", "+str(catid)+")"        
                results = customQueryNoResults(sql,4)      
        return HttpResponse(group, mimetype='application/html') 
        
@csrf_exempt
def categorize(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skillid = objs['skillid']

        catsgroup = objs['catsgroup']      

           
        if (iscategorized(skillid)==True):         
             
            for catid in catsgroup:
                id = getmaxid("skills_skills_subcategories",4)
                sql = "insert into skills_skills_subcategories values("+str(id)+", "+str(skillid)+", "+str(catid)+")"
                results = customQueryNoResults(sql,4)      
        else:
            results = False
        return HttpResponse(results, mimetype='application/html')   


def iscategorized(skillid):
    sql = "select count(*) from skills_skills_subcategories where skill_id=" + str(skillid)
    print sql
    results = customQuery(sql,4) 
    
    if (results[0][0] > 0):
        return False
    else:
        return True

@csrf_exempt
def updateskillcat(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skillid = objs['skillid']
        categoryid = objs['categoryid']        
                    
        sql = "update skills_categories set category_id=" + str(categoryid) + " where skill_id=" +str(skillid)
        #print sql
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html') 
        
@csrf_exempt        
def updateskillgroupcat(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        
        group = objs['group']
        catsgroup = objs['catsgroup']
        for skillid in group: 
            sql = "delete from skills_skills_subcategories where skill_id=" + str(skillid)                
            customQueryNoResults(sql,4)  
            for catid in catsgroup:                                  
                print sql
                id = getmaxid("skills_skills_subcategories",4)
                sql = "insert into skills_skills_subcategories values("+str(id)+", "+str(skillid)+", "+str(catid)+")"        
                results = customQueryNoResults(sql,4) 
                print sql     
                
        return HttpResponse('done', mimetype='application/html')

         
@csrf_exempt
def uncategorize(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skillid = objs['skillid']                     
        sql = "delete from skills_categories where skill_id=" +  str(skillid)
        #print sql
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html')   

@csrf_exempt
def uncategorizegroup(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        group = objs['group']  
        for skillid in group:                           
            sql = "delete from skills_skills_subcategories where skill_id=" +  str(skillid)        
            customQueryNoResults(sql,4)      
        return HttpResponse('done', mimetype='application/html')                                        

@csrf_exempt
def categorizationstatus(request):
    if request.method == 'POST':
                    
        catsql = "select count(distinct skill_id) from skills_skills_subcategories"
        catresults = customQuery(catsql,4)   

        
        allsql = "select count(id) from skills_skill where published=true"   
        allresults = customQuery(allsql,4)
        result =  "[" +str(allresults[0][0]) + " , " + str(catresults[0][0]) +"]"
        
        return HttpResponse(result, mimetype='application/json') 


def getmaxid(table, db):
    sql = "select max(id) from " + table                 
    #print sql
    results = customQuery(sql,db)     
    try: 
        id=results[0][0]+1
    except:
        id=1
    
    return id

 
@login_required(login_url='/accounts/login/')   
def campaigns_report(request):
    
   
    t = loader.get_template('./reports/campaigns_report.html')
    c = Context({
        'campaigns_report': campaigns_report,
    })

    return HttpResponse(t.render(c)) 
    
    
    
@csrf_exempt
def campaigns_list_getdata(request):
    listsql = "select id, concat(substring(replace(replace(title,',',''), '''',''),1,45)) , substring(cast(FROM_UNIXTIME(sent) as char),1,16), cast(recipients as char)  from campaigns order by id desc limit 25;"   
            
    campaigns = customQuery(listsql,3)
   
    #campaignstring = ""
    #for campaign in campaigns:
        #campaignstring=campaignstring+","+str(campaign[1]) 
      
    #return campaignstring[1:]    
    
    c = Context({'campaigns': campaigns})     
    return HttpResponse(render_to_string('campaignslist.json', c, context_instance=RequestContext(request)), mimetype='application/json')
 
@csrf_exempt
def campaign_opens_getdata(id):
    totalsentsql = "select recipients,  substring(cast(FROM_UNIXTIME(sent) as char),1,10) from campaigns where id="+ str(id)
    
    totalsent = customQuery(totalsentsql,3)
    openssql = "select opens from campaigns where id="+str(id)            
    openstring = customQuery(openssql,3)[0][0]             
    ids = openstring.split(',')    
    idsstring=""
    
    for id in ids:
        idsstring=idsstring+","+id[:id.index(':')]
        
    openemailssql = "select email from subscribers where id in ("  +   idsstring[1:]   + ");"   
    emails = customQuery(openemailssql,3)
    emailsstring = ""
    opencount=0
    for email in emails:
        opencount=opencount+1
        emailsstring=emailsstring+ ",'" + email[0] + "'"        
        
      
    return totalsent[0], opencount,emailsstring[1:]
    
@csrf_exempt  
def emailcampaign_getdata(request):
    if request.method == 'POST':       
        objs = simplejson.loads(request.raw_post_data)
                 
        campaignid = objs['id']      
         
        campaigninfo = campaign_opens_getdata(campaignid)
        
        
        wheresql = " where au.email in ("+ campaigninfo[2] + ")  and au.date_joined>='" +  campaigninfo[0][1] +"'"
        
        sql = ("select count(distinct u.id) as user_count, count(distinct applicants.id) as applicants_count, count(distinct proposals.applicant_id) as proposal_count, count(distinct invoices.applicant_id) as invoice_count, count(distinct applicants.applicationid) as applicationscount, count(distinct proposals.proposalid) as proposalscount, count(distinct invoiceid) as invoicescount from users u inner join auth_user au on u.django_user_id=au.id left outer join (select u1.id,ca.id as applicationid from users u1 inner join contracts_application ca on ca.applicant_id=u1.id) applicants on applicants.id=u.id left outer join (select ca1.applicant_id,ca1.id,cp.message_ptr_id  as proposalid from contracts_application ca1 inner join contracts_message cm on cm.application_id=ca1.id inner join contracts_proposal cp on cp.message_ptr_id=cm.id) proposals on proposals.applicant_id=u.id left outer join (select ca2.applicant_id,ci.message_ptr_id as invoiceid from contracts_message cm1 inner join contracts_invoice ci on ci.message_ptr_id=cm1.id inner join contracts_application ca2 on ca2.id=cm1.application_id) invoices on invoices.applicant_id=u.id " + wheresql)
        
        results = customQuery(sql,1)
 	
 	
        c = Context({'statistics': results, 'totalsent': campaigninfo[0][0], 'opens': campaigninfo[1] })
        return HttpResponse(render_to_string('emailcampaign.json', c, context_instance=RequestContext(request)), mimetype='application/json')                   
    
@csrf_exempt
def ga_get_visits_query(service,profile_id, start, end, limit):
    dims = ""
    if limit=='Month':
        dims="ga:year,ga:month"
    elif limit=="Day":
        dims="ga:year,ga:month,ga:day"
    else:
        dims="ga:year,ga:week"    
    data = service.data().ga().get(ids="ga:" + profile_id, start_date=start, end_date=end, max_results=100000, dimensions = dims,       metrics="ga:visits,ga:pageviews").execute()
    
    results=[]
    if limit=='Month':
        for row in data['rows']:
            newrow=[row[0]+'-'+row[1], row[2], row[3]]            
            results.append(newrow)
            
    elif limit=='Day':
        for row in data['rows']:            
            newrow=[row[0]+'-'+row[1] + '-' + row[2], row[3], row[4]]
            results.append(newrow)
    else:
        for row in data['rows']:            
            newrow=[row[0]+'-'+row[1], row[2], row[3]]
            results.append(newrow)          
    return results

@csrf_exempt
def ga_get_visits(start_date, end_date, limit):      
    
    service = initialize_service()
    try:   
        profile_id = get_first_profile_id(service)
        param = profile_id
        print profile_id   
        results = ga_get_visits_query(service, profile_id, start_date, end_date, limit)

	return results
	    
	    
    except TypeError, error:
        param=error 
    except HttpError, error:
        param=error
    except AccessTokenRefreshError:
        param=error

   
 
                
@csrf_exempt
def get_results(service, profile_id,t1,t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems):
 
    rules = ['ga:pagePath=~job_posted=true,ga:pagePath=~finished_signup']

    print rules
    if  len(mediumCheckedItems)>0:
        rules.append(mediumCheckedItems)
    if  len(sourceCheckedItems)>0:
        rules.append(sourceCheckedItems)
    if  len(campaignCheckedItems)>0:
        rules.append(campaignCheckedItems)
   
    filters =  ';'.join(rules)
    #print filters
    params = {
        'ids': 'ga:' + profile_id,
        'start_date': str(t1),
        'end_date': str(t2),
        'metrics': 'ga:pageviews',
        'dimensions': 'ga:pagePath, ga:medium, ga:source, ga:campaign',
        'max_results': 100000,
        'filters' : filters
    }
    return service.data().ga().get(**params).execute()

      
      
      
@csrf_exempt
def get_sourceliststring():
    service = initialize_service()
    try:
        profile_id = get_first_profile_id(service)       
        param = profile_id
        if profile_id:
	    results=get_sourcelist(service, profile_id)
	    sources = ""
	    for source in results:
	        sources = sources + "" +source[0] + ","
	    sources = sources[:-1]  
            return sources
            
    except TypeError, error:
        param=error 
    except HttpError, error:

        param=error
    except AccessTokenRefreshError:
        param=error
        
    
    c = Context({'googleanalytics_report': freelancerdemography_report,  'param': param})
    return HttpResponse(t.render(c))
      
@csrf_exempt
def get_mediumliststring():
    service = initialize_service()
    try:
        profile_id = get_first_profile_id(service)       
        param = profile_id
        if profile_id:
	    results=get_mediumlist(service, profile_id)
	    sources = ""
	    for source in results:
	        sources = sources + "" +source[0] + ","
	    sources = sources[:-1]  
            return sources
            
    except TypeError, error:
        param=error 
    except HttpError, error:

        param=error
    except AccessTokenRefreshError:
        param=error
        
    
    c = Context({'googleanalytics_report': freelancerdemography_report,  'param': param})
    return HttpResponse(t.render(c))


@csrf_exempt
def get_campaignliststring():
    service = initialize_service()
    try:
        profile_id = get_first_profile_id(service)       
        param = profile_id
        if profile_id:
	    results=get_campaignlist(service, profile_id)
	    sources = ""
	    for source in results:
	        sources = sources + "" +source[0] + ","
	    sources = sources[:-1]  
            return sources
            
    except TypeError, error:
        param=error 
    except HttpError, error:

        param=error
    except AccessTokenRefreshError:
        param=error
        
    
    c = Context({'googleanalytics_report': freelancerdemography_report,  'param': param})
    return HttpResponse(t.render(c))


@csrf_exempt
def get_sourcelist(service, profile_id):
  return service.data().ga().get(
      ids="ga:" + profile_id,
      start_date="2013-01-01",
      end_date="2020-02-28",
      max_results=100000, 
      dimensions = "ga:source",
      metrics="ga:pageViews").execute()['rows']


@csrf_exempt
def get_campaignlist(service, profile_id):
  return service.data().ga().get(
      ids="ga:" + profile_id,
      start_date="2013-01-01",
      end_date="2020-02-28",
      max_results=100000, 
      dimensions = "ga:campaign",
      metrics="ga:pageViews").execute()['rows']


@csrf_exempt
def get_mediumlist(service, profile_id):
  return service.data().ga().get(
      ids="ga:" + profile_id,
      start_date="2013-01-01",
      end_date="2020-02-28",
      max_results=100000, 
      dimensions = "ga:medium",
      metrics="ga:pageViews").execute()['rows']



@login_required(login_url='/accounts/login/')     
def googleanalytics_report(request):
    
    t = loader.get_template('./reports/googleanalytics_report.html')
    service = initialize_service()
    try:
    # Step 2. Get the user's first profile ID.
        profile_id = get_first_profile_id(service)
        param = profile_id
        if profile_id:
	    results=get_sourcelist(service, profile_id)
	    sources = ""
	    for source in results:
	        sources = sources + "'" +source[0] + "',"
	    sources = "[" + sources[:-1]   + "]"   
            param = sources
           
           
      #print_results(results)

    except TypeError, error:
    # Handle errors in constructing a query.
        param=error 
     
    except HttpError, error:
    # Handle API errors.
        param=error

    except AccessTokenRefreshError:
    # Handle Auth errors.
        param=error
        
    
    c = Context({'googleanalytics_report': freelancerdemography_report,  'param': param})
    return HttpResponse(t.render(c))




@csrf_exempt        
def getcpcGroup(t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems):        
    service = initialize_service()
    try:   
        profile_id = get_first_profile_id(service)
        param = profile_id
        if profile_id:    
            results = get_results(service, profile_id,t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems)
            
            count=0
            userprofiles=""
            jobsids=""
            for userprofile in results['rows']:           
                if userprofile[0] .find('just_finished_signup')>0:
                    profileid =  "'" + userprofile[0].replace("?just_finished_signup=True","").replace("/profile/","").replace("/","").replace("&edit=true","").lower() + "',"                               
                    userprofiles = userprofiles + profileid
                    count=count+1
                    
                else:                    
                    profileid =  "'" + userprofile[0].replace("profiles?job_posted=true","").replace("job","").replace("/","") + "',"                               
                    jobsids = jobsids + profileid

            usersbyjobs = getProfileIdsByJobIds(jobsids) 
           
	    userprofiles= "(" +  ','.join([userprofiles[:-1], usersbyjobs]) +  ")"
            print userprofiles
	    return userprofiles
	    
    except TypeError, error:
        param=error 
    except HttpError, error:
        param=error
    except AccessTokenRefreshError:
        param=error
        
def getcpcGroupNewAndOld(t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems):      
    cpcresponse = getcpcGroup(t1, t2, mediumCheckedItems, sourceCheckedItems, campaignCheckedItems)
    sql1 = ("select id from users where lower(homepage) in " + cpcresponse)
    sql2 = ("select id from users where lower(cast(id as text)) in " + cpcresponse)
    

    result1 = customQuery(sql1,2)
    result2 = customQuery(sql2,1)
    
    result = result1 + result2  
    count=0
    userprofiles=""
    for userprofile in result:
        userprofiles = userprofiles + str(userprofile[0]) + ","
        count=count+1
    userprofiles= "(" + userprofiles[:-1] + ")"

    return userprofiles
    
    
def getProfileIdsByJobIds(jobsids):      

    sql = ("select employer_id from contracts_job where id in (" + jobsids[:-1] + ")")
    print sql
    
    result = customQuery(sql,1)    

    count=0
    userprofiles=""
    for userprofile in result:
        userprofiles = userprofiles + "'" + str(userprofile[0]) + "',"
        count=count+1
    userprofiles= userprofiles[:-1]
    
    return userprofiles     


def get_first_profile_id(service):
  # Get a list of all Google Analytics accounts for this user
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    # Get the first Google Analytics account
    firstAccountId = accounts.get('items')[0].get('id')

    # Get a list of all the Web Properties for the first account
    webproperties = service.management().webproperties().list(accountId=firstAccountId).execute()

    if webproperties.get('items'):
      # Get the first Web Property ID
      firstWebpropertyId = webproperties.get('items')[0].get('id')

      # Get a list of all Views (Profiles) for the first Web Property of the first Account
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      if profiles.get('items'):
        # return the first View (Profile) ID
        return profiles.get('items')[0].get('id')

  return None
  
  
def detect(path):
    urllib.urlretrieve (path, "img.jpg") 
    img = cv2.imread("img.jpg")
    print img
    cascade = cv2.CascadeClassifier("/home/mahfouz/nabbeshreports/templates/haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20)) 
    print rects
    return rects


@csrf_exempt    
def download(request):
    revenue_getdata(request)
    response = ''
    return response

@csrf_exempt
def crm_notes_getdata(request):
        objs = simplejson.loads(request.raw_post_data)        
        print objs         
        user_id = objs['user_id']      
        print user_id
        sql = ("select crm.*, case when (u.photo <>'' and u.photo is not null and u.photo<>'/static/images/thumb.png') then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end as cphoto  from crm_notes crm inner join users u on crm.crm_user_id=u.id where user_id="+str(user_id)+" order by created desc")
        print sql
        results = customQuery(sql,4)

     
        results = customQuery(sql,1) 


        c = Context({'notes': results})
        return HttpResponse(render_to_string('crm_notes.html', c, context_instance=RequestContext(request)), mimetype='application/html') 

def get_current_userid(request):                 

        
        sql = ("select u.id from users u inner join auth_user au on u.django_user_id=au.id where au.username ='" + str(request.user)+"'")
        
        results = customQuery(sql,4)

        return results[0][0] 


@csrf_exempt
def crm_notes_add(request):
        
        objs = simplejson.loads(request.raw_post_data)     
        print objs            
        user_id = objs['user_id']      
        message = objs['message']
        crm_user_id = str(get_current_userid(request))
        sql = ("insert into crm_notes(user_id, message, created, crm_user_id) values("+str(user_id)+", '"+message+"', now(), "+ crm_user_id +")")
        print sql            
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html')     

@csrf_exempt
def crm_notes_delete(request):        
        objs = simplejson.loads(request.raw_post_data)     
        print objs                 
        messageId = objs['messageId']
        sql = "delete from crm_notes where id=" +str(messageId)
        print sql            
        results = customQueryNoResults(sql,4)      
        return HttpResponse(results, mimetype='application/html')   

@csrf_exempt
def tracker_image(request):
    import urllib2;   
    url ="https://s3-us-west-2.amazonaws.com/nabbeshscripts/tracker.png"; 
    opener = urllib2.urlopen(url);  
    mimetype = "application/octet-stream"
    response = HttpResponse(opener.read(), mimetype=mimetype)
    response["Content-Disposition"]= "attachment; filename=tracker.png"
    return response 


