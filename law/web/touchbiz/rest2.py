"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from functools             import wraps
from datetime              import datetime, date, timedelta

from flask                 import Blueprint, jsonify, request, url_for, json
from flask.ext.login       import current_user
from law.util.touchbizdb   import (session_context as tb_session, loader as tb_loader, 
                                  Touchbiz, Session )
from law.util              import touchbiz
from law.util.timeutil     import iso8601_to_dt
from sqlalchemy            import and_, or_, not_, func, distinct
from sqlalchemy.sql import label

blueprint = Blueprint( 'rest2.touchbiz', __name__ )
DEFAULT_OWNER = 'loggly'
TIMEFORMAT = '%Y-%m-%d %H:%M:%S'

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


@blueprint.route( '/subdomain/<string:subd>', methods=['GET', 'POST'] )
def history( subd ):
    #subd = request.form.get('subdomain',' ')
    rows = [ touchbiz.flatten( row )._asdict() for row in touchbiz.touchbiz_by_account( subd )]
    rows = sorted(rows,key=lambda x:x['created'].strftime(TIMEFORMAT) if isinstance(x['created'],datetime)   else '9999-99-99-9999', reverse=True)
    recid = 0
    userlist = []
    userqueue = {}

    for row in rows:
        userdat = {}
        recid += 1
        userdat['recid'] = recid
        userdat['plan_type'] = row.get('plan_type')
        userdat['payment_method'] = row.get('payment_method')
        userdat['period'] = row.get('period')
        if row.get('created') != 'pending':
            userdat['created'] = row.get('created').strftime(TIMEFORMAT)
        else:
            userdat['created'] = 'pending'
        userdat['rate'] = row.get('rate') if row.get('rate') is not None else 0
        userdat['tier'] = row.get('tier') if row.get('tier') is not None else ''
        userdat['retention'] = row.get('retention') if row.get('retention') is not None else ''
        userdat['volume'] = int(row.get('volume')) if int(row.get('volume')) is not None else 0
        sales_id = touchbiz.get_sales_rep_id(row.get('owner'))
        userdat['owner'] = row.get('owner')    if row.get('owner') is not None else 'loggly'
        userlist.append(userdat)
    if recid > 0:
        userqueue['status'] = 'success'
        userqueue['total'] = recid
        userqueue['records'] = userlist

    return  json.dumps(userqueue)

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
            plan_type      = request.form['plan_type'],
            tier           = request.form['tier'].lower(),
            retention      = request.form['retention'],
            volume         = request.form['volume'],
            sub_rate       = request.form['sub_rate'],
            payment_method = request.form['payment_method'],
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
                              Touchbiz.tier, Touchbiz.sales_rep_id, Touchbiz.modified, Touchbiz.plan_type, Touchbiz.payment_method ).\
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



@blueprint.route('/subdomain/edit', methods=['POST','GET'])
def change_touchbiz():
    rows = json.loads(request.data)
    tbdata = rows.get('meta')
    changes = tbdata.get('changes')
    createdTime = datetime.strptime(tbdata.get('created'),TIMEFORMAT)
    subd = rows.get('subdomain')
    sales_id = touchbiz.get_sales_rep_id(changes.get('owner')) if changes.get('owner') is not None \
        else touchbiz.get_sales_rep_id(tbdata.get('owner'))
    import ipdb;ipdb.set_trace()
    if changes.get('owner') != DEFAULT_OWNER:
         with tb_session() as s:
            entry = Touchbiz(
                acct_id        = touchbiz.acct_id_for_subdomain(subd),
                sales_rep_id   = sales_id,
                created        = createdTime - timedelta(seconds=2),
                modified       = datetime.now(),
                plan_type      = tbdata.get('plan_type') ,
                tier           = changes.get('tier').lower() if changes.get('tier') else tbdata.get('tier') ,
                retention      = changes.get('retention') if changes.get('retention') else tbdata.get('retention'),
                volume         = changes.get('volume') if changes.get('volume') else tbdata.get('volume'),
                sub_rate       = changes.get('rate') if changes.get('rate') else tbdata.get('rate') ,
            )
            s.merge( entry )

         return json.dumps({'status':'200','success':True})
    else:
        return json.dumps({'status':'400','success':False})


