"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/15/2014
"
" Flask interface for the web module
"
"""
import os

from datetime            import datetime, date
from flask               import Flask
from flask.json          import JSONEncoder
from law                 import config
from law.web             import subscription

app = Flask( config.get( 'webapp', 'name' ) )
app.debug = config.getboolean( 'webapp', 'debug' )

app.register_blueprint( subscription.views.blueprint, url_prefix = '/subscription' )
app.register_blueprint( subscription.rest.blueprint, url_prefix = '/rest/subscription' )

class JSONLawDEncoder( JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, ( datetime, date ) ):
            return obj.strftime( config.get( 'api', 'dtformat' ) )
        else:
            super( JSONLawDEncoder, self ).default( obj )

app.json_encoder = JSONLawDEncoder
