from django.contrib import admin
from app_auth.models import UserProfile, School, Teacher, Student, Admin, SUadmin

admin.site.register(UserProfile)
admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Admin)
admin.site.register(SUadmin)
