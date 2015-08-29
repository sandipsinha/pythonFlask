__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_client_state
from law.util           import requires_auth


blueprint = Blueprint( 'rest.userinfo', __name__ )

#@requires_auth
@blueprint.route( '/sfdcapi/<int:acctid>', methods = ['GET'])
def account_history(acctid ):
    client_id= acctid
    clients = query_client_state(client_id)
    clientdict = {}
    clientdict['acct_id'] = clients.acct_id
    clientdict['rulescount'] = clients.rulescount
    clientdict['groupcount'] = clients.groupcount
    clientdict['usercount'] = clients.usercount
    js = json.dumps(clientdict)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
