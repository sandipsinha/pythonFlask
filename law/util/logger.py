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

from law import config

LOG_PREFIX    = 'LAW'
LOG_FORMAT    = config.get( 'logging', 'format', raw=True )
LOG_PATH      = config.get( 'logging', 'logdir' )
LOG_LEVEL     = getattr( logging, config.get( 'logging', 'level' ) )
LOG_MAX_BYTES = config.getint( 'logging', 'maxbytes' )
LOG_BACKUPS   = config.getint( 'logging', 'numbackups' )

def make_logger( name, level=LOG_LEVEL, path=LOG_PATH ):
    if not os.path.exists( LOG_PATH ):
        os.makedirs( LOG_PATH, 0775 )
    logger = logging.getLogger( '{}.{}'.format( LOG_PREFIX, name ) )
    logger.setLevel( level )

    rfh = logging.handlers.RotatingFileHandler( os.path.join( LOG_PATH, name ), 
                                                maxBytes    = LOG_MAX_BYTES,
                                                backupCount = LOG_BACKUPS)
    formatter = logging.Formatter( LOG_FORMAT )
    rfh.setFormatter( formatter )
    logger.addHandler( rfh )

    return logger
