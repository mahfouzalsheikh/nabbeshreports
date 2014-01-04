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
from django.contrib.auth.decorators import login_required


@login_required(login_url='/admin/')
def home(request):
    
    user_list = Users.objects.filter(id__gt=5000)
    t = loader.get_template('index.html')
    c = Context({
        'user_list': user_list,
    })
#    return render_to_response('index.html', content)
    return HttpResponse(t.render(c))

def userlist(request,day,month,year):
    date1 = dateutil.parser.parse(month + '-' + day +'-' + year + ' 00:00:00 GMT')
    user_list = AuthUser.objects.filter(date_joined__gt= date1)
    t = loader.get_template('userlist.xml')
    c = Context({
        'user_list': user_list,
    })
#    return render_to_response('index.html', content)
    return HttpResponse(t.render(c), mimetype='application/xml')


def skillslist(request):
    context = {'skills': SkillsSkill.objects.filter(published=True).values('id','name', 'slug').order_by('name')}
    return HttpResponse(render_to_string('skills.json', context, context_instance=RequestContext(request)), mimetype='application/json')

def skillslistp(request,p):
    context = {'skills': SkillsSkill.objects.filter(published=True, id__gt=p).values('id','name', 'slug').order_by('name')}
    return HttpResponse(render_to_string('skills.json', context, context_instance=RequestContext(request)), mimetype='application/json')
    
    # data=SkillsSkill.objects.all().values_list('name', 'slug')
    #return HttpResponse(simplejson.dumps(list(data)))

