from django.conf.urls import patterns, url
from app_classes import views

urlpatterns = patterns('',
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^classes/$', views.class_teacher, name='classes'),
	url(r'^classes/add/$', views.teacher_addNewClass, name='add'),
	url(r'^classes/addClass_admin/(?P<teacher_id>\d+)/$', views.addClass_admin, name='addClass_admin'),
	url(r'^classes/disableTeacher/(?P<teacher_id>\d+)/(?P<place>\d+)$', views.disableTeacher, name='disableTeacher'),
	url(r'^classes/add_teacher/$', views.add_teacher, name='add_teacher'),
	url(r'^classes/viewTeachers/(?P<teacher_id>\d+)$', views.viewTeachers, name='viewTeachers'),
	url(r'^classes/send_newPassword/$', views.send_newPassword, name='send_newPassword'),
	url(r'^classes/submit/$', views.submit, name='submitClass'),
	url(r'^classes/submitTeachers/$', views.submitTeachers, name='submitTeachers'),
	url(r'^classes/(?P<class_id>\d+)/edit/(?P<place>\d+)$', views.edit, name='edit'),
	url(r'^classes/enroll/$', views.enroll, name='enroll'),
	url(r'^classes/(?P<class_id>\d+)/viewClass/(?P<place>\d+)$', views.viewClassList, name='viewClass'),
	# ex: /polls/5/vote/
    url(r'^classes/delete/$', views.delete, name='delete'),
    url(r'^classes/delete_teacher/$', views.delete_teacher, name='delete_teacher'),
    url(r'^classes/removeStudent/$', views.removeStudent, name='removeStudent'),
    url(r'^classes/editSchool/(?P<school_id>\d+)$', views.editSchool, name='editSchool'),
    url(r'^classes/inviteStudent/$', views.inviteStudent, name='inviteStudent'),
)
