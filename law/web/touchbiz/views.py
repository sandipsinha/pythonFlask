"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from flask                import Blueprint, render_template, request, url_for, json, request, jsonify,flash
from law.web.touchbiz     import rest
from law.util             import touchbiz
from datetime import datetime
import forms
from law.util.touchbizdb   import (sales_rep_session,Touchbiz, SalesReps )
from law.util.touchbiz import acct_id_for_subdomain, localize_time
from sqlalchemy.sql import and_


blueprint = Blueprint( 'touchbiz', __name__, 
                        template_folder = 'templates',
                        static_folder   = 'static' )

@blueprint.route( '/<string:subd>/table' )
def table(subd):
    data = rest.history( subd )
    return render_template( 'touchbiz/touchbiz_table.html', **{
        'data': data,
        'subdomain':subd,
    })

@blueprint.route( '/<string:subd>/latest' )
def latest( subd ):
    latest = rest.latest( subd )
    return render_template( 'touchbiz/touchbiz_latest.html', **{
        'new_url': url_for( 'rest.touchbiz.new', subd=subd ),
        'data': latest,
    })

@blueprint.route( '/realign/<string:subd>', methods=['GET'])
def display_tbrep_info(subd):

    return render_template('touchbiz/touchbiz_add_rep.html', grid2=subd,form=forms.tbrep(),mode='i')

@blueprint.route( '/getrep', methods=['GET', 'POST'] )
def re_align( ):
    subd = request.form.get('subdomain',' ')
    tblist = []
    recid = 0
    tblqueue = {}

    import ipdb;ipdb.set_trace()
    keyval = acct_id_for_subdomain(subd)
    #import ipdb;ipdb.set_trace()
    data = rest.history( subd )
    #import ipdb;ipdb.set_trace()
    for row in list(reversed(data)):
        tbqueue = {}
        #import ipdb;ipdb.set_trace()
        if row.get('created') != 'pending' and row.get('created') != None:
            get_tb_data = rest.get_tb_rows(keyval, touchbiz.localize_time(row.get('created')) )
            modestate = 'u'
            tbqueue['tb_created_dt'] = get_tb_data.created
            tbqueue['tb_rep_id'] = get_tb_data.sales_rep_id
        else:
            modestate = 'i'

        tbqueue['statemode'] = modestate
        tbqueue['rep_name'] = row.get('owner')
        tbqueue['tier'] = row.get('tier')
        tbqueue['retention'] = row.get('retention')
        tbqueue['volume'] = row.get('volume')
        tbqueue['billing_period'] = row.get('period')
        tbqueue['sub_rate'] = row.get('rate')
        recid += 1
        tbqueue['recid'] = recid
        tbqueue['acct_id'] = keyval
        tbqueue['created'] = row.get('created')
        tblist.append(tbqueue)
    if recid > 0:
        tblqueue['status'] = 'success'
        tblqueue['total'] = recid
        tblqueue['records'] = tblist

    return json.dumps(tblqueue)

@blueprint.route( '/updatetb', methods=['GET', 'POST'] )
@blueprint.route( '/updatetb/<string:subd>/<string:created>', methods=['GET', 'POST'] )
def upserttb():
    tbform = forms.tbrep(request.form)
    #import ipdb;ipdb.set_trace()
    if request.form.get('Update') is None and request.form.get('Insert') is None:
        return render_template('touchbiz/touchbiz_add_rep.html', grid2=tbform.subdomain.data,form=forms.tbrep(),mode='i')

    if tbform.validate():
        if request.form.get('Update') == 'Update':
            with sales_rep_session() as s:
                tbrep = s.query(Touchbiz).filter(and_(Touchbiz.acct_id==tbform.acct_id.data ,Touchbiz.created == tbform.orig_created.data)).one()

                tbrep.sales_rep_id = tbform.sales_rep_id.data
                tbrep.volume = tbform.volume.data
                tbrep.acct_id = tbform.acct_id.data
                tbrep.billing_period = tbform.billing_period.data
                tbrep.retention = tbform.retention.data
                tbrep.sub_rate = tbform.sub_rate.data
                tbrep.tier = tbform.tier.data
                tbrep.created = tbform.created.data
                tbrep.modified = datetime.now()
                s.commit()

        if request.form.get('Insert') == 'Insert':

                subd = tbform.subdomain.data
                acct_id  = touchbiz.acct_id_for_subdomain( subd )
                with sales_rep_session() as s:
                    tbrep = Touchbiz()
                    tbrep.sales_rep_id = tbform.sales_rep_id.data
                    tbrep.volume = tbform.volume.data
                    tbrep.acct_id = tbform.acct_id.data
                    tbrep.volume = tbform.volume.data
                    tbrep.billing_period = tbform.billing_period.data
                    tbrep.retention = tbform.retention.data
                    tbrep.sub_rate = tbform.sub_rate.data
                    tbrep.tier = tbform.tier.data
                    tbrep.created = tbform.created.data
                    tbrep.acct_id = acct_id
                    tbrep.modified = datetime.now()
                    s.add(tbrep)
                    s.commit()
    else:
        mod = 'a' if request.form.get('Insert') == 'Insert' else 'e'
        flash('Sales Rep fields did not pass validation checks', category='info')
        return render_template('touchbiz/touchbiz_add_rep.html', grid2=tbform.subdomain.data,form=forms.tbrep(),mode='i')

    return render_template('touchbiz/touchbiz_add_rep.html', grid2=tbform.subdomain.data,form=forms.tbrep(),mode='i')






