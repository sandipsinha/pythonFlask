"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" Module that acts as a controller to the Touchbiz data model
"
"""
from datetime    import datetime
from collections import namedtuple

import pytz
from law                    import config
from law.util.touchbizdb    import loader as tb_loader, Touchbiz, SalesReps, SalesStages
from law.util.adb           import loader as adb_loader, AccountState, Account

FlatTouchbiz = namedtuple( 'FlatTouchbiz', [
    'created', 
    'tier', 
    'retention', 
    'volume', 
    'period', 
    'rate', 
    'owner',
    'status'] 
)

PENDING = 'pending'
WON = 'won'

TIMEZONE = pytz.timezone( 'US/Pacific' ) 

def localized_tb( tb_entries, timezone=TIMEZONE ):
    """ Localizes created and modified colums of all Touchbiz object in 
    tb_entries to the supplied timezone.  This does not make the datetime
    objects timezone aware, but rather just applies the timezone offsets.
    """
    def localized( tb ):
        tb.created  = timezone.normalize( pytz.utc.localize( tb.created ) ).replace( tzinfo=None )
        tb.modified = timezone.normalize( pytz.utc.localize( tb.modified ) ).replace( tzinfo=None )
        return tb

    return (localized( tb ) for tb in tb_entries )

def getattr_nested(obj, name, default=None ):
    """ Allows dot notation in getattr. """
    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError:
        return default


def initial_touchbiz_entry():
    epoch_start = datetime( 1970, 1, 1 )
    with tb_loader() as l:
        company = l.query( SalesReps )\
                   .filter( SalesReps.email == config.get( 'touchbiz', 'company_user' ) )\
                   .one()


        initial = Touchbiz( 
            created  = epoch_start, 
            modified = epoch_start,
        )
        initial.owner = company

    return initial

def acct_id_for_subdomain( subdomain ):
    with adb_loader() as l:
        acct = l.query( Account )\
                .filter( Account.subdomain == subdomain )\
                .one()

    return acct.acct_id

def apply_touchbiz( sub_entries, tb_entries ):
    """ Applies touchbiz rows to the supplied standard rows.
    This should add an owner column to each subscription row.
    """
    tb_entries.append( initial_touchbiz_entry() )

    tbd    = {tb.created: tb for tb in localized_tb( tb_entries ) }
    tbkeys = sorted( tbd.keys(), reverse=True )
    subs   = sorted( sub_entries, key=lambda x: x.updated )

    applied = []
    key = tbkeys.pop()
    match = False

    for sub in subs:
        # While there are still touchbiz entries that occured before this
        # sub iterate through them until we find the one the occured right
        # before the subscription change.
        while len( tbkeys ) != 0 and tbd[ tbkeys[-1] ].created <= sub.updated:
            key = tbkeys.pop()
            match = True

        sub.owner = tbd[key].owner
        sub.status = WON

        applied.append( sub )

    # If there are touchbiz entries left apply the most recent one 
    # to the returned rows
    if len( tbkeys ) != 0:
        tbd[tbkeys[0]].created = PENDING
        tbd[tbkeys[0]].status  = PENDING
        applied.append( tbd[tbkeys[0]] )

    return applied
        

def touchbiz_by_account_id( acct_id ):
    """ Munges subscription changes with our touchbiz entries"""

    with adb_loader() as l:
        sub_entries = l.query( AccountState )\
                       .filter( AccountState.acct_id == acct_id )\
                       .all()

    with tb_loader() as l:
        tb_entries = l.query( Touchbiz )\
                      .filter( Touchbiz.acct_id == acct_id )\
                      .all()

    return apply_touchbiz( sub_entries, tb_entries )

def touchbiz_by_account( subdomain ):
    return touchbiz_by_account_id( acct_id_for_subdomain( subdomain ) )

def flatten( row ):
    if isinstance( row, AccountState ):
        cols = ['updated', 'tPlan.name', 'tDays', 'tGB', 'billing_period', 'tRate', 'owner.sfdc_alias', 'status']
        flattened = FlatTouchbiz( *[ item[1] for item in as_tuple( row, cols )] )
    elif isinstance( row, Touchbiz ):
        cols = ['created', 'tier', 'retention', 'volume', 'billing_period', 'sub_rate', 'owner.sfdc_alias', 'status']
        flattened = FlatTouchbiz( *[ item[1] for item in as_tuple( row, cols )] )

    return flattened

def as_tuple( row, columns, column_map=None ):
    column_map = column_map or {} 
    return [ (column_map.get( column, column ), getattr_nested( row, column )) for column in columns ]

def tuplify( rows, columns=None, column_map=None ):
    """ Returns the rows as a list of tuples containing ((colum name, value), ... )"""
    column_map = column_map or {} 
    tuplified = [ as_tuple( row, columns, column_map ) for row in rows ]

    return tuplified

def dictify( rows, columns=None, column_map=None ):
    return [ dict( pairs ) for pairs in tuplify( rows, columns, column_map ) ]

def owner_id( email ):
    with tb_loader() as l:
        return l.query( SalesReps ).filter( SalesReps.email == email ).one().id
