"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from flask                import Blueprint, render_template, request, url_for
from law.web.touchbiz     import rest

blueprint = Blueprint( 'touchbiz', __name__, 
                        template_folder = 'templates',
                        static_folder   = '../static' )

@blueprint.route( '/<string:subd>/table' )
def table(subd):
    data = rest.history( subd )
    return render_template( 'touchbiz/touchbiz_table.html', **{
        'data': data,
        'subdomain':subd,
    })

@blueprint.route( '/<string:subd>/latest' )
def latest( subd ):
    return render_template( 'touchbiz/touchbiz_latest.html', **{
        'new_url': url_for( 'rest.touchbiz.new', subd=subd ),
    })
