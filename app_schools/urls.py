from django.conf.urls import patterns, url
from app_schools import views

urlpatterns = patterns('',
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^schools/add/$', views.suadmin_addNewSchool, name='add'),
	url(r'^schools/submit/$', views.submit, name='submitSchool'),
	url(r'^schools/(?P<school_id>\d+)/edit/$', views.edit, name='edit'),
	url(r'^schools/(?P<school_id>\d+)/viewSchool/$', views.viewSchoolAdmins, name='viewSchool'),
	# ex: /polls/5/vote/
    url(r'^schools/delete/$', views.delete, name='delete'),
    url(r'^schools/removeAdmin/$', views.removeAdmin, name='removeAdmin'),
    url(r'^schools/inviteAdmin/$', views.inviteAdmin, name='inviteAdmin'),
)
