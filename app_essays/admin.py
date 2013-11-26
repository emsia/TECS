from django.contrib import admin
from app_essays.models import GradingSystem, Grade, Essay, EssayResponse, EssayComment

admin.site.register(GradingSystem)
admin.site.register(Grade)
admin.site.register(Essay)
admin.site.register(EssayResponse)
admin.site.register(EssayComment)