"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
from datetime import datetime

from law.util.adb_touchbiz import Touchbiz

MODEL = Touchbiz
FIXTURES = [
{
    'acct_id'       : 1000,
    'sales_rep_id'  : 2,
    'created'       : datetime( 2014, 5, 9 ),
    'modified'      : datetime( 2014, 5, 9 ),
    'stage_id'      : 2,
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
{
    'acct_id'       : 1001,
    'sales_rep_id'  : 2,
    'created'       : datetime( 2014, 5, 7 ),
    'modified'      : datetime( 2014, 5, 7 ),
    'stage_id'      : 2,
    'tier'          : 'Development',
    'retention'     : 7,
    'volume'        : 100000000000,
    'sub_rate'      : 49,
    'billing_period': 'monthly',
},
]
