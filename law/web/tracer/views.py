
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
from law.util.queries    import query_user_state
from law.web.tracer    import rest
from datetime           import datetime



blueprint = Blueprint( 'tracer', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )



@blueprint.route( '/', methods=['GET'])
def display_tracer_data():
    return render_template('tracer/actualcontent.html' )










