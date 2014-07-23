"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/22/2014
"
" All things authentication related.  
"
" Uses flask-security extension: https://pythonhosted.org/Flask-Security
"
"""
from flask.ext.security.utils   import encrypt_password
from law.web                    import db, app
from law.util.lawdb             import user_datastore

def create_tables():
    db.create_all( app=app )

def create_user( email, password ):
    with app.app_context():
        user_datastore.create_user( email=email, password=encrypt_password(password) )
        db.session.commit()
