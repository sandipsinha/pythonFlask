__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_tracer_bullet, get_cluster_names, query_tracer_percentile
from datetime           import datetime



blueprint = Blueprint( 'rest.tracer', __name__ )

@blueprint.route( '/tracergrid/', methods = ['GET', 'POST'])
@blueprint.route( '/tracergrid/<string:sdate>/<string:scluster>', methods = ['GET', 'POST'])
def tracer_data(sdate=None, scluster=None):
    datechosen = datetime.now() if (sdate == '*' or sdate is None) else datetime.strptime(sdate,'%Y-%m-%d %H:%M:%S')
    datechosen =  datechosen.replace(microsecond=0)
    clusterchosen = '*' if scluster is None else scluster
    tracers = query_tracer_bullet(datechosen, clusterchosen)
    clientdict = {}
    clientdict['bullet'] = tracers
    
    recid = 0
    tracerlist = []
    tracerqueue = {}
    for row in tracers:
        tracerdat = {}
        recid += 1
        tracerdat['recid'] = recid
        tracerdat['cluster'] = row.newcluster
        tracerdat['status'] = row.status
        tracerdat['run_start_time'] = row.run_start_time
        tracerdat['run_end_time'] = row.run_end_time
        tracerdat['run_secs'] = row.run_secs
        tracerdat['uid'] = row.uid
        if clusterchosen != '*' and row.newcluster !=  clusterchosen:
            pass
        else:
            tracerlist.append(tracerdat)
    if recid > 0:
        tracerqueue['status'] = 'success'
        tracerqueue['total'] = recid
        tracerqueue['records'] = tracerlist
    return json.dumps(tracerqueue)

@blueprint.route( '/tracerpercentile/', methods = ['GET', 'POST'])
def tracer_percentile():
    datas = request.json
    datechosen = datetime.now() if len(datas['Date']) == 0 else datetime.strptime(datas['Date'],'%Y-%m-%d %H:%M:%S')
    datechosen =  datechosen.replace(microsecond=0)
    datecond = datechosen.date()
    clusterchosen = '*' if len(datas['Cluster']) == 0 else datas['Cluster']

    tiledata = query_tracer_percentile(datecond, clusterchosen)
    graphlist = []
    for rows in tiledata:
        graphitem = {}

        graphitem['cluster']     = rows.repcluster
        graphitem['95th_perc']   = rows.ninty_five
        graphitem['98th_perc']   = rows.ninty_eight
        graphitem['99th_perc']   = rows.ninty_nine
        graphitem['98th_perc']   = rows.ninty_eight
        graphitem['min_latency'] = rows.min_latency
        graphitem['max_latency'] = rows.max_latency
        graphitem['pcnt_LT30']   = rows.pcnt_LT30
        graphitem['start_date']  = rows.start_date.strftime('%Y-%m-%d')
        if clusterchosen != '*' and clusterchosen != rows.repcluster:
            pass
        else:
            graphlist.append(graphitem)

    return json.dumps(graphlist)

@blueprint.route( '/getclusters', methods=['GET'] )
def autocomplete():
    bs = request.args.get('term', '')
    clsdtl = get_cluster_names(bs)
    rowlist = clsdtl.fetchall()
    clsnames = [items[0] + '|' + items[1]  for items in rowlist]
    return json.dumps(clsnames)