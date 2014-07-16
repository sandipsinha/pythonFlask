"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/15/2014
"
"""
from flask import Blueprint, request, render_template, url_for

blueprint = Blueprint( 'subscription', __name__, 
                        template_folder = '../templates',
                        static_folder   = '../static' )

@blueprint.route( '/table' )
def subscription_table():
    subd = request.args['subdomain']
    return render_template( 'subscription_table.html', **{
        'url': url_for( 'rest.subscription.subd_acct_history', subd=subd)
    })

@blueprint.route( '/' )
def index():
    return 'hello'
