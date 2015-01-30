"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from contextlib import contextmanager

from law                        import config
from sqlalchemy                 import (create_engine, Column, 
                                        Integer, DateTime, 
                                        Boolean, String,
                                        Float, Numeric, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref

Base = declarative_base()

db_url = '{dialect}://{user}:{passwd}@{host}:{port}/{dbname}'.format(
    dialect = config.get( 'adb', 'dialect' ),
    user    = config.get( 'adb', 'username' ),
    passwd  = config.get( 'adb', 'password' ),
    host    = config.get( 'adb', 'host' ),
    port    = config.get( 'adb', 'port' ),
    dbname  = config.get( 'adb', 'dbname' ),
)

engine = create_engine( 
            db_url, 
            echo=config.getboolean( 'adb', 'debug' ), 
            pool_recycle=3600 
         )

Session = sessionmaker( bind=engine )

class Account( Base ):
    __tablename__ = 'accounts'

    acct_id     = Column( Integer, primary_key=True )
    id          = Column( Integer )
    deployment  = Column( String(length=20) )
    legacy      = Column( Boolean )
    created     = Column( DateTime )
    subdomain   = Column( String(length=100) )
    email       = Column( String(length=200) )
    phone       = Column( String(length=25) )
    zip         = Column( String(length=10) )
    is_test     = Column( 'is_test_acct', Boolean )
             
    def __repr__(self):
        return "<account({},{})>".format(
            self.acct_id, 
            self.subdomain)

class AccountState( Base ):
    """ Compressed subscription table.  Any subscriptions that take place from
    sun-sat are compressed into a single entry
    """
    __tablename__ = 'aawsc'
    
    acct_id   = Column( Integer, primary_key=True )
    updated   = Column( DateTime, primary_key=True )
    subdomain = Column( String(length=100) )
    state     = Column( 'stNam', String(length=10) )
    tRate     = Column( 'trate', Float )
    fRate     = Column( 'frate', Float )
    tPlan_id  = Column( 'tPlan', Integer, ForeignKey( 'subscription_plan.id' ) )
    tGB       = Column( Numeric( asdecimal=False ) )
    tDays     = Column( Integer )
    tPlan     = relationship("Tier", 
                             lazy='joined',
                             backref=backref("AAWSC", uselist=False))

    @property
    def rate_delta( self ):
        return self.tRate - self.fRate 

    def __repr__(self):
        return "<AccountState({},{})>".format(
            self.acct_id, 
            self.updated)

class AccountStateUncompressed( Base ):
    """ Account state where subcriptions are not compressed """
    __tablename__ = 'aaws'
    
    acct_id   = Column( Integer, primary_key=True )
    updated   = Column( DateTime, primary_key=True )
    subdomain = Column( String(length=100) )
    state     = Column( 'stNam', String(length=10) )
    tRate     = Column( 'trate', Float )
    fRate     = Column( 'frate', Float )
    tPlan_id  = Column( 'tPlan', Integer, ForeignKey( 'subscription_plan.id' ) )
    tGB       = Column( Numeric( asdecimal=False ) )
    tDays     = Column( Integer )
    tPlan     = relationship("Tier", 
                             lazy='joined',
                             backref=backref("AAWS", uselist=False))

    @property
    def rate_delta( self ):
        return self.tRate - self.fRate 

    def __repr__(self):
        return "<AccountStateUncompressed({},{})>".format(
            self.acct_id, 
            self.updated)

class Tier( Base ):
    __tablename__ = 'subscription_plan'

    id   = Column( Integer, primary_key=True )
    name = Column( String(length=100) )
    code = Column( Integer )

    def __repr__(self):
        return "<Tier({},{},{})>".format(
            self.id, 
            self.name, 
            self.code)

class VolumeAccepted( Base ):
    __tablename__ = 'chopper_account_volumes'

    acct_id = Column( Integer, primary_key=True )
    date    = Column( 'vol_date', DateTime, primary_key=True )
    bytes   = Column( Integer )

    def __repr__(self):
        return "<VolumeAccepted({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.bytes)

class VolumeDropped( Base ):
    __tablename__ = 'chopper_account_volumes_dropped'

    acct_id = Column( Integer, primary_key=True )
    date    = Column( 'vol_date', DateTime, primary_key=True )
    bytes   = Column( Integer )

    def __repr__(self):
        return "<VolumeDropped({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.bytes)

class EventsAccepted( Base ):
    __tablename__ = 'chopper_events_allowed'

    acct_id = Column( Integer, primary_key=True )
    date    = Column( DateTime, primary_key=True )
    events  = Column( Integer )

    def __repr__(self):
        return "<EventsAccepted({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.events)


class EventsDropped( Base ):
    __tablename__ = 'chopper_events_denied'

    acct_id = Column( Integer, primary_key=True )
    date    = Column( DateTime, primary_key=True )
    events  = Column( Integer )

    def __repr__(self):
        return "<EventsDropped({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.events)

class Owners( Base ):
    __tablename__ = 'account_owners'

    acct_id    = Column( Integer )
    subdomain  = Column( String, primary_key=True )
    owner      = Column( String )
    start_date = Column( DateTime, primary_key=True )
    end_date   = Column( DateTime )

    def __repr__(self):
        return "<Owners({},{},{},{},{})>".format(
            self.acct_id, 
            self.subdomain, 
            self.owner,
            self.start_date,
            self.end_date)

@contextmanager
def session_context():
    """ Because ADB is read only we do not need commit """
    session = Session()
    try:
        # flask-sqlalchemy patches the session object and enforces
        # This model changes dict for signaling purposes.  Because
        # We don't want flask-sqlalchemy dealing with these models
        # Lets just fake this shit.
        session._model_changes = {}
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def loader():
    """ Loads objects from an ORM session then immediately
    expunges them so they are not written back to the DB
    """
    session = Session()
    try:
        # flask-sqlalchemy patches the session object and enforces
        # This model changes dict for signaling purposes.  Because
        # We don't want flask-sqlalchemy dealing with these models
        # Lets just fake this shit.
        session._model_changes = {}
        yield session
        session.expunge_all()
        session.rollback()
    except:
        session.rollback()
        raise
    finally:
        session.close()



