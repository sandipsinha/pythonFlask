
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
from law.util.queries    import get_cluster_names, get_cluster_details
from law.web.cluster    import rest



blueprint = Blueprint( 'cluster', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )



@blueprint.route( '/', methods=['GET'])
def display_cluster_data():
    clstrdata = get_cluster_names('%')
    return render_template('cluster/displaypage.html',option_list = clstrdata )














