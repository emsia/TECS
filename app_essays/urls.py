from django.conf.urls import patterns, url
from app_essays import views

urlpatterns = patterns('',
	url(r'^essays/new/$', views.new_essay, name='new'),
	url(r'^essays/$', views.list_essay, name='list'),
	url(r'^essays/(?P<essay_id>\d+)/$', views.exam_details, name='details'),
	url(r'^essays/answer/(?P<essay_response_id>\d+)/$', views.answer_essay, name='answer'),
	url(r'^essays/submissions/(?P<essay_response_id>\d+)/$', views.essay_submission, name='submission'),
	url(r'^essays/time_remaining/(?P<essay_response_id>\d+)/$', views.time_remaining_ajax, name='time_remaining'),
)
