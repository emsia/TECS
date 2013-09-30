from django.conf.urls import patterns, url
from app_auth import views

urlpatterns = patterns('',
	#url(r'^$', views.user_login, name='user_login'),
	url(r'^$', views.LoginView.as_view(), name='user_login'),
	url(r'^logout$', views.user_logout, name='user_logout'),
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^profile/$', views.profile_view, name='profile'),
	url(r'^help/$', views.help,  name='help'),
	url(r'^settings/profile/$', views.profile_edit, name='edit_profile'),
	url(r'^settings/account/$', views.password_edit, name='edit_password'),
	url(r'^settings/grading-system/$', views.grading_system, name='gradesys'),
	url(r'^settings/grading-system/new$', views.grading_system_new, name='gradesys_new'),
	url(r'^settings/grading-system/(?P<gradeSys_id>\d+)/$', views.grading_system_view, name='grades'),
	url(r'^settings/grading-system/delete/$', views.grading_system_delete, name='gradesys_delete'),

)
