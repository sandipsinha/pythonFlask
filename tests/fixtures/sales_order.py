from datetime import datetime

from model import Salesorder

MODEL = Salesorder
FIXTURES = [
{
    'order_id'       : 958,
    'volume'         : 400,
    'ret_days'       : 5,
    'plan_type'      : 'Pro',
    'tier_name'      : 'Top tier',
    'acct_id'        : 1000,
    'billing_channel': 'Channel 2',
    'effective_date' :  '2015-06-01',
},
{
    'order_id'       : 959,
    'volume'         : 300,
    'ret_days'       : 10,
    'plan_type'      : 'Economy',
    'tier_name'      : 'Top tier2',
    'acct_id'        : 1002,
    'billing_channel': 'Channel 2',
    'effective_date' :  '2015-06-15',
},
]
