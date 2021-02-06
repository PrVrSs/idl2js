import logging
from logging.config import dictConfig as logging_dict_config

import click


TRACE_LOG_LEVEL = 5


LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'trace': TRACE_LOG_LEVEL,
}


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'idl2js.logger.IDL2JSFormatter',
            'fmt': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S',
            'use_colors': True,
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        '': {'handlers': ['default'], 'level': 'ERROR'},
        'idl2js.error': {'level': 'INFO'},
    },
}


class IDL2JSFormatter(logging.Formatter):
    level_name_colors = {
        TRACE_LOG_LEVEL: lambda message: click.style(message, fg='blue'),
        logging.DEBUG: lambda message: click.style(message, fg='cyan'),
        logging.INFO: lambda message: click.style(message, fg='green'),
        logging.WARNING: lambda message: click.style(message, fg='yellow'),
        logging.ERROR: lambda message: click.style(message, fg='red'),
        logging.CRITICAL: lambda message: click.style(message, fg='bright_red'),
    }

    def __init__(self, fmt=None, datefmt=None, style='%', use_colors=False):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = use_colors

    def formatMessage(self, record):
        if not self.use_colors:
            return super().formatMessage(record)

        colored = self.level_name_colors[record.levelno]

        record.__dict__['message'] = colored(record.msg)
        record.__dict__['asctime'] = colored(f'[+] {record.asctime}')
        record.__dict__['levelname'] = colored(f'{record.levelname}:')

        return super().formatMessage(record)


def configure_logging(log_level):
    logging.addLevelName(TRACE_LOG_LEVEL, 'TRACE')
    logging_dict_config(LOGGING_CONFIG)
    logging.getLogger('').setLevel(LOG_LEVELS[log_level])
