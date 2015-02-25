"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from contextlib import contextmanager
from datetime import date, datetime

import pytz
from law                        import config
from sqlalchemy                 import (create_engine, Column, 
                                        Integer, DateTime, Date,
                                        Boolean, String,
                                        Numeric, ForeignKey,
                                        Index)
from sqlalchemy.dialects.mysql  import BIGINT, SMALLINT, MEDIUMINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker, relationship, backref

Base = declarative_base()
# Duplicate models of the same table need another base declaration
# so that they have a separate MetaData instance
OwnersBase = declarative_base()

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
            pool_recycle=config.getint( 'adb', 'pool_recycle' ),
         )

Session = sessionmaker( bind=engine )

def _localize( dt ):
    if dt is None:
        return dt

    timezone = pytz.timezone( 'US/Pacific' )
    if type( dt ) is date:
        dt = datetime( *(dt.timetuple()[:3]) )
    return pytz.utc.normalize( timezone.localize( dt ) ).replace( tzinfo=None )

class Account( Base ):
    __tablename__  = 'accounts'
    __table_args__ = {'mysql_engine':'InnoDB'}

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

class AccountActivitySchema( object ):
    acct_id        = Column( Integer, primary_key=True, index=True )
    updated        = Column( DateTime, primary_key=True, index=True )
    created        = Column( DateTime)
    from_vol_bytes = Column( BIGINT(unsigned=True), default=0 )
    from_ret_days  = Column( SMALLINT(unsigned=True), default=0 )
    from_sub_rate  = Column( MEDIUMINT(unsigned=True), default=0 )
    from_plan_id   = Column( SMALLINT(unsigned=True), default=0 )
    from_sched_id  = Column( SMALLINT(unsigned=True), default=0 )
    from_bill_per  = Column( String(length=2), default='' )
    from_bill_chan = Column( SMALLINT(unsigned=True), default=0 ) 
    to_vol_bytes   = Column( BIGINT(unsigned=True), default=0 )
    to_ret_days    = Column( SMALLINT(unsigned=True), default=0 )
    to_sub_rate    = Column( MEDIUMINT(unsigned=True), default=0 )
    to_plan_id     = Column( SMALLINT(unsigned=True), default=0 )
    to_sched_id    = Column( SMALLINT(unsigned=True), default=0 )
    to_bill_per    = Column( String(length=2), default='' )
    to_bill_chan   = Column( SMALLINT(unsigned=True), default=0) 
    trial_exp      = Column( DateTime, default=None )

class AccountActivity( Base, AccountActivitySchema ):
    __tablename__  = 'account_activity'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    def __repr__(self):
        return "<AccountActivity([{id},{upd}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            frate = self.from_sub_rate,
            fvol  = self.from_vol_bytes,
            fret  = self.from_ret_days,
            fper  = self.from_bill_per,
            trate = self.to_sub_rate,
            tvol  = self.to_vol_bytes,
            tret  = self.to_ret_days,
            tper  = self.to_bill_per,
        )

class AAOwner( OwnersBase, AccountActivitySchema ):
    __tablename__  = 'account_activity_owners'
    __table_args__ = {'mysql_engine':'InnoDB'}

    owner = Column( String(length=100) )
    
    def __repr__(self):
        return "<AAOwner([{id},{upd},{owner}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            owner = self.owner,
            frate = self.from_sub_rate,
            fvol  = self.from_vol_bytes,
            fret  = self.from_ret_days,
            fper  = self.from_bill_per,
            trate = self.to_sub_rate,
            tvol  = self.to_vol_bytes,
            tret  = self.to_ret_days,
            tper  = self.to_bill_per,
        )

class AAWithStatesBase( AccountActivitySchema ):
    subdomain        = Column( String(length=100) )
    state_name       = Column( String(length=6) )
    plan_state_name  = Column( String(length=20) )

class AAWithStates( Base, AAWithStatesBase ):
    __tablename__  = 'account_activity_with_states'
    __table_args__ = {'mysql_engine':'InnoDB'}

class AAWithStatesCollapsed( Base, AAWithStatesBase ):
    __tablename__  = 'account_activity_with_states_collapsed'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    paid_status      = Column( String(length=6) )
    collapse_count   = Column( Integer )

class AAWSBase( object ):
    
    acct_id   = Column( Integer, primary_key=True )
    subdomain = Column( String(length=100) )

    updated   = Column( DateTime, primary_key=True )
    created   = Column( DateTime )
    trial_exp = Column( Date )
    stNam     = Column( String(length=6) )
    pStNam    = Column( String(length=20) )

    fGB       = Column( Numeric( 14, 1 ) )
    fDays     = Column( SMALLINT( unsigned=True ) )
    frate     = Column( MEDIUMINT )
    fPlan     = Column( SMALLINT( unsigned=True ) )
    fPer      = Column( String(length=2) )
    fBC       = Column( SMALLINT( unsigned=True ) )

    tGB       = Column( Numeric( 14, 1 ) )
    tDays     = Column( SMALLINT( unsigned=True ) )
    trate     = Column( MEDIUMINT )
    tPlan     = Column( SMALLINT( unsigned=True ) )
    tPer      = Column( String(length=2) )
    tBC       = Column( SMALLINT( unsigned=True ) )

    @property
    def state( self ):
        return self.stNam

    @property
    def utc_created(self):
        return _localize( self.created )
    
    @property
    def utc_updated(self):
        return _localize( self.updated )

class AAWS( OwnersBase, AAWSBase ):
    __tablename__  = 'aaws'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    def __repr__(self):
        return "<AAWS([{id},{upd}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            frate = self.frate,
            fvol  = self.fGB,
            fret  = self.fDays,
            fper  = self.fPer,
            trate = self.trate,
            tvol  = self.tGB,
            tret  = self.tDays,
            tper  = self.tPer,
        )

