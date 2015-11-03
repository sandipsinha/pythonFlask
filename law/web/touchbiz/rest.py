"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from functools             import wraps
from datetime              import datetime

from flask                 import Blueprint, jsonify, request, url_for, json
from flask.ext.login       import current_user
from law.util.touchbizdb   import (session_context as tb_session, loader as tb_loader, 
                                  Touchbiz, Session )
from law.util              import touchbiz
from law.util.timeutil     import iso8601_to_dt
from sqlalchemy         import and_, or_, not_, func, distinct
from sqlalchemy.sql import label

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
            tier           = request.form['tier'].lower(),
            retention      = request.form['retention'],
            volume         = request.form['volume'],
            sub_rate       = request.form['sub_rate'],
            billing_period = request.form['billing_period'].lower(),
        )
        s.add( entry )

    latest = touchbiz.flatten( touchbiz.touchbiz_by_account( subd )[-1] )._asdict()

    return {
        'status':'success',
        'new'   : latest,
    }

def get_tb_rows(acctid, created):
    #import ipdb;ipdb.set_trace()
    if created != 'pending':
        createdtime = touchbiz.localize_time(created)
        try:
            session = Session()
            max_date = session.query(func.max(Touchbiz.created)).filter(and_(Touchbiz.acct_id == acctid, Touchbiz.created < createdtime))
            q=session.query(Touchbiz).filter(and_(Touchbiz.acct_id == acctid, Touchbiz.created == max_date)).one()
            return q
        except Exception as e:
            print e
            return None
    else:
        try:
            with tb_session() as s:
                q = s.query(label('created',func.max(Touchbiz.created)), Touchbiz.billing_period,
                              Touchbiz.sub_rate, Touchbiz.retention, Touchbiz.tier, Touchbiz.volume,
                              Touchbiz.tier, Touchbiz.sales_rep_id, Touchbiz.modified).\
                    filter(and_(Touchbiz.acct_id == acctid))\
                    .group_by(Touchbiz.acct_id).one()

            s.expunge_all()
            return q
        except Exception as e:
            return None


@blueprint.route( '/salesrepid', methods=['GET'] )
def autocomplete():
    bs = request.args.get('term', '')
    salesrep = touchbiz.get_sales_rep_details(bs)
    rowlist = salesrep.all()
    custacct = [items[0] + ',' + items[1] + '|' + items[2] + '|' + str(items[3])  for items in rowlist]
    return json.dumps(custacct)

