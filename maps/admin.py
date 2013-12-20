from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from maps.models import Marker
from legacy.models import Users
admin.site.register(Marker)
admin.site.register(Users)
