
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, flash,redirect, json
import forms
from model import session_context, Salesorder, MDB
from sqlalchemy  import and_
from flask import jsonify



blueprint = Blueprint( 'salesorder', __name__,
                        template_folder = 'templates',
                        static_folder   = 'static' )



@blueprint.route( '/', methods=['GET', 'POST'])
@blueprint.route( '/soinq', methods=['GET', 'POST'])
def pointoforigin():

    form = forms.OrderOption(request.form)

    if request.method == 'POST':

        if request.form.get('lookup') != None:
           if form.order_id.data and form.subdomain.data:
               acct_id = MDB.get_loggly_id(form.subdomain.data)
               if acct_id is not None:
                   with session_context() as s:
                       sord = s.query( Salesorder) \
                           .filter( and_( Salesorder.order_id == form.order_id.data, Salesorder.acct_id == acct_id ))
               else:
                    form.stateind.data = 'e'
                    flash('Enter a valid value of Order ID or Sub-Domain', category='info')
                    return render_template('salesorder/initiatequery.html', form=form)
           elif form.subdomain.data:
               acct_id = MDB.get_loggly_id(form.subdomain.data)
               with session_context() as s:
                   sord = s.query( Salesorder) \
                        .filter( Salesorder.acct_id == acct_id )
           elif form.order_id.data:
                with session_context() as s:
                    sord = s.query( Salesorder) \
                        .filter( Salesorder.order_id == form.order_id.data )
           else:
                form.stateind.data = 'e'
                flash('Enter a valid value of Order ID or Sub-Domain', category='info')
                return render_template('salesorder/initiatequery.html', form=form)


           if sord.first():
               res = sord.first()
               form=forms.SalesOrder()
               form.billing_channel.data = res.billing_channel
               form.order_id.data = int(res.order_id)
               form.effective_date.data = res.effective_date
               form.subdomain.data = MDB.get_loggly_name(int(res.acct_id))
               form.volume.data = int(res.volume)
               form.plan_type.data = res.plan_type
               form.ret_days.data = int(res.ret_days)
               form.tier_name.data = res.tier_name
               return render_template('salesorder/upsertorder.html', form=form)
           else:
               form.stateind.data = 'e'
               flash('Enter a valid value of Order ID or Sub-Domain')
               return render_template('salesorder/initiatequery.html', form=form)

        elif request.form.get('create') != None:
            return render_template('salesorder/upsertorder.html', form=forms.SalesOrder())
        else:
            return render_template('salesorder/initiatequery.html', form=form)


    else:
        form.stateind.data = 'i'
        return render_template('salesorder/initiatequery.html', form=form)


@blueprint.route( '/orderdetails', methods=['GET', 'POST'] )
def upsertorderdetails():
    if request.form.get('Inquire') != None:
        return redirect("/salesorder")

    form = forms.SalesOrder(request.form)
    so = Salesorder()
    if (form.order_id.data == None or form.order_id.data == '') and request.form.get('Update') == 'Add':
        so.billing_channel = form.billing_channel.data
        so.effective_date = form.effective_date.data
        so.plan_type = form.plan_type.data
        so.ret_days = form.ret_days.data
        so.tier_name = form.tier_name.data
        so.volume = form.volume.data
        acct_id = MDB.get_loggly_id(form.subdomain.data)
        if acct_id is None:
            form.stateind.data = 'e'
            flash('Invalid sub doamin specified. The order was not added')
            return render_template('salesorder/upsertorder.html', form=form)
        else:
            so.acct_id = acct_id
        with session_context() as s:
            s.add(so)
        form.stateind.data = 's'
        flash('The order was added', category='message')
        return render_template('salesorder/upsertorder.html', form=forms.SalesOrder())
    else:
        if request.form.get('Update') == 'Update':
            try:
                if form.validate():
                    with session_context() as s:
                        sord = s.query(Salesorder)\
                            .filter(Salesorder.order_id == form.order_id.data).one()
                        #import ipdb;ipdb.set_trace()
                        acct_id = MDB.get_loggly_id(form.subdomain.data)
                        if acct_id is not None:
                            sord.acct_id = acct_id
                        else:
                            form.stateind.data = 'e'
                            flash('Invalid sub domain specified')
                            return render_template('salesorder/upsertorder.html', form=form)
                        sord.billing_channel = form.billing_channel.data
                        sord.effective_date = form.effective_date.data
                        sord.plan_type = form.plan_type.data
                        sord.ret_days = form.ret_days.data
                        sord.tier_name = form.tier_name.data
                        sord.volume = form.volume.data
                        sord.order_id = form.order_id.data
                        s.commit()
                        form.stateind.data = 's'
                        flash('The order was updated')

            except:
                form.stateind.data = 'e'
                flash('The order was not updated. It did not pass Validation checks')
            finally:
                return render_template('salesorder/upsertorder.html', form=form)


@blueprint.route( '/custs', methods=['GET'] )
def autocomplete():
    bs = request.args.get('term', '')
    customers = MDB.get_loggly_match(bs)
    rowlist = customers.all()
    custacct = [items[0] for items in rowlist]
    return json.dumps(custacct)
