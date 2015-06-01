"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import random
import calendar
from datetime    import datetime, timedelta
from operator    import attrgetter, itemgetter
from collections import OrderedDict
from functools   import partial

from flask               import Blueprint, render_template, request, jsonify, url_for
from law.util.conversion import to_js_time
from law.util.timeutil   import Timebucket, BucketedList, iso8601_to_dt
from law.util.queries    import query_state, query_product_state, QueryOwners

blueprint = Blueprint( 'salesdash', __name__, 
                        template_folder = 'templates',
                        static_folder   = 'static' )

TODAY         = datetime.today()
DEFAULT_START = datetime( TODAY.year, 1, 1 ).strftime( '%Y-%m-%d' )
DEFAULT_END   = datetime( TODAY.year, TODAY.month, calendar.monthrange(TODAY.year, TODAY.month)[-1] )\
                .strftime( '%Y-%m-%d' )


@blueprint.route( '/slider' )
def test_slider():
    return render_template( 'salesdash/slider.html', start='2014-04-08', end='2014-09-01' )
    
def sum_delta( value_prop1, value_prop2, items ):
    return sum(( getattr( entry, value_prop1, 0 ) - getattr( entry, value_prop2, 0 ) for entry in items ))

def sum_states( value_prop, items ):
    return sum(( getattr( entry, value_prop, 0 ) for entry in items ))

sum_rate           = partial( sum_states, 'tRate' ) 
sum_rate_change    = partial( sum_states, 'rate_delta' )

#query_newbiz       = partial( query_state, ['CTP', '%WP'] )
query_newbiz       = partial( query_state, ['%WP'] )
#query_gross_newbiz = partial( query_state, ['CTP', '%WP', 'PWF'] )
query_gross_newbiz = partial( query_state, ['%WP', 'PWF'] )
query_lostbiz      = partial( query_state, ['PWF'] )
query_upsell       = partial( query_state, ['%WU'] )
#query_gross_upsell = partial( query_state, ['%WU', '%WD'] )
query_gross_upsell = partial( query_state, ['%WU', 'PWD'] )
# Why was I using %WD?  This could mean TWD
#query_downgrades   = partial( query_state, ['%WD'] )
query_downgrades   = partial( query_state, ['PWD'] )
query_upsell_and_newbiz     = partial( query_state, ['%WP', '%WU'] )

query_std          = partial( query_product_state, ['CTP', '%WP'], ['development'] )           
query_pro          = partial( query_product_state, ['CTP', '%WP'], ['production'] )           

query_std_count    = partial( query_product_state, ['%WP'], ['development'] )           
query_pro_count    = partial( query_product_state, ['%WP'], ['production'] )           

# TODO query std_to_pro needs to know previous tier
#query_std_to_pro   = partial( query_product_state, ['PWU'],        ['production'] )           

query_std_newbiz   = partial( query_product_state, ['CTP', '%WP'], ['development'] )
#query_std_newbiz   = partial( query_product_state, ['%WP'], ['development'] )
query_std_upsell   = partial( query_product_state, ['%WU'], ['development'] )
query_pro_newbiz   = partial( query_product_state, ['CTP', '%WP'], ['production'] )
#query_pro_newbiz   = partial( query_product_state, ['%WP'], ['production'] )
query_pro_upsell   = partial( query_product_state, ['%WU'], ['production'] )

def _mrr( start, end ):
    bucket = request.args.get( 'bucketed', 'quarter' )
    owners = QueryOwners( ['CTP', '%WP', '%WU'], start, end, owners=None ).bucketed( bucket )

    # This will essentially zero any periods that do not exist but are in our
    # time range of the other series
    pset = BucketedList.period_set( *owners.values() )
    map( lambda bl: bl.fill_missing_periods( pset ), owners.values() )

    # Used as a map across bucketed lists to sum each period
