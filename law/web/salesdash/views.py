"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import random
import calendar
from datetime    import datetime, timedelta
from operator    import attrgetter
from collections import OrderedDict
from functools   import partial

from flask               import Blueprint, render_template, request, jsonify, url_for
from law.util.conversion import to_js_time
from law.util.timeutil   import Timebucket, BucketedList, iso8601_to_dt
from law.util.queries    import query_state, QueryOwners

blueprint = Blueprint( 'salesdash', __name__, 
                        template_folder = 'templates',
                        static_folder   = 'static' )

TODAY         = datetime.today()
DEFAULT_START = datetime( TODAY.year, 1, 1 ).strftime( '%Y-%m-%d' )
DEFAULT_END   = datetime( TODAY.year, TODAY.month, calendar.monthrange(TODAY.year, TODAY.month)[-1] )\
                .strftime( '%Y-%m-%d' )

@blueprint.route( '/' )
def index():
    return 'Yep, you found it'

@blueprint.route( '/slider' )
def test_slider():
    return render_template( 'slider.html', start='2014-04-08', end='2014-09-01' )
    
def sum_states( value_prop, items ):
    return sum(( getattr( entry, value_prop, 0 ) for entry in items ))

sum_rate         = partial( sum_states, 'tRate' ) 
sum_rate_change  = partial( sum_states, 'rate_delta' )

query_newbiz     = partial( query_state, ['CTP', '%WP'] )
query_lostbiz    = partial( query_state, ['%WF'] )
query_upsell     = partial( query_state, ['%WU'] )
query_downgrades = partial( query_state, ['%WD'] )

def _mrr( start, end ):
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
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )
    series = _mrr( start, end )
    return jsonify({'series':series})

@blueprint.route( '/mrr' )
def mrr():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _mrr( start, end )
    return render_template( 
        'upsell_newbiz.html', 
        series=series, 
        data_url=url_for( '.api_mrr' ),
        start=start, 
        end=end 
    )

def _new_biz_plus_upsell( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    newbiz     = query_upsell( start, end )
    sum_newbiz = bucket_func( Timebucket( newbiz, 'updated' ) )()
    
    upsell     = query_newbiz( start, end )
    sum_upsell = bucket_func( Timebucket( upsell, 'updated' ) )()
    
#    downgrade      = query_downgrades( start, end )
#    sum_downgrades = bucket_func( Timebucket( downgrade, 'updated' ) )()
#    
#    lostbiz     = query_lostbiz( start, end )
#    sum_lostbiz = bucket_func( Timebucket( lostbiz, 'updated' ) )()

    bucketed_lists = OrderedDict({
        'upsell'    : sum_upsell, 
        'newbiz'    : sum_newbiz, 
#        'downgrades': sum_downgrades, 
#        'lostbiz'   : sum_lostbiz 
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

@blueprint.route( '/apiv1/newbiz+upsell' )
def api_new_biz_plus_upsell():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _new_biz_plus_upsell( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/newbiz+upsell' )
def new_biz_plus_upsell():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _new_biz_plus_upsell( start, end )
    return render_template( 
            'upsell_newbiz.html', 
            series=series, 
            data_url=url_for( '.api_new_biz_plus_upsell' ),
            start=start, 
            end=end 
    )

