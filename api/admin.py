from django.contrib import admin
from .models import User, Application, Profile, Instance, Service

admin.site.register(User)
admin.site.register(Application)
admin.site.register(Profile)
admin.site.register(Instance)
admin.site.register(Service)
