from django.conf.urls import patterns, url
from app_classes import views

urlpatterns = patterns('',
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^classes/$', views.class_teacher, name='classes'),
	url(r'^classes/add/$', views.teacher_addNewClass, name='add'),
	url(r'^classes/submit/$', views.submit, name='submitClass'),
	url(r'^classes/(?P<class_id>\d+)/edit/$', views.edit, name='edit'),
	url(r'^classes/enroll/$', views.enroll, name='enroll'),
	url(r'^classes/(?P<class_id>\d+)/viewClass/$', views.viewClassList, name='viewClass'),
	# ex: /polls/5/vote/
    url(r'^classes/(?P<class_id>\d+)/delete/$', views.delete, name='delete'),
    url(r'^classes/(?P<class_id>\d+)/(?P<student_id>\d+)/removeStudent/$', views.removeStudent, name='removeStudent'),
    url(r'^classes/(?P<class_id>\d+)/inviteStudent/$', views.inviteStudent, name='inviteStudent'),
)
