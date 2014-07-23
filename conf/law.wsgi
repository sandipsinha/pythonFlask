#!/usr/bin/env python
import os
import sys

# Package building should create the following directories:
#    <package install>/loggly-analytics-web/conf/law.wsgi
#    <package install>/loggly-analytics-web/environment
conf_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(conf_dir)
sys.path.append( app_dir )

# activate virtual python environment
activate_this = os.path.join( app_dir, 'environment', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# Will attempt to write egg cache from build LAW under apache's www
# which the user may not have privileges to write to.  Just point
# at tmp and all should be well
os.environ['PYTHON_EGG_CACHE'] = '/tmp/python-eggs'

# This will look for law.conf in /etc/law/law.conf
os.environ['LAW'] = 'PROD'

from law.web import app as application
