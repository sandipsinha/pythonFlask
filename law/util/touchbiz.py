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
        if len( tbkeys ) != 0:
            if tbd[ tbkeys[-1] ].created <= sub.updated:
                key = tbkeys.pop()

        sub.owner = tbd[key].owner
        applied.append( sub )

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
