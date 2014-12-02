"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
" General purpose queries/query classes.
"
"""
from collections        import defaultdict
from operator           import attrgetter

from sqlalchemy         import and_, or_, not_, func
from law.util.timeutil  import Timebucket
from law.util.adb       import session_context, AccountState, Owners, Tier

def state_query( s, states, start, end, g2only=True):
    # operator | or's the states together ( | is overloaded in SQLAlchemy query construction)
    q = s.query( AccountState ) \
         .filter( AccountState.updated >= start ) \
         .filter( AccountState.updated < end ) \
         .filter( reduce( lambda query, func: query | func, [ AccountState.state.like( state ) for state in states] ) ) \

    if g2only:
        q = q.filter( AccountState.tPlan_id < 100 ) 

    return q

def query_state( states, start, end, g2only=True ):
    with session_context() as s:
        subs = state_query( s, states, start, end, g2only=g2only ).all()
        s.expunge_all()
    return subs

def query_product_state( states, products, start, end ):
    with session_context() as s:
        q = state_query( s, states, start, end )
        q = q.join( Tier, aliased=True )\
              .filter( or_(( Tier.name.__eq__( product ) for product in products )) )
        subs = q.all()
        s.expunge_all()
    return subs

class QueryOwners(object):

    def __init__( self, states, start, end, owners=None ):
        self.states = states
        self.start  = start
        self.end    = end
        self.names  = owners

    def _query_owners( self, states, start, end, owners=None):
        with session_context() as s:
            subq = state_query( s, states, start, end ).subquery()
#            aliased_subq = aliased( AccountState, subq )
#            q = s.query( Owners, aliased_subq )\
            q = s.query( Owners, subq )\
                .join( subq, and_( Owners.acct_id == subq.c.acct_id,
                                    Owners.subdomain == subq.c.subdomain,
                                    func.DATE( subq.c.updated ) >= Owners.start_date,
                                    func.DATE( subq.c.updated ) <=  Owners.end_date ))

            # If we're only querying for specific users then apply the or'd constraints
            if owners != None:
                q.filter( reduce( lambda query, func: query | func, [ Owners.owner == owner for owner in owners] ) ) \

            subs = q.all()
            s.expunge_all()

        return subs

    @property
    def subs( self ):
        return self._query_owners( self.states, self.start, self.end, self.names )

    @property
    def owners( self ):
        owners = defaultdict( list )
        for row in self.subs:
            owners[ row.Owners.owner ].append( row )

        return owners

    def bucketed( self, bucket ):
        bucket_func = attrgetter( bucket )

        owners = self.owners
        for name in owners:
            owners[name] = bucket_func( Timebucket( owners[name], 'updated' ) )()

        return owners

