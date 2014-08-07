"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 08/06/2014
"
"
"""
from datetime           import datetime
import time

from flask              import Blueprint, render_template, request
from law.util.adb       import VolumeAccepted, VolumeDropped, Account, session_context
from scry.preprocessing import ChargedVolume, ChargedVolumeDropped

cb_config = ('localhost', 7999, 0)
cb_staging = ('localhost', 7998, 0)

blueprint = Blueprint( 'volumes', __name__, 
                        template_folder = 'templates',
                        static_folder   = 'static' )

def to_js_time( d ):
    return int(time.mktime(d.timetuple())) * 1000 + 1

def ts_to_date( date ):
    if date:
        return datetime.strptime( date, '%Y-%m-%d' )
    return None

def qtime( model, subd, start, end ):
    with session_context() as s:
        subq = s.query( Account )\
                .filter( Account.subdomain == subd )\
                .subquery()

        q = s.query( model )\
            .filter( model.acct_id == subq.c.acct_id )\
            .order_by( model.date )

        if start:
            q = q.filter( model.date >= start )
        if end:
            q = q.filter( model.date <= end )

        res = q.all()

        return {item.date:item.bytes for item in res}

@blueprint.route( '/crystalball/chart' )
def cb_volume_graph():
    cid   = request.args['cid']
    start = datetime.strptime( request.args['start'], '%Y-%m-%d' )
    end   = request.args.get('end', 'now') 

    if request.args.get('env') == 'chipper':
        cv = ChargedVolume( *cb_staging )
        cvd = ChargedVolumeDropped( *cb_staging )
    else:
        cv = ChargedVolume( *cb_config )
        cvd = ChargedVolumeDropped( *cb_config )

    avols = cv.timeperiod( start=start, end=end, bucketed='day' ).customer( cid )
    dvols = cvd.timeperiod( start=start, end=end, bucketed='day' ).customer( cid )
    
    keys = sorted( avols.keys() )
    series = []
    series.append( ['allowed'] + [avols[key] for key in keys] )
    series.append( ['dropped'] + [dvols[key] for key in keys] )
    series.append( ['total'] + [(avols[key] + dvols[key]) for key in keys] )
    keys = [key.strftime( '%Y-%m-%d' ) for key in keys]
    
    return render_template( 'chart.html', keys=keys, series=series )

@blueprint.route( '/chart' )
def volume_graph():
    subd  = request.args['subdomain']
    start = ts_to_date( request.args.get( 'start' ) )
    end   = ts_to_date( request.args.get( 'end' ) )


    avols = qtime( VolumeAccepted, subd, start, end )
    dvols = qtime( VolumeDropped, subd, start, end )
    
    keys = sorted( avols.keys() )
    series = []
    series.append( ['allowed'] + [avols[key] for key in keys] )
    series.append( ['dropped'] + [dvols.get( key, 0 ) for key in keys] )
    keys = [key.strftime( '%Y-%m-%d' ) for key in keys]
    
    return render_template( 'chart.html', keys=keys, series=series )

@blueprint.route( '/chart/nvd3' )
def volume_graph_nvd3():
    subd  = request.args['subdomain']
    start = ts_to_date( request.args.get( 'start' ) )
    end   = ts_to_date( request.args.get( 'end' ) )

    avols = qtime( VolumeAccepted, subd, start, end )
    dvols = qtime( VolumeDropped, subd, start, end )
    
    keys = sorted( avols.keys() )
    series = []
    series.append({ 
        'key':'allowed', 
        'values':[(to_js_time( key ), avols[key]) for key in keys] 
    })
    series.append({ 
        'key':'dropped', 
        'values':[(to_js_time( key ), dvols.get( key, 0 )) for key in keys] 
    })
    
    return render_template( 'area_chart.html', series=series )
