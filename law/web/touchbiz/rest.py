"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from functools             import wraps
from datetime              import datetime

from flask                 import Blueprint, jsonify, request, url_for
from flask.ext.login       import current_user
from law.util.touchbizdb   import (session_context as tb_session, loader as tb_loader, 
                                  Touchbiz, SalesReps )
from law.util              import touchbiz
from law.util.timeutil     import iso8601_to_dt

blueprint = Blueprint( 'rest.touchbiz', __name__ )

def rest_endpoint( route, methods=None ):
    def rest_endpoint_wrap( func ):
        """ A decorator that binds the decorated function to
        an enpoint.  This will jsonify the results automatically
        and pack them in {'data':<results>} json property.
        If this function is not called via a REST endpiont (ala via
        a module import) then it will not jsonify the results.
        """
        @blueprint.route( route, methods=methods )
        @wraps( func )
        def wrapped( *args, **kwargs ):
            res = func( *args, **kwargs )
            try:
                # Matching the built url with the request means that it was
                # it was a direct call to this rest endpoint
                if request.path == url_for( '{}.{}'.format( blueprint.name, func.func_name ), **kwargs ):
                    return jsonify({'data':res})
                else:
                    return res
            # URL build error encountered.  Request did not match our endpoint
            except Exception:
                return res

        return wrapped
    return rest_endpoint_wrap


@rest_endpoint( '/subdomain/<string:subd>' )
def history( subd ):
#    columns = ['updated', 'tRate', 'tPlan.name', 'tGB', 'tDays', 'owner.sfdc_alias', 'stage.name']
#    column_map = {'tPlan.name':'Tier', 'owner.sfdc_alias':'owner', 'stage.name':'stage'}
#    rows = [ dict( pair ) for pair in touchbiz.tuplify( 
#                                        touchbiz.touchbiz_by_account( subd ), 
#                                        columns, 
#                                        column_map )]
    rows = [ touchbiz.flatten( row )._asdict() for row in touchbiz.touchbiz_by_account( subd )]
    return rows

@rest_endpoint( '/subdomain/<string:subd>/latest', methods=['POST','PUT'] )
def latest( subd ):
    latest = touchbiz.flatten( touchbiz.touchbiz_by_account( subd )[-1] )._asdict()

    return latest


@rest_endpoint( '/subdomain/<string:subd>/new', methods=['POST','PUT'] )
def new( subd ):

    acct_id  = touchbiz.acct_id_for_subdomain( subd )

    try:
        owner_id = touchbiz.owner_id( current_user.email )
    except:
        raise Exception( 'Unauthorized to add touchbiz entry.' )
    
    created  = iso8601_to_dt( request.form.get( 'created' ) ) if 'created' in request.form else datetime.today() 

    with tb_session() as s:
        entry = Touchbiz( 
            acct_id        = acct_id,
            sales_rep_id   = owner_id,
            created        = created,
            modified       = created,
            tier           = request.form['tier'],
            retention      = request.form['retention'],
            volume         = request.form['volume'],
            sub_rate       = request.form['sub_rate'],
            billing_period = request.form['billing_period'],
        )
        s.add( entry )

    latest = touchbiz.flatten( touchbiz.touchbiz_by_account( subd )[-1] )._asdict()

    return {
        'status':'success',
        'new'   : latest,
    }

#@blueprint.route( '/subdomain/<string:subd>' )
#def touchbiz_by_account( subd ):
#    rows = history( subd )
#    return jsonify({ 'data':rows })
