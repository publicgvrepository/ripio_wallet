# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

from .settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': env_var('DATABASE_DEFAULT_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': env_var('POSTGRES_DB', 'not_set'),
        'USER': env_var('POSTGRES_USER', 'not_set'),
        'PASSWORD': env_var('POSTGRES_PASSWORD', 'not_set'),
        'HOST': env_var('POSTGRES_HOST', 'postgres'),
        'PORT': env_var('POSTGRES_PORT', '5432'),
    }
}
