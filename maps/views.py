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
import datetime
import dateutil.parser
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db import connection
from django.db import connections
from django.contrib.auth.decorators import login_required


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
        print result
        return result
    else:
        result=customQueryLive(sql)
        print result
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

        sql = "select * from (select count(*) as usercount,\
        replace(reverse(substring(reverse(replace(formatted_address,'-',',')),1,position(',' in reverse(replace(formatted_address,'-',','))))),', ','') \
        as country from users group by country order by usercount desc) total where usercount>="+objs['limit']+" and country  is not null and country  <>'' union \
	select sum(usercount) as usercount, 'All The Rest' from (select count(*) as usercount,replace(reverse(substring(reverse(replace(formatted_address,'-',',')),\
	1,position(',' in reverse(replace(formatted_address,'-',','))))),', ','') as country from users group by country order by usercount desc)\
	 total where usercount<"+objs['limit']+" order by usercount desc;"
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
        
        header_sql = ("select msgdate,COALESCE(message_count,0) as message_count,COALESCE(nmessage_count,0) as nmessage_count,COALESCE(freelancer_count,0) as freelancer_count,COALESCE(employers_count,0) as employers_count,COALESCE(realemployers_count,0) as realemployers_count ,COALESCE(job_count,0) as job_count, COALESCE(proposal_count,0) as proposal_count, COALESCE(paidproposal_count,0) as paidproposal_count, COALESCE(application_count,0) as application_count, COALESCE(invoice_count,0) as invoice_count,COALESCE(invoicepaid_count,0) as invoicepaid_count from ")
        
        workflow_messages_sql = ("(select count(distinct id) as message_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as msgdate from contracts_message where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by msgdate) contractsmessages left outer join ")
        
        freelancers_sql = ("(select count(distinct u.id) as freelancer_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_freelancer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) freelancers on contractsmessages.msgdate=freelancers.datejoined left outer join")
        
        employers_sql = ("(select count(distinct u.id) as employers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_employer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) employers on freelancers.datejoined=employers.datejoined left outer join")
        
        realemployers_sql = ("(select count(distinct u.id) as realemployers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id inner join contracts_job cj on cj.employer_id=u.id where  date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) realemployers on contractsmessages.msgdate=realemployers.datejoined left outer join")
        
        jobs_sql =("(select count(id) as job_count, substring(to_char(created_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as createdat from contracts_job  where created_at>='"+t1+"' and created_at<='"+t2+"' group by createdat) jobs on jobs.createdat=contractsmessages.msgdate  left outer join")
        
        contractsmessages_sql = ("(select count(distinct id) as nmessage_count, substring(to_char(sent_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as sentat from messages_message where sent_at>='"+t1+"' and sent_at<='"+t2+"' group by sentat) messages on messages.sentat=contractsmessages.msgdate   left outer join")
        
        porposals_sql  = ("(select substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as proposalsent,count(*) as proposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalsent) proposals on proposals.proposalsent=contractsmessages.msgdate left outer join ")
                
        proposalspaid_sql = ("(select substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as proposalpaid,sum(case when cp.status=4 then 1 else 0 end) as paidproposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalpaid) paidproposals on paidproposals.proposalpaid=contractsmessages.msgdate left outer join ")  
                     
        
        application_sql = ("(select count(distinct id) as application_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as appliedat from contracts_application   where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by appliedat) applications on applications.appliedat=contractsmessages.msgdate left outer join ")
                
        
        invoicesent_sql = ("(select count(distinct ci.message_ptr_id) as invoice_count,substring(to_char(cm.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as invoicesent from contracts_invoice ci inner join contracts_message cm on ci.message_ptr_id=cm.id where cm.timestamp>='"+t1+"' and cm.timestamp<='"+t2+"' group by invoicesent) invoicessent on invoicessent.invoicesent=contractsmessages.msgdate left outer join ")
        
        invoicepaid_sql = ("(select count(distinct cp.id) as invoicepaid_count,substring(to_char(cp.timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datepaid from contracts_invoice ci inner join contracts_paidout cp on ci.paid_out_id=cp.id  where cp.timestamp>='"+t1+"' and cp.timestamp<='"+t2+"' group by datepaid) invoicespaid on invoicespaid.datepaid=contractsmessages.msgdate")
        sql = (header_sql + workflow_messages_sql + freelancers_sql + employers_sql + realemployers_sql + jobs_sql + contractsmessages_sql + porposals_sql + proposalspaid_sql + application_sql + invoicesent_sql + invoicepaid_sql + "  order by msgdate")
        
        
        
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
       
       
        sql = ("select au.first_name || ' ' || au.last_name as employer_name,au.email as Employer_Email, cj.id as job_id,substring(cj.title,1,30) as job_title,substring(to_char(cj.created_at,'YYYY-MM-DD HH24:MI:SS'),1,16) as created_at,count(distinct ca.id) as application_count, sum(case when cm.from_applicant=true then 1 else 0 end) as applicant_messages, sum(case when cm.from_applicant=false then 1 else 0 end) as employer_responses,count(distinct cp.message_ptr_id) as proposal_count, sum(case when cp.status=4 then 1 else 0 end) as acceptedproposal_count, case when cj.status=1 then 'Active' when cj.status=2 then 'Closed' end as JobStatus from contracts_job cj left outer join contracts_application ca   on cj.id=ca.job_id left outer join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id where created_at>='"+t1+"' and created_at<='"+t2+"' "+searchsql+" group by employer_name,cj.id,job_title,cj.created_at,au.email order by cj.created_at desc;")
        
       
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
        
        sql = ("select u.id,au.email,ca.id as application_id,count(cp.message_ptr_id) as proposals, sum(case when cp.status=4 then 1 else 0 end) as acceptedproposal_count, sum(case when cm.from_applicant=false then 1 else 0 end) as employer_responses from contracts_application ca inner join users u on u.id=ca.applicant_id inner join auth_user au on u.django_user_id=au.id inner join contracts_message cm on cm.application_id=ca.id left outer join contracts_proposal cp on cp.message_ptr_id=cm.id where job_id= "+job_id+" group by u.id,au.email, ca.id;")
        
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
           
        sql = ("select * from (select count(distinct au.email) as signed_up, count(distinct jobsposted.id) as posted_jobs, count(distinct paidproposal.id) as paid_proposal, count(distinct invoices.applicant_id) as invoices_paid  from users u inner join auth_user au on u.django_user_id=au.id  left outer join (select u1.id from users u1 inner join contracts_job cj on cj.employer_id= u1.id) jobsposted on jobsposted.id=u.id left outer join (select u2.id from users u2 inner join contracts_application ca2 on ca2.applicant_id=u2.id inner join contracts_message cm2 on cm2.application_id=ca2.id inner join contracts_proposal cp2 on cp2.message_ptr_id=cm2.id where cp2.status=4) paidproposal on paidproposal.id=u.id left outer join (select distinct ca1.job_id,ci.status,ci.message_ptr_id,ca1.applicant_id from contracts_invoice ci inner join contracts_message cm1 on cm1.id=ci.message_ptr_id inner join contracts_application ca1 on ca1.id=cm1.application_id where ci.paid_out_id is not null) invoices on invoices.applicant_id=u.id " + wheresql +") total ")
        
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
        sql = ("select u.id,au.first_name || ' ' || au.last_name as fullname ,au.email, 'http://www.nabbesh.com/' || u.homepage as homepage, 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') as photo, count(distinct su.skill_id) skills_count, count(distinct ca.id) as application_count from users u inner join auth_user au on u.django_user_id=au.id inner join skills_users su on su.id_user=u.id  left outer join contracts_application ca on ca.applicant_id=u.id where u.photo is not null and u.photo <>'' group  by u.id,au.email,fullname,photo,homepage "+ sortsql+" limit " + limit)
        
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
        
        sql = ("select u.id,au.first_name || ' ' || au.last_name as fullname ,au.email, 'http://www.nabbesh.com/' || u.homepage as homepage, 'https://nabbesh-images.s3.amazonaws.com/'  || replace(u.photo,'/','') as photo, count(distinct cj.id) as jobs_count    from users u inner join auth_user au on u.django_user_id=au.id inner join skills_users su on su.id_user=u.id  left outer join contracts_job cj on cj.employer_id=u.id where u.photo is not null and u.photo <>'' group  by u.id,au.email,fullname,photo,homepage order by jobs_count desc limit " + limit)
        
        results = customQuery(sql,0)
 	#print results	
        c = Context({'users': results})
        return HttpResponse(render_to_string('top_employers.json', c, context_instance=RequestContext(request)), mimetype='application/json')             
        
        
        
        

