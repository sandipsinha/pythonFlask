__author__ = 'ssinha'
from flask              import Blueprint, jsonify, request, Response, json
from law.util.queries   import query_tracer_bullet, get_cluster_names, query_tracer_percentile, query_tracer_average
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
    isithot = request.form.get('isithot')
    clusterchosen = '*' if (scluster is None or len(scluster) == 0) else scluster
    tracers = query_tracer_bullet(fromDate, endDate, clusterchosen, True if isithot == 'true' else False)
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

def calc_start_date(tdate, dateind, period):
    if len(dateind.strip()) == 0:
        dateDiff = timedelta(days = period)
    elif dateind == 'w':
        dateDiff = timedelta(weeks = period)
    elif dateind == 'rw':
        dateDiff = timedelta(weeks = period)
    elif dateind == 'm':
        dateDiff = timedelta(weeks = period * 4)
    elif dateind == 'rm':
        dateDiff = timedelta(weeks = period * 4)
    elif dateind == 'd':
        dateDiff = timedelta(days = period)
    fdate = tdate - dateDiff

    return fdate

def convert_time_period(dateind):
    cperiod = 'week'
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
    return cperiod


@blueprint.route( '/tracerpercentile/', methods = ['GET', 'POST'])
def tracer_percentile():
    datas = request.json
    dateind = datas.get('dateind')
    period = int(datas.get('periods'))
    isithot = request.form.get('isithot')
    tdate =  datetime.now() if len(datas['tdate']) == 0 else datetime.strptime(datas['tdate'],'%Y-%m-%d %H:%M:%S')

    fdate = calc_start_date(tdate, dateind, period)

    clusterchosen = '*' if len(datas['Cluster']) == 0 else datas['Cluster']
    cperiod = convert_time_period(dateind)

    fdate = fdate.date()
    tdate = tdate.date()
    tiledata = query_tracer_percentile(fdate, tdate, clusterchosen, cperiod, True if isithot == 'true'  else False)
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
        graphitem['pcnt_LT30']   = float("{0:.4f}".format(rows.pcnt_LT30))
        graphitem['start_date']  = rows.start_date.strftime('%Y-%m-%d')
        if clusterchosen != '*' and clusterchosen != rows.repcluster:
            pass
        else:
            graphlist.append(graphitem)

    return json.dumps(graphlist)


@blueprint.route( '/traceraverage/', methods = ['GET', 'POST'])
def tracer_average():
    datas = request.json
    dateind = datas.get('dateind')
    period = int(datas.get('periods'))
    isithot = request.form.get('isithot')
    tdate = datetime.strptime(datas['tdate'],'%Y-%m-%d %H:%M:%S')

    fdate = calc_start_date(tdate, dateind, period)

    cperiod = convert_time_period(dateind)

    fdate = fdate.date()
    tdate = tdate.date()
    summdata = query_tracer_average(fdate, tdate, cperiod, True if isithot == 'true' else False)
    graphlist = []
    for rows in summdata:
        graphitem = {}
        graphitem['average']   = float("{0:.4f}".format(rows.average))
        graphitem['start_date']  = rows.start_date.strftime('%Y-%m-%d')
        graphlist.append(graphitem)

    return json.dumps(graphlist)


@blueprint.route( '/getclusters', methods=['GET'] )
def autocomplete():
    bs = request.args.get('term', '')
    clsdtl = get_cluster_names(bs)
    rowlist = clsdtl.fetchall()
    clsnames = [items[0] + '|' + items[1]  for items in rowlist]
    return json.dumps(clsnames)