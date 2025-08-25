import logging
import logging.config

def configure_logging(environment):
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
                'formatter': 'detailed' if environment in ['development', 'testing'] else 'simple',
                'level': 'DEBUG' if environment in ['development', 'testing'] else 'INFO',
            },
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                'level': 'DEBUG',
                'filename': 'app.log',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if environment in ['development', 'testing'] else 'INFO',
        },
    }

    # Apply logging configuration
    logging.config.dictConfig(log_config) 