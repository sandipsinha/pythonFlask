"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/14/2014
"
"""
import os
from os.path import dirname, join

from conman  import load_config, ConfigLoadError

__version__ = '0.1'

PROD_CONF = '/etc/law/law.conf' 
CONF_DIR = join( dirname( dirname( __file__ ) ), 'conf' )


if os.environ.get('LAW') == 'PROD':
    config = load_config( PROD_CONF )
elif os.environ.get('LAW') == 'TEST':
    config = load_config( join( CONF_DIR, 'law.test.conf' ) )
elif os.environ.get('LAW') == 'INSTALL':
    pass
else:
    # Default to dev config and if it doesn't exist then 
    # attempt PROD config if it exists
    try:
        config = load_config( join( CONF_DIR, 'law.dev.conf' ) )
    except ConfigLoadError:
        config = load_config( PROD_CONF )
