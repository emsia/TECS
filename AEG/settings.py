# Django settings for mejango project.
from __future__ import absolute_import
#import dj_database_url
import os
import urlparse
from celery import Celery

#from rq import Queue
#from worker import conn
import djcelery
djcelery.setup_loader()

#BROKER_URL = 'django://'
BROKER_URL = 'amqp://pmanomsh:b67iwhrWStPYwosFHF8KSGbY40Sb8jxN@tiger.cloudamqp.com/pmanomsh'
BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

app = Celery('AEG', backend=BROKER_BACKEND, broker=BROKER_URL)

#CELERY_ACCEPT_CONTENT = ['json']
PROJECT_DIR = os.path.dirname(__file__) # this is not Django setting.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Molen Fernando', 'molenfernando@gmail.com'),
    ('Efren Ver Sia', 'fsvaeg@gmail.com'),
    ('Chery Verano', 'cheryleighverano@gmail.com'),
)

#redis_url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://pub-redis-11493.us-east-1-3.1.ec2.garantiadata.com:11493'))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'caches_table',
        'TIMEOUT': 60,
    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'redis_cache.RedisCache',
#        'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
#        'OPTIONS': {
#            'DB': 0,
#            'PASSWORD': redis_url.password,
#        }
#    }
#}

#redis_q = Queue(connection=conn)

MANAGERS = ADMINS

#DATABASES = {
#    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
#}
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'aeg',                    # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                   # Set to empty string for default.
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fsvaeg@gmail.com'
EMAIL_HOST_PASSWORD = 'Waterbury'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Taipei'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, '../media') #'mediafiles'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, './static/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, '../static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'k#btkr9jz$jsu6yi5741j0w6km$=qh3k^ih1p*vy^1pqy$04^j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'AEG.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'AEG.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "../templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'kombu.transport.django',
    'djkombu',
    'celery',
    'djcelery',
    'app_auth',
    'BruteBuster',
    'app_classes',
    'app_essays',
    'app_registration',
    'app_captcha',
    'app_schools',
)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend',
)

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window;
RECAPTCHA_PUBLIC_KEY = '6Lf-oOcSAAAAAO2-8-yrUFxYjQyluvupPS6GQYQY'
AUTH_PROFILE_MODULE = "app_registration.CustomRegistrationProfile"
RECAPTCHA_PRIVATE_KEY = '6Lf-oOcSAAAAAICjmXmGuAjsraOVkrHRIAUENjHJ'
RECAPTCHA_USE_SSL = False

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_REDIRECT_URL = '/dashboard'