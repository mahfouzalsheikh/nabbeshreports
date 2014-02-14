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
    
    user_list = Users.objects.filter(id__gt=5000)
    t = loader.get_template('index.html')
    #c = Context({
    #    'user_list': user_list,
    #})
    #return render_to_response('index.html', c)
    
    return render_to_response('index.html', context_instance=RequestContext(request))
    #return HttpResponse(t.render(c))



def customQuery(sql, db):
    print sql
    if db==0:
        result=customQueryOffline(sql)
        #print result
        return result
    else:
        result=customQueryLive(sql)
        #print result
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

        
        
       
@csrf_exempt        
def freelancerdemography_report(request):
    
    t = loader.get_template('./reports/freelancerdemography_report.html')
    c = Context({
        'freelancerdemography_report': freelancerdemography_report,
    })
    return HttpResponse(t.render(c))

    
    
@csrf_exempt
def freelancerdemography_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        grouper = objs['grouper']
        sql = ("select "+grouper+", count(id) as usercount from users where "+grouper+" is not null and "+grouper+" <>''  group by "+grouper+" order by usercount desc")
 
        results = customQuery(sql,0)

        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('freelancersdemography.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        
        
        
        
        
@csrf_exempt
def freelancersgender_report(request):
    
    t = loader.get_template('./reports/freelancersgender_report.html')
    c = Context({
        'freelancersgender_report': freelancersgender_report,
    })
    return HttpResponse(t.render(c))
            
@csrf_exempt
def freelancersgender_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select usercount, case gender when 0 then 'Male' when 1 then 'Female' end from \
         (select count(*) as usercount, gender from users where gender < 2 group by gender) total;"
        results = customQuery(sql,0)
        print results
 
        c = Context({'genders': results})
   
        return HttpResponse(render_to_string('freelancersgender.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        
        
        
@csrf_exempt
def freelancerseducation_report(request):
    
    t = loader.get_template('./reports/freelancerseducation_report.html')
    c = Context({
        'freelancerseducation_report': freelancerseducation_report,
    })
    return HttpResponse(t.render(c))
            
@csrf_exempt
def freelancerseducation_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select  case degree when 6 then 'Bachelor of Science' when 7 then 'High School' when 5 then 'Bachelor of Arts' when 4 then 'Executive MBA' when 3 then 'MBA' when 2 then 'Masters' when 1 then 'PHD' end as education, usercount from (select count(distinct u.id ) as usercount, edu.degree from education edu inner join users u on edu.id_user=u.id group by edu.degree) total"
        results = customQuery(sql,0)
        print results
 
        c = Context({'educations': results})
   
        return HttpResponse(render_to_string('freelancerseducation.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        

@csrf_exempt
def freelancersages_report(request):
    
    t = loader.get_template('./reports/freelancersages_report.html')
    c = Context({
        'freelancersages_report': freelancersgender_report,
    })
    return HttpResponse(t.render(c))

@csrf_exempt            
def freelancersages_getdata(request):
    if request.method == 'POST':
        #objs = simplejson.loads(request.raw_post_data)

        sql = "select  sum(ucount) as usercounts,case when ageu <18 then '1) Under 18' when ageu >= 18 and ageu<=24 then '2) 18 to 24' when ageu >= 25 and ageu<=34 then '3) 25 to 34' when ageu >= 35 then '4) Over 35' END as age_range from (select count(total.id) as ucount, 2013 - total.yobn as ageu from (select t1.id, t1.yob :: integer yobn from(select id, substring(dob,length(dob)-3, length(dob)) as yob from users where dob<>'') t1 where t1.yob ~E'^\\\d+$') total group by ageu order by ageu) total group by age_range order by age_range;"
        results = customQuery(sql,0)

        
        c = Context({'ages': results})
        return HttpResponse(render_to_string('freelancersages.json', c, context_instance=RequestContext(request)), mimetype='application/json')        
        
        
 
@csrf_exempt
def dashboard(request):
    
    t = loader.get_template('./reports/dashboard.html')
    c = Context({
        'dashboard': dashboard,
    })
    return HttpResponse(t.render(c))
    
    
@csrf_exempt 
def dashboard_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate'] + ' 00:00:00+00'
        t2 = objs['todate']  + ' 23:59:59+00'
        
        print t1
        print t2

        grouppertext= objs['limit']
        #grouppertext = "7"
        if grouppertext=="Month":
            grouper="7"
        else:
            grouper="10"
        
        header_sql = ("select msgdate,COALESCE(message_count,0) as message_count,COALESCE(nmessage_count,0) as nmessage_count,COALESCE(allusers_count,0) as allusers_count,COALESCE(freelancer_count,0) as freelancer_count,COALESCE(employers_count,0) as employers_count,COALESCE(realemployers_count,0) as realemployers_count ,COALESCE(job_count,0) as job_count, COALESCE(proposal_count,0) as proposal_count, COALESCE(paidproposal_count,0) as paidproposal_count, COALESCE(application_count,0) as application_count,COALESCE(invitation_count,0) as invitation_count , COALESCE(invoice_count,0) as invoice_count,COALESCE(invoicepaid_count,0) as invoicepaid_count,round(COALESCE(invperjobavg,0),2) as invperjobavg, round(appperjobavg::numeric,2) as appperjobavg  from ")
        
        workflow_messages_sql = ("(select count(distinct id) as message_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as msgdate from contracts_message where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by msgdate) contractsmessages left outer join ")
        
        allusers_sql = ("(select count(distinct u.id) as allusers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) allusers on contractsmessages.msgdate=allusers.datejoined left outer join")
        
        freelancers_sql = ("(select count(distinct u.id) as freelancer_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_freelancer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) freelancers on contractsmessages.msgdate=freelancers.datejoined left outer join")
        
        employers_sql = ("(select count(distinct u.id) as employers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_employer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) employers on freelancers.datejoined=employers.datejoined left outer join")
        
        realemployers_sql = ("(select count(distinct u.id) as realemployers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id inner join contracts_job cj on cj.employer_id=u.id where  date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) realemployers on contractsmessages.msgdate=realemployers.datejoined left outer join")
        
        jobs_sql =("(select count(id) as job_count, substring(to_char(created_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as createdat from contracts_job  where created_at>='"+t1+"' and created_at<='"+t2+"' group by createdat) jobs on jobs.createdat=contractsmessages.msgdate  left outer join")
        
        contractsmessages_sql = ("(select count(distinct id) as nmessage_count, substring(to_char(sent_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as sentat from messages_message where sent_at>='"+t1+"' and sent_at<='"+t2+"' group by sentat) messages on messages.sentat=contractsmessages.msgdate   left outer join")
        
        porposals_sql  = ("(select substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as proposalsent,count(*) as proposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalsent) proposals on proposals.proposalsent=contractsmessages.msgdate left outer join ")
                
        proposalspaid_sql = ("(select substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as proposalpaid,sum(case when cp.status=4 then 1 else 0 end) as paidproposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalpaid) paidproposals on paidproposals.proposalpaid=contractsmessages.msgdate left outer join ")  
                     
        
        application_sql = ("(select count(distinct id) as application_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as appliedat from contracts_application   where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by appliedat) applications on applications.appliedat=contractsmessages.msgdate left outer join ")
                
        invited_sql = ("(select count(*) as invitation_count, substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as invited_at  from contracts_job_invited cji inner join contracts_job cj on cj.id=cji.job_id where cj.created_at>='"+t1+"' and cj.created_at<='"+t2+"' group by invited_at) invitations on invitations.invited_at=contractsmessages.msgdate left outer join")
        
        invoicesent_sql = ("(select count(distinct ci.message_ptr_id) as invoice_count,substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as invoicesent from contracts_invoice ci inner join contracts_message cm on ci.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by invoicesent) invoicessent on invoicessent.invoicesent=contractsmessages.msgdate left outer join ")
        
        invoicepaid_sql = ("(select count(distinct ci.message_ptr_id) as invoicepaid_count,substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as invoicepaid from contracts_invoice ci inner join contracts_message cm on ci.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by invoicepaid) invoicespaid on invoicespaid.invoicepaid=contractsmessages.msgdate left outer join ")
        
        invperjob_sql = ("(select avg(inv.jobinv) as invperjobavg, substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as invsentat from contracts_job cj inner join (select count(cji.id) as jobinv,cji.job_id from contracts_job_invited cji  group by cji.job_id) inv on inv.job_id=cj.id group by invsentat) invitationsperjob on invitationsperjob.invsentat=contractsmessages.msgdate left outer join ")
        
        appperjob_sql = ("(select count(ca.id)::float/count(distinct ca.job_id)::float as appperjobavg,substring(to_char(ca.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as appliedat  from contracts_application ca  group by appliedat) applicationperjob on applicationperjob.appliedat=contractsmessages.msgdate ")
        
        sql = (header_sql + workflow_messages_sql + allusers_sql + freelancers_sql + employers_sql + realemployers_sql + jobs_sql + contractsmessages_sql + porposals_sql + proposalspaid_sql + application_sql +invited_sql+ invoicesent_sql + invoicepaid_sql +invperjob_sql +appperjob_sql+  "  order by msgdate")
        
        
        
        results = customQuery(sql,0)

        #print results
 
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('dashboard.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
        
@csrf_exempt
def jobs_employers_statistics(request):
    
    t = loader.get_template('./reports/jobs_employers_statistics.html')
    c = Context({
        'jobs_employers_statistics': dashboard,
    })
    return HttpResponse(t.render(c))
        
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
        else:
            grouper="10"
        
        header_sql = ("select datejoined,max(jobs_per_employer),min(jobs_per_employer), round(avg(jobs_per_employer),3), round(median(jobs_per_employer),3)")
        
        from_sql = ("from (select count(cj.id) as jobs_per_employer, u.id,substring(to_char(au.date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from contracts_job cj inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id where au.date_joined>='"+t1+"' and au.date_joined<='"+t2+"'  and cj.created_at<=(date_joined + INTERVAL '"+period+" Day') group by u.id,au.date_joined order by jobs_per_employer desc) total group by datejoined order by datejoined;")
        sql = (header_sql + from_sql)
        

        results = customQuery(sql,0)

        #print results
 
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('jobs_employers_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
@csrf_exempt
def jobs_applications_statistics(request):
    if request.method == 'POST':
    	objs = simplejson.loads(request.raw_post_data)
    	#print objs
        t = loader.get_template('./reports/jobs_applications_statistics.html')
        param =  objs['param']
        c = Context({'jobs_applications_statistics': dashboard, 'param': param})
        
#        return HttpResponse(t.render(c) )
        return HttpResponse(render_to_string('./reports/jobs_applications_statistics.html', c, context_instance=RequestContext(request)), mimetype='application/html') 
        
        
@csrf_exempt 
def jobs_applications_statistics_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
        keywords = objs['searchkeywords']
        
       
     
        searchsql = ""
        if keywords <> "":
            searchsql = "and (lower(substring(cj.title,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.email,1,40)) like '%%" +keywords.lower() + "%%' or lower(substring(au.first_name || ' ' || au.last_name,1,40)) like '%%" +keywords.lower() + "%%')"
       
       
        sql = ("select au.first_name || ' ' || au.last_name as employer_name,au.email as Employer_Email, cj.id as job_id,substring(cj.title,1,30) as job_title,substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16) as created_at,count(distinct ca.id) as application_count, count( distinct case when ca.shortlisted=true then ca.id else null end) as shortlisted, sum(case when cm.from_applicant=true then 1 else 0 end) as applicant_messages, sum(case when cm.from_applicant=false then 1 else 0 end) as employer_responses,count(distinct cp.message_ptr_id) as proposal_count, sum(case when cp.status=4 then 1 else 0 end) as acceptedproposal_count, case when cj.status=1 then 'Active' when cj.status=2 then 'Closed' end as JobStatus from contracts_job cj left outer join contracts_application ca   on cj.id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id where created_at>='"+t1+"' and created_at<='"+t2+"' "+searchsql+" group by employer_name,cj.id,job_title,cj.created_at,au.email order by cj.created_at desc;")
        
       
        results = customQuery(sql,1)
        
                 
     
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('jobs_applications_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json') 



@csrf_exempt 
def jobs_communications_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        job_id = objs['job_id']
        print job_id;
        
        sql = ("select u.id,au.email,ca.id as application_id,case when ca.shortlisted=true then 1 else 0 end as shortlisted,count(cp.message_ptr_id) as proposals, sum(case when cp.status=4 then 1 else 0 end) as acceptedproposal_count, sum(case when cm.from_applicant=false then 1 else 0 end) as employer_responses from contracts_application ca inner join users u on u.id=ca.applicant_id inner join auth_user au on u.django_user_id=au.id inner join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id where job_id= "+job_id+" group by u.id,au.email, ca.id,shortlisted ;")
        
        results = customQuery(sql,1)
 	print results	
        c = Context({'messages': results})
        return HttpResponse(render_to_string('jobs_communications.json', c, context_instance=RequestContext(request)), mimetype='application/json')             
        


@csrf_exempt
def sign_job_proposal_invoice(request):
    
    t = loader.get_template('./reports/sign_job_proposal_invoice.html')
    c = Context({
        'sign_job_proposal_invoice': dashboard,
    })
    return HttpResponse(t.render(c))        
        
@csrf_exempt  
def sign_job_proposal_invoice_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        signupchecked = objs['signupchecked']

        wheresql = ""
        if signupchecked== "True":
            wheresql= " Where u.is_employer=True"
        else:
            wheresql = ""
           
        sql = ("select * from (select count(distinct au.email) as signed_up, count(distinct jobsposted.id) as posted_jobs, count(distinct paidproposal.id) as paid_proposal, count(distinct invoices.applicant_id) as invoices_paid  from users u inner join auth_user au on u.django_user_id=au.id  left outer join (select u1.id from users u1 inner join contracts_job cj on cj.employer_id= u1.id) jobsposted on jobsposted.id=u.id left outer join (select u2.id from users u2 inner join contracts_application ca2 on ca2.applicant_id=u2.id inner join contracts_message cm2 on cm2.application_id=ca2.id inner join contracts_proposal cp2 on cp2.message_ptr_id=cm2.id where cp2.status=4) paidproposal on paidproposal.id=u.id left outer join (select distinct ca1.job_id,ci.status,ci.message_ptr_id,ca1.applicant_id from contracts_invoice ci inner join contracts_message cm1 on cm1.id=ci.message_ptr_id inner join contracts_application ca1 on ca1.id=cm1.application_id where ci.status=4) invoices on invoices.applicant_id=u.id " + wheresql +") total ")
        
        results = customQuery(sql,0)
 	print results	
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('sign_job_proposal_invoice.json', c, context_instance=RequestContext(request)), mimetype='application/json')                   
        
        
@csrf_exempt        
def sign_application_proposal_invoice(request):
    
    t = loader.get_template('./reports/sign_application_proposal_invoice.html')
    c = Context({
        'sign_application_proposal_invoice': dashboard,
    })
    return HttpResponse(t.render(c))        
        
@csrf_exempt  
def sign_application_proposal_invoice_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs
        
        signupchecked = objs['signupchecked']
        #t1 = objs['fromdate']  + ' 00:00:00+00'
        #t2 = objs['todate'] + ' 23:59:59+00'
        
        #keywords = objs['searchkeywords']
        wheresql = ""
        if signupchecked== "True":
            wheresql= " Where u.is_freelancer=True"
        else:
            wheresql = ""

           
        sql = ("select count(distinct u.id) as user_count, count(distinct applicants.id) as applicants_count, count(distinct proposals.applicant_id) as proposal_count, count(distinct invoices.applicant_id) as invoice_count from users u inner join auth_user au on u.django_user_id=au.id left outer join (select u1.id from users u1 inner join contracts_application ca on ca.applicant_id=u1.id) applicants on applicants.id=u.id left outer join (select ca1.applicant_id,ca1.id,cp.message_ptr_id from contracts_application ca1 inner join contracts_message cm on cm.application_id=ca1.id inner join contracts_proposal cp on cp.message_ptr_id=cm.id) proposals on proposals.applicant_id=u.id left outer join (select ca2.applicant_id,ci.message_ptr_id from contracts_message cm1 inner join contracts_invoice ci on ci.message_ptr_id=cm1.id inner join contracts_application ca2 on ca2.id=cm1.application_id) invoices on invoices.applicant_id=u.id " + wheresql)
        
        results = customQuery(sql,0)
 	print results	
        c = Context({'statistics': results})
        return HttpResponse(render_to_string('sign_application_proposal_invoice.json', c, context_instance=RequestContext(request)), mimetype='application/json')                   
        
        

@csrf_exempt
def top_freelancers(request):
    
    t = loader.get_template('./reports/top_freelancers.html')
    c = Context({
        'top_freelancers': dashboard,
    })
    return HttpResponse(t.render(c))   

@csrf_exempt 
def top_freelancers_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        print objs
        
        priority = objs['priority']
        limit = objs['limit']
        #t1 = objs['fromdate']  + ' 00:00:00+00'
        #t2 = objs['todate'] + ' 23:59:59+00'
        print priority;
        #keywords = objs['searchkeywords']
        sortsql = ""
        if priority== "Skills Count":
            sortsql= " order by skills_count desc"
        else:
            sortsql= " order by application_count desc"

        #print sortsql   
        sql = ("select u1.id,au.first_name || ' ' || au.last_name as fullname , au.email, 'http://www.nabbesh.com/profile/' || u1.id as homepage,  case when (u1.photo <>'' and u1.photo is not null) then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u1.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as photo,u1.country, total.skills_count, total.application_count  from users u1 inner join auth_user au on  u1.django_user_id=au.id   inner join  (select u.id, count(distinct su.skill_id) skills_count, count(distinct ca.id) as application_count  from users u  inner join skills_users su on su.id_user=u.id left outer join contracts_application ca on ca.applicant_id=u.id  group  by u.id "+sortsql+" limit "+ limit+") total on total.id=u1.id;")
        
        results = customQuery(sql,0)
 	#print results	
        c = Context({'users': results})
        return HttpResponse(render_to_string('top_freelancers.json', c, context_instance=RequestContext(request)), mimetype='application/json')             

@csrf_exempt
def top_employers(request):
    
    t = loader.get_template('./reports/top_employers.html')
    c = Context({
        'top_employers': dashboard,
    })
    return HttpResponse(t.render(c))   

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

        
        sql = ("select u.id, au.first_name || ' ' || au.last_name as fullname , au.email, 'http://www.nabbesh.com/profile/' || u.id as homepage, case when (u.photo <>'' and u.photo is not null) then 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') else 'http://www.nabbesh.com/static/images/thumb.png' end  as photo, u.country, count(distinct cj.id) as jobs_count, count(distinct applications.proposal_id) as accepted_proposals_count from users u inner join auth_user au on u.django_user_id=au.id  left outer join contracts_job cj on cj.employer_id=u.id   left outer join ( select distinct cj1.employer_id,cm1.id as proposal_id from contracts_job cj1 inner join contracts_application ca1 on ca1.job_id=cj1.id inner join contracts_message cm1 on cm1.application_id=ca1.id  inner join contracts_proposal cp1 on cp1.message_ptr_id=cm1.id where cp1.status=4) applications on applications.employer_id=u.id group  by u.id,au.email,fullname,photo,homepage  "+sortsql+"  desc limit " + limit)
        
        results = customQuery(sql,0)
 	#print results	
        c = Context({'users': results})
        return HttpResponse(render_to_string('top_employers.json', c, context_instance=RequestContext(request)), mimetype='application/json')  
        
        


@csrf_exempt        
def skillsdemography_report(request):
    
    t = loader.get_template('./reports/skillsdemography_report.html')
    c = Context({
        'skillsdemography_report': freelancerdemography_report,
    })
    return HttpResponse(t.render(c))

    
    
@csrf_exempt
def skillsdemography_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        limit = objs['limit']
        priority = objs['priority']
        print priority
        
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
 
        results = customQuery(sql,0)

        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('skillsdemography.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
        
        
        
@csrf_exempt
def skillsdemographydetails_getdata(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        skill_id= objs['skill_id']
        sql = ("select country, jobs_count,users_count, case when jobs_count<>0 then cast(users_count as real)/cast(jobs_count as real) else 0 end as availability_rate from  (select case when total1.country is not null then total1.country else total2.country end as country, case when total1.jobs_count is not null then total1.jobs_count else 0 end as jobs_count, case when total2.users_count is not null then total2.users_count else 0 end as users_count from ( select count(*) as jobs_count,u.country  from contracts_job cj  inner join users u on cj.employer_id=u.id  inner join contracts_requiredskill crs on crs.job_id=cj.id where crs.skill_id= "+skill_id +" group by u.country) total1 full outer join  (select count(*) as users_count, u.country  from users u  inner join skills_users su on su.id_user=u.id where su.skill_id="+skill_id+" group by u.country) total2 on total1.country=total2.country ) total")
 
        results = customQuery(sql,0)

        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('skillsdemographydetails.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
            

@csrf_exempt        
def geocodes(request):
    
    t = loader.get_template('./geocodes.json')
    c = Context({
        'geocodes': geocodes,
    })
    return HttpResponse(t.render(c))
            
            
@csrf_exempt        
def crosscountryapps_report(request):
    
    t = loader.get_template('./reports/crosscountryapps_report.html')
    c = Context({
        'crosscountryapps_report': crosscountryapps_report,
    })
    return HttpResponse(t.render(c))
            
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
 
        results = customQuery(sql,0)

        c = Context({'lines': results})
        if grouplevel=='Country':
	    return HttpResponse(render_to_string('crosscountryapps.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	else:
	    return HttpResponse(render_to_string('crosscityapps.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	    
            
                        
@csrf_exempt        
def proposals_report(request):
    
    t = loader.get_template('./reports/proposals_report.html')
    c = Context({
        'proposals_report': proposals_report,
    })
    return HttpResponse(t.render(c))
            
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
            
                  
        sql = ("select substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1, "+grouper+") as sentat, COALESCE(sum(case when cp.status=1 then cp.deposit_amount end),0) as New, count(case when cp.status=1 then 1 end) as NewCount, round(COALESCE(avg(case when cp.status=1 then cp.deposit_amount end),0),2) as NewAvg, COALESCE(sum(case when cp.status=2 then cp.deposit_amount end),0) as Canceled, count(case when cp.status=2 then 1 end) as CanceledCount, round(COALESCE(avg(case when cp.status=2 then cp.deposit_amount end),0),2) as CanceledAvg, COALESCE(sum(case when cp.status=3 then cp.deposit_amount end),0) as Declined, count(case when cp.status=3 then 1 end) as DeclinedCount, round(COALESCE(avg(case when cp.status=3 then cp.deposit_amount end),0),2) as Avg, COALESCE(sum(case when cp.status=4 then cp.deposit_amount end),0) as Accepted, count(case when cp.status=4 then 1 end) as AcceptedCount, round(COALESCE(avg(case when cp.status=4 then cp.deposit_amount end),0),2) as AcceptedAvg from contracts_proposal cp inner join contracts_message cm on cm.id=cp.message_ptr_id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"'  group  by sentat order by sentat ") 
        results = customQuery(sql,0)
        c = Context({'proposals': results})        
	return HttpResponse(render_to_string('proposals.json', c, context_instance=RequestContext(request)), mimetype='application/json')           
	
            
                       
                
@csrf_exempt
def get_results(service, profile_id):
  # Use the Analytics Service Object to query the Core Reporting API
  return service.data().ga().get(
      ids="ga:" + profile_id,
      start_date="2014-02-01",
      end_date="2014-02-28",
      max_results=10000, 
      dimensions = "ga:pagePath, ga:medium",
      metrics="ga:pageviews",
      filters="ga:pagePath=~finished_signup;ga:medium=~cpc").execute()
      
      
#@permission_required('polls.can_vote')
@csrf_exempt        
def googleanalytics_report(request):
    
    t = loader.get_template('./reports/googleanalytics_report.html')
    service = initialize_service()
    try:
    # Step 2. Get the user's first profile ID.
        profile_id = get_first_profile_id(service)
        param = profile_id
        if profile_id:
      # Step 3. Query the Core Reporting API.
            results = get_results(service, profile_id)

      # Step 4. Output the results.
            param = results['rows'][4]
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