class AAWSOwner( OwnersBase, AAWSBase ):
    __tablename__  = 'aaws_owners'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    owner  = Column( String(length=100) )
    
    def __repr__(self):
        return "<AAWSOwners([{id},{upd},{owner}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            owner = self.owner,
            frate = self.frate,
            fvol  = self.fGB,
            fret  = self.fDays,
            fper  = self.fPer,
            trate = self.trate,
            tvol  = self.tGB,
            tret  = self.tDays,
            tper  = self.tPer,
        )
    

class AAWSC( OwnersBase, AAWSBase ):
    __tablename__  = 'aawsc'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    cc      = Column( SMALLINT(unsigned=True) )
    pdStat  = Column( String(length=6) )
    
    def __repr__(self):
        return "<AAWSC([{id},{upd}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            frate = self.frate,
            fvol  = self.fGB,
            fret  = self.fDays,
            fper  = self.fPer,
            trate = self.trate,
            tvol  = self.tGB,
            tret  = self.tDays,
            tper  = self.tPer,
        )


class AAWSCOwner( OwnersBase, AAWSBase ):
    __tablename__  = 'aawsc_owners'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    cc     = Column( SMALLINT(unsigned=True) )
    pdStat = Column( String(length=6) )
    owner  = Column( String(length=100) )
    
    def __repr__(self):
        return "<AAWSCOwner([{id},{upd},{owner}] ${frate},{fvol}b,{fret}d,{fper} -> ${trate},{tvol}b,{tret}d,{tper})>".format(
            id    = self.acct_id, 
            upd   = self.updated,
            owner = self.owner,
            frate = self.frate,
            fvol  = self.fGB,
            fret  = self.fDays,
            fper  = self.fPer,
            trate = self.trate,
            tvol  = self.tGB,
            tret  = self.tDays,
            tper  = self.tPer,
        )

class AccountState( Base ):
    """ Compressed subscription table.  Any subscriptions that take place from
    sun-sat are compressed into a single entry
    """
    __tablename__  = 'aawsc'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    acct_id   = Column( Integer, primary_key=True )
    updated   = Column( DateTime, primary_key=True )
    subdomain = Column( String(length=100) )
    state     = Column( 'stNam', String(length=10) )
    tRate     = Column( 'trate', MEDIUMINT )
    fRate     = Column( 'frate', MEDIUMINT )
    tPlan_id  = Column( 'tPlan', Integer, ForeignKey( 'subscription_plan.id' ) )
    tGB       = Column( Numeric( 14, 1 ) )
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
    __tablename__  = 'aaws'
    __table_args__ = {'mysql_engine':'InnoDB'}
    
    acct_id   = Column( Integer, primary_key=True )
    updated   = Column( DateTime, primary_key=True )
    subdomain = Column( String(length=100) )
    state     = Column( 'stNam', String(length=10) )
    tRate     = Column( 'trate', MEDIUMINT )
    fRate     = Column( 'frate', MEDIUMINT )
    tPlan_id  = Column( 'tPlan', Integer, ForeignKey( 'subscription_plan.id' ) )
    tGB       = Column( Numeric( 14, 1 ) )
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
    __tablename__  = 'subscription_plan'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id   = Column( Integer, primary_key=True )
    name = Column( String(length=100) )
    code = Column( Integer )

    def __repr__(self):
        return "<Tier({},{},{})>".format(
            self.id, 
            self.name, 
            self.code)

class VolumeAccepted( Base ):
    __tablename__  = 'chopper_account_volumes'
    __table_args__ = {'mysql_engine':'InnoDB'}

    acct_id = Column( Integer, primary_key=True )
    date    = Column( 'vol_date', DateTime, primary_key=True )
    bytes   = Column( Integer )

    def __repr__(self):
        return "<VolumeAccepted({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.bytes)

class VolumeDropped( Base ):
    __tablename__  = 'chopper_account_volumes_dropped'
    __table_args__ = {'mysql_engine':'InnoDB'}

    acct_id = Column( Integer, primary_key=True )
    date    = Column( 'vol_date', DateTime, primary_key=True )
    bytes   = Column( Integer )

    def __repr__(self):
        return "<VolumeDropped({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.bytes)

class EventsAccepted( Base ):
    __tablename__  = 'chopper_events_allowed'
    __table_args__ = {'mysql_engine':'InnoDB'}

    acct_id = Column( Integer, primary_key=True )
    date    = Column( DateTime, primary_key=True )
    events  = Column( Integer )

    def __repr__(self):
        return "<EventsAccepted({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.events)


class EventsDropped( Base ):
    __tablename__  = 'chopper_events_denied'
    __table_args__ = {'mysql_engine':'InnoDB'}

    acct_id = Column( Integer, primary_key=True )
    date    = Column( DateTime, primary_key=True )
    events  = Column( Integer )

    def __repr__(self):
        return "<EventsDropped({},{},{})>".format(
            self.acct_id, 
            self.date, 
            self.events)

class Owners( Base ):
    __tablename__  = 'account_owners'
    __table_args__ = {'mysql_engine':'InnoDB'}

    acct_id    = Column( Integer )
    subdomain  = Column( String(length=100), primary_key=True )
    owner      = Column( String(length=100) )
    start_date = Column( DateTime, primary_key=True )
    end_date   = Column( DateTime )
    executive  = Column( Boolean )

    @property
    def utc_start_date( self ):
        return _localize( self.start_date )

    @property
    def utc_end_date( self ):
        return _localize( self.end_date )

    def __repr__(self):
        return "<Owner: {}>".format(
            "|".join(map( str, [
                self.acct_id, 
                self.subdomain,
                self.owner,
                self.start_date,
                self.end_date,
            ]))
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



