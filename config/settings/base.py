# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

SITE_ID = 1
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # for SlidesBlock edge case

INSTALLED_APPS = [
    'admin_tweaks',
    'search',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.search_promotions',
    'wagtail.contrib.settings',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'wagtail.contrib.routable_page',
    # 'wagtail.contrib.styleguide',

    'modelcluster',
    'taggit',

    'mnmnwag',  # mnmnwag takes template precedence over madprops
    'madprops',
    'subs',

    'djrichtextfield',  # required for seevooplay
    'seevooplay',

    'config.apps.MnmnwagAdminConfig',  # replaces 'django.contrib.admin'
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'antispam',
    'antispam.akismet',
    'cachalot',
    'capture_tag',
    'compressor',
    'crequest',
    'dbbackup',
    # 'debug_toolbar',
    'debugtools',
    'django_browser_reload',
    'django_comments_xtd',  # 1 (do not reorder)
    'django_comments',      # 2 (do not reorder)
    'django_extensions',
    'django_markdown2',
    'honeypot',
    'likes',
    'secretballot',
    'typogrify',
    # 'wagtailcache',
    'wagtailmedia',
    'wagtail_footnotes',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'crequest.middleware.CrequestMiddleware',
    'extlinks.middleware.RewriteExternalLinksMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [
        #     os.path.join(PROJECT_DIR, 'templates'),
        # ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'builtins': [
                'debugtools.templatetags.debugtools_tags',
            ],
        },
    },
]


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATICFILES_FINDERS = [
    # 'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# STATICFILES_DIRS = [
#     os.path.join(PROJECT_DIR, 'static'),
# ]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Wagtail settings

WAGTAIL_SITE_NAME = "mnmnwag"
WAGTAILEMBEDS_RESPONSIVE_HTML = True
WAGTAILIMAGES_IMAGE_MODEL = 'mnmnwag.CustomImage'
WAGTAILMEDIA_MEDIA_MODEL = 'mnmnwag.CustomMedia'
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = 'https://www.mahnamahna.net'

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
        'ATOMIC_REBUILD': True,
    }
}


# django-antispam
AKISMET_SITE_URL = 'https://www.mahnamahna.net'
AKISMET_TEST_MODE = False


# django-comments(-xtd)

COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_CONFIRM_EMAIL = False
COMMENTS_XTD_FORM_CLASS = 'mnmnwag.forms.MahnaCommentForm'
COMMENTS_XTD_MAX_THREAD_LEVEL = 8


# django-compressor

COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


# django-dbbackup

DBBACKUP_CLEANUP_KEEP = 60
DBBACKUP_FILENAME_TEMPLATE = 'mnmnwag-{datetime}.sql'
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'private', 'db')}


# django-debug-toolbar

INTERNAL_IPS = [
    '127.0.0.1',
]


# django-honeypot

HONEYPOT_FIELD_NAME = 'homepage'


# django-libsass

LIBSASS_OUTPUT_STYLE = 'compressed'


# django-richtextfield (for seevooplay)

DJRICHTEXTFIELD_CONFIG = {
    'js': [
        '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.25.1/trumbowyg.min.js',
        '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.25.1/plugins/cleanpaste/trumbowyg.cleanpaste.min.js',
        '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.25.1/plugins/history/trumbowyg.history.min.js',
    ],
    'css': {
        'all': [
            '//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/2.25.1/ui/trumbowyg.min.css',
        ]
    },
    'init_template': 'seevooplay/trumbowyg.js',
    'settings': {
        'autogrow': True,
        'semantic': False,
        'minimalLinks': True,
        'btns': [
            ['historyUndo', 'historyRedo'],
            ['strong', 'em'],
            ['link'],
            ['removeformat'],
            ['viewHTML'],
            ['fullscreen']
        ]
    }
}


# django-secretballot / django-likes
SECRETBALLOT_FOR_MODELS = {
    'wagtailcore.Page': {},
}


# extlinks

EXTLINKS_IGNORE_DOMAINS = ['www.mahnamahna.net', 'www.madprops.info']
EXTLINKS_TEMPLATES_WHITELIST = ['mnmnwag', 'madprops']
