from django.contrib import admin
from app_auth.models import UserProfile, School, Teacher, Student

admin.site.register(UserProfile)
admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Student)
