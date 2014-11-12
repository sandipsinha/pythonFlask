"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import random
from datetime    import datetime, timedelta
from operator    import attrgetter
from collections import OrderedDict
from functools   import partial

from flask               import Blueprint, render_template, request, jsonify
from law.util.conversion import to_js_time
from law.util.timeutil   import Timebucket, BucketedList
from law.util.queries    import query_state, QueryOwners

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


#def sum_periods( value_prop, periods ):
#    sums = {}
#    for period in periods:
#        sums[ period ] = sum(( getattr( entry, value_prop, 0 ) for entry in periods[period] ))
#
#    return sums
#    
#def sum_periods_delta( base_prop, delta_prop, periods ):
#    sums = {}
#    for period in periods:
#        sums[ period ] = sum(( getattr( entry, base_prop, 0 ) - getattr( entry, delta_prop, 0 ) for entry in periods[period] ))
#
#    return sums
    
def sum_states( value_prop, items ):
    return sum(( getattr( entry, value_prop, 0 ) for entry in items ))

sum_rate         = partial( sum_states, 'tRate' ) 
sum_rate_change  = partial( sum_states, 'rate_delta' )

query_newbiz     = partial( query_state, ['CTP', '%WP'] )
query_lostbiz    = partial( query_state, ['%WF'] )
query_upsell     = partial( query_state, ['%WU'] )
query_downgrades = partial( query_state, ['%WD'] )

def _mrr():
#    start = datetime( 2013, 9, 1 )
    start = datetime( 2014, 6, 1 )
    end   = datetime( 2014, 12, 31 )
    
    bucket = request.args.get( 'bucketed', 'quarter' )
    owners = QueryOwners( ['CTP','FWP'], start, end, owners=None ).bucketed( bucket )

    # This will essentially zero any periods that do not exist but are in our
    # time range of the other series
    pset = BucketedList.period_set( *owners.values() )
    map( lambda bl: bl.fill_missing_periods( pset ), owners.values() )

    # Used as a map across bucketed lists to sum each period
    sum_to_rate = partial( sum_states, 'trate' )

    series = []
    for name in owners:
        bucketed_list = owners[name]
        bucketed_list.period_map( sum_to_rate )
        series.append({
            'key'    : name,
            'values' : [ (key, bucketed_list[key]) for key in sorted( bucketed_list ) ],
        })

    return series
   
@blueprint.route( '/apiv1/mrr' )
def api_mrr():
    series = _mrr()
    return jsonify({'series':series})

@blueprint.route( '/mrr' )
def mrr():
    series = _mrr()
    return render_template( 'upsell_newbiz.html', series=series )

def _new_biz_plus_upsell():
#    start = datetime( 2013, 9, 1 )
    start = datetime( 2014, 1, 1 )
    end   = datetime( 2014, 12, 31 )

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    newbiz     = query_upsell( start, end )
    sum_newbiz = bucket_func( Timebucket( newbiz, 'updated' ) )()
    
    upsell     = query_newbiz( start, end )
    sum_upsell = bucket_func( Timebucket( upsell, 'updated' ) )()
    
    downgrade      = query_downgrades( start, end )
    sum_downgrades = bucket_func( Timebucket( downgrade, 'updated' ) )()
    
    lostbiz     = query_lostbiz( start, end )
    sum_lostbiz = bucket_func( Timebucket( lostbiz, 'updated' ) )()

    bucketed_lists = OrderedDict({
        'newbiz'    : sum_newbiz, 
        'upsell'    : sum_upsell, 
        'downgrades': sum_downgrades, 
        'lostbiz'   : sum_lostbiz 
    })

    # Make all bucketed list contain a single value summation of their rate change
    for bl in bucketed_lists.values():
        bl.period_map( sum_rate_change )

    # Zero out any bucketed timeperiod that does not have a key that the other bucketed periods do
    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    series = []

    for name, bl in bucketed_lists.items():
        series.append({
            'key'    : name,
            'values' : [ (key, bl[key]) for key in sorted( bl ) ],
        })

    return series

@blueprint.route( '/apiv1/newbiz_plus_upsell' )
def api_new_biz_plus_upsell():
    series = _new_biz_plus_upsell()
    return jsonify( {'series':series} )

@blueprint.route( '/newbiz_plus_upsell' )
def new_biz_plus_upsell():
    series = _new_biz_plus_upsell()
    return render_template( 'upsell_newbiz.html', series=series )

