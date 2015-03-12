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

TIMEZONE    = pytz.timezone( 'US/Pacific' ) 
EXPIRE_DAYS = config.getint( 'touchbiz', 'expire_days' )
PENDING     = 'pending'
WON         = 'won'
EXPIRED     = 'ownership expired'

UPSTATES    = ('SUP', 'TWP', 'TWF', 'FWP', 'PWU')
DOWNSTATES  = ('PWF', 'PWD')
PENDING_APPLICABLE  = ('TWF')

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

def ownership_expired( prev_sub, current_sub, tb_entry ):
    if prev_sub is not None:
        if prev_sub.status == EXPIRED and current_sub.state not in UPSTATES:
            return True
        if (current_sub.updated - prev_sub.updated).days >= EXPIRE_DAYS and current_sub.state not in UPSTATES:
            return True

    return False

def is_downgrade( sub ):
    if hasattr( sub, 'state' ):
        return True if sub.state in DOWNSTATES else False
    elif hasattr( sub, 'from_sub_rate' ) and hasattr( sub, 'to_sub_rate' ):
        return True if sub.from_sub_rate - sub.to_sub_rate > 0 else False

    raise Exception( 'Cannot decide on subscription transition state' )

def is_paid_or_upgrade( sub ):
    if hasattr( sub, 'state' ):
        return True if sub.state in UPSTATES else False
    elif hasattr( sub, 'from_sub_rate' ) and hasattr( sub, 'to_sub_rate' ):
        return True if sub.from_sub_rate - sub.to_sub_rate < 0 else False

    raise Exception( 'Cannot decide on subscription transition state' )

def is_pending_applicable( sub, tb ):
    """ Returns whether a subscription status could be seen as 'Pending' given
    the touchbiz entry.
    """
    if hasattr( sub, 'state' ):
        if sub.updated > tb.created and sub.state in PENDING_APPLICABLE:
            return True
    return False

def apply_touchbiz( sub_entries, tb_entries, initial_entry=None, localize=False, with_pending=True ):
    """ Applies touchbiz rows to the supplied standard rows.
    This should add an owner column to each subscription row.
    """
    default = initial_entry
    if default is None:
        default = initial_touchbiz_entry()

    tb_entries.append( default )

    if localize:
        tb_entries = localized_tb( tb_entries )

    tbd    = {tb.created: tb for tb in tb_entries }
    tbkeys = sorted( tbd.keys(), reverse=True )
    subs   = sorted( sub_entries, key=lambda x: x.updated )

    applied = []
    key = tbkeys.pop()

    last_paid = default
    prev_sub  = None
    for sub in subs:
        # While there are still touchbiz entries that occured before this
        # sub iterate through them until we find the one that occured right
        # before the subscription change.
        while len( tbkeys ) != 0 and tbd[ tbkeys[-1] ].created <= sub.updated:
            key = tbkeys.pop()

        # Owners can expire and be returned to the company after a 
        # certain timeperiod of inactivity.
        if ownership_expired( prev_sub, sub, tbd[key] ):
            sub.owner = default.owner
            sub.status = EXPIRED
        elif is_downgrade( sub ):
            sub.owner = last_paid.owner
            sub.status = WON
        else:
            sub.owner = tbd[key].owner
            sub.status = WON
            last_paid = tbd[key] if is_paid_or_upgrade( sub ) else last_paid

        if with_pending and tbd[key].owner != default.owner and is_pending_applicable( sub, tbd[key] ):
            # Shunt the touchbiz subscription by keeping the current
            # touchbiz entry in the processing pipeline
            tbkeys.append( key )

        applied.append( sub )
        prev_sub = sub

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

    return apply_touchbiz( sub_entries, tb_entries, initial_entry=initial_touchbiz_entry(),  localize=localize )

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
    
    def apply_ownership( self, localize=False ):
        source_acct_rows = self.source_rows()
        touchbiz_acct_rows = self.touchbiz_rows()

        # The default owner
        default_owner = initial_touchbiz_entry()

        # Because apply_touchbiz works at the account level we need to create
        # an mapping of acct_ids to Subscription table rows and Touchbiz rows
        # per acct_id to operate on.
        owned = []
        for acct_id in source_acct_rows:
            owned.extend( apply_touchbiz( 
                                source_acct_rows[acct_id], 
                                touchbiz_acct_rows.get(acct_id, []), 
                                initial_entry=default_owner, 
                                with_pending=False,
                                localize=localize ))
        
        def set_owner_name( row ):
            row.owner = '{} {}'.format( row.owner.first, row.owner.last )
            return row

        # Remove pending touchbiz items as they are not subject to ownership
        owned = ( set_owner_name( row ) for row in owned if row.status is not PENDING )
        self._insert( owned )

    def _insert( self, items, batch_size=5000 ):
        conn = self.engine.connect().execution_options( autocommit=False )

        # Get all destination table fields
        cols = [col.name for col in self.dest.__table__.columns]
        # Turn array of objects into a dict for insert
        inserts = dictify( items, columns=cols )

        try:
            trans = conn.begin()        
            conn.execute( self.dest.__table__.delete() )
            # Batch so MySql doesn't close the connection due to too large of a 
            # max_allowed_packet size
            for start in range( 0, len(inserts), batch_size):
                conn.execute( self.dest.__table__.insert(), inserts[start:start+batch_size] )
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

