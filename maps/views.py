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
#        sql = "select ss.name,count(u.id) as cnt from skills_skill ss inner join skills_users su on ss.id=su.skill_id inner join users u on su.id_user=u.id where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*6371+pow(u.longi-"+ str(objs['lng'])+",2)*6371) <= " + str(objs['radius']/1000) + " group by ss.name order by cnt desc limit 10"
        sql = "select Jobs.name As Skill,Skills.cnt as SkillCount, Jobs.cnt as JobCount, Skills.cnt/Jobs.cnt as Availability\
 from (select  ss.name,count(u.id) as cnt, 'Job' as Type from skills_skill ss inner join skills s on s.skill_id = ss.id inner join users u on u.id= s.id_user\
 where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*6371+pow(u.longi-"+ str(objs['lng'])+",2)*6371)<= " + str(objs['radius']/1000) + "  group by ss.name order\
 by cnt desc) Jobs inner join (select ss.name,count(u.id) as cnt,'Skill' as Type from skills_skill ss inner join skills_users\
 su on ss.id=su.skill_id inner join users u on su.id_user=u.id where sqrt(pow(u.lat-"+ str(objs['lat'])+",2)*6371+pow(u.longi-"+ str(objs['lng'])+",2)*6371)\
 <= " + str(objs['radius']/1000) + " group by ss.name order by cnt desc) Skills on Jobs.name= Skills.Name order by JobCount desc limit 20"
        print sql
        t = loader.get_template('skillsstatistics.xml')
        results = customQuery(sql)
        c = Context({'skills_list': results})
        #print t.render(c)
        return HttpResponse(t.render(c), mimetype='application/xml')
        
        
        
        
def report1(request):
    
    t = loader.get_template('./reports/report1.html')
    c = Context({
        'report1': report1,
    })
#    return render_to_response('index.html', content)
    return HttpResponse(t.render(c))

