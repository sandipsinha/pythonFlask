__author__ = 'ssinha'
"""
" Copyright:    Loggly, Inc.
" Author:       Sandip Sinha
" Email:        ssinha@loggly.com
"
"""
from flask                import Blueprint, render_template, request, url_for, flash,redirect
from law.web.touchbiz     import rest
import forms
from model import session_context, Salesorder
from sqlalchemy  import and_

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
                with session_context() as s:
                    sord = s.query( Salesorder) \
                        .filter( and_( Salesorder.order_id == form.order_id.data, Salesorder.subdomain == form.subdomain.data ))
            elif form.subdomain.data:
                with session_context() as s:
                    sord = s.query( Salesorder) \
                        .filter( Salesorder.subdomain == form.subdomain.data )
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
                form.order_id.data = res.order_id
                form.effective_date.data = res.effective_date
                form.subdomain.data = res.subdomain
                form.volume.data = res.volume
                form.plan_type.data = res.plan_type
                form.ret_days.data = res.ret_days
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
def upsertorderdetails(id=None):
    if request.form.get('Inquire') != None:
        return redirect("/salesorder")

    form = forms.SalesOrder(request.form)
    so = Salesorder()
    if (form.order_id.data == None or form.order_id.data == '') and request.form.get('Add') != None:
        so.order_id = form.order_id.data
        so.subdomain = form.subdomain.data
        so.billing_channel = form.billing_channel.data
        so.effective_date = form.effective_date.data
        so.plan_type = form.plan_type.data
        so.ret_days = form.ret_days.data
        so.tier_name = form.tier_name.data
        so.volume = form.volume.data
        with session_context() as s:
            s.add(so)
        form.stateind.data = 's'
        flash('The order was added', category='message')
        return render_template('salesorder/upsertorder.html', form=forms.SalesOrder())
    else:
        if request.form.get('Update') != None:
            with session_context() as s:
                sord = s.query(Salesorder)\
                        .filter(Salesorder.order_id == form.order_id.data)

                if sord.first():
                    s.subdomain = form.subdomain.data
                    s.billing_channel = form.billing_channel.data
                    s.effective_date = form.effective_date.data
                    s.plan_type = form.plan_type.data
                    s.ret_days = form.ret_days.data
                    s.tier_name = form.tier_name.data
                    s.volume = form.volume.data
                    s.commit()
                    flash('The order was updated')
                    return render_template('salesorder/upsertorder.html', form=form)

                else:
                    flash('Please provide a valid ID or a subdomain to lookup')
                    return render_template('salesorder/initiatequery.html', form=form)

