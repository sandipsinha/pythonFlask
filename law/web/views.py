"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/22/2014
"
" General top-level LAW pages
"
"""
from flask              import Blueprint, render_template
from flask.ext.security import login_required


blueprint = Blueprint( 'root', __name__ )

@blueprint.route( '/' )
@blueprint.route( '/index' )
def index():
    return render_template( 'index.html' )

@blueprint.route( '/login_check' )
@login_required
def login_check():
    return 'Yep... you are logged in'
