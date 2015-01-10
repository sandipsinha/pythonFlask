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
                                        ForeignKey)
from sqlalchemy.dialects.mysql  import MEDIUMINT, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref

Base = declarative_base()

db_url = '{dialect}://{user}:{passwd}@{host}:{port}/{dbname}'.format(
    dialect = config.get( 'adb_touchbiz', 'dialect' ),
    user    = config.get( 'adb_touchbiz', 'username' ),
    passwd  = config.get( 'adb_touchbiz', 'password' ),
    host    = config.get( 'adb_touchbiz', 'host' ),
    port    = config.get( 'adb_touchbiz', 'port' ),
    dbname  = config.get( 'adb_touchbiz', 'dbname' ),
)

engine = create_engine( 
            db_url, 
            echo=config.getboolean( 'adb_touchbiz', 'debug' ), 
            pool_recycle=3600 
         )

Session = sessionmaker( bind=engine )

class Touchbiz( Base ):
    __tablename__ = 'sales_touchbiz'

    acct_id        = Column( MEDIUMINT(unsigned=True), primary_key=True )
    sales_rep_id   = Column( MEDIUMINT(unsigned=True), ForeignKey( 'sales_reps.id' ) )
    created        = Column( DateTime, primary_key=True )
    modified       = Column( DateTime )
    stage_id       = Column( MEDIUMINT(unsigned=True), ForeignKey( 'sales_stages.id' ) )
    tier           = Column( String(length=100) )
    retention      = Column( Integer )
    volume         = Column( BIGINT(unsigned=True) )
    sub_rate       = Column( Integer )
    billing_period = Column( String(length=50) )
    owner          = relationship(
                        "SalesReps", 
                        lazy='joined',
                        backref=backref("sales_touchbiz", uselist=False))
    stage          = relationship(
                        "SalesStages", 
                        lazy='joined',
                        backref=backref("sales_touchbiz", uselist=False))
             
    def __repr__(self):
        return "<touchbiz({},{},{})>".format(
            self.acct_id, 
            self.created,
            self.sales_rep_id,
        )

class SalesReps( Base ):
    __tablename__ = 'sales_reps'

    id         = Column( MEDIUMINT(unsigned=True), primary_key=True )
    first      = Column( String(length=100) )
    last       = Column( String(length=100) )
    email      = Column( String(length=200) )
    sfdc_alias = Column( String(length=10) )
    active     = Column( Integer )
             
    def __repr__(self):
        return "<SalesReps({},{} {},{})>".format(
            self.id, 
            self.first,
            self.last,
            self.email,
        )

class SalesStages( Base ):
    __tablename__ = 'sales_stages'

    id   = Column( MEDIUMINT(unsigned=True ), primary_key=True )
    name = Column( String(length=100) )
    
    def __repr__(self):
        return "<SalesStages({},{})>".format(
            self.id, 
            self.first,
        )

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

def create_touchbiz_tables():
    """ Populates the sales stages table """
    Base.metadata.create_all( 
        bind=engine, 
        tables=[ 
            Touchbiz.__table__, 
            SalesReps.__table__, 
            SalesStages.__table__ 
        ]
    )

    with session_context() as s:
        s.add( SalesStages( name='Not Engaged' ) )
        s.add( SalesStages( name='Working' ) )
        s.add( SalesStages( name='Two Way Conversation' ) )
        s.add( SalesStages( name='Qualified' ) )
        s.add( SalesStages( name='Trial Close' ) )
        s.add( SalesStages( name='Closed Won' ) )
        s.add( SalesStages( name='Nurture' ) )
        s.add( SalesStages( name='Closed Lost' ) )
        s.add( SalesStages( name='Never Responded' ) )
        s.add( SalesStages( name='Went Dark' ) )
        s.add( SalesStages( name='Poor Experience / Technical Issues' ) )
        s.add( SalesStages( name='Timing' ) )
        s.add( SalesStages( name='Security' ) )
        s.add( SalesStages( name='No Budget' ) )
        s.add( SalesStages( name='Lost to Competitor' ) )
        s.add( SalesStages( name='Duplicate' ) )

