"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/15/2014
"
"""
from contextlib import contextmanager

from law                        import config
from sqlalchemy                 import (create_engine, Column, 
                                        Integer, DateTime, 
                                        Boolean, String,
                                        ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref

Base = declarative_base()
##Base = declarative_base( cls=DeferredReflection )

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

#def reflect():
#    """ Actually triggers the reflecting """
#    Base.prepare( engine )
#    return engine

Session = sessionmaker( bind=engine )

class Account( Base ):
    __tablename__ = 'accounts'

    acct_id     = Column( Integer, primary_key=True )
    id          = Column( Integer )
    deployment  = Column( String )
    legacy      = Column( Boolean )
    created     = Column( DateTime )
    subdomain   = Column( String )
    email       = Column( String )
    phone       = Column( String )
    zip         = Column( String )
    is_test     = Column( 'is_test_acct', Boolean )
             
    def __repr__(self):
        return "<account({},{})>".foramt(
            self.acct_id, 
            self.subdomain)

class AccountState( Base ):
    __tablename__ = 'aawsc'
    
    acct_id   = Column( Integer, primary_key=True )
    updated   = Column( Integer, primary_key=True )
    subdomain = Column( String )
    trate     = Column( Integer )
    tPlan_id  = Column( 'tPlan', Integer, ForeignKey( 'subscription_plan.id' ) )
    tGB       = Column( Integer )
    tDays     = Column( Integer )
    tplan     = relationship("Tier", 
                             lazy='joined',
                             backref=backref("AAWSC", uselist=False))

    def __repr__(self):
        return "<AAWSC({},{})>".foramt(
            self.acct_id, 
            self.updated)

class Tier( Base ):
    __tablename__ = 'subscription_plan'

    id   = Column( Integer, primary_key=True )
    name = Column( String )
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
    __tablename__ = 'chopper_account_volumes_denied'

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

@contextmanager
def session_context( reflect=False ):
#    if reflect:
#        Session.configure( bind=reflect() )
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
