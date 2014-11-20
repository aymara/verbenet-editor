from .local import *

# Test runner with no database creation
TEST_RUNNER = 'core.test.testrunner.NoDbTestRunner'

# Use an alternative database as a safeguard against accidents
DATABASES['default']['NAME'] = '_test_verbenet_db'

# LOG to stdout
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'database': {
            'handlers': ['console'], 'level': 'INFO', 'propagate': 'FALSE'
        },
        'verbs': {
            'handlers': ['console'], 'level': 'INFO', 'propagate': 'FALSE'
        },
        'warnings': {
            'handlers': ['console'], 'level': 'WARNING', 'propagate': 'FALSE'
        }
    }
}
