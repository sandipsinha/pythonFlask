"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime, timedelta
import random

from flask               import Blueprint, render_template, request
from law.util.conversion import to_js_time
from law.util.timeutil   import Timebucket

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

#def get_segmentation( request ):
#    segments = {
#        'quarter': timebucket.:quarterly,
#        'year'   : timebucket.yearly,
#        'month'  : timebucket.monthly,
#        'week'   : timebucket.weekly,
#        'day'    : timebucket.daily,
#    }
#    return segments[ request.args.get( 'segment_by' ) ]

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

@blueprint.route( '/newbiz+upsell' )
def new_biz_plus_upsell():
    segement = get_seqmentation()

