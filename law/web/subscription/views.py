"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/23/2014
"
"""
from flask                import Blueprint, render_template, request
from law.web.subscription import rest

blueprint = Blueprint( 'subscription', __name__, 
                        template_folder = '../templates',
                        static_folder   = '../static' )

@blueprint.route( '/table' )
def subscription_table():
    subd = request.args['subdomain']
    data = rest.account_history( subd )
    return render_template( 'subscription_table.html', **{
        'data': data
    })


@blueprint.route( '/login_check' )
def index():
    return ''
