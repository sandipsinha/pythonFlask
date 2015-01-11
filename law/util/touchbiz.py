"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" Module that acts as a controller to the Touchbiz data model
"
"""
from datetime import datetime

from law.util.adb_touchbiz  import loader as tb_loader, Touchbiz, SalesReps
from law.util.adb           import loader as adb_loader, AccountState, Account

def initial_touchbiz_entry():
    epoch_start = datetime( 1970, 1, 1 )
    with tb_loader() as l:
        company = l.query( SalesReps )\
                   .filter( SalesReps.sfdc_alias == 'integ' )\
                   .one()

        initial = Touchbiz( created = epoch_start, modified = epoch_start )
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
    tbd = {tb.created: tb for tb in tb_entries}
    tbkeys = sorted( tbd.keys(), reverse=True )

    subs = sorted( sub_entries, key=lambda x: x.updated )

    applied = []
    key = tbkeys.pop()

    for sub in subs:
        # While there are still touchbiz entries that occured before this
        # sub iterate through them until we find the one the occured right
        # before the subscription change.
        while len( tbkeys ) != 0 and tbd[ tbkeys[-1] ].created <= sub.updated:
            key = tbkeys.pop()

        sub.owner = tbd[key].owner
        applied.append( sub )

    # If there are touchbiz entries left apply the most recent one 
    # to the returned rows
    if len( tbkeys ) != 0:
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

def tuplify( columns, rows, column_map=None ):
    """ Returns the rows as a list of tuples containing ((colum name, value), ... )"""
    column_map = column_map or {} 

    # Allows dot notation in getattr.  Does not support defaults.
    def getattrd(obj, name ):
        return reduce(getattr, name.split("."), obj)

    tuplified = []
    for row in rows:
        tuplified.append( [ (column_map.get( column, column), getattrd( row, column )) for column in columns ] )

    return tuplified