@csrf_exempt
def userlistparam(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
	q1 = Q(date_joined__gte = dateutil.parser.parse(objs['nab-joined-from']  + ' 00:00:00+00'))
	q2 = Q(date_joined__lte = dateutil.parser.parse(objs['nab-joined-to'] + ' 23:59:59+00'))
	
        q3 = Q(last_login__gte = dateutil.parser.parse(objs['nab-login-from']  + ' 00:00:00+00'))
        q4 = Q(last_login__lte = dateutil.parser.parse(objs['nab-login-to'] + ' 23:59:59+00'))

        data = AuthUser.objects.filter(q1 & q2 & q3 & q4)
        print request.raw_post_data
        #objs = simplejson.loads(request.raw_post_data)
        print dateutil.parser.parse(objs['nab-joined-from']  + ' 00:00:00+00')
        print dateutil.parser.parse(objs['nab-joined-to'] + ' 23:59:59+00')
	
        t = loader.get_template('userlist.xml')
        
        c = Context({'user_list': data})
        #print t.render(c)
        results = customQuery("Select * from Users u inner join Auth_User au on u.django_user_id= au.id limit 10")
        print results[1]
        return HttpResponse(t.render(c), mimetype='application/xml')

def customQuery(sql): 
    cursor = connection.cursor()
    cursor.execute(sql,[])
    result_list = [] 
    for row in cursor.fetchall(): 
        result_list.append(row) 
    return result_list 

@csrf_exempt
def markerlist(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)

        genders = objs['nab-gender']	
        if len(genders) == 0:
            genders.append('2')
           
        nabskillslistsql = ""
	nabskillslist = objs['nab-skills']
        if len(nabskillslist) != 0:
            nabskillslistsql = "and su.skill_id in (" + str(', '.join(nabskillslist)) + ")"

        empskillslistsql = ""
        empskillslist = objs['emp-skills']
        if len(empskillslist) != 0:
            empskillslistsql = "and sk.skill_id in (" + str(', '.join(empskillslist)) + ")"


        t = loader.get_template('markers.xml')

        nabsql = "select au.first_name,au.last_name,au.email,u.lat, u.longi, u.photo, u.homepage, 'Nabbesher' \
           from users u inner join auth_user au on u.django_user_id=au.id inner join skills_users su on su.id_user = u.id \
           where au.date_joined >= '" + objs['nab-joined-from'] +"' and au.date_joined <= '" +objs['nab-joined-to'] + "' and \
           au.last_login >= '" + objs['nab-login-from'] +"' and au.last_login <='" +objs['nab-login-to'] + "' and \
           u.gender in (" +str(', '.join(genders)) + ") and u.is_employer<>True " + nabskillslistsql 
        empsql = "select au.first_name,au.last_name,au.email,u.lat, u.longi, u.photo, u.homepage, 'Employer' \
           from users u inner join auth_user au on u.django_user_id=au.id inner join skills sk on sk.id_user = u.id \
           where au.date_joined >= '" + objs['emp-joined-from'] +"' and au.date_joined <= '" +objs['emp-joined-to'] + "' and \
           au.last_login >= '" + objs['emp-login-from'] +"' and au.last_login <='" +objs['emp-login-to'] + "' and \
           u.gender in (" +str(', '.join(genders)) + ") and u.is_employer=True " + empskillslistsql
        sql = nabsql + " union  " + empsql
         
        print sql
        results = customQuery(sql)
        #print sql
	c = Context({'user_list': results})
        #print t.render(c)
        return HttpResponse(t.render(c), mimetype='application/xml')


@csrf_exempt
def applicationlist(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)

	jaskillslistsql = ""
        jaskillslist = objs['ja-skills']
        if len(jaskillslist) != 0:
            jaskillslistsql = "and sk.skill_id in (" + str(', '.join(jaskillslist)) + ")"

        sql = "select mm.sent_at,mm.opportunity_id, mm.sender_id, u1.lat as f_lat,u1.longi as f_lng, mm.recipient_id, u2.lat as t_lat,u2.longi as t_lng, u1.photo as photo1, u1.homepage as homepage1, u2.photo as photo2, u2.homepage as homepage2,sk.description from messages_message mm inner join users u1 on mm.sender_id=u1.id inner join users u2 on mm.recipient_id=u2.id inner join skills sk  on sk.id = mm.opportunity_id inner join skills_skill ss on ss.id=sk.skill_id where mm.sent_at>='"+ objs['ja-from']+"' and mm.sent_at<='"+objs['ja-to']+"' " + jaskillslistsql
        t = loader.get_template('lines.xml')
        print sql
        results = customQuery(sql)
        #print results
        c = Context({'line_list': results})
        #print t.render(c)
        return HttpResponse(t.render(c), mimetype='application/xml')


@csrf_exempt
def skillsstatistics(request):
    if request.method == 'POST':
        objs = simplejson.loads(request.raw_post_data)
        #print objs['radius']
        #R = objs['radius']
	#print objs['lat']
#        sql = "select ss.name,count(u.id) as cnt from skills_skill ss inner join skills_users su on ss.id=su.skill_id inner join users u on su.id_user=u.id where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*63101+pow(u.longi-"+ str(objs['lng'])+",2)*63101) <= " + str(objs['radius']/1000) + " group by ss.name order by cnt desc limit 10"
        sql = "select Jobs.name As Skill,Skills.cnt as SkillCount, Jobs.cnt as JobCount, Skills.cnt/Jobs.cnt as Availability\
 from (select  ss.name,count(u.id) as cnt, 'Job' as Type from skills_skill ss inner join skills s on s.skill_id = ss.id inner join users u on u.id= s.id_user\
 where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*63101+pow(u.longi-"+ str(objs['lng'])+",2)*63101)<= " + str(objs['radius']/1000) + "  group by ss.name order\
 by cnt desc) Jobs inner join (select ss.name,count(u.id) as cnt,'Skill' as Type from skills_skill ss inner join skills_users\
 su on ss.id=su.skill_id inner join users u on su.id_user=u.id where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*63101+pow(u.longi-"+ str(objs['lng'])+",2)*63101)\
 <= " + str(objs['radius']/1000) + " group by ss.name order by cnt desc) Skills on Jobs.name= Skills.Name order by JobCount desc limit 20"
        print sql
        t = loader.get_template('skillsstatistics.xml')
        results = customQuery(sql)
        c = Context({'skills_list': results})
        #print t.render(c)
        return HttpResponse(t.render(c), mimetype='application/xml')
        
        
        
        
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
        as country from users group by country order by usercount desc) total where usercount>="+objs['limit']+" union \
	select sum(usercount) as usercount, 'All The Rest' from (select count(*) as usercount,replace(reverse(substring(reverse(replace(formatted_address,'-',',')),\
	1,position(',' in reverse(replace(formatted_address,'-',','))))),', ','') as country from users group by country order by usercount desc)\
	 total where usercount<"+objs['limit']+" order by usercount desc;"
        results = customQuery(sql)
        
        print sql
        c = Context({'countries': results})
   
        return HttpResponse(render_to_string('freelancersdemography.json', c, context_instance=RequestContext(request)), mimetype='application/json')
        

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
        results = customQuery(sql)
        print results
 
        c = Context({'genders': results})
   
        return HttpResponse(render_to_string('freelancersgender.json', c, context_instance=RequestContext(request)), mimetype='application/json')


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
        results = customQuery(sql)
        print sql
        print results
 
        c = Context({'ages': results})
   
        return HttpResponse(render_to_string('freelancersages.json', c, context_instance=RequestContext(request)), mimetype='application/json')        
        
        


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
        
        t1 = objs['fromdate']  + ' 00:00:00+00'
        t2 = objs['todate'] + ' 23:59:59+00'
        
        print t1
        print t2

        grouppertext= objs['limit']
        #grouppertext = "7"
        if grouppertext=="Month":
            grouper="7"
        else:
            grouper="10"
        
        header_sql = ("select msgdate,COALESCE(message_count,0) as message_count,COALESCE(nmessage_count,0) as nmessage_count,COALESCE(freelancer_count,0) as freelancer_count,COALESCE(employers_count,0) as employers_count,COALESCE(realemployers_count,0) as realemployers_count ,COALESCE(job_count,0) as job_count, COALESCE(proposal_count,0) as proposal_count, COALESCE(application_count,0) as application_count from ")
        
        workflow_messages_sql = ("(select count(*) as message_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as msgdate from contracts_message where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by msgdate) contractsmessages left outer join ")
        
        freelancers_sql = ("(select count(distinct u.id) as freelancer_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_freelancer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) freelancers on contractsmessages.msgdate=freelancers.datejoined left outer join")
        
        employers_sql = ("(select count(distinct u.id) as employers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id where u.is_employer=true and date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) employers on freelancers.datejoined=employers.datejoined left outer join")
        
        realemployers_sql = ("(select count(distinct u.id) as realemployers_count, substring(to_char(date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from users u inner join auth_user au on au.id=u.django_user_id inner join contracts_job cj on cj.employer_id=u.id where  date_joined>='"+t1+"' and date_joined<='"+t2+"' group by datejoined) realemployers on contractsmessages.msgdate=realemployers.datejoined left outer join")
        
        jobs_sql =("(select count(*) as job_count, substring(to_char(created_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as createdat from contracts_job  where created_at>='"+t1+"' and created_at<='"+t2+"' group by createdat) jobs on jobs.createdat=contractsmessages.msgdate  left outer join")
        
        contractsmessages_sql = ("(select count(*) as nmessage_count, substring(to_char(sent_at,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as sentat from messages_message where sent_at>='"+t1+"' and sent_at<='"+t2+"' group by sentat) messages on messages.sentat=contractsmessages.msgdate   left outer join")
        
        porposals_sql  = ("(select substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as proposalsent,count(*) as proposal_count from contracts_proposal cp inner join contracts_message cm on cp.message_ptr_id=cm.id where timestamp>='"+t1+"' and timestamp<='"+t2+"'  group by proposalsent) proposals on proposals.proposalsent=contractsmessages.msgdate left outer join ")
        
        application_sql = ("(select count(*) as application_count,substring(to_char(timestamp,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as appliedat from contracts_application   where timestamp>='"+t1+"' and timestamp<='"+t2+"' group by appliedat) applications on applications.appliedat=contractsmessages.msgdate")
        
        freelancersql = (header_sql + workflow_messages_sql + freelancers_sql + employers_sql + realemployers_sql + jobs_sql + contractsmessages_sql + porposals_sql + application_sql + "  order by msgdate")
        
        #print freelancersql
        results = customQuery(freelancersql)

        #print results
 
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('dashboard.json', c, context_instance=RequestContext(request)), mimetype='application/json') 
        
        

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
        
        #t1 = '2012-01-01 00:00:00+00'
        #t2 = '2013-12-31 23:59:59+00'
        print t1
        print t2

        grouppertext= objs['limit']
        #grouppertext = "Month"
        if grouppertext=="Month":
            grouper="7"
        else:
            grouper="10"
        
        header_sql = ("select datejoined,max(jobs_per_employer),min(jobs_per_employer), avg(jobs_per_employer), median(jobs_per_employer)")
        
        from_sql = ("from (select count(cj.id) as jobs_per_employer, u.id,substring(to_char(au.date_joined,'YYYY-MM-DD HH24:MI:SS'),1,"+grouper+") as datejoined from contracts_job cj inner join users u on u.id=cj.employer_id inner join auth_user au on u.django_user_id=au.id where au.date_joined>='"+t1+"' and au.date_joined<='"+t2+"' group by u.id,au.date_joined order by jobs_per_employer desc) total group by datejoined order by datejoined;")
        sql = (header_sql + from_sql)
        
        #print freelancersql
        results = customQuery(sql)

        #print results
 
        c = Context({'statistics': results})
   
        return HttpResponse(render_to_string('jobs_employers_statistics.json', c, context_instance=RequestContext(request)), mimetype='application/json')         
