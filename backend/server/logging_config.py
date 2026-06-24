import logging
import logging.config

def configure_logging(environment):
    is_dev = environment in ['development', 'testing']
    default_level = 'DEBUG' if is_dev else 'INFO'

    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'simple': {
                'format': '%(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'detailed' if is_dev else 'simple',
                'level': default_level,
            },
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                'level': default_level,
                'filename': 'app.log',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': default_level,
        },
        'loggers': {
            'dev': {
                'handlers': ['console'],
                'level': default_level,
                'propagate': False,
            }
        }
    }

    # Apply logging configuration
    logging.config.dictConfig(log_config) 