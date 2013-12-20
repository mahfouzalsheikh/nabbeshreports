# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=80, unique=True)
    class Meta:
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)
    class Meta:
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=71, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        db_table = 'auth_user_user_permissions'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        db_table = 'django_content_type'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    django_user = models.ForeignKey(AuthUser, unique=True)
    homepage = models.CharField(max_length=255, unique=True)
    photo = models.CharField(max_length=251, blank=True)
    dob = models.CharField(max_length=600)
    gender = models.IntegerField()
    countrycode = models.CharField(max_length=12, blank=True)
    areacode = models.CharField(max_length=12, blank=True)
    mobile = models.CharField(max_length=360, blank=True)
    bio = models.TextField()
    lat = models.FloatField(null=True, blank=True)
    longi = models.FloatField(null=True, blank=True)
    #coordinates = models.GeometryField(blank=True, null=True, geography=True)
    formatted_address = models.CharField(max_length=600)
    quand = models.DateTimeField(null=True, blank=True)
    lastupdated = models.DateTimeField(null=True, blank=True)
    email_change_request = models.CharField(max_length=75, blank=True)
    is_employer = models.NullBooleanField(null=True, blank=True)
    is_hobbies_explorer = models.NullBooleanField(null=True, blank=True)
    is_freelancer = models.NullBooleanField(null=True, blank=True)
    hide_in_search = models.NullBooleanField(null=True, blank=True)
    deactivated = models.NullBooleanField(null=True, blank=True)
    view_count = models.IntegerField(null=True, blank=True)
    city_slug = models.CharField(max_length=50, blank=True)
    referral_source = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = 'users'




class Skills(models.Model):
    id = models.IntegerField(primary_key=True)
    id_user = models.ForeignKey('Users', null=True, db_column='id_user', blank=True)
    skill = models.ForeignKey('SkillsSkill')
    city_slug = models.CharField(max_length=50, blank=True)
    workload = models.IntegerField()
    duration = models.IntegerField()
    description = models.TextField()
    url = models.CharField(max_length=1500, blank=True)
    rate = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=1500, blank=True)
    location = models.CharField(max_length=1500, blank=True)
    location_type = models.IntegerField()
    task = models.IntegerField()
    quand = models.DateTimeField(null=True, blank=True)
    unpublish_date = models.DateTimeField(null=True, blank=True)
    is_live = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = 'skills'


class MessagesMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    subject = models.CharField(max_length=120)
    body = models.TextField()
    sender = models.ForeignKey(Users, null=True, related_name='sender_id', blank=True)
    recipient = models.ForeignKey(Users, null=True,related_name='recipient_id', blank=True)
    parent_msg = models.ForeignKey('self', null=True,related_name='parent_message_id', blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    sender_deleted_at = models.DateTimeField(null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(null=True, blank=True)
    opportunity = models.ForeignKey(Skills, null=True, blank=True)
    thread_parent = models.ForeignKey('self', null=True,related_name='thread_parent_id', blank=True)
    is_leaf = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = 'messages_message'


class SkillsSkill(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=251, blank=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField()
    created_by = models.ForeignKey(AuthUser)
    published = models.BooleanField()
    merge_to = models.ForeignKey('self', null=True, blank=True)
    deleted = models.BooleanField()
    class Meta:
        db_table = 'skills_skill'

