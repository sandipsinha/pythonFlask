__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_subd_from_cluster, get_subd_names, get_cluster_details



blueprint = Blueprint( 'rest.cluster', __name__ )


@blueprint.route( '/subdgrid/', methods = ['GET', 'POST'])
def get_subdomain_for_cluster():
    #import ipdb;ipdb.set_trace()
    cdata = request.form.get('cdata')
    subddata = query_subd_from_cluster(cdata)
    subdlist = []
    subdqueue = {}
    recid = 0
    for rows in subddata:
        griditem = {}
        recid += 1
        griditem['recid'] = recid
        griditem['subdomain']   = rows.subdomain
        griditem['acct_id']  = rows.acct_id
        griditem['cid']  = rows.cid
        subdlist.append(griditem)
    if recid > 0:
        subdqueue['status'] = 'success'
        subdqueue['total'] = recid
        subdqueue['records'] = subdlist

    return json.dumps(subdqueue)

@blueprint.route( '/getclstrdtls/', methods = ['GET', 'POST'])
def get_subdomain_to_cluster():
    cdata = request.args.get('term')
    #import ipdb;ipdb.set_trace()
    subdata = get_cluster_details(cdata)
    subdataformatted = subdata.cluster_type + '|' + str(subdata.cid) + '|' + str(subdata.acct_id)
    return json.dumps(subdataformatted)



@blueprint.route( '/getsubds', methods=['GET'] )
def autocomplete():
    #import ipdb;ipdb.set_trace()
    bs = request.args.get('term', '')
    clsdtl = get_subd_names(bs)
    rowlist = clsdtl.fetchall()
    subdnames = [items[0]  for items in rowlist]
    return json.dumps(subdnames)