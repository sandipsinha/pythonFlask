"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/14/2014
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

app = Flask( config.get( 'web', 'appname' ) )
app.debug = config.get( 'web', 'debug' )

app.register_blueprint( subscription.blueprint, url_prefix = '/subscription' )

class JSONLawDEncoder( JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, ( datetime, date ) ):
            return obj.strftime( config.get( 'api', 'dtformat' ) )
        else:
            super( JSONLawDEncoder, self ).default( obj )

app.json_encoder = JSONLawDEncoder

if __name__ == '__main__':
    if os.environ.get( 'LAW' ) == 'DEV':
        app.debug = True
    app.run()
