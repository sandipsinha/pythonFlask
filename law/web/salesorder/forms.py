from wtforms import Form, fields, validators, HiddenField, ValidationError
import datetime
from datetime import datetime, date
#from wtforms.ext.dateutil.fields import DateTimeField
import model as model

def validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False

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
    effective_date = fields.StringField('Effective Date',[validators.InputRequired()])
    order_id = fields.HiddenField(' ')
    stateind = fields.HiddenField(' ')

    def validate(self):
        rv = Form.validate(self)
        if not rv: raise ValidationError('Did not pass edits')

        if not validate(self.effective_date.data):
            raise ValidationError('Date is not in the right format')

        return True









