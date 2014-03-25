from django.conf.urls import patterns, url
from app_schools import views

urlpatterns = patterns('',
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^schools/$', views.suadmin_viewSchools, name='view'),
	url(r'^schools/add/$', views.suadmin_addNewSchool, name='add'),
	url(r'^schools/submit/$', views.submit, name='submitSchool'),
	url(r'^schools/(?P<school_id>\d+)/edit/$', views.edit, name='edit'),
	url(r'^schools/(?P<school_id>\d+)/viewSchool/$', views.viewSchoolAdmins, name='viewSchool'),
    url(r'^schools/delete/$', views.delete, name='delete'),
    url(r'^schools/removeAdmin/$', views.removeAdmin, name='removeAdmin'),
    url(r'^schools/(?P<school_id>\d+)/addAdmin/$', views.addAdmin, name='addAdmin'),
	url(r'^schools/submitAdmins/$', views.submitAdmins, name='submitAdmins'),
	url(r'^schools/sendnewpassword/$', views.send_newPassword, name='send_newPassword'),
)
