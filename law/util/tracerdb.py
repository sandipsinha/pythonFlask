"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from contextlib import contextmanager
from datetime import date, datetime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declared_attr

import pytz
from law                        import config
from sqlalchemy                 import (create_engine, Column, 
                                        Integer, DateTime, Date,
                                        Boolean, String,Text,
                                        Numeric, ForeignKey,
                                        Index)
from sqlalchemy.dialects.mysql  import BIGINT, SMALLINT, MEDIUMINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.orm import mapper, clear_mappers


Base = declarative_base()



# Duplicate models of the same table need another base declaration
# so that they have a separate MetaData instance
OwnersBase = declarative_base()

db_url = '{dialect}://{user}:{passwd}@{host}:{port}/{dbname}'.format(
    dialect = config.get( 'tracerdb', 'dialect' ),
    user    = config.get( 'tracerdb', 'username' ),
    passwd  = config.get( 'tracerdb', 'password' ),
    host    = config.get( 'tracerdb', 'host' ),
    port    = config.get( 'tracerdb', 'port' ),
    dbname  = config.get( 'tracerdb', 'dbname' ),
)

engine = create_engine( 
            db_url, 
            echo=config.getboolean( 'tracerdb', 'debug' ),
            pool_recycle=config.getint( 'tracerdb', 'pool_recycle' ),
         )

Session = sessionmaker( bind=engine )



class TracerBullet( Base):
    __tablename__ = 'tracer_bullet'
    __table_args__ = {'mysql_engine':'InnoDB'}
    cluster = Column( String(length=20),primary_key=True )
    index_type = Column( String(length=20),primary_key=True )
    applies_start_time = Column( DateTime ,primary_key=True)
    status = Column( String(length=20) )
    run_start_time = Column( DateTime )
    run_end_time = Column( DateTime )
    run_secs =  Column( Numeric(6,1) )
    uid = Column( String(length=18) )

    @property
    def newcluster( self ):
        return self.cluster + self.index_type[0]

    @hybrid_method
    def clusterdtl(self):
        return self.newcluster

    def __repr__(self):
        return "<TracerBullet ({}, {}, {}, {}, , {}, {}>".format(
            self.newcluster,
            self.status,
            self.run_start_time,
            self.run_end_time,
            self.run_secs,
            self.uid
            )


class TracerBulletCold( Base):
    __tablename__ = 'tracer_bullet_cold'
    __table_args__ = {'mysql_engine':'InnoDB'}
    cluster = Column( String(length=20),primary_key=True )
    index_type = Column( String(length=20),primary_key=True )
    applies_start_time = Column( DateTime ,primary_key=True)
    status = Column( String(length=20) )
    run_start_time = Column( DateTime )
    run_end_time = Column( DateTime )
    run_secs =  Column( Numeric(6,1) )
    uid = Column( String(length=18) )

    @property
    def newcluster( self ):
        return self.cluster + self.index_type[0]

    @hybrid_method
    def clusterdtl(self):
        return self.newcluster

    def __repr__(self):
        return "<TracerBullet ({}, {}, {}, {}, , {}, {}>".format(
            self.newcluster,
            self.status,
            self.run_start_time,
            self.run_end_time,
            self.run_secs,
            self.uid
            )

class TracerPercentiles( Base):
    __tablename__ = 'tracer_percentiles'
    __table_args__ = {'mysql_engine':'InnoDB'}
    deployment         = Column( String(length=20),primary_key=True )
    cluster            = Column( String(length=20),primary_key=True )
    index_type         = Column( String(length=20),primary_key=True )
    period             = Column( String(length=20),primary_key=True )
    start_date         = Column( Date ,primary_key=True )
    end_date           = Column( Date )
    pcnt_LT30          = Column( Numeric(6,5))
    min_latency        = Column( Numeric(6,1))
    max_latency        = Column( Numeric(6,1))
    ninty_five         = Column('95th_secs',Numeric(10,1))
    ninty_eight        = Column('98th_secs', Numeric(10,1))
    ninty_nine         = Column('99th_secs', Numeric(10,1))
    reporting_secs     = Column( Numeric(10,1))
    period_secs        = Column( Numeric(10,1))
    percent_of_period  = Column( Numeric(6,5))
    ndays              = Column( SMALLINT(2))
    pcnt_LT_sec_thresh = Column( Numeric(6,5))

    @property
    def repcluster( self ):
        return self.cluster + self.index_type[0]

    @hybrid_method
    def clusterdata(self, clusterrep):
        return (self.cluster + self.index_type[0]) == clusterrep

    def __repr__(self):
        return "<TracerPercentiles ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
        self.repcluster,
        self.period,
        self.start_date,
        self.end_date,
        self.pcnt_LT30,
        self.min_latency,
        self.max_latency,
        self.ninty_five,
        self.ninty_eight,
        self.ninty_nine,
        self.reporting_secs,
        self.period_secs
        )


class TracerPercentilesCold( Base):
    __tablename__ = 'tracer_percentiles_cold'
    __table_args__ = {'mysql_engine':'InnoDB'}
    deployment         = Column( String(length=20),primary_key=True )
    cluster            = Column( String(length=20),primary_key=True )
    index_type         = Column( String(length=20),primary_key=True )
    period             = Column( String(length=20),primary_key=True )
    start_date         = Column( Date ,primary_key=True )
    end_date           = Column( Date )
    pcnt_LT30          = Column('pcnt_LT2', Numeric(6,5))
    min_latency        = Column( Numeric(6,1))
    max_latency        = Column( Numeric(6,1))
    ninty_five         = Column('95th_secs',Numeric(10,1))
    ninty_eight        = Column('98th_secs', Numeric(10,1))
    ninty_nine         = Column('99th_secs', Numeric(10,1))
    reporting_secs     = Column( Numeric(10,1))
    period_secs        = Column( Numeric(10,1))
    percent_of_period  = Column( Numeric(6,5))
    ndays              = Column( SMALLINT(2))
    pcnt_LT_sec_thresh = Column( Numeric(6,5))

    @property
    def repcluster( self ):
        return self.cluster + self.index_type[0]

    @hybrid_method
    def clusterdata(self, clusterrep):
        return (self.cluster + self.index_type[0]) == clusterrep

    def __repr__(self):
        return "<TracerPercentiles ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
        self.repcluster,
        self.period,
        self.start_date,
        self.end_date,
        self.pcnt_LT30,
        self.min_latency,
        self.max_latency,
        self.ninty_five,
        self.ninty_eight,
        self.ninty_nine,
        self.reporting_secs,
        self.period_secs
        )

@contextmanager
def tdb_session_context():
    """ Because TracerDB is read only we do not need commit """
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



