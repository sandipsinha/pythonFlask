__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_client_state
from law.util.basics           import requires_auth


blueprint = Blueprint( 'rest.userinfo', __name__ )


@blueprint.route( '/sfdcapi/<string:subd>', methods = ['GET'])
@requires_auth
def account_history(subd ):
    clients = query_client_state(subd)
    clientdict = {}
    clientdict['subdomain'] = clients.subdomain
    clientdict['acct_id'] = clients.acct_id
    clientdict['rulescount'] = clients.rulescount
    clientdict['groupcount'] = clients.groupcount
    clientdict['usercount'] = clients.usercount
    js = json.dumps(clientdict)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
