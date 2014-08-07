"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 08/07/2014
"
" Flask interface for the web module
"
"""
from datetime            import datetime, date
from flask               import Flask, render_template
from flask.json          import JSONEncoder
from law                 import config
from law.web             import views, subscription, volumes
from law.util.adb        import Session, AccountState, Tier
from law.util.lawdb      import db_url, db, security
from flask.ext.login     import current_user, current_app, login_user

app = Flask( config.get( 'webapp', 'name' ) )
app.debug = config.getboolean( 'webapp', 'debug' )

# Blueprints and top-level routes
app.register_blueprint( views.blueprint )

app.register_blueprint( subscription.views.blueprint, url_prefix = '/subscription' )
app.register_blueprint( subscription.rest.blueprint, url_prefix = '/apiv1/subscription' )
app.register_blueprint( volumes.views.blueprint, url_prefix = '/volumes' )

# Config items
app.config['SECRET_KEY']              = config.get( 'flask-security', 'secret_key' )
app.config['SECURITY_PASSWORD_HASH']  = config.get( 'flask-security', 'password_hash' )
app.config['SECURITY_PASSWORD_SALT']  = config.get( 'flask-security', 'password_salt' )
app.config['SECURITY_TRACKABLE']      = True

app.config['SQLALCHEMY_ECHO' ]        = config.getboolean( 'lawdb', 'debug' )
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# LAWDB and flask-security app bindings
db.init_app( app )
security.init_app( app )

class JSONLawDEncoder( JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, ( datetime, date ) ):
            return obj.strftime( config.get( 'api', 'dtformat' ) )
        else:
            super( JSONLawDEncoder, self ).default( obj )

app.json_encoder = JSONLawDEncoder

# Privileged blueprint registry

def secure_blueprints( blueprints ):
    """ This function forces all routes in the supplied
    blueprint to force user authentication prior to serving
    the URL
    """
    
    def bp_login_required():
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()

    for bp in blueprints:
        app.before_request_funcs.setdefault( bp.name, [] ).append( bp_login_required )

secure_blueprints([
    subscription.views.blueprint,
    subscription.rest.blueprint,
    volumes.views.blueprint,
])
