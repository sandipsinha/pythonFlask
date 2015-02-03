"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" Module that acts as a controller to the Touchbiz data model
"
"""
from datetime    import datetime
from collections import namedtuple, defaultdict

import pytz
from law                    import config
from law.util.logger        import make_logger
from law.util.touchbizdb    import (loader as tb_loader, 
                                    Touchbiz, 
                                    SalesReps,)
from law.util.adb           import (loader as adb_loader, 
                                    engine as adb_engine,
                                    AccountStateUncompressed, 
                                    AccountActivity,
                                    AAOwner,
                                    Account,)

LOG = make_logger( 'sales-touchbiz' )

TIMEZONE = pytz.timezone( 'US/Pacific' ) 
PENDING  = 'pending'
WON      = 'won'

# Used to create a single ad-hoc'd object containing the most pertinent fields.
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

def owner_id( email ):
    with tb_loader() as l:
        return l.query( SalesReps ).filter( SalesReps.email == email ).one().id

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

def apply_touchbiz( sub_entries, tb_entries, localize=False, with_pending=True ):
    """ Applies touchbiz rows to the supplied standard rows.
    This should add an owner column to each subscription row.
    """
    tb_entries.append( initial_touchbiz_entry() )

    if localize:
        tb_entries = localized_tb( tb_entries )

    tbd    = {tb.created: tb for tb in tb_entries }
    tbkeys = sorted( tbd.keys(), reverse=True )
    subs   = sorted( sub_entries, key=lambda x: x.updated )

    applied = []
    key = tbkeys.pop()

    for sub in subs:
        # While there are still touchbiz entries that occured before this
        # sub iterate through them until we find the one the occured right
        # before the subscription change.
        while len( tbkeys ) != 0 and tbd[ tbkeys[-1] ].created <= sub.updated:
            key = tbkeys.pop()

        sub.owner = tbd[key].owner
        sub.status = WON

        applied.append( sub )

    # If there are touchbiz entries left apply the most recent one 
    # to the returned rows
    if len( tbkeys ) != 0 and with_pending:
        tbd[tbkeys[0]].created = PENDING
        tbd[tbkeys[0]].status  = PENDING
        applied.append( tbd[tbkeys[0]] )

    return applied

def touchbiz_by_account_id( acct_id, localize=True ):
    """ Munges subscription changes with our touchbiz entries"""

    with adb_loader() as l:
        sub_entries = l.query( AccountStateUncompressed )\
                       .filter( AccountStateUncompressed.acct_id == acct_id )\
                       .all()

    with tb_loader() as l:
        tb_entries = l.query( Touchbiz )\
                      .filter( Touchbiz.acct_id == acct_id )\
                      .all()

    return apply_touchbiz( sub_entries, tb_entries, localize=localize )

def touchbiz_by_account( subdomain ):
    return touchbiz_by_account_id( acct_id_for_subdomain( subdomain ) )

def flatten( row ):
    if isinstance( row, AccountStateUncompressed ):
        cols = ['updated', 'tPlan.name', 'tDays', 'tGB', 'billing_period', 'tRate', 'owner.sfdc_alias', 'status']
        flattened = FlatTouchbiz( *[ item[1] for item in as_tuple( row, cols )] )
    elif isinstance( row, Touchbiz ):
        cols = ['created', 'tier', 'retention', 'volume', 'billing_period', 'sub_rate', 'owner.sfdc_alias', 'status']
        flattened = FlatTouchbiz( *[ item[1] for item in as_tuple( row, cols )] )

    return flattened

def as_tuple( row, columns, column_map=None ):
    """ Converts the row into a list of (column_name, value) pairs. 
    Filters unneeded pairs by only including pairs that have a column 
    name existing in the 'columns' list of this function's params.  
    Useful for later converting to a dict.
    """
    column_map = column_map or {} 
    return tuple( (column_map.get( column, column ), getattr_nested( row, column )) for column in columns )

def tuplify( rows, columns, column_map=None ):
    """ Returns the rows as a list of tuples containing ((colum name, value), ... )"""
    column_map = column_map or {} 
    tuplified = [ as_tuple( row, columns, column_map ) for row in rows ]

    return tuplified

def dictify( rows, columns=None, column_map=None ):
    """ Returns a list of dictionaries that represent the supplied rows """
    return [ dict( pairs ) for pairs in tuplify( rows, columns, column_map ) ]


class TableCreator( object ):
    """ Creates a separate table where toucbiz ownership
    is applied by matching touchbiz to source entries 
    (subscriptoin changes) via their updated dates.  
    Writes an owner column field as '<firstname> <lastname>'.
    """

    def __init__(self,  **kargs):
        self.source     = kargs['src_table']
        self.dest       = kargs['dest_table']
        self.engine     = kargs['dest_engine']
        self.src_loader = kargs['src_loader']

    def source_rows( self ):
        with self.src_loader() as l:
            items = l.query( self.source )\
                     .order_by( self.source.acct_id, self.source.updated )\
                     .all()

        #Make a dictionary keyed by acct_id
        acct_rows = defaultdict( list )
        for row in items:
            acct_rows[row.acct_id].append( row )

        return dict( acct_rows )
    
    def touchbiz_rows( self ):
        with tb_loader() as l:
            items =  l.query( Touchbiz )\
                     .order_by( Touchbiz.acct_id, Touchbiz.created )\
                     .all()

        #Make a dictionary keyed by acct_id
        acct_rows = defaultdict( list )
        for row in items:
            acct_rows[row.acct_id].append( row )

        return dict( acct_rows )
    
    def apply_ownership( self ):
        source_acct_rows = self.source_rows()
        touchbiz_acct_rows = self.touchbiz_rows()

        # Because apply_touchbiz works at the account level we need to create
        # an mapping of acct_ids to Subscription table rows and Touchbiz rows
        # per acct_id to operate on.
        owned = []
        for acct_id in source_acct_rows:
            owned.extend( apply_touchbiz( source_acct_rows[acct_id], touchbiz_acct_rows[acct_id], with_pending=False ) )
        
        def set_owner_name( row ):
            row.owner = '{} {}'.format( row.owner.first, row.owner.last )
            return row

        # Remove pending touchbiz items as they are not subject to ownership
        owned = ( set_owner_name( row ) for row in owned if row.status is not PENDING )
        self._insert( owned )

    def _insert( self, items ):
        conn = self.engine.connect().execution_options( autocommit=False )

        # Turn array of objects into a dict for insert
        inserts = dictify( items, columns=[
            'acct_id',
            'created',
            'updated',
            'from_vol_bytes',
            'from_ret_days',
            'from_sub_rate',
            'from_plan_id',
            'from_sched_id',
            'from_bill_per',
            'from_bill_chan',
            'to_vol_bytes',
            'to_ret_days',
            'to_sub_rate',
            'to_plan_id',
            'to_sched_id',
            'to_bill_per',
            'to_bill_chan',
            'trial_exp',
            'owner',
        ])

        try:
            trans = conn.begin()        
            conn.execute( self.dest.__table__.delete() )
            conn.execute( self.dest.__table__.insert(), inserts )
            trans.commit()
        except Exception as e:
            trans.rollback()
            LOG.exception({ 
                'action':'rollback', 
                'status':'failure',
                'reason':'insert failed',
            })
            raise e

class AAOwnerCreator( TableCreator ):        
    def __init__( self ):
        super( AAOwnerCreator, self ).__init__(
            src_table   = AccountActivity,
            src_loader  = adb_loader,
            dest_table  = AAOwner,
            dest_engine = adb_engine,
        )

