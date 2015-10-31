__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_tracer_bullet, get_cluster_names, query_tracer_percentile
from datetime           import datetime, timedelta
from law.util             import touchbiz



blueprint = Blueprint( 'rest.tracer', __name__ )

@blueprint.route( '/tracergrid/', methods = ['GET', 'POST'])
def tracer_data():
    fdate = request.form.get('fdate')
    tdate = request.form.get('tdate')
    scluster = request.form.get('cluster')
    fromDate = datetime.strptime(fdate,'%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(tdate,'%Y-%m-%d %H:%M:%S')


    clusterchosen = '*' if (scluster is None or len(scluster) == 0) else scluster
    tracers = query_tracer_bullet(touchbiz.localize_time(fromDate), touchbiz.localize_time(endDate), clusterchosen)
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
    dateind = datas.get('dateind')
    period = int(datas.get('periods'))
    tdate = datetime.strptime(datas['tdate'],'%Y-%m-%d %H:%M:%S')

    if len(dateind.strip()) == 0:
        dateDiff = timedelta(days = period)
    elif dateind == 'w':
        dateDiff = timedelta(weeks = period)
    elif dateind == 'm':
        dateDiff = timedelta(weeks = period * 4)
    elif dateind == 'd':
        dateDiff = timedelta(days = period)
    if (len(datas['tdate']) == 0):
        fdate = datetime.now() - dateDiff
    else:
        fdate = tdate - dateDiff


    clusterchosen = '*' if len(datas['Cluster']) == 0 else datas['Cluster']
    cperiod = 'week'   #default value is week
    if len(dateind) == 0:
        cperiod = 'week'
    elif dateind == 'd':
        cperiod = 'day'
    elif dateind == 'w':
        cperiod = 'week'
    elif dateind == 'm':
        cperiod = 'month'
    elif dateind == 'rm':
        cperiod = 'rolling30'
    elif dateind == 'rw':
        cperiod = 'rolling7'

    tiledata = query_tracer_percentile(touchbiz.localize_time(fdate), touchbiz.localize_time(tdate), clusterchosen, cperiod)
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