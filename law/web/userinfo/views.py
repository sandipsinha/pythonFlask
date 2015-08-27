
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
from law.util.queries    import query_user_state



blueprint = Blueprint( 'userinfo', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )



@blueprint.route( '/<string:subd>', methods=['GET'])
def display_user_info(subd):
    #subd= request.args['subdomain']
    #import ipdb;ipdb.set_trace()
    return render_template('userinfo/displayuser.html', grid2=subd)

@blueprint.route( '/logindata', methods=['GET', 'POST'] )
def get_user_data():
    subd = request.form.get('subdomain',' ')

    users = query_user_state(subd)
    recid = 0
    userlist = []
    userqueue = {}
    for row in users:
        userdat = {}
        recid += 1
        userdat['recid'] = recid
        userdat['name'] = ' '
        if row.Users.first_name > " " and row.Users.last_name > " ":
            userdat['name'] = row.Users.first_name + ' ,' + row.Users.last_name
        userdat['userid'] = int(row.Users.user_id)
        userdat['username'] = row.Users.username
        userdat['email'] = row.Users.email
        userdat['Number_Of_Logins'] = row.Number_Of_Logins
        userdat['Last_Login'] = str(row.Last_Login.strftime('%Y/%m/%d'))
        userlist.append(userdat)
    if recid > 0:
        userqueue['status'] = 'success'
        userqueue['total'] = recid
        userqueue['records'] = userlist
    return json.dumps(userqueue)


