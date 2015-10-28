__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_tracer_bullet, get_cluster_names, query_tracer_percentile
from datetime           import datetime, timedelta



blueprint = Blueprint( 'rest.tracer', __name__ )

@blueprint.route( '/tracergrid/', methods = ['GET', 'POST'])
def tracer_data():
    fdate = request.form.get('fdate')
    tdate = request.form.get('tdate')
    scluster = request.form.get('cluster')
    tstype = request.form.get('tstype')
    endDate = datetime.now() if (tdate is None or len(tdate) == 0) else datetime.strptime(tdate,'%Y-%m-%d')
    if (len(fdate) == 0 and len(tdate) == 0):
        if len(tstype.strip()) == 0:
            dateDiff = timedelta(hours = 1)
        elif tstype == 'w':
            dateDiff = timedelta(weeks = 1)
        elif tstype == 'm':
            dateDiff = timedelta(weeks = 24)
        else:
            dateDiff = timedelta(hours = 1)

    fromDate = (endDate - dateDiff) if (fdate is None or len(fdate) == 0 and len(fdate) == 0) else datetime.strptime(fdate,'%Y-%m-%d')

    clusterchosen = '*' if (scluster is None or len(scluster) == 0) else scluster
    tracers = query_tracer_bullet(fromDate, endDate, clusterchosen)
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
    tstype = datas.get('tstype')
    tdate = datetime.now() if len(datas['tdate']) == 0 else datetime.strptime(datas['tdate'],'%Y-%m-%d')

    if len(tstype.strip()) == 0:
        dateDiff = timedelta(weeks = 50)
    elif tstype == 'w':
        dateDiff = timedelta(weeks = 50)
    elif tstype == 'm':
        dateDiff = timedelta(weeks = 24)
    elif tstype == 'd':
        dateDiff = timedelta(days = 50)
    if (len(datas['tdate']) == 0):
        fdate = datetime.now() - dateDiff
    else:
        fdate = tdate - dateDiff


    clusterchosen = '*' if len(datas['Cluster']) == 0 else datas['Cluster']
    period = 'week'   #default value is week
    if len(tstype) == 0:
        period = 'week'
    elif tstype == 'd':
        period = 'day'
    elif tstype == 'w':
        period = 'week'
    elif tstype == 'm':
        period = 'month'

    tiledata = query_tracer_percentile(fdate, tdate, clusterchosen, period)
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