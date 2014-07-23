"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/23/2014
"
"""
from flask              import Blueprint, jsonify, request
from flask.ext.security import login_required
from law.util.adb       import session_context, AccountState

blueprint = Blueprint( 'rest.subscription', __name__ )

def account_history( subd ):
    with session_context() as s:
        subs = s.query( AccountState )\
               .filter( AccountState.subdomain == subd )\
               .order_by( AccountState.updated.desc() )\
               .all()

        fsubs = [{ 'Date':r.updated,
                   'Rate':r.tRate,
                   'Tier':getattr( r.tPlan, 'name', 'custom' ),
                   'Volume':r.tGB,
                   'Retention':r.tDays}
                for r in subs ]

        return fsubs

@blueprint.route( '/subdomain/<string:subd>' )
def rest_account_history( subd ):
    return jsonify({ 'data':account_history( subd ) })
