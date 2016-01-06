"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
" Last Updated: 07/22/2014
"
" All things authentication related.  
"
" Uses flask-security extension: https://pythonhosted.org/Flask-Security
"
"""

"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
from werkzeug             import secure_filename
from law                  import config
import os




blueprint = Blueprint( 'fileupload', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )



@blueprint.route( '/', methods=['GET','POST'])
def fileupld():
    return render_template('tracer/actualcontent.html' )

# Get the name of the uploaded file
#     import ipdb;ipdb.set_trace()
#     file = request.files['file']
#     # Check if the file is one of the allowed types/extensions
#     if file :
#         # Make the filename safe, remove unsupported chars
#         filename = secure_filename(file.filename)
#         # Move the file form the temporal folder to
#         # the upload folder we setup
#         file.save(os.path.join(config.get('UPLOAD_FOLDER',''), filename))
#         file_status = [{'upldstatus':'complete','name':filename}]
#         return json.dumps(file_status)

