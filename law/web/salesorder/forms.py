from wtforms import Form, fields, validators, HiddenField
#from wtforms.ext.dateutil.fields import DateTimeField
import model as model

class OrderOption(Form):
    order_id = fields.IntegerField('Order ID')
    subdomain = fields.StringField('Sub Domain')
    stateind = fields.HiddenField(' ')

class SalesOrder(Form):
    subdomain = fields.StringField('Sub Domain', [validators.InputRequired(), validators.Length(max=100)])
    volume = fields.IntegerField('Volume')
    ret_days = fields.IntegerField('Retiring Days')
    plan_type = fields.StringField('Plan Type')
    tier_name = fields.StringField('Tier Name')
    billing_channel = fields.StringField('Billing Channel')
    effective_date = fields.StringField('Effective Date')
    order_id = fields.HiddenField(' ')
    stateind = fields.HiddenField(' ')

    def validate(self):
        rv = Form.validate(self)
        if not rv: return False

        if model.Salesorder.query.filter_by(subdomain=self.subdomain.data):
            pass







