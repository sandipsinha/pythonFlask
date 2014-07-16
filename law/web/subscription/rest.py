"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/15/2014
"
"""
from flask              import Blueprint, jsonify, request
from law.util.adb       import session_context, AccountState

blueprint = Blueprint( 'rest.subscription', __name__ )

@blueprint.route( '/subdomain/<string:subd>' )
def subd_acct_history( subd ):
    with session_context() as s:
        subs = s.query( AccountState )\
               .filter( AccountState.subdomain == subd )\
               .order_by( AccountState.updated.desc() )\
               .all()

        fsubs = [{ 'Date':r.updated,
                   'Rate':'${:.2f}/mo'.format( r.trate ),
                   'Tier':getattr( r.tplan, 'name', 'custom' ),
                   'Volume':'{:.2f}'.format( r.tGB ),
                   'Retention':r.tDays}
                for r in subs ]

        return jsonify({ 'data':fsubs })
