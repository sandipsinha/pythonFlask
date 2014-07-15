"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/15/2014
"
"""
from flask              import Blueprint, jsonify, request
from util.adb           import session_context, AAWSC

blueprint = Blueprint( 'subscription', __name__ )


@blueprint.route( '/table' )
def subscription_table():
    raise NotImplementedError

@blueprint.route( '/subdomain/<string:subd>' )
def subscription_history( subd ):
    with session_context() as s:
        subs = s.query( AAWSC )\
               .filter( AAWSC.subdomain == subd )\
               .order_by( AAWSC.updated.desc )\
               .all()

        fsubs = [{ 'Date':r.updated,
                   'Rate':r.trate, 
                   'Tier':r.tPlan.name, 
                   'Volume':r.tGB, 
                   'Retention':r.tDays}
                for r in subs ]

        return jsonify({ 'data':fsubs })
