from django.conf.urls import patterns, include, url
from django.contrib import admin
from AEG import settings
admin.autodiscover()

urlpatterns = patterns('',
	#url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^', include('app_auth.urls', namespace='auth')),
	url(r'^', include('app_classes.urls', namespace='classes')),
	url(r'^', include('app_essays.urls', namespace='essays')),	
	#url(r'^', include('app_registration.urls', namespace='register')),
  	url(r'^accounts/', include('app_registration.backends.default.urls')),
)

