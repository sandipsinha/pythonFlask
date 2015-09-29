from wtforms import Form, fields, validators, HiddenField, ValidationError
import datetime
from datetime import datetime, date
#from wtforms.ext.dateutil.fields import DateTimeField


def validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False

class tbrep(Form):

    tier = fields.SelectField('Tier',choices=[('Pro','Pro'),('Standard','Standard')])
    volume = fields.StringField('Volume')
    retention = fields.IntegerField('Retention')
    sub_rate = fields.IntegerField('Subscription Rate')
    billing_period = fields.SelectField('Billing Period', choices=[('Annual','Annual'),('Monthly','Monthly')])
    created  = fields.StringField('Created Date',[validators.InputRequired()])
    rep_name  = fields.StringField('Rep Name')
    acct_id = fields.HiddenField(' ')
    subdomain = fields.HiddenField(' ')
    sales_rep_id = fields.HiddenField(' ')
    mode = fields.HiddenField(' ')
    orig_created = fields.HiddenField(' ')











