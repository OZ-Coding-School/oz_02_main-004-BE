from pathlib import Path
from datetime import timedelta
import json, platform, os

# cicd 머지 test

# 개발환경과 서버환경 구분을 위한 변수
platform_index = platform.system()
# Linux : 서버 환경
# others : 개발 환경

if platform_index == 'Linux':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# load 'secret.json' file
with open(os.path.join(BASE_DIR, 'secret.json')) as secret_file:
    secret_keys = json.load(secret_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wy(7)!%^)5tv3%42m*a%3430g#(9k$l#cr%yk1b^z83cuonfqk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
SYSTEM_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles',
]

CUSTOM_APPS = [
    'common.apps.CommonConfig', 'users.apps.UsersConfig', 'posts.apps.PostsConfig', 'pets.apps.PetsConfig',
    'recommendation.apps.RecommendationConfig', 'guestbook.apps.GuestbookConfig',
]

THIRD_PARTY_APPS = [
    'rest_framework', 'rest_framework.authtoken', 'rest_framework_simplejwt', 'django.contrib.sites',
    'allauth', 'allauth.account', 'allauth.socialaccount', 'allauth.socialaccount.providers.kakao', 'corsheaders', 'drf_yasg',
]

INSTALLED_APPS = SYSTEM_APPS + CUSTOM_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', 'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



if platform_index == 'Linux':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db',
            'USER': 'admin',
            'PASSWORD': 'admin',
            'HOST': 'db',
            'PORT': '5432',  # 5432는 PostgreSQL의 기본포트이다
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'nickname'
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=600),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # 리프레시 토큰을 갱신할 때마다 새 토큰을 생성하지 않도록 설정합니다.
    'ROTATE_REFRESH_TOKENS': False,
    # 토큰을 갱신한 후 이전 토큰을 블랙리스트에 추가합니다.
    'BLACKLIST_AFTER_ROTATION': True,
    # JWT에 사용할 서명 알고리즘으로 HS256을 사용합니다.
    'ALGORITHM': 'HS256',
    # JWT를 서명하는 데 사용할 키로 Django의 SECRET_KEY를 사용합니다.
    'SIGNING_KEY': SECRET_KEY,
    # JWT 검증에 사용할 키입니다. HS256 알고리즘에서는 None으로 설정됩니다.
    'VERIFYING_KEY': None,
    # 인증 헤더의 타입으로 'Bearer'를 사용합니다.
    # Authorization: Bearer <token>
    'AUTH_HEADER_TYPES': ('Bearer',),
    # 토큰에 포함될 사용자 식별자 필드로 'id'를 사용합니다.
    'USER_ID_FIELD': 'id',
    # 토큰 클레임에서 사용자 식별자에 해당하는 키로 'user_id'를 사용합니다.
    'USER_ID_CLAIM': 'user_id',
    # 사용할 토큰 클래스로 AccessToken을 사용합니다.
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'allauth.account.auth_backends.AuthenticationBackend',]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000', 'https://www.oz-02-main-04.xyz', 'https://api.oz-02-main-04.xyz', 'https://oz-02-main-04.xyz',]
CSRF_COOKIE_NAME = 'csrftoken'
if platform_index == 'Linux':
    CORS_ORIGIN_ALLOW_ALL = True
    CSRF_COOKIE_DOMAIN = '.oz-02-main-04.xyz'
    SESSION_COOKIE_DOMAIN = '.oz-02-main-04.xyz'
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000', 'https://www.oz-02-main-04.xyz', 'https://api.oz-02-main-04.xyz', 'https://oz-02-main-04.xyz',]
CORS_ALLOW_HEADERS = [
    'access-control-allow-credentials', 'access-control-allow-origin', 'access-control-request-method', 'access-control-request-headers',
    'accept', 'accept-encoding', 'accept-language', 'authorization', 'connection', 'content-type', 'dnt', 'credentials', 'host',
    'origin', 'user-agent', 'x-csrftoken', 'csrftoken', 'x-requested-with',
    ]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

SITE_ID = 1

# key management
SPOTIPY_CLIENT_ID = secret_keys['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = secret_keys['SPOTIPY_CLIENT_SECRET']