#    sum_to_rate = partial( sum_delta, 'trate' )
    sum_rate_delta= partial( sum_delta, 'trate', 'frate' )
#    states = partial( map, lambda x: x[1] ) 

    series = []
    for name in owners:
        bucketed_list = owners[name]
        bucketed_list.period_map( sum_rate_delta )
#        bucketed_list.period_map( states )
#        bucketed_list.period_map( sum_rate_change )
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
        'salesdash/currencybarchart.html', 
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
    
    bucketed_lists = OrderedDict((
        ('newbiz',  sum_newbiz),
        ('upsell',  sum_upsell),
    ))

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
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api_new_biz_plus_upsell' ),
            start=start, 
            end=end 
    )


def _downgrades_plus_churn( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    downgrade      = query_downgrades( start, end )
    sum_downgrades = bucket_func( Timebucket( downgrade, 'updated' ) )()
    
    churn          = query_lostbiz( start, end )
    sum_churn      = bucket_func( Timebucket( churn, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('churn',     sum_churn),
        ('downgrade', sum_downgrades),
    ))

    def negate( entry ):
        return entry * 1

    # Make all bucketed list contain a single value summation of their rate change
    for bl in bucketed_lists.values():
        bl.period_map( sum_rate_change )
        # Negate the numbers
        bl.period_map( lambda x: x*-1 )

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

@blueprint.route( '/apiv1/downgrades+churn' )
def api_downgrades_plus_churn():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _downgrades_plus_churn( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/downgrades+churn' )
def downgrades_plus_churn():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _downgrades_plus_churn( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api_downgrades_plus_churn' ),
            start=start, 
            end=end 
    )

def _downgrades_plus_churn_count( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    downgrade      = query_downgrades( start, end )
    tb_downgrades = bucket_func( Timebucket( downgrade, 'updated' ) )()
    
    churn          = query_lostbiz( start, end )
    tb_churn      = bucket_func( Timebucket( churn, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('churn',     tb_churn),
        ('downgrade', tb_downgrades),
    ))
    
    def counts( alist ):
        return sum( 1 for entry in alist )

    # Make all bucketed list contain a single value summation of their rate change
    for bl in bucketed_lists.values():
        bl.period_map( counts )

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

@blueprint.route( '/apiv1/downgrades+churn-count' )
def api_downgrades_plus_churn_count():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _downgrades_plus_churn_count( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/downgrades+churn-count' )
def downgrades_plus_churn_count():
    datasource = _downgrades_plus_churn_count

    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = datasource( start, end )
    return render_template( 
            'salesdash/barchart.html', 
            series=series, 
            data_url=url_for( '.api{}'.format( datasource.__name__ )  ),
            start=start, 
            end=end 
    )

def _paid_account_count( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    std      = query_std_count( start, end )
    tb_std   = bucket_func( Timebucket( std, 'updated' ) )()
    
    pro      = query_pro_count( start, end )
    tb_pro   = bucket_func( Timebucket( pro, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('standard', tb_std),
        ('pro',      tb_pro),
    ))
    
    def counts( alist ):
        return sum( 1 for entry in alist )

    # Make all bucketed list contain a single value summation of their rate change
    for bl in bucketed_lists.values():
        bl.period_map( counts )

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

@blueprint.route( '/apiv1/paid-account-count' )
def api_paid_account_count():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _paid_account_count( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/paid-account-count' )
def paid_account_count():
    datasource = _paid_account_count

    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = datasource( start, end )
    return render_template( 
            'salesdash/barchart.html', 
            series=series, 
            data_url=url_for( '.api{}'.format( datasource.__name__ )  ),
            start=start, 
            end=end 
    )


def _product_mrr( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    std_newbiz     = query_std_newbiz( start, end )
    std_sum_newbiz = bucket_func( Timebucket( std_newbiz, 'updated' ) )()
    
    std_upsell     = query_std_upsell( start, end )
    std_sum_upsell = bucket_func( Timebucket( std_upsell, 'updated' ) )()
    
    pro_newbiz     = query_pro_newbiz( start, end )
    pro_sum_newbiz = bucket_func( Timebucket( pro_newbiz, 'updated' ) )()
    
    pro_upsell     = query_pro_upsell( start, end )
    pro_sum_upsell = bucket_func( Timebucket( pro_upsell, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('dev newbiz',  std_sum_newbiz), 
        ('dev upsell',  std_sum_upsell), 
        ('pro newbiz',  pro_sum_newbiz),
        ('pro upsell',  pro_sum_upsell), 
    ))

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

@blueprint.route( '/apiv1/product-mrr' )
def api_product_mrr():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _product_mrr( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/product-mrr' )
def product_mrr():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _product_mrr( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api_product_mrr' ),
            start=start, 
            end=end 
    )


def _average_deal_size( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    newbiz     = query_newbiz( start, end )
    avg_newbiz = bucket_func( Timebucket( newbiz, 'updated' ) )()
    
    upsell     = query_upsell( start, end )
    avg_upsell = bucket_func( Timebucket( upsell, 'updated' ) )()
    
    bucketed_lists = OrderedDict((
        ('avg acquisition',  avg_newbiz), 
        ('avg growth',       avg_upsell), 
    ))
    
    # Zero out any bucketed timeperiod that does not have a key that the other bucketed periods do
    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    def average( alist ):
        # Make sure that there is at least some kind of positive movement
        culled_list = [item for item in alist if item.rate_delta > 0 ]
        num_items = len( culled_list )
        if num_items != 0:
            avg = reduce( lambda acc, val: acc + val.rate_delta, culled_list, 0 ) / float( num_items )
        else:
            avg = 0
        return avg

    # Caluculate the average deal size and mutate each bucket
    for bl in bucketed_lists.values():
        bl.period_map( average )

    series = []

    for name, bl in bucketed_lists.items():
        series.append({
            'key'    : name,
            'values' : [ (key, bl[key]) for key in sorted( bl ) ],
        })

    return series


@blueprint.route( '/apiv1/avg-deal-size' )
def api_average_deal_size():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _average_deal_size( start, end )
    return jsonify( {'series':series} )


@blueprint.route( '/avg-deal-size' )
def average_deal_size():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _average_deal_size( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api_average_deal_size' ),
            start=start, 
            end=end 
    )

def _average_deal_size_combined( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    all_paid   = query_upsell_and_newbiz( start, end )
    avg_all_paid = bucket_func( Timebucket( all_paid, 'updated' ) )()
    
    bucketed_lists = OrderedDict((
        ('ADS',  avg_all_paid), 
    ))
    
    # Zero out any bucketed timeperiod that does not have a key that the other bucketed periods do
    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    def average( alist ):
        # Make sure that there is at least some kind of positive movement
        culled_list = [item for item in alist if item.rate_delta > 0 ]
        num_items = len( culled_list )
        if num_items != 0:
            avg = reduce( lambda acc, val: acc + val.rate_delta, culled_list, 0 ) / float( num_items )
        else:
            avg = 0
        return avg

    # Caluculate the average deal size and mutate each bucket
    for bl in bucketed_lists.values():
        bl.period_map( average )

    series = []

    for name, bl in bucketed_lists.items():
        series.append({
            'key'    : name,
            'values' : [ (key, bl[key]) for key in sorted( bl ) ],
        })

    return series


@blueprint.route( '/apiv1/avg-deal-size-combined' )
def api_average_deal_size_combined():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _average_deal_size_combined( start, end )
    return jsonify( {'series':series} )


@blueprint.route( '/avg-deal-size-combined' )
def average_deal_size_combined():
    datasource = _average_deal_size_combined
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = datasource( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api{}'.format( datasource.__name__ ) ),
            start=start, 
            end=end 
    )

def _product_average_deal_size( start, end ):

    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    std     = query_std( start, end )
    avg_std = bucket_func( Timebucket( std, 'updated' ) )()
    
    pro     = query_pro( start, end )
    avg_pro = bucket_func( Timebucket( pro, 'updated' ) )()
    
    bucketed_lists = OrderedDict((
        ('avg standard',  avg_std), 
        ('avg pro',       avg_pro), 
    ))
    
    # Zero out any bucketed timeperiod that does not have a key that the other bucketed periods do
    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    def average( alist ):
        # Make sure that there is at least some kind of positive movement
        culled_list = [item for item in alist if item.rate_delta > 0 ]
        num_items = len( culled_list )
        if num_items != 0:
            avg = reduce( lambda acc, val: acc + val.rate_delta, culled_list, 0 ) / float( num_items )
        else:
            avg = 0
        return avg

    # Caluculate the average deal size and mutate each bucket
    for bl in bucketed_lists.values():
        bl.period_map( average )

    series = []

    for name, bl in bucketed_lists.items():
        series.append({
            'key'    : name,
            'values' : [ (key, bl[key]) for key in sorted( bl ) ],
        })

    return series


@blueprint.route( '/apiv1/product-avg-deal-size' )
def api_product_average_deal_size():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = _product_average_deal_size( start, end )
    return jsonify( {'series':series} )


@blueprint.route( '/product-avg-deal-size' )
def product_average_deal_size():
    datasource = _product_average_deal_size
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    series = datasource( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
            series=series, 
            data_url=url_for( '.api{}'.format( datasource.__name__ ) ),
            start=start, 
            end=end 
    )

# TODO - This needs to Query the ENTIRE dataset and set the accumulator prior to
def _net_value( start, end ):
    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )
    
    prev      = query_state( ['CTP', '%WP', '%WD', '%WU', '%WF'], datetime( 2008, 1, 1 ), start, g2only=True )
    prev_acc  = reduce( lambda pacc, val: pacc + val.rate_delta, prev, 0 )

    value     = query_state( ['CTP', '%WP', '%WD', '%WU', '%WF'], start, end )
    net_value = bucket_func( Timebucket( value, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('net value',  net_value), 
    ))

    def accumulated_net( bl, accumulated=0 ):
        period_keys = sorted( bl.periods )
        for period in period_keys:
            bl[period] = reduce( lambda pacc, val: pacc + val.rate_delta, bl[period], accumulated )
            accumulated = bl[period]
    
    # Mutate the bucketedlist componenets
    for bl in bucketed_lists.values():
        accumulated_net( bl, accumulated=prev_acc )
    
    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    series = []

    for name, bl in bucketed_lists.items():
        series.append({
            'key'    : name,
            'values' : [ (key, bl[key]) for key in sorted( bl ) ],
        })

    return series


@blueprint.route( '/apiv1/net-value' )
def api_net_value():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )
    
    series = _net_value( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/net-value' )
def net_value():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )
    
    series = _net_value( start, end )
    return render_template( 
            'salesdash/currencybarchart.html', 
#            'salesdash/barandlinechart.html', 
            series=series, 
            data_url=url_for( '.api_net_value' ),
            start=start, 
            end=end 
    )

def _conversion_rate( start, end ):
    bucket_func = attrgetter( request.args.get( 'bucketed', 'quarter' ) )

    trials    = query_state( ['SUT'], start, end )
    bl_trials = bucket_func( Timebucket( trials, 'updated' ) )()

    converted    = query_state( ['TWP', 'FWP'], start, end )
    bl_converted = bucket_func( Timebucket( converted, 'updated' ) )()
   
    # Segment by Standard/Pro
    dev_conv    = query_product_state( [ 'TWP', 'FWP'], ['development'], start, end )
    bl_dev_conv = bucket_func( Timebucket( dev_conv, 'updated' ) )()
    
    pro_conv    = query_product_state( [ 'TWP', 'FWP'], ['production'], start, end )
    bl_pro_conv = bucket_func( Timebucket( pro_conv, 'updated' ) )()

    bucketed_lists = OrderedDict((
        ('trial',  bl_trials), 
        ('conversions',  bl_converted), 
        ('dev conversion',  bl_dev_conv), 
        ('pro conversion',  bl_pro_conv), 
    ))

    pset = BucketedList.period_set( *(bucketed_lists.values()) )
    map( lambda bl: bl.fill_missing_periods( pset ), bucketed_lists.values() )

    def counts( alist ):
        return sum( 1 for entry in alist )

    # Mutate the bucketedlist componenets
    for bl in bucketed_lists.values():
        bl.period_map( counts )

    series = []
    series.append({
        'key'    : 'trials',
        'values' : [ {'x':i, 'y':bl_trials[key]} for i, key in enumerate( sorted( bl_trials ) ) ],
        'labels' : [ key for key in sorted( bl ) ],
        'bar'    : True,
    })
    
    for name, bl in OrderedDict( bucketed_lists.items()[-3:] ).items():
        # Calculate the conversion rate
        for key in bl:
            if bl_trials[key]:
                bl[key] = float( bl.get(key, 0) ) / bl_trials[key]
            else:
                bl[key] = float( bl.get(key, 0) ) 

        series.append({
            'key'    : name,
            'values' : [ {'x':i, 'y':bl[key]} for i, key in enumerate( sorted( bl ) ) ],
            'labels' : [ key for key in sorted( bl ) ],
        })

    return series


@blueprint.route( '/apiv1/conversion-rate' )
def api_conversion_rate():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )
    
    series = _conversion_rate( start, end )
    return jsonify( {'series':series} )

@blueprint.route( '/conversion-rate' )
def conversion_rate():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )
    
    series = _conversion_rate( start, end )
    return render_template( 
            'salesdash/barandlinechart.html', 
            series=series, 
            data_url=url_for( '.api_conversion_rate' ),
            start=start, 
            end=end 
    )


@blueprint.route( '/overview' )
def overview():
    
    urls = [ {'name':name, 'url':url_for( funcname ) } 
             for name, funcname in sorted([
                ( 'Conversion Rate', '.conversion_rate' ),
#                ( 'Running Net Value', '.net_value'),
                # Numbers slightly off.  Sames as other ADS?
                ( 'ADS: Acquisition vs Growth', '.average_deal_size'),
                # Number off... monthly vs annual?
                ( 'ADS: Combined', '.average_deal_size_combined'),
                # Numbers seem off.  Is annual counted as annual and not monthly?
                ( 'ADS: Product', '.product_average_deal_size'),
                # Why does CTP make this closer to the yearly we expect?
                ( 'MRR: Owner', '.mrr' ),
                ( 'MRR: Sale Type', '.new_biz_plus_upsell') ,
                ( 'MRR: Product', '.product_mrr' ),
                ( 'Downgrades and Churn Amount', '.downgrades_plus_churn' ),
                ( 'Downgrades and Churn Count', '.downgrades_plus_churn_count' ),
                ( 'New Deal Transaction Count', '.paid_account_count' ),
            ], key=itemgetter( 0 ) )
    ]

    return render_template( 'salesdash/overview.html', urls=urls )

@blueprint.route( '/' )
@blueprint.route( '/salesdash' )
def salesdash():
    start = iso8601_to_dt( request.args.get( 'start', DEFAULT_START) )
    end   = iso8601_to_dt( request.args.get( 'end', DEFAULT_END) )

    return render_template( 
            'salesdash/dashboard.html', 
            start=start, 
            end=end,
            upsell_newbiz_data_url=url_for( '.api_new_biz_plus_upsell' ),
            mrr_data_url=url_for( '.api_mrr' ),
            product_mrr_data_url=url_for( '.api_product_mrr' ),
    )
