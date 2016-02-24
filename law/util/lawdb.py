"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/21/2014
"
" LAW Database models/functions
"
"""
from law                  import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security   import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy                 import (create_engine, Column,
                                        Integer, DateTime,
                                        Boolean, String,
                                        ForeignKey)
from contextlib import contextmanager
from sqlalchemy.orm             import sessionmaker, relationship, backref

db_url = '{dialect}://{user}:{passwd}@{host}:{port}/{dbname}'.format(
    dialect = config.get( 'lawdb', 'dialect' ),
    user    = config.get( 'lawdb', 'username' ),
    passwd  = config.get( 'lawdb', 'password' ),
    host    = config.get( 'lawdb', 'host' ),
    port    = config.get( 'lawdb', 'port' ),
    dbname  = config.get( 'lawdb', 'dbname' ),
)

# We'll bind the app later
db = SQLAlchemy()


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role( db.Model, RoleMixin ):
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User( db.Model, UserMixin ):
    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.String(255), unique=True)
    password         = db.Column(db.String(255))
    active           = db.Column(db.Boolean())
    confirmed_at     = db.Column(db.DateTime())
    last_login_at    = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip    = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count      = db.Column(db.Integer)
    roles            = db.relationship('Role', secondary=roles_users,
                                        backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore( db, User, Role )
security       = Security( datastore = user_datastore )
engine = create_engine(
            db_url
         )
Session = sessionmaker( bind=engine )

@contextmanager
def session_context():
    """ Because ADB is read only we do not need commit """
    session = Session()
    try:
        # flask-sqlalchemy patches the session object and enforces
        # This model changes dict for signaling purposes.  Because
        # We don't want flask-sqlalchemy dealing with these models
        # Lets just fake this shit.
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

