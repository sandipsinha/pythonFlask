"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" Routines that gift touch business based on our old account_owner tables.
"
"""
from datetime  import datetime, timedelta
from types     import FunctionType
from itertools import chain

from law.util.logger     import make_logger
from law.util.adb        import loader as adb_loader, AAWSC
from law.util.touchbizdb import loader as tbz_loader, SalesReps

LOG = make_logger( 'touchbiz-gifts' )

class DataSource( object ):
    def __init__(self, table, loader ):
        self.table  = table
        self.loader = loader

class DataDestination( object ):
    def __init__(self, table, engine ):
        self.table  = table
        self.engine = engine

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
        items = self.migrate_by_sub_state( items )

        self._insert( items )
    
        return len( items )

    def migrate_columns( self, row ):

        migrate_rules = {
            'acct_id'       : lambda x: x.acct_id,
            'sales_rep_id'  : lambda x: self.get_salesrep_id( x.owner ),
            'created'       : lambda x: x.utc_start_date,
            'modified'      : lambda x: x.utc_start_date,
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

    def migrate_by_sub_state( self, touchbiz ):
        """ Migrates based on special business rules that apply based
        on the previous state of the account.
        """
        with adb_loader() as l:
            subs = l.query( AAWSC ).all()

        # Bucket by acct_id
        subd = {}
        for s in subs:
            try:
                subd[ s.acct_id ].append( s )
            except KeyError:
                subd[ s.acct_id ] = [s]

        tbd  = {}
        for t in touchbiz:
            try:
                tbd[ t['acct_id'] ].append( t )
            except KeyError:
                tbd[ t['acct_id'] ] = [t]

        migrated_tbd = {}
        for acct_id in tbd:
            if acct_id in subd:
                migrated_tbd[ acct_id ] = self._migrate_by_sub_state( subd[acct_id], tbd[acct_id] )
            else:
                migrated_tbd[ acct_id ] = tbd[acct_id]

        # flatten
        return list( chain.from_iterable( migrated_tbd.values() ) )

    def _migrate_by_sub_state( self, sub_entries, tb_entries ):
        """ Performs the migration with special rules given the previous subscripton state.
        For instance, if someone has a FWP|TWP|PWU then ownership was transfered and the first
        move as PWD|PWF then the initial owner is given the downgrade.

        Works on a per-account basis.
        """
        tbd    = {tb['created']: tb for tb in tb_entries }
        tbkeys = sorted( tbd.keys(), reverse=True )
        subs   = sorted( sub_entries, key=lambda x: x.utc_updated )

        key     = tbkeys.pop()
        states  = []
        prev_owner_id = None
        for sub in subs:
            states.append( sub.state )
            # While there are still touchbiz entries that occured before this
            # sub iterate through them until we find the one that occured right
            # before the subscription change.
            while len( tbkeys ) != 0 and tbd[ tbkeys[-1] ]['created'] <= sub.utc_updated:
                key = tbkeys.pop()

            # TODO - might have to write routine that finds the most applicable 
            # owner for a subscription independent of this flow

            # In the case of a downgrade, apply touchbiz to the previous subs
            # owner that won the subscription.
            if sub.state in ('PWF', 'PWD') and prev_owner_id != tbd[key]['sales_rep_id']:
                for state in states[::-1]:
                    if state in ('SUP', 'TWP', 'FWP', 'PWU' ):
                        # Move the current owner to a time that exists just after this 
                        # subscription entry so that the previous owner will be seen
                        # as the owner of this subscription.

                        # Because there may be multiple subscriptions that this applies to
                        # we need to continue processing in our normal way once the sub is
                        # bumped.
                        update_entry = tbd.pop(key)
                        update_entry['created'] = sub.utc_updated + timedelta( minutes=1 )
                        update_entry['modified'] = update_entry['created']
                        update_key = update_entry['created']
                        tbd[update_key] = update_entry
                        tbkeys.append( update_key )
                        # Found the downgrade owner. Stop going through old states.
                        break
            else:
                prev_owner_id = tbd[key]['sales_rep_id']

        return tbd.values()

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
