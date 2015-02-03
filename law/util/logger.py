"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" LAW specific loggers.
"
"""
import os
import logging, logging.handlers

LOG_FORMAT = '%(astime)s - %(name)s [%(levelname)s]: %(message)s' 
LOG_PATH = '/var/log/loggly/LAW/' 
LOG_PREFIX = 'LAW'
LOG_LEVEL = logging.INFO
LOG_MAX_BYTES = 100000000
LOG_BACKUPS = 3

def make_logger( name, level=LOG_LEVEL, path=LOG_PATH ):
    if not os.path.exists( LOG_PATH ):
        os.makedirs( LOG_PATH, 0755 )
    logger = logging.getLogger( '{}.{}'.format( LOG_PREFIX, name ) )
    logger.setLevel( level )

    rfh = logging.handlers.RotatingFileHandler( os.path.join( LOG_PATH, name ), 
                                                maxBytes    = LOG_MAX_BYTES,
                                                backupCount = LOG_BACKUPS)
    formatter = logging.Formatter( LOG_FORMAT )
    rfh.setFormatter( formatter )
    logger.addHandler( rfh )

    return logger
