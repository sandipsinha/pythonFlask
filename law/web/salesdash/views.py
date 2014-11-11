"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import random
from datetime    import datetime, timedelta
from operator    import attrgetter
from collections import defaultdict
from functools   import partial

from flask               import Blueprint, render_template, request
from sqlalchemy          import and_, or_
from law.util.conversion import to_js_time
from law.util.timeutil   import Timebucket
from law.util.adb        import session_context, AccountState, Owners

blueprint = Blueprint( 'salesdash', __name__, 
                        template_folder = 'templates',
                        static_folder   = 'static' )


@blueprint.route( '/' )
def index():
    return 'Yep, you found it'

def random_values( numvals ):
    start = datetime( 2014, 4, 8 )
    keys = {}
    for i in range( numvals ):
        keys[ start + timedelta( days=i ) ] = random.randint( 0, 100 ) * i

    return keys

@blueprint.route( '/chartest' )
def chartest():
    series = []
    keys = random_values( 40 )
    series.append({
        'key'    : 'Travis',
        'values' : [(to_js_time( key ),  keys[key] ) for key in sorted( keys )]
    })
    keys = random_values( 40 )
    series.append({
        'key'    : 'Angela',
        'values' : [(to_js_time( key ),  keys[key] ) for key in sorted( keys )]
    })
    keys = random_values( 40 )
    series.append({
        'key'    : 'Stephanie',
        'values' : [(to_js_time( key ),  keys[key] ) for key in sorted( keys )]
    })
    keys = random_values( 40 )
    series.append({
        'key'    : 'Kati',
        'values' : [(to_js_time( key ),  keys[key] ) for key in sorted( keys )]
    })
    return render_template( 'sum_mrr.html', series=series )

def fill_empty_periods( fillval, *args ):
    """ This makes sure that all dictionaries supplied in args contain the same
    keys.  If a key is missing then it will be inserted and fillval will be used
    as it's value.  This function MUTATES the supplied args values in place.
    """
    period_lists = [set( periods.keys() ) for periods in args]
    periods = set()
    for period_set in period_lists:
        periods = periods.union( period_set )

    for period in periods:
        for arg in args:
            if period not in arg:
                arg[period]=fillval
   
zero_empty_periods = partial( fill_empty_periods, 0 )

def sum_periods( periods, value_prop ):
    sums = {}
    for period in periods:
        sums[ period ] = sum(( getattr( entry, value_prop, 0 ) for entry in periods[period] ))

    return sums
    
def sum_periods_delta( periods, base_prop, delta_prop ):
    sums = {}
    for period in periods:
        sums[ period ] = sum(( getattr( entry, base_prop, 0 ) - getattr( entry, delta_prop, 0 ) for entry in periods[period] ))

    return sums

class QueryOwners(object):

    def __init__( self, states, start, end, owners=None ):
        self.states = states
        self.start  = start
        self.end    = end
        self.names  = owners

    def _query_owners( self, states, start, end, owners=None):
        with session_context() as s:
            subq = state_query( s, states, start, end ).subquery()
            q = s.query( Owners, subq )\
                .join( subq, and_( Owners.acct_id == subq.c.acct_id,
                                    subq.c.updated >= Owners.start_date,
                                    subq.c.updated <  Owners.end_date ))

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


@blueprint.route( '/mrr' )
def mrr():
    start = datetime( 2013, 9, 1 )
    end   = datetime( 2014, 12, 31 )
    
    bucket = request.args.get( 'bucketed', 'quarter' )
    owners = QueryOwners( ['CTP','FWP'], start, end, owners=None ).bucketed( bucket )

    # This will essentially zero any periods that do not exist but are in our
    # time range of the other series
    fill_empty_periods( [], *[owners[name] for name in owners] )

    series = []
    for name in owners:
        rows = owners[name]
        sum_newbiz = sum_periods( rows, 'trate' )
        series.append({
            'key'    : name,
            'values' : [ (key, sum_newbiz[key]) for key in sorted( sum_newbiz ) ],
        })
   
    return render_template( 'upsell_newbiz.html', series=series )
   
def state_query( s, states, start, end ):
    # operator | or's the states together ( | is overloaded in SQLAlchemy query construction)
    q = s.query( AccountState ) \
         .filter( AccountState.updated >= start ) \
         .filter( AccountState.updated <= end ) \
         .filter( reduce( lambda query, func: query | func, [ AccountState.state.like( state ) for state in states] ) ) \

    return q

def query_state( states, start, end ):
    with session_context() as s:
        subs = state_query( s, states, start, end ).all()
        s.expunge_all()
    return subs

query_newbiz     = partial( query_state, ['CTP', '%WP'] )
query_lostbiz    = partial( query_state, ['%WF'] )
query_upsell     = partial( query_state, ['%WU'] )
query_downgrades = partial( query_state, ['%WD'] )

@blueprint.route( '/newbiz_plus_upsell' )
def new_biz_plus_upsell():
    start = datetime( 2014, 1, 1 )
    end   = datetime( 2014, 12, 31 )

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )

    
    newbiz     = query_upsell( start, end )
    sum_newbiz = sum_periods( bucket_func( Timebucket( newbiz, 'updated' ) )(), 'tRate' )
    
    upsell     = query_newbiz( start, end )
    sum_upsell = sum_periods_delta( bucket_func( Timebucket( upsell, 'updated' ) )(), 'tRate', 'fRate' )

    
    downgrade      = query_downgrades( start, end )
    sum_downgrades = sum_periods( bucket_func( Timebucket( downgrade, 'updated' ) )(), 'tRate' )
    
    lostbiz        = query_lostbiz( start, end )
    sum_lostbiz    = sum_periods_delta( bucket_func( Timebucket( lostbiz, 'updated' ) )(), 'fRate', 'tRate' )

    # Zero out any bucketed timeperiod that does not have a key that the other bucketed periods do
    fill_empty_periods( [], *[ sum_newbiz, sum_upsell, sum_downgrades, sum_lostbiz] )

    series = []
    series.append({
        'key'    : 'Upsell',
        'values' : [ (key, sum_upsell[key]) for key in sorted( sum_upsell ) ],
    })
    series.append({
        'key'    : 'Newbiz',
        'values' : [ (key, sum_newbiz[key]) for key in sorted( sum_newbiz ) ],
    })
    series.append({
        'key'    : 'Downgrades',
        'values' : [ (key, -sum_downgrades[key]) for key in sorted( sum_downgrades ) ],
    })
    series.append({
        'key'    : 'Lostbiz',
        'values' : [ (key, -sum_lostbiz[key]) for key in sorted( sum_lostbiz ) ],
    })

    return render_template( 'upsell_newbiz.html', series=series )
