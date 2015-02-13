"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" Routines that gift touch business based on our old account_owner tables.
"
"""
from datetime import datetime, date
from types    import FunctionType

import pytz
from law.util.logger     import make_logger
from law.util.adb        import loader as adb_loader, Owners, AAWSC #tmp_uspg1?
from law.util.touchbizdb import session_context as tbz_session, loader as tbz_loader, Touchbiz, SalesReps

LOG      = make_logger( 'touchbiz-gifts' )
TIMEZONE = pytz.timezone( 'US/Pacific' ) 

class DataSource( object ):
    def __init__(self, table, loader ):
        self.table  = table
        self.loader = loader

class DataDestination( object ):
    def __init__(self, table, engine ):
        self.table  = table
        self.engine = engine

# Simple Migration
class AccountOwnersMigrator( object ):
    """ Creates a management objects that performs a simple migration
    of account_owners to the touchbiz model.  This is stupid in that
    it just injects a touchbiz entry for the start_date of the 
    account_owners entry
    """
    def __init__(self, source, dest, default_rep=None ):
        """ Source and dest are DataSource objects.
        Before is a datetime object to use as the upper time bound when
        querying source objects
        """
        self.source       = source
        self.dest         = dest
        self.default_rep  = default_rep
        self._rep_lookup  = None

    @property
    def salesrep( self ):
        """ Rep lazy loader """
        if self._rep_lookup is None:
            with tbz_loader() as l:
                reps = l.query( SalesReps ).all()

            self._rep_lookup = { rep.full_name: rep for rep in reps }

        return self._rep_lookup

    def get_salesrep_id( self, full_name ):
        try:
            rep = self.salesrep[ full_name ]
        except KeyError as e:
            if self.default_rep is not None:
                rep = self.salesrep[ self.default_rep ]
            else:
                raise e

        return rep.id

    def migrate( self, before=None ):
        before = before if before is not None else datetime.now()
        src = self.source

        with src.loader() as l:
            owners = l.query( src.table )\
                      .filter( src.table.start_date < before )\
                      .all()

        # Construct a batch dict for entry
        # Should set touchbiz created/modified to the start date
        items = [self.migrate_columns( owner ) for owner in owners ]
        self._insert( items )
    
        return len( items )


    def migrate_columns( self, row ):
        
        # Account owners is always US/Pacific (from SFDC) and touchbiz is always UTC
        def localize( dt ):
            if isinstance( dt, date ):
                dt = datetime( *(dt.timetuple()[:3]) )
            return pytz.utc.normalize( TIMEZONE.localize( dt ) ).replace( tzinfo=None )

        migrate_rules = {
            'acct_id'       : lambda x: x.acct_id,
            'sales_rep_id'  : lambda x: self.get_salesrep_id( x.owner ),
            'created'       : lambda x: localize( x.start_date ),
            'modified'      : lambda x: localize( x.start_date ),
            'tier'          : '',
            'retention'     : 0,
            'volume'        : 0,
            'sub_rate'      : 0,
            'billing_period': '',
        }

        def apply_migrate( source ):
            res = {}
            for col in migrate_rules:
                if isinstance( migrate_rules[col], FunctionType ):
                    res[col] = migrate_rules[col]( source )
                else:
                    res[col] = migrate_rules[col]

            return res

        return apply_migrate( row )

    def _insert( self, inserts, batch_size=5000 ):
        conn = self.dest.engine.connect().execution_options( autocommit=False )

        try:
            trans = conn.begin()        
            # Batch so MySql doesn't close the connection due to too large of a 
            # max_allowed_packet size
            for start in range( 0, len(inserts), batch_size):
                conn.execute( self.dest.table.__table__.insert(), inserts[start:start+batch_size] )
            trans.commit()

            LOG.info({
                'action'    : 'commit',
                'status'    : 'success',
                'item_count': len( inserts ),
            })
        except Exception as e:
            trans.rollback()
            LOG.exception({ 
                'action':'rollback', 
                'status':'failure',
                'reason':'insert failed',
            })
            raise e


# More complex migration rules
# 1. find all accounts that are Trial(/Free?) at time of go-live and enter owner based touchbiz
# 2. Before M&C set touchbiz start to that of ownership start for ALL PAID accounts.
# 3. After M&C set touchbiz start to that of ownership only for ALL new accounts regard
